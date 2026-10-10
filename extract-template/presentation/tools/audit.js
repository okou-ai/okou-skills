/* Source-configured rendered QA. No built-in palette, motif or crop policy. */
(async () => {
  const M = window.PresentationMetrics;
  const config = window.PRESENTATION_QA_CONFIG || {};
  const report = {pages: 0, navigableSlides: 0, decks: 0, minFontSizePx: 10, status: "BLOCKED", hardGateFailures: 0, blocking: {}, failures: [], reviewRequired: []};
  const fail = (code, page, element, message) => {
    report.hardGateFailures++;
    report.blocking[code] = (report.blocking[code] || 0) + 1;
    if (report.failures.length < 80) report.failures.push({code, page, element: element ? `${element.tagName.toLowerCase()}${element.id ? `#${element.id}` : ""}` : null, message});
  };
  const reviews = new Set();
  const review = (code, page, message) => {
    const key = `${code}:${page}`;
    if (!reviews.has(key)) { reviews.add(key); report.reviewRequired.push({code, page, message}); }
  };
  if (!M) { fail("missingRuntime", 0, null, "Load the packaged dom-metrics.js"); return JSON.stringify(report); }
  await window.PresentationNavigationReady;
  if (config.minFontSizePx !== undefined && config.minFontSizePx !== 10) fail("invalidConfig", 0, null, "The minimum font size is fixed at 10px");
  if (config.minContrastRatio !== undefined && (!Number.isFinite(config.minContrastRatio) || config.minContrastRatio < 3 || config.minContrastRatio > 21)) fail("invalidConfig", 0, null, "minContrastRatio must be within 3..21");
  const decks = [...document.querySelectorAll(".deck")];
  const slides = [...document.querySelectorAll(".slide")];
  const stages = [...document.querySelectorAll(".stage")];
  report.decks = decks.length; report.pages = stages.length;
  report.navigableSlides = decks.reduce((count, deck) => count + [...deck.children].filter(child => child.classList.contains("slide")).length, 0);
  if (decks.length !== 1 || !slides.length || !stages.length) fail("deckStructure", 0, null, "Exactly one nonempty deck is required");
  if (slides.some(slide => !slide.parentElement.classList.contains("deck")) || slides.length !== stages.length || report.navigableSlides !== stages.length) {
    fail("deckStructure", 0, null, "Every direct-child slide must contain exactly one stage");
  }
  for (const slide of slides) if (slide.querySelectorAll(".stage").length !== 1) fail("deckStructure", 0, slide, "Expected one stage per slide");
  const expected = config.expectedPages;
  if (!Number.isInteger(expected) || expected < 1) fail("pageCount", 0, null, "Set a positive expectedPages from the requested story plan");
  else if (stages.length !== expected) fail("pageCount", 0, null, `Rendered ${stages.length} pages, expected ${expected}`);
  const fit = window.PresentationFit;
  if (!fit || !fit.report) fail("missingFit", 0, null, "The shared fitter must finish before QA");
  else {
    for (const error of fit.report.errors) fail("fitReadiness", 0, null, error);
    for (const region of fit.report.regions) if (!["unchanged", "fitted"].includes(region.status)) fail("unresolvedFit", region.page, null, `${region.region}: ${region.reason || region.status}`);
    if (fit.report.status !== "READY" && !fit.report.errors.length && !fit.report.regions.some(region => !["unchanged", "fitted"].includes(region.status))) fail("fitReadiness", 0, null, "Fit report is not ready");
  }
  const context = document.createElement("canvas").getContext("2d", {willReadFrequently: true});
  const color = value => {
    if (value === "none") return [0, 0, 0, 0];
    context.clearRect(0, 0, 1, 1); context.fillStyle = value; context.fillRect(0, 0, 1, 1);
    return [...context.getImageData(0, 0, 1, 1).data].map(channel => channel / 255);
  };
  const composite = (top, bottom) => [0, 1, 2].map(i => top[i] * top[3] + bottom[i] * (1 - top[3])).concat(1);
  const luminance = rgba => rgba.slice(0, 3).map(v => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4).reduce((sum, v, i) => sum + v * [0.2126, 0.7152, 0.0722][i], 0);
  const hasPaint = style => style.backgroundImage !== "none" || color(style.backgroundColor)[3] > 0 || style.boxShadow !== "none" ||
    ["Top", "Right", "Bottom", "Left"].some(side => parseFloat(style[`border${side}Width`]) > 0 && color(style[`border${side}Color`])[3] > 0);
  const paintedPseudo = node => ["::before", "::after"].some(pseudo => {
    const style = getComputedStyle(node, pseudo);
    return !["none", "normal"].includes(style.content) && style.display !== "none" && Number(style.opacity) > 0 && hasPaint(style);
  });
  const paintedLayers = new Map();
  const layeredGround = element => {
    const scope = element.closest(".slide") || element.closest(".stage");
    if (!scope) return true;
    if (!paintedLayers.has(scope)) paintedLayers.set(scope, [scope, ...scope.querySelectorAll("*")].filter(M.visible).map(node => ({
      node, pseudo: paintedPseudo(node),
      paint: hasPaint(getComputedStyle(node)) || node.matches("img,svg,canvas,video,iframe,object"),
    })));
    const boxes = M.textRects(element);
    return paintedLayers.get(scope).some(({node, pseudo, paint}) => {
      // Pseudo-element geometry and sibling stacking cannot be inferred from an
      // ancestor's background. Do not certify contrast against the wrong layer.
      if (pseudo) return true;
      if (!paint || node.contains(element) || element.contains(node)) return false;
      return boxes.some(box => overlap(box, node.getBoundingClientRect()));
    });
  };
  const ground = element => {
    if (layeredGround(element)) return null;
    const layers = [];
    if (element instanceof SVGElement && element.ownerSVGElement) {
      const probe = M.textRects(element)[0];
      if (probe) for (const shape of [...element.ownerSVGElement.querySelectorAll("rect,circle,ellipse,path,polygon")].reverse()) {
        if (!(shape.compareDocumentPosition(element) & Node.DOCUMENT_POSITION_FOLLOWING) || !M.visible(shape)) continue;
        const style = getComputedStyle(shape);
        if (style.fill === "none" || !shape.isPointInFill || !shape.getScreenCTM()) continue;
        const point = new DOMPoint((probe.left + probe.right) / 2, (probe.top + probe.bottom) / 2).matrixTransform(shape.getScreenCTM().inverse());
        if (!shape.isPointInFill(point)) continue;
        if (/url\(/.test(style.fill)) return null;
        const paint = color(style.fill); paint[3] *= Number(style.fillOpacity) * Number(style.opacity);
        layers.push(paint); if (paint[3] >= 0.999) return paint;
      }
    }
    for (let node = element; node instanceof Element; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (style.backgroundImage !== "none") return null;
      const paint = color(style.backgroundColor);
      layers.push(paint);
      if (paint[3] >= 0.999) return layers.reverse().reduce((base, layer) => composite(layer, base), [1, 1, 1, 1]);
    }
    return null;
  };
  const overlap = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > 1 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 1;
  const ink = rect => rect;
  const validSafe = value => value && ["left", "right", "top", "bottom"].every(key => Number.isFinite(value[key]) && value[key] >= 0 && value[key] < 1) && value.left + value.right < 1 && value.top + value.bottom < 1;
  for (const [index, stage] of stages.entries()) {
    const page = index + 1;
    let restoreHidden;
    try {
    restoreHidden = M.revealStage(stage);
    const rect = stage.getBoundingClientRect();
    if (!rect.width || !rect.height) { fail("unmeasurablePage", page, stage, "Page has zero geometry; use the documented hidden-page display adapter"); continue; }
    const content = stage.querySelector(".fit");
    if (!content) { fail("safeArea", page, stage, "Missing .fit content root"); continue; }
    const key = stage.dataset.layout || stage.dataset.sourceProfile || "default";
    const safe = config.layoutSafeAreas?.[key] || config.safeArea;
    if (!validSafe(safe)) fail("invalidConfig", page, stage, `Record the source safe area for ${key}; no foreign-template margin is assumed`);
    const boundary = validSafe(safe) ? {
      left: rect.left + rect.width * safe.left, right: rect.right - rect.width * safe.right,
      top: rect.top + rect.height * safe.top, bottom: rect.bottom - rect.height * safe.bottom,
    } : M.innerBox(content);
    const allText = M.leaves(stage);
    const contents = allText.filter(M.visible);
    for (const element of allText.filter(element => !M.visible(element))) fail("hiddenText", page, element, "Remove unused slots; never conceal content to make it fit");
    if (!M.leaves(content).some(M.visible) && !content.querySelector("img,svg[data-chart-kind],svg[data-diagram-kind],svg[data-content],canvas[data-content]")) fail("emptyPage", page, stage, "Page has no meaningful content");
    for (const element of contents) {
      const size = M.logicalFontSize(element);
      if (!Number.isFinite(size) || size < 10 - 1e-6) fail("smallText", page, element, `Rendered logical font size ${size.toFixed(3)}px is below 10px`);
      const own = M.ownText(element).map(node => node.textContent).join("");
      if (/\{\{[\w-]+\}\}/.test(own) && !element.closest("[data-literal-content]")) fail("placeholder", page, element, "Replace every library content slot");
      const limit = element.closest("[data-chrome]") ? rect : boundary;
      if (M.textOverflow(element, limit)) fail("textOverflow", page, element, "Text crosses its safe area or is clipped by an ancestor");
      const background = ground(element);
      if (!background) {
        review("unknownTextGround", page, "Text over imagery, gradients or overlapping paint layers needs source-style visual review");
      } else {
        const style = getComputedStyle(element);
        if (element instanceof SVGElement && (/url\(/.test(style.fill) || (style.fill === "none" && style.stroke !== "none"))) {
          review("unknownTextPaint", page, "Pattern/outline text needs source-style visual review");
          continue;
        }
        const foreground = color(element instanceof SVGElement ? style.fill : style.color);
        let alpha = 1;
        for (let node = element; node && node !== stage; node = node.parentElement) alpha *= Number(getComputedStyle(node).opacity);
        foreground[3] *= alpha;
        const a = luminance(composite(foreground, background)), b = luminance(background);
        const ratio = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
        if (ratio < (config.minContrastRatio || 3)) fail("lowContrast", page, element, `Text contrast ${ratio.toFixed(2)}:1; identical foreground/background is never skipped`);
      }
    }
    for (const image of stage.querySelectorAll("img")) {
      const box = image.getBoundingClientRect();
      if (!image.complete || !image.naturalWidth || !image.naturalHeight || box.width < 1 || box.height < 1) fail("brokenImage", page, image, "Every image must load and have nonzero rendered geometry");
      if (/\{\{[\w-]+\}\}/.test(image.getAttribute("src") || "")) fail("placeholder", page, image, "Replace the image slot");
    }
    for (const cell of stage.querySelectorAll("[data-photocell],[data-media-required]")) {
      if (!cell.querySelector("img") && !cell.matches("img") && !M.backgroundUrls(cell).length) fail("emptyMedia", page, cell, "Remove unsupported media instead of retaining a placeholder");
    }
    for (const chart of stage.querySelectorAll("svg[data-chart-kind]")) {
      if (!chart.querySelector("[data-plot-mark]")) fail("unmarkedChart", page, chart, "Mark quantitative SVG geometry with data-plot-mark so final QA can measure it");
    }
    for (const element of stage.querySelectorAll("*")) {
      const height = /(?:^|;)\s*height\s*:\s*([\d.]+)%/i.exec(element.getAttribute("style") || "");
      if (element.hasAttribute("data-plot-mark")) {
        const kind = element.dataset.plotMark || "bar", raw = element.dataset.value;
        const quantity = kind === "bar" || kind === "area";
        if (!["bar", "area", "point", "line"].includes(kind) ||
          (quantity && (!raw?.trim() || !Number.isFinite(Number(raw)))) ||
          (element instanceof SVGElement && !(element instanceof SVGGeometryElement))) {
          fail("invalidChartMark", page, element, "Use a bar/area with finite data-value, or a point/line, on the actual mark geometry");
        } else if (!quantity || Number(raw) !== 0) {
          const box = element.getBoundingClientRect();
          const nonzero = kind === "line" ? Math.max(box.width, box.height) >= 1 : box.width >= 1 && box.height >= 1;
          if (!M.visible(element) || !nonzero) fail("collapsedChart", page, element, "A required chart mark has zero or hidden rendered geometry");
        }
      } else if (height && Number(height[1]) > 0) {
        if (M.visible(element) && element.getBoundingClientRect().height < 1) fail("collapsedChart", page, element, "A nonzero chart value has zero rendered height");
      }
      for (const pseudo of ["::before", "::after"]) {
        const style = getComputedStyle(element, pseudo);
        if (["none", "normal", '""', "''"].includes(style.content) || style.display === "none") continue;
        if (parseFloat(style.fontSize) * M.fontFactor(element) < 10 - 1e-6) fail("smallText", page, element, "Text-bearing pseudo-element is below 10px; materialize it as editable HTML");
      }
    }
    for (const rule of config.requiredChrome || []) {
      if (rule.layouts && !rule.layouts.includes(key)) continue;
      if (!rule.role || !Number.isInteger(rule.min ?? 1) || !Number.isInteger(rule.max ?? rule.min ?? 1)) { fail("invalidConfig", page, stage, "Invalid source chrome rule"); continue; }
      const count = [...stage.querySelectorAll(`[data-chrome="${CSS.escape(rule.role)}"]`)].filter(M.visible).length;
      if (count < (rule.min ?? 1) || count > (rule.max ?? rule.min ?? 1)) fail("requiredChrome", page, stage, `${rule.role}: ${count} visible, expected ${rule.min ?? 1}..${rule.max ?? rule.min ?? 1}`);
    }
    const titleLeaves = contents.filter(element => element.closest('[data-text-role="title"],h1,[data-title]'));
    const bodyLeaves = contents.filter(element => content.contains(element) && !titleLeaves.includes(element));
    if (titleLeaves.some(title => bodyLeaves.some(body => M.textRects(title).map(ink).some(a => M.textRects(body).map(ink).some(b => overlap(a, b)))))) fail("titleBodyOverlap", page, stage, "Title ink overlaps body ink");
    for (const chrome of stage.querySelectorAll('[data-chrome="action"],[data-chrome="cta"],[data-chrome="footer"]')) {
      if (bodyLeaves.some(body => M.textRects(body).map(ink).some(a => overlap(a, chrome.getBoundingClientRect())))) fail("chromeOverlap", page, chrome, "Body text overlaps reserved chrome");
    }
    for (const mark of stage.querySelectorAll("[data-plot-mark]")) {
      // A line's bounding box is mostly unpainted space, not an occluding block.
      if (mark.dataset.plotMark === "line" || mark.closest("[data-overlap-ok]")) continue;
      if (contents.filter(element => !mark.contains(element) && !element.closest("[data-overlap-ok]")).some(element => M.textRects(element).map(ink).some(box => overlap(box, mark.getBoundingClientRect())))) fail("plotTextOverlap", page, mark, "A plot mark overlaps unrelated text");
    }
    if (stage.querySelector('[data-fit-state="unresolved"],[data-fit-state="unmeasurable"],[data-overflow]')) fail("unresolvedFit", page, stage, "Unresolved fit flag remains");
    } catch (error) { fail("unmeasurablePage", page, stage, error.message); }
    finally { if (restoreHidden) restoreHidden(); }
  }
  if (stages.length && !stages.some(M.visible)) fail("deckStructure", 0, null, "The deck has no initially visible page");
  for (const error of M.fontErrors(document.documentElement, config.allowedFontFallbacks || [])) fail("fontLoad", 0, null, error);
  // Test every advertised direction against live state, not string presence.
  if (slides.length > 1 && decks.length === 1) {
    const marked = () => slides.findIndex(slide => slide.getAttribute("aria-current") === "page");
    const shown = index => {
      if (index < 0 || !M.visible(slides[index])) return false;
      const box = slides[index].getBoundingClientRect(), viewport = decks[0].getBoundingClientRect();
      return Math.min(box.bottom, viewport.bottom, innerHeight) - Math.max(box.top, viewport.top, 0) > 10 &&
        Math.min(box.right, viewport.right, innerWidth) - Math.max(box.left, viewport.left, 0) > 10;
    };
    const press = async key => {
      document.dispatchEvent(new KeyboardEvent("keydown", {key, code: key, bubbles: true, cancelable: true}));
      // Include the navigation scroll debounce; two paint frames can precede it.
      await new Promise(resolve => setTimeout(resolve, 150)); await M.frame(); await M.frame();
    };
    const original = marked();
    await press("Home");
    if (marked() !== 0 || !shown(0)) fail("keyboardNavigation", 0, null, "Home must show the first page");
    for (const key of ["ArrowRight", "ArrowDown"]) {
      await press("Home");
      for (let index = 1; index <= Math.min(2, slides.length - 1); index++) {
        await press(key);
        if (marked() !== index || !shown(index)) fail("keyboardNavigation", 0, null, `${key} must show page ${index + 1} on consecutive presses`);
      }
    }
    for (const key of ["ArrowLeft", "ArrowUp"]) {
      await press("End");
      if (marked() !== slides.length - 1 || !shown(slides.length - 1)) fail("keyboardNavigation", 0, null, "End must show the last page");
      for (let step = 1; step <= Math.min(2, slides.length - 1); step++) {
        const index = slides.length - 1 - step;
        await press(key);
        if (marked() !== index || !shown(index)) fail("keyboardNavigation", 0, null, `${key} must show page ${index + 1} on consecutive presses`);
      }
    }
    await press("Home");
    if (original > 0) for (let i = 0; i < original; i++) await press("ArrowRight");
  }
  report.status = report.hardGateFailures ? "BLOCKED" : report.reviewRequired.length ? "NEEDS_VISUAL_REVIEW" : "READY_TO_PUBLISH";
  return JSON.stringify(report);
})();
