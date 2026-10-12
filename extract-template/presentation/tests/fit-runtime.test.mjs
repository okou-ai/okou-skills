import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync} from "node:fs";
import os from "node:os";
import path from "node:path";
import {fileURLToPath, pathToFileURL} from "node:url";
import {after, before, test} from "node:test";
import {chromium} from "playwright";

const source = file => readFileSync(new URL(`../${file}`, import.meta.url), "utf8");
const metrics = source("scripts/dom-metrics.js");
const fitter = source("scripts/fit-text.js");
const audit = source("tools/audit.js");
let browser;
before(async () => {
  browser = await chromium.launch({executablePath: process.env.PRESENTATION_CHROMIUM_PATH, headless: true});
});
after(async () => { await browser?.close(); });

async function fixture(t, {content = '<h1 id="title">AI teammate</h1>', css = "", setup, slides} = {}) {
  const page = await browser.newPage({viewport: {width: 1600, height: 900}, reducedMotion: "reduce"});
  t.after(() => page.close());
  await page.setContent(`<!doctype html><html data-presentation-prepared="capture"><head><style>
    * { box-sizing:border-box; }
    body { margin:0; color:#111; background:#fff; font:24px/1.2 Arial,sans-serif; }
    .stage { position:relative; width:1600px; height:900px; background:#fff; }
    .fit { position:absolute; left:0; top:0; width:1600px; height:900px; }
    h1 { margin:0; font-size:83.2px; line-height:1.2; font-weight:400; white-space:nowrap; }
    p { margin:0; }
    ${css}
    </style></head><body><main class="deck">${slides || `<section class="slide"><div class="stage"><div class="fit">${content}</div></div></section>`}</main></body></html>`);
  await page.evaluate(() => {
    window.PRESENTATION_QA_CONFIG = {minFontSizePx: 11, expectedPages: document.querySelectorAll(".stage").length,
      safeArea: {left: 0, right: 0, top: 0, bottom: 0}, requiredChrome: [], allowedFontFallbacks: []};
  });
  await page.addScriptTag({content: metrics});
  if (setup) await setup(page);
  await page.addScriptTag({content: fitter});
  return page;
}
const fit = page => page.evaluate(() => window.PresentationFit.fit());
const inspect = async page => JSON.parse(await page.evaluate(audit));
const fontSize = (page, selector = "#title") => page.$eval(selector, element => parseFloat(getComputedStyle(element).fontSize));
const near = (actual, expected) => assert.ok(Math.abs(actual - expected) < 0.002, `${actual} != ${expected}`);
async function capacity(page, ratio) {
  await page.evaluate(ratio => {
    const range = document.createRange();
    range.selectNodeContents(document.querySelector("#title"));
    document.querySelector(".fit").style.width = `${range.getBoundingClientRect().width * ratio}px`;
  }, ratio);
}
function blockedBy(report, code) {
  assert.equal(report.status, "BLOCKED", JSON.stringify(report));
  assert.ok(report.blocking[code] > 0, JSON.stringify(report));
}

test("a fitting page keeps source typography and passes rendered QA", async t => {
  const page = await fixture(t, {content: '<h1 id="title" style="font-size:83.2px!important;line-height:99.84px;letter-spacing:1px">AI teammate</h1>'});
  const original = await page.$eval("#title", element => element.getAttribute("style"));
  const report = await fit(page);
  assert.equal(report.status, "READY");
  assert.equal(report.regions[0].status, "unchanged");
  assert.equal(report.regions[0].scale, 1);
  assert.equal(await page.$eval("#title", element => element.getAttribute("style")), original);
  assert.equal((await inspect(page)).status, "READY_TO_PUBLISH");
});

for (const [ratio, expected] of [[0.975, 0.95], [0.925, 0.9], [0.875, 0.85], [0.825, 0.8]]) {
  test(`first fitting step is ${expected * 100}% and applies to title and body together`, async t => {
    const page = await fixture(t, {content: '<header data-fit-region="title"><h1 id="title">AI teammate</h1></header><div data-fit-region="body"><p id="body">Body</p></div>'});
    await capacity(page, ratio);
    const report = await fit(page);
    assert.equal(report.status, "READY", JSON.stringify(report));
    assert.equal(report.regions.length, 1);
    assert.equal(report.regions[0].scale, expected);
    near(await fontSize(page), 83.2 * expected);
    near(await fontSize(page, "#body"), 24 * expected);
    assert.equal((await inspect(page)).status, "READY_TO_PUBLISH");
  });
}

