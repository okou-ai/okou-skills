#!/usr/bin/env node
import {execFileSync} from "node:child_process";
import {createHash} from "node:crypto";
import {readFileSync, writeFileSync, existsSync} from "node:fs";
import path from "node:path";
import {fileURLToPath, pathToFileURL} from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--final") continue;
  if (args[i].startsWith("--")) options[args[i].slice(2)] = args[++i];
  else if (!options.input) options.input = args[i];
  else throw new Error(`Unexpected argument: ${args[i]}`);
}
if (!options.input || !/^[1-9]\d*$/.test(options["expected-pages"] || "")) {
  console.error("Usage: node tools/qa.mjs --final <deck.html> --expected-pages <n> [--config <json>] [--report <json>] [--review <json>] [--prepared <capture-copy.html>]");
  process.exit(2);
}
const config = JSON.parse(readFileSync(options.config || path.join(here, "qa-config.json"), "utf8"));
config.expectedPages = Number(options["expected-pages"]);
if (config.minFontSizePx !== 10) throw new Error("qa-config.json must set minFontSizePx to 10");
const session = `presentation-qa-${process.pid}`;
const browser = (...command) => execFileSync("agent-browser", ["--session", session, ...command], {encoding: "utf8", timeout: 60000, maxBuffer: 8 * 1024 * 1024});
const parse = value => { const decoded = JSON.parse(value.trim()); return typeof decoded === "string" ? JSON.parse(decoded) : decoded; };
let report;
try {
  browser("set", "viewport", "1600", "900");
  browser("set", "media", "reduced-motion");
  const input = /^https?:\/\//.test(options.input) ? options.input : pathToFileURL(path.resolve(options.input)).href;
  browser("open", input);
  browser("eval", `window.PRESENTATION_QA_CONFIG=${JSON.stringify(config)};1`);
  for (const filename of ["dom-metrics.js", "fit-text.js"]) {
    const source = readFileSync(path.join(here, "../scripts", filename), "utf8");
    const alreadyLoaded = filename === "dom-metrics.js" ? "window.PresentationMetrics" : "window.PresentationFit";
    browser("eval", "-b", Buffer.from(`if(!${alreadyLoaded}){${source}};1`).toString("base64"));
  }
  browser("eval", "-b", Buffer.from("(async()=>{await window.PresentationFit.fit(document.documentElement,window.PRESENTATION_QA_CONFIG);await window.PresentationFit.ready;return 1})()").toString("base64"));
  report = parse(browser("eval", "-b", Buffer.from(readFileSync(path.join(here, "audit.js"), "utf8")).toString("base64")));
  if (report.status === "NEEDS_VISUAL_REVIEW" && options.review && !/^https?:/.test(options.input)) {
    const review = JSON.parse(readFileSync(options.review, "utf8"));
    const hash = createHash("sha256").update(readFileSync(options.input)).digest("hex");
    const pages = new Set(review.pages || []);
    const evidence = review.sourceReferences || [];
    const valid = review.deckSha256 === hash && report.reviewRequired.every(item => pages.has(item.page)) &&
      typeof review.notes === "string" && review.notes.trim().length > 0 && evidence.length > 0 &&
      evidence.every(file => typeof file === "string" && existsSync(path.resolve(path.dirname(options.review), file)));
    if (valid) { report.status = "READY_TO_PUBLISH"; report.visualReview = {deckSha256: hash, pages: [...pages], notes: review.notes}; }
    else { report.status = "BLOCKED"; report.hardGateFailures++; report.blocking.invalidVisualReview = 1; }
  }
  if (options.prepared && report.status === "READY_TO_PUBLISH") {
    const source = path.resolve(options.input);
    const target = path.resolve(options.prepared);
    if (/^https?:/.test(options.input) || source === target || path.dirname(source) !== path.dirname(target)) throw new Error("Prepared capture copy must be a separate HTML file beside the local input");
    browser("eval", 'document.documentElement.dataset.presentationPrepared="capture";1');
    const html = parse(browser("eval", "JSON.stringify(document.documentElement.outerHTML)"));
    writeFileSync(target, "<!doctype html>\n" + html);
    report.prepared = target;
  }
} catch (error) {
  report = {status: "BLOCKED", hardGateFailures: 1, blocking: {qaExecution: 1}, failures: [{code: "qaExecution", message: error.message}]};
} finally {
  try { browser("close"); } catch {}
}
report.target = options.input;
if (options.report) writeFileSync(options.report, JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify(report, null, 2));
process.exitCode = report.status === "READY_TO_PUBLISH" ? 0 : 1;
