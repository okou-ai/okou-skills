import {createHash} from "node:crypto";
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import path from "node:path";

// Runs in the QA browser, after the same fitter and audit used for publication.
export async function showCapturePage(index) {
  await window.PresentationNavigationReady;
  const slides = [...document.querySelectorAll(".deck > .slide")];
  if (!slides[index]) throw new Error(`Missing capture page ${index + 1}`);
  if (window.PresentationNavigation) await window.PresentationNavigation.go(index);
  else if (slides.length !== 1) throw new Error("Capture needs the installed navigation runtime");
  await window.PresentationFit?.ready;
  await window.PresentationMetrics.assetsReady(slides[index], window.PRESENTATION_QA_CONFIG?.allowedFontFallbacks || []);
  await window.PresentationMetrics.frame();
  await window.PresentationMetrics.frame();
  const slide = slides[index], stage = slide.querySelector(":scope > .stage");
  const box = stage?.getBoundingClientRect();
  if (!box || !window.PresentationMetrics.visible(slide) || box.width < 1 || box.height < 1 ||
      box.left < -1 || box.top < -1 || box.right > innerWidth + 1 || box.bottom > innerHeight + 1 ||
      (slides.length > 1 && slide.getAttribute("aria-current") !== "page")) {
    throw new Error(`Capture page ${index + 1} is not the visible, complete canvas`);
  }
  return {page: index + 1, width: innerWidth, height: innerHeight,
    stage: {x: box.x, y: box.y, width: box.width, height: box.height}};
}

export function capturePages({browser, parse, input, directory, pages}) {
  const started = performance.now();
  if (/^https?:/i.test(input)) throw new Error("Review capture needs the local publication HTML");
  const source = path.resolve(input), web = path.dirname(source), output = path.resolve(directory);
  const relative = path.relative(web, output);
  if (!relative || (!relative.startsWith(`..${path.sep}`) && relative !== ".." && !path.isAbsolute(relative))) {
    throw new Error("Keep capture output outside the web directory");
  }
  const deckSha256 = createHash("sha256").update(readFileSync(source)).digest("hex");
  mkdirSync(output, {recursive: true});
  const evaluate = source => parse(browser("eval", "-b", Buffer.from(source).toString("base64")));
  const original = evaluate("window.PresentationNavigation?.current ?? 0");
  const captures = [];
  try {
    for (const number of [...new Set(pages)].sort((a, b) => a - b)) {
      const frame = evaluate(`(${showCapturePage.toString()})(${number - 1})`);
      const file = path.join(output, `page-${String(number).padStart(3, "0")}.png`);
      browser("screenshot", file);
      const bytes = readFileSync(file);
      if (bytes.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a" ||
          bytes.readUInt32BE(16) !== frame.width || bytes.readUInt32BE(20) !== frame.height) {
        throw new Error(`Capture page ${number} is not the expected viewport PNG`);
      }
      captures.push({...frame, file, sha256: createHash("sha256").update(bytes).digest("hex")});
    }
  } finally {
    evaluate(`(async()=>{await window.PresentationNavigation?.go(${original});return 1})()`);
  }
  const manifest = {deckSha256, pages: captures, durationSeconds: (performance.now() - started) / 1000};
  writeFileSync(path.join(output, "captures.json"), JSON.stringify(manifest, null, 2) + "\n");
  return manifest;
}