test("non-monotonic measurements keep a larger feasible step instead of discarding it after 50% fails", async t => {
  const page = await fixture(t, {setup: async page => page.evaluate(() => {
    // Regression oracle for the reported 60%-pass / 50%-overflow landscape.
    // The feasible 90% band must remain reachable regardless of smaller outcomes.
    window.PresentationMetrics = {...window.PresentationMetrics, regionState() {
      const scale = parseFloat(getComputedStyle(document.querySelector("#title")).fontSize) / 83.2;
      return scale < 0.4924 || (scale > 0.59 && scale < 0.61) || (scale > 0.89 && scale < 0.91) ? "fits" : "overflow";
    }};
  })});
  const outcomes = await page.evaluate(() => {
    const title = document.querySelector("#title"), content = document.querySelector(".fit");
    const outcomes = [0.6, 0.5].map(scale => {
      title.style.fontSize = `${83.2 * scale}px`;
      return window.PresentationMetrics.regionState(content);
    });
    title.style.removeProperty("font-size");
    return outcomes;
  });
  assert.deepEqual(outcomes, ["fits", "overflow"]);
  const report = await fit(page);
  assert.equal(report.regions[0].scale, 0.9);
  near(await fontSize(page), 74.88);
});

test("real font-dependent geometry can fit at 60% and overflow at 50%; forbidden sizes are never kept", async t => {
  const page = await fixture(t, {css: '.fit {width:350px} #title {position:relative;width:max-content}'});
  const outcomes = await page.evaluate(() => {
    const title = document.querySelector("#title"), content = document.querySelector(".fit");
    const range = document.createRange(); range.selectNodeContents(title);
    const width = range.getBoundingClientRect().width;
    title.style.left = `calc(700px - ${(width + 600) / 83.2}em)`;
    const outcomes = [0.6, 0.5].map(scale => {
      title.style.fontSize = `${83.2 * scale}px`;
      return window.PresentationMetrics.regionState(content);
    });
    title.style.removeProperty("font-size");
    return outcomes;
  });
  assert.deepEqual(outcomes, ["fits", "overflow"]);
  const report = await fit(page);
  assert.equal(report.regions[0].status, "fit-floor");
  assert.equal(report.regions[0].scale, 1);
  near(await fontSize(page), 83.2);
  blockedBy(await inspect(page), "fitFloor");
});

test("exhausted steps restore exact styles, including line-height, tracking and priority", async t => {
  const page = await fixture(t, {content: '<h1 id="title" style="font-size:83.2px!important;line-height:99.84px!important;letter-spacing:1.2px!important">AI teammate</h1>'});
  await capacity(page, 0.79);
  const original = await page.$eval("#title", element => element.style.cssText);
  const report = await fit(page);
  assert.equal(report.status, "BLOCKED");
  assert.equal(report.regions[0].status, "fit-floor");
  assert.equal(report.regions[0].scale, 1);
  assert.equal(await page.$eval("#title", element => element.style.cssText), original);
  assert.equal(await page.$eval(".fit", element => element.dataset.overflow), "fit-floor");
  blockedBy(await inspect(page), "fitFloor");
});

test("a small label stops the whole page before the next step falls below 11px", async t => {
  const page = await fixture(t, {content: '<h1 id="title">AI teammate</h1><p id="label" style="font-size:12px">Label</p>'});
  await capacity(page, 0.875);
  const report = await fit(page);
  assert.equal(report.regions[0].status, "fit-floor");
  near(await fontSize(page), 83.2);
  near(await fontSize(page, "#label"), 12);
});

