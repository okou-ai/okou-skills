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
const sourceProfiles = new Set();
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
const checkResource = (value, base, label, inspectContent = true) => {
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
  } else if (!inspected.has(target) && (/\.md$/i.test(target) || inspectContent && /\.(?:css|svg|html?)$/i.test(target))) {
    inspected.add(target);
    const source = readFileSync(target, "utf8"), resourceLabel = path.relative(root, target);
    if (/\.md$/i.test(target)) {
      for (const reference of markdownTargets(source)) {
        // Provenance links may be external; local guidance must travel with the package.
        if (/^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(reference)) continue;
        checkResource(reference, path.dirname(target), resourceLabel, false);
      }
    } else if (/\.css$/i.test(target)) inspectCssResources(source, path.dirname(target), resourceLabel);
    else inspectHtmlResources(source, path.dirname(target), resourceLabel);
  }
};
function markdownTargets(source) {
  const text = source.replace(/^ {0,3}(`{3,}|~{3,})[^\n]*\n[\s\S]*?^ {0,3}\1[ \t]*$/gm, "")
    .replace(/(`+)[^\n]*?\1/g, "");
  const inline = [...text.matchAll(/\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)]+))(?:\s+["'][^"'\n]*["'])?\s*\)/g)];
  const definitions = [...text.matchAll(/^ {0,3}\[[^\]\n]+\]:[ \t]*(?:<([^>\n]+)>|([^\s]+))/gm)];
  return [...inline, ...definitions].map(match => match[1] ?? match[2]);
}
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
const htmlSource = html => html.replace(/<!--[\s\S]*?-->/g, "").replace(/(<script\b[^>]*>)[\s\S]*?<\/script\s*>/gi, "$1</script>");
function* htmlElements(html) {
  const tags = /<(\/?)([a-z][\w:-]*)\b(?:[^>"']|"[^"]*"|'[^']*')*>/gi;
  const attributes = /([^\s"'<>/=]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))/g;
  const stack = [], voids = new Set("area base br col embed hr img input link meta param source track wbr".split(" "));
  for (const tag of htmlSource(html).replace(/<style\b[^>]*>[\s\S]*?<\/style\s*>/gi, "").matchAll(tags)) {
    const name = tag[2].toLowerCase();
    if (tag[1]) {
      const at = stack.findLastIndex(element => element.name === name);
      if (at >= 0) stack.length = at;
      continue;
    }
    const attrs = new Map();
    for (const match of tag[0].matchAll(attributes)) {
      const name = match[1].toLowerCase();
      if (!attrs.has(name)) attrs.set(name, decodeEntities(match[2] ?? match[3] ?? match[4]));
    }
    const element = {name, attrs, parent: stack.at(-1)};
    yield element;
    if (!voids.has(name) && !/\/\s*>$/.test(tag[0])) stack.push(element);
  }
}
const hasClass = (element, name) => Boolean(element && (element.attrs.get("class") || "").split(/\s+/).includes(name));
const inside = (element, ancestor) => {
  for (let parent = element.parent; parent; parent = parent.parent) if (parent === ancestor) return true;
  return false;
};
function inspectLayoutStructure(html, label, sharedShell = false) {
  const elements = [...htmlElements(html)];
  const slides = elements.filter(element => hasClass(element, "slide"));
  const stages = elements.filter(element => hasClass(element, "stage"));
  const fits = elements.filter(element => hasClass(element, "fit"));
  if (!sharedShell && slides.length !== 1) errors.push(`${label}: source fragment needs exactly one .slide`);
  for (const slide of slides) {
    if (sharedShell && !hasClass(slide.parent, "deck")) errors.push(`${label}: shell slides must be direct children of .deck`);
    if (!sharedShell && slide.parent) errors.push(`${label}: source .slide must be a top-level fragment`);
    if (stages.filter(stage => inside(stage, slide)).length !== 1) errors.push(`${label}: each .slide needs exactly one .stage`);
  }
  for (const stage of stages) {
    if (slides.filter(slide => inside(stage, slide)).length !== 1) errors.push(`${label}: .stage must belong to exactly one .slide`);
    if (fits.filter(fit => inside(fit, stage)).length !== 1) errors.push(`${label}: each .stage needs exactly one .fit content root`);
  }
  for (const fit of fits) {
    if (stages.filter(stage => inside(fit, stage)).length !== 1) errors.push(`${label}: .fit must be inside its .stage`);
  }
}
const inspectHtmlResources = (html, base, label, sourceLayout = false) => {
  for (const style of htmlSource(html).matchAll(/<style\b[^>]*>([\s\S]*?)<\/style\s*>/gi)) inspectCssResources(style[1], base, label);
  for (const {name, attrs} of htmlElements(html)) {
    if (sourceLayout && (attrs.get("class") || "").split(/\s+/).includes("stage")) {
      sourceProfiles.add(attrs.get("data-layout") || attrs.get("data-source-profile") || "default");
    }
    if (attrs.has("style")) inspectCssResources(attrs.get("style"), base, label);
    if (!/^(img|script|source|video|audio|link|iframe|object|embed|image|use)$/i.test(name)) continue;
    for (const name of ["src", "href", "xlink:href", "poster", "data"]) {
      if (attrs.has(name)) checkResource(attrs.get(name), base, label);
    }
    for (const name of ["srcset", "imagesrcset"]) {
      if (attrs.has(name)) for (const url of srcsetUrls(attrs.get(name))) checkResource(url, base, label);
    }
  }
};
const countClass = (html, className) => [...htmlElements(html)]
  .filter(({attrs}) => (attrs.get("class") || "").split(/\s+/).includes(className)).length;
for (const file of ["SKILL.md", "design-system.md", "layouts/_shell.html", "layouts/README.md", "layouts/source-index.json", "styles/template.css",
  "scripts/dom-metrics.js", "scripts/fit-text.js", "scripts/navigation.js", "tools/qa-config.json", "tools/audit.js", "tools/qa.mjs", "tools/run.sh",
  "references/generate/workflow.md", "references/generate/qa.md", "references/generate/runtime-contract.md", "references/generate/typography-fit.md", "references/generate/layout-reuse.md",
  "library/README.md", "library/references/catalog.md", "library/styles/geometry.css"]) {
  checkResource(file, root, "Required package file");
}
try {
  const entrypoint = readFileSync(path.join(root, "SKILL.md"), "utf8");
  const workflow = path.join(root, "references/generate/workflow.md");
  if (!markdownTargets(entrypoint).some(reference => path.resolve(root, decodeURIComponent(reference.split(/[?#]/, 1)[0])) === workflow)) {
    errors.push("Package SKILL.md must link to references/generate/workflow.md");
  }
  for (const name of readdirSync(path.join(root, "references"))) {
    if (name !== "generate") errors.push(`Package references are generation-only: references/${name}`);
  }
  for (const file of ["scripts/inventory-html.py", "scripts/source-derivatives.py", "scripts/install-qa.mjs", "scripts/render-pages.mjs", "scripts/libreoffice.mjs", "tools/verify-package.mjs", "tests"]) {
    if (existsSync(path.join(root, file))) errors.push(`Extraction/development file belongs outside the saved package: ${file}`);
  }
  const index = JSON.parse(readFileSync(path.join(root, "layouts/source-index.json"), "utf8"));
  if (!index.sourceFilename || !Number.isInteger(index.pageCount) || index.pageCount < 1 || !index.sourceAspectRatio) errors.push("Source filename, positive pageCount and original sourceAspectRatio are required");
  const shell = readFileSync(path.join(root, "layouts/_shell.html"), "utf8");
  if (countClass(shell, "deck") !== 1) errors.push("Shared shell needs exactly one .deck insertion point");
  inspectLayoutStructure(shell, "layouts/_shell.html", true);
  inspectHtmlResources(shell, layoutRoot, "layouts/_shell.html", true);
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
    if (existsSync(file)) {
      const html = readFileSync(file, "utf8"), label = `layouts/${layout.file}`;
      inspectLayoutStructure(html, label);
      inspectHtmlResources(html, layoutRoot, label, true);
    }
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
    const entries = readdirSync(options["source-pages"], {withFileTypes: true});
    const pages = entries.map(entry => entry.name).sort();
    const expected = Array.from({length: index.pageCount}, (_, i) => `page-${String(i + 1).padStart(3, "0")}.png`);
    const unexpected = entries.filter(entry => !entry.isFile() || !expected.includes(entry.name)).map(entry => entry.name);
    if (unexpected.length) errors.push(`Unexpected source capture entries: ${unexpected.join(", ")}. Keep contact sheets, review outputs and PDFs outside --source-pages.`);
    if (JSON.stringify(pages) !== JSON.stringify(expected)) errors.push("Original ordered page images must exactly match source pageCount");
  }
  const config = JSON.parse(readFileSync(path.join(root, "tools/qa-config.json"), "utf8"));
  const object = value => value !== null && typeof value === "object" && !Array.isArray(value);
  const validSafe = value => object(value) && ["left", "right", "top", "bottom"].every(key => Number.isFinite(value[key]) && value[key] >= 0 && value[key] < 1) && value.left + value.right < 1 && value.top + value.bottom < 1;
  if (!object(config)) throw new Error("qa-config.json must be an object");
  if (config.minFontSizePx !== 11) errors.push("The fixed minimum is 11px");
  if (config.safeArea != null && !validSafe(config.safeArea)) errors.push("Invalid source safeArea");
  const areas = config.layoutSafeAreas ?? {};
  if (!object(areas)) errors.push("layoutSafeAreas must be an object");
  else {
    for (const [key, area] of Object.entries(areas)) if (!key.trim() || !validSafe(area)) errors.push(`Invalid layoutSafeAreas entry: ${key}`);
    if (!validSafe(config.safeArea)) {
      if (!Object.values(areas).some(validSafe)) errors.push("Record a source safeArea or layoutSafeAreas before saving the template");
      for (const key of sourceProfiles) if (!Object.hasOwn(areas, key) || !validSafe(areas[key])) errors.push(`Missing source safe area for ${key}`);
    }
  }
  if (config.minContrastRatio !== undefined && (!Number.isFinite(config.minContrastRatio) || config.minContrastRatio < 3 || config.minContrastRatio > 21)) errors.push("minContrastRatio must be within 3..21");
  if (config.allowedFontFallbacks !== undefined && (!Array.isArray(config.allowedFontFallbacks) || config.allowedFontFallbacks.some(family => typeof family !== "string" || !family.trim()))) errors.push("allowedFontFallbacks must be an array of font-family names");
  if (config.requiredChrome !== undefined) {
    if (!Array.isArray(config.requiredChrome)) errors.push("requiredChrome must be an array");
    else for (const rule of config.requiredChrome) {
      const min = rule?.min ?? 1, max = rule?.max ?? min;
      if (!object(rule) || typeof rule.role !== "string" || !rule.role.trim() || !Number.isInteger(min) || min < 0 || !Number.isInteger(max) || max < min ||
        (rule.layouts !== undefined && (!Array.isArray(rule.layouts) || rule.layouts.some(key => typeof key !== "string" || !key.trim())))) errors.push("Invalid source requiredChrome rule");
    }
  }
} catch (error) { errors.push(error.message); }
console.log(JSON.stringify({status: errors.length ? "BLOCKED" : "PACKAGE_VALID", errors}, null, 2));
process.exitCode = errors.length ? 1 : 0;
