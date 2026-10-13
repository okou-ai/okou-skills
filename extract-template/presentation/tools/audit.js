/* Source-configured rendered QA. No built-in palette, motif or crop policy. */
(async () => {
  const M = window.PresentationMetrics;
  const config = window.PRESENTATION_QA_CONFIG || {};
  const MIN_FONT_SIZE_PX = 11;
  const report = {pages: 0, navigableSlides: 0, decks: 0, minFontSizePx: MIN_FONT_SIZE_PX, status: "BLOCKED", hardGateFailures: 0, blocking: {}, failures: [], reviewRequired: [], advisories: []};
  const fail = (code, page, element, message) => {
    report.hardGateFailures++;
    report.blocking[code] = (report.blocking[code] || 0) + 1;
    if (report.failures.length < 80) report.failures.push({code, page, element: element ? `${element.tagName.toLowerCase()}${element.id ? `#${element.id}` : ""}` : null, message});
  };
  const fitFloorPages = new Set();
  const failFitFloor = (page, element, message) => {
    if (fitFloorPages.has(page)) return;
    fitFloorPages.add(page);
    fail("fitFloor", page, element, message);
  };
  const reviews = new Set();
  const review = (code, page, message) => {
    const key = `${code}:${page}`;
    if (!reviews.has(key)) { reviews.add(key); report.reviewRequired.push({code, page, message}); }
  };
  if (!M) { fail("missingRuntime", 0, null, "Load the packaged dom-metrics.js"); return JSON.stringify(report); }
  await window.PresentationNavigationReady;
  await window.PresentationViewportReady;
  if (M.MIN_FONT_SIZE_PX !== MIN_FONT_SIZE_PX) fail("invalidRuntime", 0, null, "Refresh the shell and runtime together to use the 11px minimum");
  if (config.minFontSizePx !== undefined && config.minFontSizePx !== MIN_FONT_SIZE_PX) fail("invalidConfig", 0, null, "The minimum font size is fixed at 11px");
  if (config.minContrastRatio !== undefined && (!Number.isFinite(config.minContrastRatio) || config.minContrastRatio < 3 || config.minContrastRatio > 21)) fail("invalidConfig", 0, null, "minContrastRatio must be within 3..21");
  const decks = [...document.querySelectorAll(".deck")];
  const slides = [...document.querySelectorAll(".slide")];
  const stages = [...document.querySelectorAll(".stage")];
  if (window.PresentationViewport && [document.documentElement, document.body, ...decks, ...slides].some(
    element => getComputedStyle(element).backgroundColor !== "rgb(0, 0, 0)")) {
    fail("viewportBackground", 0, null, "The viewer surround must be pure black; keep source backgrounds on the stage");
  }
  if (window.PresentationViewport && decks.some(deck => {
    const frame = deck.getBoundingClientRect();
    return Math.abs(frame.left) > 1 || Math.abs(frame.top) > 1 ||
      Math.abs(frame.right - innerWidth) > 1 || Math.abs(frame.bottom - innerHeight) > 1;
  })) fail("viewportFrame", 0, null, "The viewer frame must cover the browser viewport");
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
    if (fit.report.minFontSizePx !== MIN_FONT_SIZE_PX) fail("invalidRuntime", 0, null, "The fitter must use the 11px minimum");
    for (const error of fit.report.errors) fail("fitReadiness", 0, null, error);
    for (const region of fit.report.regions) {
      if (region.status === "fit-floor") failFitFloor(region.page, null, region.reason || "Content reached the fitting limit");
      else if (!["unchanged", "fitted"].includes(region.status)) fail("unresolvedFit", region.page, null, `${region.region}: ${region.reason || region.status}`);
      if (!Number.isFinite(region.scale) || region.scale < 0.8 - 1e-6 || region.scale > 1 + 1e-6) fail("fitScale", region.page, null, "Typography must stay within 80–100% of source size");
    }
    if (fit.report.status !== "READY" && !fit.report.errors.length && !fit.report.regions.some(region => !["unchanged", "fitted"].includes(region.status))) fail("fitReadiness", 0, null, "Fit report is not ready");
  }
  // Readability advice only: measure final typography without changing the fitter,
  // content or publish gates. Group inline runs by their flow container so spans
  // on one line are not mistaken for separate lines or reported more than once.
  const compactLineSpacing = (root, page) => {
    if (!root) return [];
    const excluded = 'script,style,noscript,svg,[data-chrome],[data-decoration],[data-deco],[data-ornament],h1,h2,h3,h4,h5,h6,[role="heading"],[data-title],[data-text-role="title"],[data-text-role="heading"],[data-text-role="metric"],.h1,.h2,.h3,.display,.stat';
    const groups = new Map();
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let node; (node = walker.nextNode());) {
      const parent = node.parentElement;
      if (!node.textContent.trim() || !parent || parent.closest(excluded)) continue;
      let shown = true;
      for (let element = parent; element; element = element.parentElement) {
        const style = getComputedStyle(element);
        if (style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) {
          shown = false;
          break;
        }
      }
      if (!shown) continue;
      let block = parent;
      while (block !== root && /^(inline|contents)$/.test(getComputedStyle(block).display)) block = block.parentElement;
      const range = document.createRange();
      range.selectNodeContents(node);
      const rects = [...range.getClientRects()].filter(rect => rect.width > 0 && rect.height > 0);
      if (!rects.length) continue;
      if (!groups.has(block)) groups.set(block, []);
      groups.get(block).push({parent, text: node.textContent, rects});
    }
    const findings = [];
    for (const [block, runs] of groups) {
      const blockStyle = getComputedStyle(block);
      const firstStyle = getComputedStyle(runs[0].parent);
      const uniform = runs.every(run => {
        const inline = getComputedStyle(run.parent);
        return inline.fontSize === firstStyle.fontSize && inline.fontFamily === firstStyle.fontFamily &&
          inline.lineHeight === firstStyle.lineHeight && inline.verticalAlign === firstStyle.verticalAlign;
      });
      const style = uniform ? firstStyle : blockStyle;
      if (style.writingMode !== "horizontal-tb") continue;
      const rows = [];
      for (const rect of runs.flatMap(run => run.rects).sort((a, b) => a.top - b.top)) {
        const center = (rect.top + rect.bottom) / 2;
        const row = rows.find(row => Math.abs(row.center - center) < Math.max(row.height, rect.height) * 0.5);
        if (!row) rows.push({center, height: rect.height});
      }
      if (rows.length < 2) continue;
      const fontSizePx = parseFloat(style.fontSize);
      let lineHeightPx = parseFloat(style.lineHeight);
      let measurement = "computed";
      if (style.lineHeight === "normal") {
        // normal has no computed pixel value. Homogeneous runs let us measure
        // actual baseline spacing; undo transforms/zoom, not font metrics.
        if (runs.some(run => {
          const inline = getComputedStyle(run.parent);
          return inline.fontSize !== style.fontSize || inline.fontFamily !== style.fontFamily ||
            inline.lineHeight !== "normal" || inline.verticalAlign !== "baseline";
        })) continue;
        let matrix = new DOMMatrix(), zoom = 1;
        for (let element = block; element; element = element.parentElement) {
          const ancestor = getComputedStyle(element);
          if (ancestor.transform !== "none") matrix = new DOMMatrix(ancestor.transform).multiply(matrix);
          zoom *= parseFloat(ancestor.zoom) || 1;
        }
        if (Math.abs(matrix.b) > 1e-6 || Math.abs(matrix.c) > 1e-6) continue;
        const scale = Math.abs(matrix.d) * zoom;
        const gaps = rows.slice(1).map((row, index) => row.center - rows[index].center).sort((a, b) => a - b);
        lineHeightPx = gaps[Math.floor(gaps.length / 2)] / scale;
        measurement = "rendered-normal";
      }
      const ratio = lineHeightPx / fontSizePx;
      if (!Number.isFinite(ratio) || !(fontSizePx > 0) || ratio >= 1.33 - 1e-6) continue;
      const parts = [];
      for (let element = block; element && element !== root; element = element.parentElement) {
        if (element.id) { parts.unshift(`#${CSS.escape(element.id)}`); break; }
        const siblings = [...element.parentElement.children].filter(sibling => sibling.tagName === element.tagName);
        parts.unshift(`${element.tagName.toLowerCase()}:nth-of-type(${siblings.indexOf(element) + 1})`);
      }
      findings.push({
        code: "compactLineSpacing", page, element: parts.join(" > ") || ".fit",
        text: runs.map(run => run.text).join("").trim().replace(/\s+/g, " ").slice(0, 100),
        fontSizePx, lineHeightPx, ratio, minRatio: 1.33, measurement,
        message: `Line-height ratio ${Number(ratio.toFixed(4))} is below 1.33; this multiline text layout is too compact. Reorganize the content or layout (for example, widen the text column or redistribute blocks) to give lines more room. Preserve all source information and any fixed page-count requirement; do not squeeze typography further.`,
      });
    }
    return findings;
  };

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
    if (window.PresentationViewport) {
      const canvas = stage.getBoundingClientRect(), frame = stage.parentElement.getBoundingClientRect();
      if (!(canvas.width > 0 && canvas.height > 0) || M.outside(canvas, frame, 1) ||
        Math.abs((canvas.left + canvas.right) - (frame.left + frame.right)) > 2 ||
        Math.abs((canvas.top + canvas.bottom) - (frame.top + frame.bottom)) > 2) {
        fail("viewportFrame", page, stage, "The complete canvas must fit and be centered within its slide viewport");
      }
    }
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
    report.advisories.push(...compactLineSpacing(content, page));
    const allText = M.leaves(stage);
    const contents = allText.filter(M.visible);
    const pageFit = fit?.report?.regions.find(region => region.page === page && region.region === "content");
    const contentText = M.leaves(content);
    if (pageFit?.baselineSizesPx?.length === contentText.length && contentText.some((element, i) =>
      M.visible(element) && M.logicalFontSize(element) < pageFit.baselineSizesPx[i] * 0.8 - 0.001)) {
      fail("fitScale", page, content, "Rendered text is below 80% of its source size, including transforms and SVG scaling");
    }
    for (const element of allText.filter(element => !M.visible(element))) fail("hiddenText", page, element, "Remove unused slots; never conceal content to make it fit");
    if (!M.leaves(content).some(M.visible) && !content.querySelector("img,svg[data-chart-kind],svg[data-diagram-kind],svg[data-content],canvas[data-content]")) fail("emptyPage", page, stage, "Page has no meaningful content");
    for (const element of contents) {
      const size = M.logicalFontSize(element);
      if (!Number.isFinite(size) || size < MIN_FONT_SIZE_PX - 1e-6) fail("smallText", page, element, `Rendered logical font size ${size.toFixed(3)}px is below 11px`);
      const own = M.ownText(element).map(node => node.textContent).join("");
      if (/\{\{[\w-]+\}\}/.test(own) && !element.closest("[data-literal-content]")) fail("placeholder", page, element, "Replace every library content slot");
      const limit = element.closest("[data-chrome]") ? rect : boundary;
      if (M.textOverflow(element, limit)) fail("textOverflow", page, element, "Text crosses its safe area or is clipped by an ancestor");
      const background = ground(element);
      if (!background) {
        review("unknownTextGround", page, "Visually confirm text readability over imagery, gradients or paint layers; readable texture/image overlap needs no content changes");
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
    for (const element of [stage, ...stage.querySelectorAll("*")]) {
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
        if (parseFloat(style.fontSize) * M.fontFactor(element) < MIN_FONT_SIZE_PX - 1e-6) fail("smallText", page, element, "Text-bearing pseudo-element is below 11px; materialize it as editable HTML");
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
    const floorSelector = '[data-fit-state="fit-floor"],[data-overflow="fit-floor"]';
    if (stage.matches(floorSelector) || stage.querySelector(floorSelector)) failFitFloor(page, stage, "fit-floor remains; restore capacity through geometry, recomposition or splitting");
    if (stage.querySelector('[data-fit-state="unresolved"],[data-fit-state="unmeasurable"],[data-overflow]:not([data-overflow="fit-floor"])')) fail("unresolvedFit", page, stage, "Unresolved fit flag remains");
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