test("the exact 11px boundary is allowed at the 80% step", async t => {
  const page = await fixture(t, {content: '<h1 id="title">AI teammate</h1><p id="label" style="font-size:13.75px">Label</p>'});
  await capacity(page, 0.825);
  const report = await fit(page);
  assert.equal(report.regions[0].scale, 0.8);
  near(await fontSize(page, "#label"), 11);
  assert.equal((await inspect(page)).status, "READY_TO_PUBLISH");
});

test("computed-style rounding at 80% preserves a valid fractional source font size", async t => {
  const page = await fixture(t, {css: '#title {font-size:83.3333px}'});
  await capacity(page, 0.825);
  assert.equal((await fit(page)).regions[0].scale, 0.8);
  near(await fontSize(page), 66.66664);
  assert.equal((await inspect(page)).status, "READY_TO_PUBLISH");
});

test("repeated fitting starts from the source and clears a previous fit-floor after capacity is fixed", async t => {
  const page = await fixture(t);
  await capacity(page, 0.79);
  assert.equal((await fit(page)).status, "BLOCKED");
  await capacity(page, 0.925);
  assert.equal((await fit(page)).regions[0].scale, 0.9);
  assert.equal((await fit(page)).regions[0].scale, 0.9);
  near(await fontSize(page), 74.88);
  assert.equal(await page.$eval(".fit", element => element.hasAttribute("data-overflow")), false);
  await page.$eval(".fit", element => element.style.width = "1600px");
  assert.equal((await fit(page)).regions[0].status, "unchanged");
  near(await fontSize(page), 83.2);
});

test("hidden-page display and visibility survive fitting and rollback", async t => {
  const page = await fixture(t, {css: '.hidden {display:none}', slides: '<section class="slide"><div class="stage"><div class="fit"><h1>Visible</h1></div></div></section><section class="slide hidden" data-fit-display="block" hidden><div class="stage"><div class="fit" style="width:1px"><h1 id="title">Hidden page</h1></div></div></section>'});
  const report = await fit(page);
  assert.equal(report.regions[0].status, "unchanged");
  assert.equal(report.regions[1].status, "fit-floor");
  assert.deepEqual(await page.$eval(".hidden", element => [element.hasAttribute("hidden"), element.style.cssText, getComputedStyle(element).display]), [true, "", "none"]);
  near(await fontSize(page), 83.2);
});

test("source text below 11px stays unchanged and blocks QA even without overflow", async t => {
  const page = await fixture(t, {content: '<p id="small" style="font-size:10.9px">Small source caption</p>'});
  assert.equal((await fit(page)).regions[0].status, "unchanged");
  near(await fontSize(page, "#small"), 10.9);
  const report = await inspect(page);
  blockedBy(report, "smallText");
  assert.equal(report.blocking.textOverflow, undefined);
});

for (const [size, ready] of [[5.5, true], [5.4, false]]) {
  test(`font floor uses the logical 1600px canvas: ${size}px on an 800px stage`, async t => {
    const page = await fixture(t, {css: '.stage,.fit {width:800px;height:450px}', content: `<p style="font-size:${size}px">Caption</p>`});
    await page.setViewportSize({width: 400, height: 300});
    await fit(page);
    const report = await inspect(page);
    if (ready) assert.equal(report.status, "READY_TO_PUBLISH"); else blockedBy(report, "smallText");
  });
}

for (const [name, content, css] of [
  ["HTML transform", '<p style="font-size:20px;transform:scale(.5);transform-origin:top left">Small transformed text</p>', ""],
  ["SVG viewBox", '<svg width="400" height="100" viewBox="0 0 800 200"><text x="20" y="70" font-size="20">Small SVG label</text></svg>', ""],
  ["pseudo-element", '<p class="note">Body</p>', '.note::after {content:"Caption";font-size:10.9px}'],
]) {
  test(`${name} counts towards the 11px QA floor`, async t => {
    const page = await fixture(t, {content, css});
    await fit(page);
    blockedBy(await inspect(page), "smallText");
  });
}

test("QA explicitly rejects a fit-floor marker even when the fit report and geometry pass", async t => {
  const page = await fixture(t);
  await fit(page);
  await page.$eval(".stage", element => element.dataset.overflow = "fit-floor");
  const report = await inspect(page);
  blockedBy(report, "fitFloor");
  assert.equal(report.blocking.textOverflow, undefined);
});

