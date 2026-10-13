import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {createHash} from "node:crypto";
import {mkdtempSync, mkdirSync, rmSync, writeFileSync} from "node:fs";
import os from "node:os";
import path from "node:path";
import {fileURLToPath, pathToFileURL} from "node:url";
import {after, before, test} from "node:test";
import {chromium} from "playwright";
import {showCapturePage} from "../tools/capture.mjs";

let browser;
before(async () => { browser = await chromium.launch({executablePath: process.env.PRESENTATION_CHROMIUM_PATH, headless: true}); });
after(async () => { await browser?.close(); });

for (const mode of ["paged", "scroll"]) {
  test(`QA captures actual ${mode} pages with nested sections and positional CSS`, async t => {
    const root = mkdtempSync(path.join(os.tmpdir(), "presentation-capture-"));
    t.after(() => rmSync(root, {recursive: true, force: true}));
    mkdirSync(path.join(root, "layouts")); mkdirSync(path.join(root, "tools"));
    writeFileSync(path.join(root, "tools/qa-config.json"), JSON.stringify({minFontSizePx: 11,
      safeArea: {left: 0, right: 0, top: 0, bottom: 0}, requiredChrome: [], allowedFontFallbacks: []}));
    const file = path.join(root, "layouts/_shell.html");
    writeFileSync(file, `<!doctype html><html><head><style>
      .stage{width:1600px;height:900px;background:#fff;color:#111;font:40px/1.3 Arial}
      .fit{position:absolute;inset:10%} .slide:nth-child(2) .stage{background:#f0a040}
      .slide:nth-child(3) .stage{background:#40a0f0} canvas{width:200px;height:100px}
      </style></head><body><main class="deck" data-navigation-mode="${mode}">
      ${[1, 2, 3].map(i => `<section class="slide" data-fit-display="block"><div class="stage"><div class="fit">
        <section><section><h1>Page ${i}</h1></section><canvas width="200" height="100"></canvas></section>
        </div></div></section>`).join("")}</main></body></html>`);
    execFileSync(process.execPath, [fileURLToPath(new URL("../scripts/install-qa.mjs", import.meta.url)), "--package", root]);
    const page = await browser.newPage({viewport: {width: 1600, height: 900}, reducedMotion: "reduce"});
    t.after(() => page.close());
    await page.goto(pathToFileURL(file).href);
    await page.evaluate(async () => {
      await window.PresentationNavigationReady;
      document.querySelectorAll("canvas").forEach((canvas, i) => {
        const ctx = canvas.getContext("2d"); ctx.fillStyle = ["red", "green", "blue"][i]; ctx.fillRect(0, 0, 200, 100);
      });
    });
    const hashes = [];
    for (const index of [2, 0, 1]) {
      const frame = await page.evaluate(showCapturePage, index);
      assert.equal(frame.page, index + 1);
      assert.equal(frame.stage.width, 1600);
      assert.equal(frame.stage.height, 900);
      const shown = await page.locator('.slide[aria-current="page"] h1').textContent();
      assert.equal(shown, `Page ${index + 1}`);
      const before = await page.screenshot();
      await page.evaluate(showCapturePage, index);
      assert.deepEqual(await page.screenshot(), before, "repeat capture preserves the same painted page");
      hashes.push(createHash("sha256").update(before).digest("hex"));
    }
    assert.equal(new Set(hashes).size, 3, "captures must not repeat the cover");
    assert.equal(await page.locator('.deck > .slide').count(), 3, "capture leaves the DOM intact");
    await assert.rejects(page.evaluate(showCapturePage, 3), /Missing capture page 4/);
  });
}
