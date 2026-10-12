/* Shared viewer frame. Source paint and typography stay inside the canvas. */
(() => {
  if (window.PresentationViewport) return;
  const M = window.PresentationMetrics;
  if (!M) throw new Error("Load dom-metrics.js before viewport.js");
  let refresh = () => {};
  const boot = () => {
    const deck = document.querySelector(".deck");
    if (!deck) return;
    const slides = [...deck.children].filter(element => element.classList.contains("slide"));
    const stages = slides.flatMap(slide => [...slide.children].filter(element => element.classList.contains("stage")));
    // Detect source visibility before the fitter temporarily reveals hidden pages.
    const paged = deck.dataset.navigationMode === "paged" ||
      (deck.dataset.navigationMode !== "scroll" && slides.some(slide => slide.hidden || getComputedStyle(slide).display === "none"));
    // A transparent canvas previously showed its ancestor's solid background.
    // Preserve that canvas fill before changing the viewer surround to black.
    for (const stage of stages) {
      if (getComputedStyle(stage).backgroundColor !== "rgba(0, 0, 0, 0)") continue;
      let fill = "#fff";
      for (let node = stage.parentElement; node; node = node.parentElement) {
        const color = getComputedStyle(node).backgroundColor;
        if (color !== "rgba(0, 0, 0, 0)") { fill = color; break; }
      }
      stage.style.backgroundColor = fill;
    }
    document.documentElement.dataset.presentationViewport = "";
    deck.dataset.presentationViewport = paged ? "paged" : "scroll";
    let style = document.querySelector("style[data-presentation-viewport]");
    if (!style) {
      style = document.createElement("style");
      style.dataset.presentationViewport = "";
      document.head.append(style);
    }
    style.textContent = `
      html[data-presentation-viewport], html[data-presentation-viewport] body {
        margin:0!important; padding:0!important; width:100%!important; height:100%!important;
        overflow:hidden!important; background:#000!important;
      }
      .deck[data-presentation-viewport] {
        position:fixed!important; inset:0!important; width:100%!important; height:100%!important;
        margin:0!important; padding:0!important; border:0!important; box-sizing:border-box!important;
        max-width:none!important; max-height:none!important; transform:none!important; background:#000!important;
        overflow:auto!important;
      }
      .deck[data-presentation-viewport] > .slide {
        position:relative!important; inset:auto!important; width:100%!important; height:100%!important;
        min-width:100%!important; min-height:100%!important; flex:0 0 100%!important;
        margin:0!important; padding:0!important; border:0!important; box-sizing:border-box!important;
        overflow:clip!important; background:#000!important; scroll-snap-align:start;
      }
      .deck[data-presentation-viewport="paged"] { overflow:hidden!important; }
      .deck[data-presentation-viewport="paged"] > .slide { position:absolute!important; inset:0!important; }
      .deck[data-presentation-viewport] > .slide > .stage {
        position:absolute!important; left:50%!important; top:50%!important; right:auto!important; bottom:auto!important;
        margin:0!important; flex:none!important; transform-origin:center!important;
        transform:translate(-50%,-50%) scale(var(--presentation-viewport-scale,1))!important;
      }
    `;
    refresh = () => {
      for (const stage of stages) {
        const undo = M.revealStage(stage);
        let scale;
        try {
          const slide = stage.parentElement;
          scale = Math.min(slide.clientWidth / stage.offsetWidth, slide.clientHeight / stage.offsetHeight);
          if (!(scale > 0) || !Number.isFinite(scale)) throw new Error("Slide canvas needs measurable width and height");
        } finally { undo(); }
        stage.style.setProperty("--presentation-viewport-scale", String(scale));
      }
    };
    refresh();
    // Centering is independent of display:flex/grid/block, including capture tools.
    window.addEventListener("resize", refresh, {passive: true});
    new ResizeObserver(refresh).observe(deck);
  };
  window.PresentationViewport = Object.freeze({refresh: () => refresh()});
  window.PresentationViewportReady = document.readyState === "loading"
    ? new Promise((resolve, reject) => document.addEventListener("DOMContentLoaded", () => {
      try { boot(); resolve(); } catch (error) { reject(error); }
    }, {once: true}))
    : Promise.resolve().then(boot);
})();
