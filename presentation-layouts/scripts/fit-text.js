/* Template-neutral bounded text fitting. No font-size floor or preset scale. */
(() => {
  const queues = new WeakMap();
  const frame = () => new Promise(resolve => requestAnimationFrame(resolve));
  const bounded = (promise, ms, message) => new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(message)), ms);
    promise.then(value => { clearTimeout(timer); resolve(value); }, error => { clearTimeout(timer); reject(error); });
  });
  const properties = ["font-size", "line-height", "letter-spacing"];
  function leaves(region) {
    return [region, ...region.querySelectorAll("*")].filter(element =>
      !element.closest("svg,[data-decoration]") && [...element.childNodes].some(node => node.nodeType === 3 && node.textContent.trim()));
  }
  function fontElements(region) {
    const result = new Set(leaves(region));
    // Inline text inherits a parent strut. Scale it too, but not em-sized artwork.
    for (const leaf of [...result]) {
      for (let parent = leaf.parentElement; parent && region.contains(parent); parent = parent.parentElement) {
        const display = getComputedStyle(parent).display;
        if (!/flex|grid|^table$|table-row|table-row-group/.test(display) && !parent.querySelector("svg,img")) result.add(parent);
        if (parent === region) break;
      }
    }
    return [...result];
  }
  function restore(element) {
    if (!element.dataset.okpBaselineStyle) {
      element.dataset.okpBaselineStyle = JSON.stringify(properties.map(name => [name, element.style.getPropertyValue(name), element.style.getPropertyPriority(name)]));
    }
    for (const [name, value, priority] of JSON.parse(element.dataset.okpBaselineStyle)) {
      if (value) element.style.setProperty(name, value, priority);
      else element.style.removeProperty(name);
    }
  }
  function reveal(region, root) {
    const changed = [];
    for (let element = region; element && element !== document.body; element = element.parentElement) {
      if (getComputedStyle(element).display === "none" || element.hidden) {
        changed.push([element, ["display", "position", "left"].map(name => [name, element.style.getPropertyValue(name), element.style.getPropertyPriority(name)]), element.hidden]);
        element.hidden = false;
        element.style.setProperty("display", "block", "important");
        element.style.setProperty("position", "absolute", "important");
        element.style.setProperty("left", "-100000px", "important");
      }
      if (element === root && element.getBoundingClientRect().width > 0) break;
    }
    return () => {
      for (const [element, style, hidden] of changed.reverse()) {
        for (const [name, value, priority] of style) {
          if (value) element.style.setProperty(name, value, priority); else element.style.removeProperty(name);
        }
        element.hidden = hidden;
      }
    };
  }
  function bounds(region) {
    const rectangles = [region, region.closest(".okp-main"), region.closest(".okp-layout")].filter(Boolean).map(element => element.getBoundingClientRect());
    return {left: Math.max(...rectangles.map(r => r.left)), right: Math.min(...rectangles.map(r => r.right)), top: Math.max(...rectangles.map(r => r.top)), bottom: Math.min(...rectangles.map(r => r.bottom))};
  }
  function measure(region, tolerance) {
    const box = bounds(region);
    if (box.right <= box.left || box.bottom <= box.top) return "unmeasurable";
    if (region.scrollWidth > region.clientWidth + tolerance || region.scrollHeight > region.clientHeight + tolerance) return "overflow";
    for (const element of leaves(region)) {
      const clips = [];
      for (let parent = element; parent && region.contains(parent); parent = parent.parentElement) {
        const style = getComputedStyle(parent);
        const x = /hidden|clip|auto|scroll/.test(style.overflowX);
        const y = /hidden|clip|auto|scroll/.test(style.overflowY);
        if (x || y) {
          const rect = parent.getBoundingClientRect();
          const scaleX = parent.offsetWidth ? rect.width / parent.offsetWidth : 1;
          const scaleY = parent.offsetHeight ? rect.height / parent.offsetHeight : 1;
          const left = rect.left + parent.clientLeft * scaleX;
          const top = rect.top + parent.clientTop * scaleY;
          clips.push({x, y, left, top, right: left + parent.clientWidth * scaleX, bottom: top + parent.clientHeight * scaleY});
        }
        if (parent === region) break;
      }
      const range = document.createRange();
      range.selectNodeContents(element);
      for (const rect of range.getClientRects()) {
        if (rect.width <= 0 || rect.height <= 0) continue;
        if (rect.left < box.left - tolerance || rect.right > box.right + tolerance || rect.top < box.top - tolerance || rect.bottom > box.bottom + tolerance) return "overflow";
        if (clips.some(clip => (clip.x && (rect.left < clip.left - tolerance || rect.right > clip.right + tolerance)) || (clip.y && (rect.top < clip.top - tolerance || rect.bottom > clip.bottom + tolerance)))) return "overflow";
      }
    }
    return "fits";
  }
  function apply(records, scale) {
    for (const {element, size, lineHeight, letterSpacing} of records) {
      element.style.fontSize = `${size * scale}px`;
      if (Number.isFinite(lineHeight)) element.style.lineHeight = `${lineHeight * scale}px`;
      if (Number.isFinite(letterSpacing)) element.style.letterSpacing = `${letterSpacing * scale}px`;
    }
  }
  async function ready(root, timeoutMs) {
    await bounded(document.fonts.ready, timeoutMs, "Font readiness timeout");
    await Promise.all([...root.querySelectorAll("img")].map(image => {
      if (image.complete) {
        if (!image.naturalWidth) throw new Error("Image load failed");
        return undefined;
      }
      return bounded(new Promise((resolve, reject) => {
        image.addEventListener("load", resolve, {once: true});
        image.addEventListener("error", () => reject(new Error("Image load failed")), {once: true});
      }), timeoutMs, "Image readiness timeout");
    }));
    await frame();
  }
  async function execute(root, policy) {
    const started = performance.now();
    const regions = [...root.querySelectorAll("[data-fit-region]")];
    if (root.matches("[data-fit-region]")) regions.unshift(root);
    const iterations = policy.maxIterations ?? 10;
    const tolerance = policy.tolerancePx ?? 0.5;
    const timeoutMs = policy.timeoutMs ?? 5000;
    if (!Number.isInteger(iterations) || iterations < 1 || iterations > 16 || !Number.isFinite(tolerance) || tolerance < 0 || !Number.isFinite(timeoutMs) || timeoutMs < 1 || timeoutMs > 30000) throw new Error("Invalid bounded fitting policy");
    // Restore every region before measuring; earlier fits cannot taint later baselines.
    for (const region of regions) for (const element of fontElements(region)) restore(element);
    try { await ready(root, timeoutMs); }
    catch (error) {
      return {regions: regions.map(region => ({regionId: region.dataset.fitRegion, status: "unmeasurable", reason: error.message})), elapsedMs: performance.now() - started};
    }
    const results = [];
    const byRegion = new Map();
    for (const region of regions) {
      const hideAgain = reveal(region, root);
      try {
        const records = leaves(region).map(element => {
          const style = getComputedStyle(element);
          return {element, role: element.closest("[data-text-role]")?.dataset.textRole, size: parseFloat(style.fontSize), lineHeight: parseFloat(style.lineHeight), letterSpacing: parseFloat(style.letterSpacing)};
        });
        const allRecords = fontElements(region).map(element => {
          const style = getComputedStyle(element);
          return {element, size: parseFloat(style.fontSize), lineHeight: parseFloat(style.lineHeight), letterSpacing: parseFloat(style.letterSpacing)};
        });
        const result = {slideId: region.closest("[data-slide]")?.dataset.slide, regionId: region.dataset.fitRegion, baselineSizesPx: records.map(r => r.size), scale: 1};
        const initial = measure(region, tolerance);
        if (initial === "unmeasurable" || !records.length || records.some(r => !Number.isFinite(r.size) || r.size <= 0)) {
          result.status = "unmeasurable";
        } else if (initial === "fits") {
          result.status = "unchanged";
        } else {
          let lower = 0;
          let invalid = "";
          for (const record of records) {
            const effectiveRole = policy.roleMap?.[record.role] ?? record.role;
            const limit = policy.roleBounds?.[record.role] ?? policy.roleBounds?.[effectiveRole];
            if (!limit || limit.enabled === false || (limit.minScale === undefined && limit.minFontSizePx === undefined)) { invalid = "Missing or disabled role bound"; break; }
            if ((limit.minScale !== undefined && (!Number.isFinite(limit.minScale) || limit.minScale <= 0 || limit.minScale > 1)) || (limit.minFontSizePx !== undefined && (!Number.isFinite(limit.minFontSizePx) || limit.minFontSizePx <= 0 || limit.minFontSizePx > record.size))) { invalid = "FIT_BOUND_CONFLICT"; break; }
            lower = Math.max(lower, limit.minScale ?? 0, limit.minFontSizePx !== undefined ? limit.minFontSizePx / record.size : 0);
          }
          if (invalid) {
            result.status = "unresolved"; result.reason = invalid;
          } else {
            apply(allRecords, lower);
            if (measure(region, tolerance) !== "fits") {
              for (const record of allRecords) restore(record.element);
              result.status = "unresolved"; result.reason = "Content cannot fit within role bounds";
            } else {
              let low = lower, high = 1;
              for (let i = 0; i < iterations; i++) {
                const mid = (low + high) / 2;
                apply(allRecords, mid);
                if (measure(region, tolerance) === "fits") low = mid; else high = mid;
              }
              apply(allRecords, low);
              result.status = "fitted"; result.scale = low;
            }
          }
        }
        result.finalSizesPx = records.map(r => parseFloat(getComputedStyle(r.element).fontSize));
        results.push(result);
        byRegion.set(region, result);
      } finally { hideAgain(); }
    }
    // A local fit may change the safe area available to its peers.
    for (const region of regions) {
      const result = byRegion.get(region);
      if (!result || !["unchanged", "fitted"].includes(result.status)) continue;
      const hideAgain = reveal(region, root);
      try {
        if (measure(region, tolerance) !== "fits") {
          result.status = "unresolved"; result.reason = "Peer geometry changed after fitting";
        }
      } finally { hideAgain(); }
    }
    return {regions: results, elapsedMs: performance.now() - started};
  }
  const api = {
    fit(root, policy = {}) {
      const previous = queues.get(root) ?? Promise.resolve();
      const promise = previous.catch(() => undefined).then(() => execute(root, policy));
      queues.set(root, promise);
      api.ready = promise;
      return promise;
    },
    reset(root) {
      const regions = [...root.querySelectorAll("[data-fit-region]")];
      if (root.matches("[data-fit-region]")) regions.unshift(root);
      for (const region of regions) for (const element of fontElements(region)) restore(element);
    },
    ready: Promise.resolve()
  };
  window.OkpFit = api;
})();
