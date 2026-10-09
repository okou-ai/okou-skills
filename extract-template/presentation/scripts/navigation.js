/* One shared navigation handler; independent of source styling. */
(() => {
  const boot = () => {
    const deck = document.querySelector(".deck");
    if (!deck || deck.__presentationNavigationAttached) return;
    deck.__presentationNavigationAttached = true;
    const slides = [...deck.children].filter(node => node.classList.contains("slide"));
    if (!slides.length) return;
    let current = 0;
    const mark = () => slides.forEach((slide, index) => {
      if (index === current) slide.setAttribute("aria-current", "page"); else slide.removeAttribute("aria-current");
    });
    const go = next => {
      current = Math.max(0, Math.min(slides.length - 1, next));
      mark(); slides[current].scrollIntoView({block: "start", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "auto"});
    };
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
    let pending;
    deck.addEventListener("scroll", () => {
      clearTimeout(pending);
      pending = setTimeout(() => {
        const top = deck.getBoundingClientRect().top;
        current = slides.reduce((best, slide, index) => Math.abs(slide.getBoundingClientRect().top - top) <
          Math.abs(slides[best].getBoundingClientRect().top - top) ? index : best, 0);
        mark();
      }, 100);
    }, {passive: true});
    mark();
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, {once: true}); else boot();
})();
