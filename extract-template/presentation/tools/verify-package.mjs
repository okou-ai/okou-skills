#!/usr/bin/env node
import {existsSync, readFileSync, readdirSync} from "node:fs";
import path from "node:path";
const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length; i += 2) options[args[i]?.replace(/^--/, "")] = args[i + 1];
if (!options.package) { console.error("Usage: node tools/verify-package.mjs --package <dir> [--source-pages <dir>]"); process.exit(2); }
const root = path.resolve(options.package);
const errors = [];
// Source fragments are inserted into layouts/_shell.html, so resolve their
// package-relative resources from layouts/ just as the assembled shell does.
const layoutRoot = path.join(root, "layouts");
const checkResource = (value, base, label) => {
  const reference = value.trim().replaceAll("&amp;", "&");
  if (!reference || /^(?:data:|blob:|#)/i.test(reference)) return;
  if (/^(?:https?:)?\/\//i.test(reference) || /^[a-z][a-z\d+.-]*:/i.test(reference)) {
    errors.push(`External package resource: ${label} -> ${reference}`);
    return;
  }
  let pathname;
  try { pathname = decodeURIComponent(reference.split(/[?#]/, 1)[0]); }
  catch { errors.push(`Invalid package resource path: ${label} -> ${reference}`); return; }
  if (!pathname) return;
  const target = path.resolve(base, pathname);
  const relative = path.relative(root, target);
  if (relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    errors.push(`Package resource escapes package: ${label} -> ${reference}`);
  } else if (!existsSync(target)) {
    errors.push(`Missing package resource: ${label} -> ${reference}`);
  }
};
const inspectHtmlResources = (html, base, label) => {
  const tags = /<(?:img|script|source|video|audio|link|iframe|object|embed|image|use)\b[^>]*>/gi;
  const attributes = /\b(?:src|href|xlink:href|poster|data)\s*=\s*(["'])(.*?)\1/gi;
  for (const tag of html.matchAll(tags)) {
    for (const match of tag[0].matchAll(attributes)) checkResource(match[2], base, label);
  }
  for (const match of html.matchAll(/url\(\s*(?:"([^"]*)"|'([^']*)'|([^)]*))\s*\)/gi)) {
    checkResource(match[1] ?? match[2] ?? match[3], base, label);
  }
};
const countClass = (html, className) => [...html.matchAll(/<[^>]+\bclass\s*=\s*(["'])(.*?)\1[^>]*>/gs)]
  .filter(match => match[2].split(/\s+/).includes(className)).length;
for (const file of ["SKILL.md", "design-system.md", "layouts/_shell.html", "layouts/README.md", "styles/template.css", "scripts/dom-metrics.js", "scripts/fit-text.js", "tools/qa-config.json", "tools/audit.js", "tools/qa.mjs", "library/references/catalog.md"]) {
  if (!existsSync(path.join(root, file))) errors.push(`Missing ${file}`);
}
try {
  const index = JSON.parse(readFileSync(path.join(root, "layouts/source-index.json"), "utf8"));
  if (!index.sourceFilename || !Number.isInteger(index.pageCount) || index.pageCount < 1 || !index.sourceAspectRatio) errors.push("Source filename, positive pageCount and original sourceAspectRatio are required");
  const shell = readFileSync(path.join(root, "layouts/_shell.html"), "utf8");
  if (countClass(shell, "slide") !== index.pageCount) errors.push(`Source shell has ${countClass(shell, "slide")} slides; expected ${index.pageCount}`);
  if (countClass(shell, "stage") !== index.pageCount) errors.push(`Source shell has ${countClass(shell, "stage")} stages; expected ${index.pageCount}`);
  inspectHtmlResources(shell, layoutRoot, "layouts/_shell.html");
  const stylesheet = path.join(root, "styles/template.css");
  inspectHtmlResources(readFileSync(stylesheet, "utf8"), path.dirname(stylesheet), "styles/template.css");
  const covered = new Set(), ids = new Set();
  if (!Array.isArray(index.layouts) || !index.layouts.length) throw new Error("Source layouts are required");
  for (const layout of index.layouts) {
    if (!layout.id || ids.has(layout.id)) errors.push("Source layout IDs must be unique");
    ids.add(layout.id);
    const file = path.resolve(root, "layouts", layout.file || "");
    const relative = path.relative(path.join(root, "layouts/source"), file);
    if (relative.startsWith("..") || path.isAbsolute(relative) || !relative.endsWith(".html") || !existsSync(file)) errors.push(`Invalid source layout file: ${layout.id}`);
    if (!layout.purpose || !Array.isArray(layout.regions) || !layout.regions.length || !layout.capacity) errors.push(`Record purpose, regions and capacity for ${layout.id}`);
    if (existsSync(file)) inspectHtmlResources(readFileSync(file, "utf8"), layoutRoot, `layouts/${layout.file}`);
    if (!Array.isArray(layout.sourcePages) || !layout.sourcePages.length) errors.push(`Source pages missing: ${layout.id}`);
    for (const page of layout.sourcePages || []) {
      if (!Number.isInteger(page) || page < 1 || page > index.pageCount) errors.push(`Invalid source page: ${layout.id}`);
      else covered.add(page);
    }
  }
  if (covered.size !== index.pageCount) errors.push(`Covered ${covered.size} of ${index.pageCount} original pages`);
  const table = readFileSync(path.join(root, "library/references/catalog.md"), "utf8");
  const links = [...table.matchAll(/\[([a-z0-9-]+)\]\(\.\.\/layouts\/fragments\/([a-z0-9-]+\.html)\)/g)];
  const files = readdirSync(path.join(root, "library/layouts/fragments")).filter(name => name.endsWith(".html"));
  if (links.length < 40 || files.length < 40) errors.push("The local neutral library must contain 40+ references");
  const listed = new Set(links.map(match => match[2]));
  if (listed.size !== links.length || files.length !== listed.size || files.some(file => !listed.has(file))) errors.push("The layout table must list every local fragment exactly once");
  for (const [, id, file] of links) {
    if (file !== `${id}.html` || !existsSync(path.join(root, "library/layouts/fragments", file))) errors.push(`Missing or invalid local reference ${id}`);
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
