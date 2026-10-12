import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync} from "node:fs";
import os from "node:os";
import path from "node:path";
import {fileURLToPath, pathToFileURL} from "node:url";
import {after, before, test} from "node:test";
import {chromium} from "playwright";

const audit = readFileSync(new URL("../tools/audit.js", import.meta.url), "utf8");
const installer = fileURLToPath(new URL("../scripts/install-qa.mjs", import.meta.url));
let browser;
before(async () => { browser = await chromium.launch({executablePath: process.env.PRESENTATION_CHROMIUM_PATH, headless: true}); });
after(async () => { await browser?.close(); });

async function fixture(t, {display = "block", mode = "paged", fluid = false, transparent = false, width = 1600, height = 900} = {}) {
  const root = mkdtempSync(path.join(os.tmpdir(), "presentation-viewport-"));
  t.after(() => rmSync(root, {recursive: true, force: true}));
  mkdirSync(path.join(root, "layouts")); mkdirSync(path.join(root, "tools"));
  writeFileSync(path.join(root, "tools/qa-config.json"), JSON.stringify({minFontSizePx: 11, expectedPages: 3,
    safeArea: {left: 0, right: 0, top: 0, bottom: 0}, requiredChrome: [], allowedFontFallbacks: []}));
  const file = path.join(root, "layouts/_shell.html");
  writeFileSync(file, `<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>
    * {box-sizing:border-box} body {margin:0;background:#e7e8ea;color:#111;font:24px/1.2 Arial,sans-serif}
    .deck {width:1600px;height:900px;margin:auto;overflow:auto;${mode === "horizontal" ? "display:flex;scroll-snap-type:x mandatory" : "scroll-snap-type:y mandatory"}}
    .slide {width:1600px;height:900px;background:#fff;display:${mode === "paged" ? "none" : display};place-items:center;align-items:center;justify-content:center}
    .slide.active {display:${display}}
    .stage {width:${fluid ? "min(100vw,177.777778vh)" : `${width}px`};height:${fluid ? "min(56.25vw,100vh)" : `${height}px`};position:relative;container-type:inline-size;${transparent ? "" : "background:#f4ebdd"}}
    .fit {position:absolute;inset:5%} h1 {margin:0;font-size:${fluid ? "2cqw" : "32px"};line-height:1.2}
    </style></head><body><main class="deck" ${mode === "paged" ? 'data-navigation-mode="paged"' : 'data-navigation-mode="scroll"'}>
    ${[1, 2, 3].map(i => `<section class="slide${i === 1 ? " active" : ""}" data-fit-display="${display}"><div class="stage"><div class="fit"><h1>Page ${i}</h1></div></div></section>`).join("")}
    </main></body></html>`);
  execFileSync(process.execPath, [installer, "--package", root]);
  // Refreshing an already-installed shell must remain idempotent.
  execFileSync(process.execPath, [installer, "--package", root]);
  const page = await browser.newPage({viewport: {width: 1280, height: 800}, reducedMotion: "reduce"});
  t.after(() => page.close());
  await page.goto(pathToFileURL(file).href);
  await settle(page);
  return page;
}