test("QA rejects a 49.237% fit even when 40.97px text has no final overflow", async t => {
  const page = await fixture(t);
  await fit(page);
  await page.evaluate(() => {
    document.querySelector("#title").style.fontSize = "40.97px";
    Object.assign(window.PresentationFit.report.regions[0], {status: "fitted", scale: 0.49237});
  });
  const report = await inspect(page);
  blockedBy(report, "fitScale");
  assert.equal(report.blocking.smallText, undefined);
  assert.equal(report.blocking.textOverflow, undefined);
});

test("QA blocks a stale embedded 10px runtime instead of accepting its fit report", async t => {
  const page = await fixture(t, {setup: async page => page.evaluate(() => {
    window.PresentationMetrics = {...window.PresentationMetrics, MIN_FONT_SIZE_PX: 10};
  })});
  await fit(page);
  blockedBy(await inspect(page), "invalidRuntime");
});

test("font-relative SVG sizing cannot compound a permitted step into more than 20% reduction", async t => {
  const page = await fixture(t, {content: '<h1 id="title">AI teammate</h1><div style="font-size:40px">Lead <svg width="5em" height="2em" viewBox="0 0 400 160"><text x="20" y="70" font-size="48">SVG label</text></svg></div>'});
  await capacity(page, 0.875);
  const report = await fit(page);
  assert.equal(report.regions[0].status, "fit-floor");
  near(await fontSize(page), 83.2);
  near(await page.$eval("svg text", element => window.PresentationMetrics.logicalFontSize(element)), 24);
});

test("QA measures excessive reduction independently of a passing reported scale", async t => {
  const page = await fixture(t);
  await fit(page);
  await page.$eval("#title", element => element.style.transform = "scale(.7)");
  const report = await inspect(page);
  blockedBy(report, "fitScale");
  assert.equal(report.blocking.smallText, undefined);
});

test("installed shell fits on startup and passes live hidden-page navigation QA", async t => {
  const root = mkdtempSync(path.join(os.tmpdir(), "presentation-live-runtime-"));
  t.after(() => rmSync(root, {recursive: true, force: true}));
  mkdirSync(path.join(root, "layouts"));
  mkdirSync(path.join(root, "tools"));
  writeFileSync(path.join(root, "tools/qa-config.json"), JSON.stringify({minFontSizePx: 10,
    expectedPages: 2, safeArea: {left: 0, right: 0, top: 0, bottom: 0}, requiredChrome: [], allowedFontFallbacks: []}));
  const shell = path.join(root, "layouts/_shell.html");
  writeFileSync(shell, `<!doctype html><html><head><style>
    body {margin:0;color:#111;background:#fff;font:24px/1.2 monospace}
    .deck,.stage {width:1600px;height:900px;position:relative}
    .slide {display:none} .slide.active {display:block}
    .fit {position:absolute;inset:0}
    h1 {margin:0;font-size:83.2px;font-weight:400;white-space:nowrap}
    </style></head><body><main class="deck">
    <section class="slide active" data-fit-display="block"><div class="stage"><div class="fit"><h1>Source</h1></div></div></section>
    <section class="slide" data-fit-display="block"><div class="stage"><div class="fit" style="width:185px"><h1 id="title">TEST</h1></div></div></section>
    </main></body></html>`);
  execFileSync(process.execPath, [fileURLToPath(new URL("../scripts/install-qa.mjs", import.meta.url)), "--package", root]);
  const page = await browser.newPage({viewport: {width: 1600, height: 900}, reducedMotion: "reduce"});
  t.after(() => page.close());
  await page.goto(pathToFileURL(shell).href);
  const report = await page.evaluate(async () => {
    await window.PresentationNavigationReady;
    await window.PresentationFit.ready;
    return window.PresentationFit.report;
  });
  assert.equal(report.status, "READY", JSON.stringify(report));
  assert.equal(report.minFontSizePx, 11);
  assert.equal(report.regions[1].scale, 0.9);
  near(await fontSize(page), 74.88);
  assert.equal((await inspect(page)).status, "READY_TO_PUBLISH");
});
