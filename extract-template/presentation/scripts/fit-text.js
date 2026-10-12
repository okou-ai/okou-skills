/* Fit each page's content at descending source-relative steps; restore on failure. */
(() => {
  const M = window.PresentationMetrics;
  if (!M) throw new Error("Load dom-metrics.js before fit-text.js");
  const properties = ["font-size", "line-height", "letter-spacing"];
  const STEPS = [0.95, 0.9, 0.85, 0.8];
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
  function apply(items, scale) {
    for (const item of items) {
      item.element.style.setProperty("font-size", `${item.size * scale}px`, "important");
      if (Number.isFinite(item.lineHeight)) item.element.style.setProperty("line-height", `${item.lineHeight * scale}px`, "important");
      if (Number.isFinite(item.tracking)) item.element.style.setProperty("letter-spacing", `${item.tracking * scale}px`, "important");
    }
  }
  function contentOf(stage) {
    const roots = [...stage.querySelectorAll(".fit")];
    if (roots.length !== 1) throw new Error("Each page needs exactly one .fit content root");
    return roots[0];
  }
  function regionsOf(content) {
    const explicit = [...content.querySelectorAll("[data-fit-region]")];
    if (explicit.some(region => region.querySelector("[data-fit-region]"))) throw new Error("Fit regions must not be nested");
    return [content, ...explicit];
  }
  function pageState(content) {
    // Regions retain their local bounds, but share one scale for the whole page.
    const states = regionsOf(content).map(M.regionState);
    return states.includes("unmeasurable") ? "unmeasurable" : states.includes("overflow") ? "overflow" : "fits";
  }
  function minimumFont(stage) {
    const sizes = M.leaves(stage).filter(M.visible).map(M.logicalFontSize);
    for (const element of [stage, ...stage.querySelectorAll("*")].filter(M.visible)) {
      for (const pseudo of ["::before", "::after"]) {
        const style = getComputedStyle(element, pseudo);
        if (["none", "normal", '""', "''"].includes(style.content) || style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) continue;
        sizes.push(parseFloat(style.fontSize) * M.fontFactor(element));
      }
    }
    return Math.min(...sizes);
  }
  function clearState(content) {
    for (const region of regionsOf(content)) {
      delete region.dataset.fitState;
      delete region.dataset.fitScale;
      if (region.dataset.overflow === "fit-floor") delete region.dataset.overflow;
    }
  }
  function recordState(content, result) {
    content.dataset.fitState = result.status;
    content.dataset.fitScale = result.scale.toFixed(3);
    if (result.status === "fit-floor") content.dataset.overflow = "fit-floor";
  }
  // CSSOM rounds computed font sizes; allow a subpixel rounding error at 80%.
  const withinScaleLimit = (leaves, baseline) => leaves.every((element, index) =>
    M.logicalFontSize(element) >= baseline[index] * 0.8 - 0.001);
  async function execute(root, options) {
    const started = performance.now();
    const stages = [...root.querySelectorAll(".stage")];
    if (root.matches(".stage")) stages.unshift(root);
    const report = {status: "BLOCKED", minFontSizePx: M.MIN_FONT_SIZE_PX, regions: [], errors: [], elapsedMs: 0};
    const undo = [];
    const completed = new Map();
    const allElements = new Set();
    try {
      if (!stages.length) throw new Error("EMPTY_DECK");
      for (const stage of stages) undo.push(M.revealStage(stage));
      for (const stage of stages) {
        const content = contentOf(stage);
        clearState(content);
        for (const element of [...M.leaves(stage), ...fontElements(content)]) allElements.add(element);
      }
      for (const element of allElements) restore(element);
      await M.assetsReady(root, options.allowedFontFallbacks || []);
      const originalSizes = new Map([...allElements].map(element => [element, M.logicalFontSize(element)]));
      for (const [index, stage] of stages.entries()) {
        const content = contentOf(stage);
        const leaves = M.leaves(content);
        const items = records(fontElements(content));
        const result = {page: index + 1, region: "content", scale: 1,
          baselineSizesPx: leaves.map(element => originalSizes.get(element)), status: "unchanged"};
        const initial = pageState(content);
        if (initial === "unmeasurable") result.status = "unmeasurable";
        else if (initial === "overflow") {
          result.status = "fit-floor";
          result.reason = "Content cannot fit within 95/90/85/80% and the 11px minimum; inspect geometry, recompose or split";
          for (const step of STEPS) {
            apply(items, step);
            if (!(minimumFont(stage) >= M.MIN_FONT_SIZE_PX - 1e-6)) break;
            if (!withinScaleLimit(leaves, result.baselineSizesPx)) break;
            const state = pageState(content);
            if (state === "unmeasurable") { result.status = state; break; }
            if (state === "fits") {
              result.scale = step;
              result.status = "fitted";
              delete result.reason;
              break;
            }
          }
          if (result.status !== "fitted") items.forEach(({element}) => restore(element));
        }
        recordState(content, result);
        report.regions.push(result);
        completed.set(content, {result, items, leaves});
      }
      // Recheck committed geometry; a failed page always returns to its source styles.
      for (const stage of stages) {
        const content = contentOf(stage);
        const {result, items, leaves} = completed.get(content);
        if (["fitted", "unchanged"].includes(result.status) && (pageState(content) !== "fits" ||
          (result.status === "fitted" && (!(minimumFont(stage) >= M.MIN_FONT_SIZE_PX - 1e-6) ||
            !withinScaleLimit(leaves, result.baselineSizesPx))))) {
          items.forEach(({element}) => restore(element));
          result.status = "fit-floor"; result.scale = 1;
          result.reason = "Page geometry changed after fitting; source typography restored";
          recordState(content, result);
        }
        result.finalSizesPx = leaves.map(M.logicalFontSize);
      }
      report.status = report.regions.every(region => ["unchanged", "fitted"].includes(region.status)) ? "READY" : "BLOCKED";
    } catch (error) {
      for (const element of allElements) restore(element);
      for (const [content, {result, leaves}] of completed) {
        result.status = "unmeasurable"; result.scale = 1;
        result.finalSizesPx = leaves.map(M.logicalFontSize);
        recordState(content, result);
      }
      report.errors.push(error.message);
    }
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
      for (const content of root.querySelectorAll(".fit")) clearState(content);
      api.report = null;
      delete root.dataset.fitStatus;
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
