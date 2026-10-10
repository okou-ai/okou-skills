#!/usr/bin/env node
import {existsSync, readFileSync, readdirSync, realpathSync, statSync} from "node:fs";
import path from "node:path";
const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length; i += 2) options[args[i]?.replace(/^--/, "")] = args[i + 1];
if (!options.package) { console.error("Usage: node tools/verify-package.mjs --package <dir> [--source-pages <dir>]"); process.exit(2); }
const root = realpathSync(path.resolve(options.package));
const errors = [];
// Source fragments are inserted into layouts/_shell.html, so resolve their
// package-relative resources from layouts/ just as the assembled shell does.
const layoutRoot = path.join(root, "layouts");
const inspected = new Set();
const decodeEntities = value => value.replace(/&(?:amp|quot|apos|lt|gt|#\d+|#x[\da-f]+);/gi, entity => {
  const name = entity.slice(1, -1).toLowerCase();
  if (!name.startsWith("#")) return {amp: "&", quot: '"', apos: "'", lt: "<", gt: ">"}[name];
  const code = name[1] === "x" ? parseInt(name.slice(2), 16) : Number(name.slice(1));
  return code > 0 && code <= 0x10ffff ? String.fromCodePoint(code) : "\ufffd";
});
const escapesRoot = target => {
  const relative = path.relative(realpathSync(root), target);
  return relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative);
};
const checkResource = (value, base, label) => {
  const reference = value.trim();
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
  if (escapesRoot(target) || (existsSync(target) && escapesRoot(realpathSync(target)))) {
    errors.push(`Package resource escapes package: ${label} -> ${reference}`);
  } else if (!existsSync(target) || !statSync(target).isFile()) {
    errors.push(`Missing package resource: ${label} -> ${reference}`);
  } else if (!inspected.has(target) && /\.(?:css|svg|html?)$/i.test(target)) {
    inspected.add(target);
    const source = readFileSync(target, "utf8"), resourceLabel = path.relative(root, target);
    if (/\.css$/i.test(target)) inspectCssResources(source, path.dirname(target), resourceLabel);
    else inspectHtmlResources(source, path.dirname(target), resourceLabel);
  }
};
const cssUnescape = value => value.replace(/\\([\da-f]{1,6})(?:\s)?|\\(.)/gi, (_, hex, character) => {
  const code = hex ? parseInt(hex, 16) : 0;
  return hex ? code > 0 && code <= 0x10ffff ? String.fromCodePoint(code) : "\ufffd" : character;
});
function inspectCssResources(source, base, label) {
  const css = source.replace(/\/\*[\s\S]*?\*\//g, "");
  for (const match of css.matchAll(/url\(\s*(?:"((?:\\.|[^"\\])*)"|'((?:\\.|[^'\\])*)'|([^)]*))\s*\)/gi)) {
    checkResource(cssUnescape(match[1] ?? match[2] ?? match[3]), base, label);
  }
  // String-form @import has no url(), and may introduce further stylesheets.
  for (const match of css.matchAll(/@import\s+(?:"((?:\\.|[^"\\])*)"|'((?:\\.|[^'\\])*)')/gi)) {
    checkResource(cssUnescape(match[1] ?? match[2]), base, label);
  }
}
function srcsetUrls(value) {
  const urls = [];
  let at = 0;
  while (at < value.length) {
    while (/[\s,]/.test(value[at] || "") && at < value.length) at++;
    const start = at;
    while (at < value.length && !/\s/.test(value[at])) at++;
    const url = value.slice(start, at);
    if (!url) break;
    urls.push(url.replace(/,+$/, ""));
    if (url.endsWith(",")) continue;
    // Commas inside a data URL belong to the URL; descriptors end at the next
    // separator outside parentheses, as in the HTML srcset parsing algorithm.
    let parentheses = 0;
    while (at < value.length) {
      const character = value[at++];
      if (character === "(") parentheses++;
      else if (character === ")") parentheses = Math.max(0, parentheses - 1);
      else if (character === "," && !parentheses) break;
    }
  }
  return urls;
}
const inspectHtmlResources = (html, base, label) => {
  const source = html.replace(/<!--[\s\S]*?-->/g, "").replace(/(<script\b[^>]*>)[\s\S]*?<\/script\s*>/gi, "$1</script>");
  for (const style of source.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style\s*>/gi)) inspectCssResources(style[1], base, label);
  const tags = /<([a-z][\w:-]*)\b(?:[^>"']|"[^"]*"|'[^']*')*>/gi;
  const attributes = /([^\s"'<>/=]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))/g;
  for (const tag of source.replace(/<style\b[^>]*>[\s\S]*?<\/style\s*>/gi, "").matchAll(tags)) {
    const attrs = new Map();
    for (const match of tag[0].matchAll(attributes)) {
      const name = match[1].toLowerCase();
      if (!attrs.has(name)) attrs.set(name, decodeEntities(match[2] ?? match[3] ?? match[4]));
    }
    if (attrs.has("style")) inspectCssResources(attrs.get("style"), base, label);
    if (!/^(img|script|source|video|audio|link|iframe|object|embed|image|use)$/i.test(tag[1])) continue;
    for (const name of ["src", "href", "xlink:href", "poster", "data"]) {
      if (attrs.has(name)) checkResource(attrs.get(name), base, label);
    }
    for (const name of ["srcset", "imagesrcset"]) {
      if (attrs.has(name)) for (const url of srcsetUrls(attrs.get(name))) checkResource(url, base, label);
    }
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
  checkResource("styles/template.css", root, "styles/template.css");
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
