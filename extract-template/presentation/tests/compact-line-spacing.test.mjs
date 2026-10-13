import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {mkdtempSync, readFileSync, rmSync, writeFileSync} from "node:fs";
import os from "node:os";
import path from "node:path";
import {fileURLToPath, pathToFileURL} from "node:url";
import test from "node:test";

const MODE = "custom";
const here = path.dirname(fileURLToPath(import.meta.url));
const session = `line-spacing-${MODE}-${process.pid}`;
const browser = (...args) => execFileSync("agent-browser", ["--session", session, ...args], {
  encoding: "utf8", timeout: 60000, maxBuffer: 4 * 1024 * 1024,
});
const evaluate = source => {
  const result = JSON.parse(browser("eval", "-b", Buffer.from(source).toString("base64")).trim());
  return typeof result === "string" ? JSON.parse(result) : result;
};
const auditSource = readFileSync(path.join(here, "../tools/audit.js"), "utf8");
const inspect = () => evaluate(auditSource);
const snapshot = () => evaluate(`JSON.stringify([...document.querySelectorAll('.fit [id]')].map(element => ({
  id: element.id, text: element.textContent, inline: element.getAttribute('style'),
  font: getComputedStyle(element).fontSize, lineHeight: getComputedStyle(element).lineHeight
})))`);
const expected = ["low", "below", "pixels-low", "wrapped", "inline", "normal", "normal-scale", "normal-zoom", "scaled", "table", "list"].sort();

test("rendered compact line spacing remains actionable, non-blocking and read-only", () => {
  try {
    browser("set", "viewport", "1600", "900");
    browser("open", pathToFileURL(path.join(here, "fixtures/compact-line-spacing.html")).href);
    evaluate('window.PRESENTATION_QA_CONFIG={expectedPages:1,minFontSizePx:11,safeArea:{left:.06,right:.06,top:.06,bottom:.06},requiredChrome:[]};true');
    for (const file of ["dom-metrics.js", "fit-text.js"]) {
      evaluate(readFileSync(path.join(here, "../scripts", file), "utf8") + ";true");
    }
    evaluate("(async()=>{await PresentationFit.fit(document.documentElement,PRESENTATION_QA_CONFIG);return true})()");
    const before = snapshot();
    const report = inspect();
    assert.equal(report.status, "READY_TO_PUBLISH", JSON.stringify(report));
    assert.equal(report.hardGateFailures, 0);
    assert.deepEqual(report.reviewRequired || [], []);
    assert.deepEqual(report.advisories.map(item => item.element.slice(1)).sort(), expected);
    for (const item of report.advisories) {
      assert.equal(item.code, "compactLineSpacing");
      assert.equal(item.page, 1);
      assert.equal(item.minRatio, 1.33);
      assert.ok(item.ratio < 1.33 && item.text.length > 0);
      assert.match(item.message, /too compact.*Reorganize the content or layout/u);
      assert.match(item.message, /Preserve all source information and any fixed page-count requirement/u);
    }
    const fitted = report.advisories.find(item => item.element === "#scaled");
    assert.equal(fitted.fontSizePx, 16);
    assert.ok(Math.abs(fitted.lineHeightPx - 18.08) < 0.001);
    const normal = report.advisories.find(item => item.element === "#normal");
    for (const id of ["normal-scale", "normal-zoom"]) {
      const scaled = report.advisories.find(item => item.element === `#${id}`);
      assert.equal(scaled.measurement, "rendered-normal");
      // CSS zoom can change font hinting; transforms preserve the original metrics.
      assert.ok(Math.abs(scaled.ratio - normal.ratio) < (id === "normal-zoom" ? 0.05 : 0.001));
    }
    assert.deepEqual(snapshot(), before, "QA changed text or typography");

    // Hidden text is handled by existing gates; it must not add readability advice.
    evaluate(`document.querySelector('#low').style.visibility='hidden';document.querySelector('#inline').parentElement.style.opacity='0';true`);
    assert.deepEqual(inspect().advisories || [], []);
    evaluate(`document.querySelector('#low').style.visibility='';document.querySelector('#inline').parentElement.style.opacity='';true`);

    // Fixing only the relevant spacing clears the advice without deleting content.
    evaluate(`document.querySelectorAll('.fit p,.fit td,.fit li').forEach(element=>element.style.lineHeight='1.5');true`);
    const fixed = inspect();
    assert.equal(fixed.status, "READY_TO_PUBLISH", JSON.stringify(fixed));
    assert.deepEqual(fixed.advisories || [], []);

    // Force the real custom fitter to reduce both font size and pixel line height.
    evaluate(`document.querySelector('.cases').innerHTML='<p id="fitted-region" data-fit-region style="font-size:20px;line-height:26px;height:42px;overflow:hidden">Fitted first line<br>Second line</p>';true`);
    const fitReport = evaluate("(async()=>{await PresentationFit.fit(document.documentElement,PRESENTATION_QA_CONFIG);return JSON.stringify(PresentationFit.report)})()");
    assert.equal(fitReport.status, "READY");
    assert.ok(fitReport.regions[0].scale < 1, JSON.stringify(fitReport));
    const afterFit = snapshot();
    const fittedReport = inspect();
    assert.equal(fittedReport.status, "READY_TO_PUBLISH", JSON.stringify(fittedReport));
    assert.equal(fittedReport.advisories.length, 1);
    const advice = fittedReport.advisories[0];
    assert.equal(advice.element, "#fitted-region");
    assert.ok(advice.fontSizePx < 20);
    assert.ok(Math.abs(advice.ratio - 1.3) < 0.001);
    assert.deepEqual(snapshot(), afterFit, "QA altered the fitted result");
  } finally {
    try { browser("close"); } catch {}
  }
});

test("the final custom runner retains advice without requesting visual review", () => {
  const directory = mkdtempSync(path.join(os.tmpdir(), "custom-spacing-"));
  try {
    const config = path.join(directory, "config.json");
    writeFileSync(config, JSON.stringify({minFontSizePx: 11,
      safeArea: {left: 0.06, right: 0.06, top: 0.06, bottom: 0.06}, requiredChrome: []}));
    const output = execFileSync(process.execPath, [path.join(here, "../tools/qa.mjs"), "--final",
      path.join(here, "fixtures/compact-line-spacing.html"), "--expected-pages", "1", "--config", config,
      "--capture-dir", path.join(directory, "captures")], {
      encoding: "utf8", timeout: 60000, maxBuffer: 4 * 1024 * 1024,
    });
    const report = JSON.parse(output);
    assert.equal(report.status, "READY_TO_PUBLISH");
    assert.equal(report.hardGateFailures, 0);
    assert.deepEqual(report.advisories.map(item => item.element.slice(1)).sort(), expected);
    assert.deepEqual(report.reviewRequired, []);
    assert.equal(report.captures, undefined);
    assert.equal(report.visualReview, undefined);
  } finally {
    rmSync(directory, {recursive: true, force: true});
  }
});
