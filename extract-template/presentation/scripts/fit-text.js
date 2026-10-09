/* Fit only declared text regions. Source styles are baselines, never minimums. */
(() => {
  const M = window.PresentationMetrics;
  if (!M) throw new Error("Load dom-metrics.js before fit-text.js");
  const properties = ["font-size", "line-height", "letter-spacing"];
  const queues = new WeakMap();
  function restore(element) {
    if (!element.hasAttribute("data-presentation-baseline")) {
      element.setAttribute("data-presentation-baseline", JSON.stringify(properties.map(name =>
        [name, element.style.getPropertyValue(name), element.style.getPropertyPriority(name)])));
    }
    for (const [name, value, priority] of JSON.parse(element.getAttribute("data-presentation-baseline"))) {
      if (value) element.style.setProperty(name, value, priority);
      else element.style.removeProperty(name);
    }
  }
  function fontElements(region) {
    const elements = new Set(M.leaves(region));
    for (const leaf of [...elements]) {
      if (leaf instanceof SVGElement) continue;
      for (let parent = leaf.parentElement; parent && region.contains(parent); parent = parent.parentElement) {
        const display = getComputedStyle(parent).display;
        if (!/flex|grid|table/.test(display) && !parent.querySelector("img,svg")) elements.add(parent);
        if (parent === region) break;
      }
    }
    return [...elements];
  }
  function records(elements) {
    return elements.map(element => {
      const style = getComputedStyle(element);
      return {element, size: parseFloat(style.fontSize), lineHeight: parseFloat(style.lineHeight), tracking: parseFloat(style.letterSpacing)};
    });
  }
  function clampFloor(elements) {
    for (let pass = 0; pass < 3; pass++) {
      let changed = false;
      for (const element of elements) {
        const factor = M.fontFactor(element);
        if (!(factor > 0)) throw new Error("Text geometry is unmeasurable");
        const size = parseFloat(getComputedStyle(element).fontSize);
        if (size * factor < M.MIN_FONT_SIZE_PX - 1e-6) {
          element.style.setProperty("font-size", `${(M.MIN_FONT_SIZE_PX + 0.0001) / factor}px`, "important");
          changed = true;
        }
      }
      if (!changed) return;
    }
    if (elements.some(element => M.logicalFontSize(element) < M.MIN_FONT_SIZE_PX - 1e-6)) throw new Error("10px floor could not be applied");
  }
  function apply(items, scale) {
    for (const item of items) {
      const factor = M.fontFactor(item.element);
      if (!(factor > 0)) throw new Error("Text geometry is unmeasurable");
      const size = Math.max((M.MIN_FONT_SIZE_PX + 0.0001) / factor, item.size * scale);
      const ratio = size / item.size;
      item.element.style.setProperty("font-size", `${size}px`, "important");
      if (Number.isFinite(item.lineHeight)) item.element.style.setProperty("line-height", `${item.lineHeight * ratio}px`, "important");
      if (Number.isFinite(item.tracking)) item.element.style.setProperty("letter-spacing", `${item.tracking * ratio}px`, "important");
    }
    clampFloor(items.map(item => item.element));
  }
  function regionsOf(stage) {
    const explicit = [...stage.querySelectorAll("[data-fit-region]")];
    if (explicit.some(region => region.querySelector("[data-fit-region]"))) throw new Error("Fit regions must not be nested");
    return explicit.length ? explicit : [...stage.querySelectorAll(".fit")];
  }
  async function execute(root, options) {
    const started = performance.now();
    const stages = [...root.querySelectorAll(".stage")];
    if (root.matches(".stage")) stages.unshift(root);
    const report = {status: "BLOCKED", minFontSizePx: M.MIN_FONT_SIZE_PX, regions: [], errors: [], elapsedMs: 0};
    const undo = [];
    const completed = new Map();
    try {
      if (!stages.length) throw new Error("EMPTY_DECK");
      for (const stage of stages) undo.push(M.revealStage(stage));
      const allElements = new Set(stages.flatMap(stage => [...M.leaves(stage), ...regionsOf(stage).flatMap(fontElements)]));
      for (const element of allElements) restore(element);
      await M.assetsReady(root, options.allowedFontFallbacks || []);
      const originalSizes = new Map([...allElements].map(element => [element, M.logicalFontSize(element)]));
      clampFloor([...allElements]);
      for (const [index, stage] of stages.entries()) {
        const regions = regionsOf(stage);
        if (!regions.length) throw new Error(`Page ${index + 1} has no .fit content root`);
        for (const region of regions) {
          const leaves = M.leaves(region);
          const items = records(fontElements(region));
          const result = {page: index + 1, region: region.dataset.fitRegion || "content", scale: 1,
            baselineSizesPx: leaves.map(element => originalSizes.get(element)), status: "unchanged"};
          if (M.regionState(region) === "unmeasurable") result.status = "unmeasurable";
          else if (M.regionState(region) !== "fits") {
            if (!items.length) result.status = "unresolved";
            else {
              apply(items, 0);
              if (M.regionState(region) !== "fits") {
                apply(items, 1);
                result.status = "unresolved";
                result.reason = "Content cannot fit at the 10px minimum; change layout or split";
              } else {
                let low = 0, high = 1;
                for (let attempt = 0; attempt < 14; attempt++) {
                  const midpoint = (low + high) / 2;
                  apply(items, midpoint);
                  if (M.regionState(region) === "fits") low = midpoint; else high = midpoint;
                }
                apply(items, low);
                result.scale = low;
                result.status = "fitted";
              }
            }
          }
          result.finalSizesPx = leaves.map(M.logicalFontSize);
          region.dataset.fitState = result.status;
          report.regions.push(result);
          completed.set(region, result);
        }
      }
      // Font changes may reflow neighbouring regions. Recheck the committed geometry.
      for (const stage of stages) {
        for (const region of regionsOf(stage)) {
          const result = completed.get(region);
          if (M.regionState(region) !== "fits" && ["fitted", "unchanged"].includes(result.status)) {
            result.status = "unresolved"; result.reason = "Peer geometry changed after fitting";
            region.dataset.fitState = result.status;
          }
        }
      }
      report.status = report.regions.every(region => ["unchanged", "fitted"].includes(region.status)) ? "READY" : "BLOCKED";
    } catch (error) { report.errors.push(error.message); }
    finally { undo.reverse().forEach(restoreHidden => restoreHidden()); }
    report.elapsedMs = performance.now() - started;
    api.report = report;
    root.dataset.fitStatus = report.status;
    return report;
  }
  const api = {
    minFontSizePx: M.MIN_FONT_SIZE_PX,
    report: null,
    ready: Promise.resolve(),
    fit(root = document.documentElement, options = window.PRESENTATION_QA_CONFIG || {}) {
      const previous = queues.get(root) || Promise.resolve();
      const promise = previous.catch(() => {}).then(() => execute(root, options));
      queues.set(root, promise);
      api.ready = promise;
      return promise;
    },
    reset(root = document.documentElement) {
      for (const element of root.querySelectorAll("[data-presentation-baseline]")) restore(element);
    },
  };
  window.PresentationFit = api;
  let pending;
  const schedule = () => {
    clearTimeout(pending);
    pending = setTimeout(() => api.fit(), 0);
  };
  const boot = () => {
    if (document.documentElement.dataset.presentationPrepared === "capture") return;
    api.fit();
    new MutationObserver(schedule).observe(document.body, {childList: true, characterData: true, subtree: true, attributes: true, attributeFilter: ["src", "srcset"]});
    window.addEventListener("resize", schedule);
    document.fonts.addEventListener("loadingdone", schedule);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, {once: true}); else boot();
})();
