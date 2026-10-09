/* Shared, style-neutral measurements for presentation fitting and QA. */
(() => {
  const MIN_FONT_SIZE_PX = 10;
  const CANVAS_WIDTH = 1600;
  const ownText = element => [...element.childNodes].filter(node => node.nodeType === 3 && node.textContent.trim());
  const visible = element => {
    for (let node = element; node instanceof Element; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) return false;
    }
    return true;
  };
  const leaves = root => [root, ...root.querySelectorAll("*")].filter(element =>
    element instanceof Element && !element.closest("script,style,template,noscript") && ownText(element).length);
  const stageOf = element => element.closest(".stage,[data-stage]");
  function transformMatrix(element, stop = null) {
    let matrix = new DOMMatrix();
    for (let node = element; node && node !== stop; node = node.parentElement) {
      const value = getComputedStyle(node).transform;
      if (value !== "none") matrix = new DOMMatrix(value).multiply(matrix);
    }
    return matrix;
  }
  function minimumScale(matrix) {
    const sum = matrix.a ** 2 + matrix.b ** 2 + matrix.c ** 2 + matrix.d ** 2;
    const determinant = matrix.a * matrix.d - matrix.b * matrix.c;
    return Math.sqrt(Math.max(0, (sum - Math.sqrt(Math.max(0, sum ** 2 - 4 * determinant ** 2))) / 2));
  }
  function fontFactor(element) {
    const stage = stageOf(element);
    const intrinsic = stage ? stage.clientWidth / CANVAS_WIDTH : 1;
    if (!(intrinsic > 0)) return NaN;
    let matrix;
    if (element instanceof SVGElement && element.getScreenCTM) {
      const screen = element.getScreenCTM();
      if (!screen) return NaN;
      matrix = stage ? transformMatrix(stage).inverse().multiply(screen) : screen;
    } else {
      matrix = transformMatrix(element, stage);
    }
    return minimumScale(matrix) / intrinsic;
  }
  const logicalFontSize = element => parseFloat(getComputedStyle(element).fontSize) * fontFactor(element);
  const textCanvas = document.createElement("canvas").getContext("2d");
  const inkCache = new Map();
  function textRects(element) {
    const style = getComputedStyle(element);
    const font = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
    return ownText(element).flatMap(node => {
      const range = document.createRange();
      range.selectNodeContents(node);
      const key = `${font}|${style.fontVariantCaps}|${node.textContent}`;
      let metrics = inkCache.get(key);
      if (!metrics) {
        textCanvas.font = font;
        if ("fontVariantCaps" in textCanvas) textCanvas.fontVariantCaps = style.fontVariantCaps;
        metrics = textCanvas.measureText(node.textContent);
        if (inkCache.size > 1000) inkCache.clear();
        inkCache.set(key, metrics);
      }
      return [...range.getClientRects()].filter(rect => rect.width > 0 && rect.height > 0).map(rect => {
        // Range boxes include a font's empty ascent/descent, not just painted ink.
        const height = metrics.fontBoundingBoxAscent + metrics.fontBoundingBoxDescent;
        const scale = height > 0 ? rect.height / height : 1;
        const top = rect.top + (metrics.fontBoundingBoxAscent - metrics.actualBoundingBoxAscent) * scale;
        const bottom = rect.bottom - (metrics.fontBoundingBoxDescent - metrics.actualBoundingBoxDescent) * scale;
        return {left: rect.left, right: rect.right, top, bottom, width: rect.width, height: bottom - top};
      });
    });
  }
  function innerBox(element) {
    const rect = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    const x = element.offsetWidth ? rect.width / element.offsetWidth : 1;
    const y = element.offsetHeight ? rect.height / element.offsetHeight : 1;
    return {
      left: rect.left + (parseFloat(style.borderLeftWidth) + parseFloat(style.paddingLeft)) * x,
      right: rect.right - (parseFloat(style.borderRightWidth) + parseFloat(style.paddingRight)) * x,
      top: rect.top + (parseFloat(style.borderTopWidth) + parseFloat(style.paddingTop)) * y,
      bottom: rect.bottom - (parseFloat(style.borderBottomWidth) + parseFloat(style.paddingBottom)) * y,
    };
  }
  const outside = (rect, box, tolerance = 0.5) =>
    rect.left < box.left - tolerance || rect.right > box.right + tolerance || rect.top < box.top - tolerance || rect.bottom > box.bottom + tolerance;
  function textOverflow(element, boundary, tolerance = 0.5) {
    const rectangles = textRects(element);
    if (rectangles.some(rect => outside(rect, boundary, tolerance))) return true;
    for (let node = element; node instanceof Element && !node.classList.contains("stage"); node = node.parentElement) {
      const style = getComputedStyle(node);
      const x = /hidden|clip|auto|scroll/.test(style.overflowX);
      const y = /hidden|clip|auto|scroll/.test(style.overflowY);
      if (!x && !y) continue;
      const rect = node.getBoundingClientRect();
      const kx = node.offsetWidth ? rect.width / node.offsetWidth : 1;
      const ky = node.offsetHeight ? rect.height / node.offsetHeight : 1;
      const left = rect.left + (node.clientLeft || 0) * kx;
      const top = rect.top + (node.clientTop || 0) * ky;
      const box = {left, top, right: left + node.clientWidth * kx, bottom: top + node.clientHeight * ky};
      if (rectangles.some(r => (x && (r.left < box.left - tolerance || r.right > box.right + tolerance)) ||
        (y && (r.top < box.top - tolerance || r.bottom > box.bottom + tolerance)))) return true;
    }
    return false;
  }
  function regionState(region) {
    const stage = stageOf(region);
    const box = innerBox(region);
    if (!stage || !stage.clientWidth || !(box.right > box.left) || !(box.bottom > box.top)) return "unmeasurable";
    const content = region.closest(".fit");
    if (content) {
      const safe = innerBox(content);
      box.left = Math.max(box.left, safe.left); box.right = Math.min(box.right, safe.right);
      box.top = Math.max(box.top, safe.top); box.bottom = Math.min(box.bottom, safe.bottom);
      // Font ink may naturally overhang a non-clipping flow line box. Respect the
      // actual source safe top, not that line box; clipping ancestors remain hard.
      if (getComputedStyle(region).overflowY === "visible") {
        const config = window.PRESENTATION_QA_CONFIG || {};
        const key = stage.dataset.layout || stage.dataset.sourceProfile || "default";
        const area = config.layoutSafeAreas?.[key] || config.safeArea;
        box.top = area && Number.isFinite(area.top) ? stage.getBoundingClientRect().top + stage.getBoundingClientRect().height * area.top : safe.top;
        if (area && Number.isFinite(area.bottom) && Math.abs(box.bottom - safe.bottom) < 0.5) {
          box.bottom = stage.getBoundingClientRect().bottom - stage.getBoundingClientRect().height * area.bottom;
        }
      }
    }
    return leaves(region).some(element => textOverflow(element, box)) ? "overflow" : "fits";
  }
  const frame = () => new Promise(resolve => requestAnimationFrame(resolve));
  const bounded = (promise, label, timeout = 12000) => new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`${label} timed out`)), timeout);
    promise.then(value => { clearTimeout(timer); resolve(value); }, error => { clearTimeout(timer); reject(error); });
  });
  const backgroundUrls = element => [null, "::before", "::after"].flatMap(pseudo => {
    const style = getComputedStyle(element, pseudo);
    if (pseudo && ["none", "normal"].includes(style.content)) return [];
    return [...style.backgroundImage.matchAll(/url\((?:"([^"]*)"|'([^']*)'|([^)]*))\)/g)]
      .map(match => (match[1] ?? match[2] ?? match[3]).trim()).filter(Boolean);
  });
  const familyNames = value => value.split(",").map(name => name.trim().replace(/^['"]|['"]$/g, "").toLowerCase());
  function fontErrors(root, allowedFallbacks = []) {
    const used = new Set(leaves(root).flatMap(element => familyNames(getComputedStyle(element).fontFamily)));
    const allowed = new Set(allowedFallbacks.map(name => name.toLowerCase()));
    return [...document.fonts].filter(face => face.status === "error" && used.has(familyNames(face.family)[0]) && !allowed.has(familyNames(face.family)[0]))
      .map(face => `Font failed: ${face.family}`);
  }
  async function assetsReady(root, allowedFallbacks = []) {
    root.getBoundingClientRect();
    await bounded(frame(), "Layout");
    await bounded(document.fonts.ready, "Fonts");
    const errors = fontErrors(root, allowedFallbacks);
    if (errors.length) throw new Error(errors.join("; "));
    await Promise.all([...root.querySelectorAll("img")].map(async image => {
      if (!image.complete) await bounded(new Promise(resolve => {
        image.addEventListener("load", resolve, {once: true});
        image.addEventListener("error", resolve, {once: true});
      }), "Image");
      if (!image.naturalWidth || !image.naturalHeight) throw new Error(`Image failed: ${image.id || image.alt || "img"}`);
    }));
    const urls = new Set([root, ...root.querySelectorAll("*")].flatMap(backgroundUrls));
    await Promise.all([...urls].map(url => bounded(new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve();
      image.onerror = () => reject(new Error("CSS background image failed"));
      image.src = url;
    }), "Background image")));
    await frame(); await frame();
  }
  function revealStage(stage) {
    const changed = [];
    const undo = () => changed.reverse().forEach(([element, style, hidden]) => {
      if (style === null) element.removeAttribute("style"); else element.setAttribute("style", style);
      if (hidden === null) element.removeAttribute("hidden"); else element.setAttribute("hidden", hidden);
    });
    try {
      for (let element = stage; element && element !== document.body; element = element.parentElement) {
        if (getComputedStyle(element).display !== "none" && !element.hasAttribute("hidden")) continue;
        changed.push([element, element.getAttribute("style"), element.getAttribute("hidden")]);
        element.removeAttribute("hidden"); element.style.removeProperty("display");
        if (getComputedStyle(element).display === "none") {
          const display = element.dataset.fitDisplay;
          if (!display || !CSS.supports("display", display) || /^(none|contents)$/.test(display)) throw new Error("Hidden page needs data-fit-display");
          element.style.setProperty("display", display, "important");
        }
        element.style.setProperty("position", "absolute", "important");
        element.style.setProperty("left", "-100000px", "important");
      }
      return undo;
    } catch (error) { undo(); throw error; }
  }
  window.PresentationMetrics = Object.freeze({MIN_FONT_SIZE_PX, CANVAS_WIDTH, ownText, visible, leaves, stageOf, revealStage,
    fontFactor, logicalFontSize, textRects, innerBox, outside, textOverflow, regionState, frame, bounded, backgroundUrls, fontErrors, assetsReady});
})();
