/* One navigation owner for scrolling decks and explicitly adapted hidden pages. */
(() => {
  const afterFitting = async () => {
    if (!window.PresentationFit) return;
    let ready;
    do { ready = window.PresentationFit.ready; await ready; } while (ready !== window.PresentationFit.ready);
  };
  const boot = async () => {
    // The fitter temporarily reveals hidden slides. Detect the authored mode
    // only after it has restored them, including any queued initial refits.
    await afterFitting();
    const deck = document.querySelector(".deck");
    if (!deck || deck.__presentationNavigationAttached) return;
    const slides = [...deck.children].filter(node => node.classList.contains("slide"));
    if (!slides.length) return;
    const concealed = slide => slide.hidden || getComputedStyle(slide).display === "none";
    const paged = deck.dataset.navigationMode === "paged" ||
      (deck.dataset.navigationMode !== "scroll" && slides.some(concealed));
    let current = Math.max(0, slides.findIndex(slide => !concealed(slide)));
    const activeClass = deck.dataset.navigationActiveClass ||
      ["active", "is-active"].find(name => slides[current].classList.contains(name));
    const displays = paged ? slides.map(slide => {
      let display = slide.dataset.fitDisplay || getComputedStyle(slide).display;
      if (display === "none") {
        const hidden = slide.getAttribute("hidden"), style = slide.getAttribute("style");
        slide.removeAttribute("hidden"); slide.style.removeProperty("display");
        display = getComputedStyle(slide).display;
        if (hidden !== null) slide.setAttribute("hidden", hidden);
        if (style === null) slide.removeAttribute("style"); else slide.setAttribute("style", style);
      }
      if (!CSS.supports("display", display) || /^(none|contents)$/.test(display)) throw new Error("Hidden slides need their authored data-fit-display");
      // Fitting must also be able to reveal the page that navigation hides next.
      slide.dataset.fitDisplay = display;
      return display;
    }) : [];
    const mark = () => slides.forEach((slide, index) => {
      if (index === current) slide.setAttribute("aria-current", "page"); else slide.removeAttribute("aria-current");
      if (paged) {
        slide.hidden = index !== current;
        slide.style.setProperty("display", index === current ? displays[index] : "none", "important");
        if (activeClass) slide.classList.toggle(activeClass, index === current);
      }
    });
    const visibleArea = slide => {
      const box = slide.getBoundingClientRect(), viewport = deck.getBoundingClientRect();
      const width = Math.min(box.right, viewport.right, innerWidth) - Math.max(box.left, viewport.left, 0);
      const height = Math.min(box.bottom, viewport.bottom, innerHeight) - Math.max(box.top, viewport.top, 0);
      return Math.max(0, width) * Math.max(0, height);
    };
    let pending, request = 0, moving = false;
    const sync = () => {
      if (paged || moving) return;
      // Intersection works for horizontal, vertical and document-scrolling decks.
      current = slides.reduce((best, slide, index) => visibleArea(slide) > visibleArea(slides[best]) ? index : best, current);
      mark();
    };
    const go = async next => {
      if (!Number.isInteger(next)) throw new Error("Slide index must be an integer");
      clearTimeout(pending);
      current = Math.max(0, Math.min(slides.length - 1, next));
      const ticket = ++request;
      moving = true;
      // A refit restores the old hidden/display attributes. Apply navigation
      // after that restoration; rapid key presses retain the latest target.
      await afterFitting();
      if (ticket !== request) return;
      moving = false;
      mark(); slides[current].scrollIntoView({block: "start", inline: "start", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "auto"});
    };
    window.PresentationNavigation = Object.freeze({go, next: () => go(current + 1), previous: () => go(current - 1), get current() { return current; }});
    deck.__presentationNavigationAttached = true;
    window.addEventListener("keydown", event => {
      if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey ||
        (event.target instanceof Element && (event.target.closest("input,textarea,select,button") || event.target.isContentEditable))) return;
      const key = event.key;
      if (["ArrowLeft", "ArrowUp", "PageUp"].includes(key)) go(current - 1);
      else if (["ArrowRight", "ArrowDown", "PageDown"].includes(key)) go(current + 1);
      else if (key === "Home") go(0);
      else if (key === "End") go(slides.length - 1);
      else return;
      event.preventDefault(); event.stopImmediatePropagation();
    }, true);
    const onScroll = () => {
      if (paged || moving) return;
      clearTimeout(pending);
      pending = setTimeout(sync, 100);
    };
    deck.addEventListener("scroll", onScroll, {passive: true});
    window.addEventListener("scroll", onScroll, {passive: true});
    sync();
    mark();
  };
  window.PresentationNavigationReady = document.readyState === "loading"
    ? new Promise((resolve, reject) => document.addEventListener("DOMContentLoaded", () => boot().then(resolve, reject), {once: true}))
    : boot();
})();
