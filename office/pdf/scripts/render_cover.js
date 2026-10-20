#!/usr/bin/env node
/**
 * render_cover.js — Render cover.html → cover.pdf via Playwright.
 *
 * Usage:
 *   node render_cover.js --input cover.html --out cover.pdf
 *   node render_cover.js --input cover.html --out cover.pdf --wait 1200
 *
 * Exit codes: 0 success, 1 bad args, 2 dependency missing, 3 render error
 */

const path = require("path");
const fs   = require("fs");
const { pathToFileURL } = require("url");

function usage() {
  console.error("Usage: node render_cover.js --input <file.html> --out <file.pdf> [--wait <ms>]");
  process.exit(1);
}

// ── Arg parsing ────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const checkOnly = args.includes("--check");
let inputFile = null, outFile = null, waitMs = 800;

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--input" && args[i + 1]) { inputFile = args[++i]; }
  else if (args[i] === "--out"   && args[i + 1]) { outFile   = args[++i]; }
  else if (args[i] === "--wait"  && args[i + 1]) { waitMs    = parseInt(args[++i], 10); }
}

if (!checkOnly && (!inputFile || !outFile)) usage();
if (!checkOnly && !fs.existsSync(inputFile)) {
  console.error(JSON.stringify({ status: "error", error: `File not found: ${inputFile}` }));
  process.exit(1);
}

// ── Playwright loader (tolerates global npm installs) ─────────────────────────
function loadPlaywright() {
  const { execSync } = require("child_process");
  try { return require("playwright"); } catch (_) {}
  try {
    const root = execSync("npm root -g", { stdio: ["ignore","pipe","ignore"] }).toString().trim();
    return require(path.join(root, "playwright"));
  } catch (_) {}
  console.error(JSON.stringify({
    status: "error",
    error: "playwright not found",
    hint: "Run: npm install -g playwright && npx playwright install chromium"
  }));
  process.exit(2);
}

// ── Main ───────────────────────────────────────────────────────────────────────
(async () => {
  const { chromium } = loadPlaywright();

  let browser;
  try {
    browser = await chromium.launch();
  } catch (e) {
    console.error(JSON.stringify({
      status: "error", error: String(e),
      hint: "Run: bash scripts/make.sh fix (install Chromium and its OS dependencies)"
    }));
    process.exit(2);
  }

  if (checkOnly) {
    await browser.close();
    console.log("Chromium launch check passed");
    return;
  }

  try {
    const page = await browser.newPage();
    const fileUrl = pathToFileURL(path.resolve(inputFile)).href;
    await page.goto(fileUrl);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(waitMs);   // let CSS + any JS settle

    await page.pdf({
      path:            outFile,
      width:           "794px",
      height:          "1123px",
      printBackground: true,
    });

    await browser.close();

    // Basic sanity: output file must exist and be > 5 KB
    const stat = fs.statSync(outFile);
    if (stat.size < 5000) {
      console.error(JSON.stringify({
        status: "error",
        error: "Output PDF is suspiciously small — cover may be blank",
        hint:  "Check cover.html for render errors"
      }));
      process.exit(3);
    }

    console.log(JSON.stringify({
      status: "ok",
      out:    outFile,
      size_kb: Math.round(stat.size / 1024),
    }));

  } catch (e) {
    if (browser) await browser.close().catch(() => {});
    console.error(JSON.stringify({ status: "error", error: String(e) }));
    process.exit(3);
  }
})();