async function settle(page) {
  await page.evaluate(async () => {
    await window.PresentationViewportReady;
    await window.PresentationNavigationReady;
    await new Promise(requestAnimationFrame);
    let ready;
    do { ready = window.PresentationFit.ready; await ready; } while (ready !== window.PresentationFit.ready);
    await new Promise(requestAnimationFrame);
  });
}
async function checkFrame(page, index, ratio = 16 / 9) {
  const result = await page.evaluate(index => {
    const slide = document.querySelectorAll(".deck > .slide")[index], stage = slide.querySelector(".stage");
    const rect = stage.getBoundingClientRect();
    return {x: rect.x, y: rect.y, width: rect.width, height: rect.height,
      viewportWidth: innerWidth, viewportHeight: innerHeight,
      fill: getComputedStyle(stage).backgroundColor,
      surround: [document.documentElement, document.body, document.querySelector(".deck"), slide].map(node => getComputedStyle(node).backgroundColor),
      current: window.PresentationNavigation.current,
      fontSize: parseFloat(getComputedStyle(stage.querySelector("h1")).fontSize),
      logicalSize: window.PresentationMetrics.logicalFontSize(stage.querySelector("h1")),
      fit: window.PresentationFit.report.status,
      styleCount: document.querySelectorAll("style[data-presentation-viewport]").length};
  }, index);
  const near = (actual, expected) => assert.ok(Math.abs(actual - expected) < 0.1, JSON.stringify(result));
  near(result.width / result.height, ratio);
  near(result.x, (result.viewportWidth - result.width) / 2);
  near(result.y, (result.viewportHeight - result.height) / 2);
  assert.ok(result.x >= -0.1 && result.y >= -0.1 && result.width > 0 && result.height > 0, JSON.stringify(result));
  assert.deepEqual(result.surround, Array(4).fill("rgb(0, 0, 0)"));
  assert.equal(result.current, index);
  assert.equal(result.fit, "READY");
  assert.equal(result.styleCount, 1);
  return result;
}

for (const display of ["block", "flex", "grid"]) {
  test(`installed fixed canvas stays centered with ${display} slides through resize, navigation and capture overrides`, async t => {
    const page = await fixture(t, {display});
    for (const viewport of [{width: 1920, height: 900}, {width: 1280, height: 800}, {width: 390, height: 844}]) {
      await page.setViewportSize(viewport); await settle(page);
      for (const [key, index] of [["Home", 0], ["ArrowRight", 1], ["End", 2]]) {
        await page.keyboard.press(key); await settle(page);
        const result = await checkFrame(page, index);
        assert.equal(result.fontSize, 32); assert.equal(result.logicalSize, 32);
        assert.equal(result.fill, "rgb(244, 235, 221)");
      }
      await page.locator('.slide[aria-current="page"]').evaluate(slide => slide.style.setProperty("display", "block", "important"));
      await checkFrame(page, 2);
    }
    assert.equal(JSON.parse(await page.evaluate(audit)).status, "READY_TO_PUBLISH");
  });
}

for (const mode of ["vertical", "horizontal"]) {
  test(`responsive source canvas keeps ${mode} scrolling and container typography`, async t => {
    const page = await fixture(t, {mode, display: "grid", fluid: true});
    for (const viewport of [{width: 1920, height: 900}, {width: 390, height: 844}]) {
      await page.setViewportSize(viewport); await settle(page);
      await page.keyboard.press("Home"); await settle(page); await checkFrame(page, 0);
      await page.keyboard.press("End"); await settle(page);
      const result = await checkFrame(page, 2);
      assert.ok(Math.abs(result.logicalSize - 32) < 0.1);
    }
    assert.equal(JSON.parse(await page.evaluate(audit)).status, "READY_TO_PUBLISH");
  });
}

test("source 4:3 canvas retains its aspect ratio", async t => {
  const page = await fixture(t, {width: 1200, height: 900});
  await checkFrame(page, 0, 4 / 3);
  await page.setViewportSize({width: 390, height: 844}); await settle(page);
  await checkFrame(page, 0, 4 / 3);
});

test("transparent canvas retains its source slide fill while the surround turns black", async t => {
  const page = await fixture(t, {transparent: true});
  assert.equal((await checkFrame(page, 0)).fill, "rgb(255, 255, 255)");
});

test("QA rejects a canvas displaced out of the viewport center", async t => {
  const page = await fixture(t);
  await page.locator(".stage").first().evaluate(stage => stage.style.setProperty("left", "0", "important"));
  const report = JSON.parse(await page.evaluate(audit));
  assert.equal(report.status, "BLOCKED"); assert.ok(report.blocking.viewportFrame > 0, JSON.stringify(report));
});

test("QA rejects a gray viewer surround", async t => {
  const page = await fixture(t);
  await page.locator("body").evaluate(body => body.style.setProperty("background", "#ddd", "important"));
  const report = JSON.parse(await page.evaluate(audit));
  assert.equal(report.status, "BLOCKED"); assert.ok(report.blocking.viewportBackground > 0, JSON.stringify(report));
});
