#!/usr/bin/env node
import {existsSync, readFileSync, readdirSync} from "node:fs";
import path from "node:path";
const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length; i += 2) options[args[i]?.replace(/^--/, "")] = args[i + 1];
if (!options.package) { console.error("Usage: node tools/verify-package.mjs --package <dir> [--source-pages <dir>]"); process.exit(2); }
const root = path.resolve(options.package);
const errors = [];
for (const file of ["SKILL.md", "design-system.md", "layouts/_shell.html", "layouts/README.md", "styles/template.css", "scripts/dom-metrics.js", "scripts/fit-text.js", "tools/qa-config.json", "tools/audit.js", "tools/qa.mjs", "library/references/catalog.json"]) {
  if (!existsSync(path.join(root, file))) errors.push(`Missing ${file}`);
}
try {
  const index = JSON.parse(readFileSync(path.join(root, "layouts/source-index.json"), "utf8"));
  if (!index.sourceFilename || !Number.isInteger(index.pageCount) || index.pageCount < 1 || !index.sourceAspectRatio) errors.push("Source filename, positive pageCount and original sourceAspectRatio are required");
  const covered = new Set(), ids = new Set();
  if (!Array.isArray(index.layouts) || !index.layouts.length) throw new Error("Source layouts are required");
  for (const layout of index.layouts) {
    if (!layout.id || ids.has(layout.id)) errors.push("Source layout IDs must be unique");
    ids.add(layout.id);
    const file = path.resolve(root, "layouts", layout.file || "");
    const relative = path.relative(path.join(root, "layouts/source"), file);
    if (relative.startsWith("..") || path.isAbsolute(relative) || !relative.endsWith(".html") || !existsSync(file)) errors.push(`Invalid source layout file: ${layout.id}`);
    if (!layout.purpose || !Array.isArray(layout.regions) || !layout.regions.length || !layout.capacity) errors.push(`Record purpose, regions and capacity for ${layout.id}`);
    if (!Array.isArray(layout.sourcePages) || !layout.sourcePages.length) errors.push(`Source pages missing: ${layout.id}`);
    for (const page of layout.sourcePages || []) {
      if (!Number.isInteger(page) || page < 1 || page > index.pageCount) errors.push(`Invalid source page: ${layout.id}`);
      else covered.add(page);
    }
  }
  if (covered.size !== index.pageCount) errors.push(`Covered ${covered.size} of ${index.pageCount} original pages`);
  const catalogue = JSON.parse(readFileSync(path.join(root, "library/references/catalog.json"), "utf8"));
  if (!Array.isArray(catalogue.layouts) || catalogue.layouts.length < 40) errors.push("The local neutral library must contain 40+ references");
  for (const entry of catalogue.layouts || []) {
    if (!existsSync(path.resolve(root, "library/references", entry.file))) errors.push(`Missing local reference ${entry.id}`);
  }
  if (options["source-pages"]) {
    const pages = readdirSync(options["source-pages"]).filter(name => /^page-\d{3}\.png$/.test(name)).sort();
    const expected = Array.from({length: index.pageCount}, (_, i) => `page-${String(i + 1).padStart(3, "0")}.png`);
    if (JSON.stringify(pages) !== JSON.stringify(expected)) errors.push("Original ordered page images must exactly match source pageCount");
  }
  const config = JSON.parse(readFileSync(path.join(root, "tools/qa-config.json"), "utf8"));
  if (config.minFontSizePx !== 10) errors.push("The fixed minimum is 10px");
} catch (error) { errors.push(error.message); }
console.log(JSON.stringify({status: errors.length ? "BLOCKED" : "PACKAGE_VALID", errors}, null, 2));
process.exitCode = errors.length ? 1 : 0;
