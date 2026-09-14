#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { resolveHyperframesPackage } from "./review-project.mjs";

const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const layoutCatalog = fs.readFileSync(path.join(skillRoot, "references/LAYOUT-CATALOG.md"), "utf8");
const layouts = new Set([...layoutCatalog.matchAll(/^### ([a-z]+\/[a-z0-9-]+)$/gm)].map(match => match[1]));
const router = fs.readFileSync(path.join(skillRoot, "references/ROUTER.md"), "utf8");
const routerRows = new Map([...router.matchAll(/^\| `([a-z]+\/[a-z0-9-]+)` \|.*$/gm)].map(match => [match[1], match[0]]));
const layoutFilename = id => id.replace("/", "--");

function usage(exitCode = 0) {
  const out = exitCode ? console.error : console.log;
  out([
    "Usage:",
    "  node scripts/stage-authoring-kit.mjs --project <dir> --presenter <off|on> [--media-mode none|voice|talking-avatar] [--language tag] [--color-system <built-in-name|custom>] [--color-tokens file] [--layouts family/id,family/id] [--content-font file] [--install] [--clean-managed] [--force]",
    "",
    "Copies the Video Composition integration kit and selected executable official-component starters into an existing HyperFrames project.",
    "It does not modify index.html, invent layouts, write content, or render video.",
    "",
    "Options:",
    "  --project <dir>       Existing HyperFrames project directory (required)",
    "  --presenter <off|on>  Explicit video-level presenter choice (required)",
    "  --media-mode <mode>    none, generated voiceover, or real talking-avatar video",
    "  --language <tag>      Visible-language tag; zh/ja/ko require --content-font on first staging",
    "  --layouts <ids>       Comma-separated layout ids whose executable starters and PNG proofs should be copied",
    "  --content-font <file>  Optional licensed WOFF2, WOFF, TTF, OTF, or TTC font for non-Latin content",
    "  --color-system <name>  One project-wide named collection; legacy blue-white/white-blue aliases are accepted",
    "  --color-tokens <file>  Optional CSS collection defining semantic palette tokens for data-color-system=custom",
    "  --install             Deduplicate and install all Registry items mapped by the selected layouts",
    "  --clean-managed       Remove obsolete or unselected files known to this template; preserve unknown files",
    "  --force               Replace only files managed by this staging script",
    "  --help                Show this message",
  ].join("\n"));
  process.exit(exitCode);
}

function parseArgs(argv) {
  const args = { layoutIds: [], install: false, cleanManaged: false, force: false, language: "en", mediaMode: "none", colorSystem: "navy-cobalt" };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") usage(0);
    if (token === "--force") {
      args.force = true;
      continue;
    }
    if (token === "--clean-managed") {
      args.cleanManaged = true;
      continue;
    }
    if (token === "--install") {
      args.install = true;
      continue;
    }
    if (token === "--project" || token === "--content-font" || token === "--language" || token === "--media-mode" || token === "--color-system" || token === "--color-tokens") {
      if (token === "--content-font") args.contentFont = argv[index + 1];
      else if (token === "--language") args.language = argv[index + 1];
      else if (token === "--media-mode") args.mediaMode = argv[index + 1];
      else if (token === "--color-system") args.colorSystem = argv[index + 1];
      else if (token === "--color-tokens") args.colorTokens = argv[index + 1];
      else args.project = argv[index + 1];
      index += 1;
      continue;
    }
    if (token === "--presenter") {
      args.presenterMode = argv[index + 1];
      index += 1;
      continue;
    }
    if (token === "--layouts") {
      args.layoutIds = (argv[index + 1] || "").split(",").map(value => value.trim()).filter(Boolean);
      index += 1;
      continue;
    }
    console.error(`Unknown argument: ${token}`);
    usage(1);
  }
  return args;
}

function normalizeColorSystem(name) {
  const aliases = {
    "navy-cobalt": "navy-cobalt",
    "blue-white": "navy-cobalt",
    "monumental-minimal": "monumental-minimal",
    "white-blue": "monumental-minimal",
    "black-gold": "black-gold",
    "obsidian-champagne": "obsidian-champagne",
    "petrol-brass": "petrol-brass",
    "parchment-oxblood": "parchment-oxblood",
    "porcelain-carbon": "porcelain-carbon",
    custom: "custom",
  };
  return aliases[name];
}

const args = parseArgs(process.argv.slice(2));
args.colorSystem = normalizeColorSystem(args.colorSystem);
if (!args.project) usage(1);
if (!["off", "on"].includes(args.presenterMode)) {
  console.error("--presenter must be explicitly set to off or on.");
  usage(1);
}
if (!["none", "voice", "talking-avatar"].includes(args.mediaMode)) {
  console.error("--media-mode must be none, voice, or talking-avatar.");
  usage(1);
}
if (!args.colorSystem) {
  console.error("Unknown --color-system. Use a built-in name from the Gallery or custom.");
  process.exit(1);
}
if (args.colorTokens) {
  args.colorTokens = path.resolve(args.colorTokens);
  if (!fs.existsSync(args.colorTokens) || !fs.statSync(args.colorTokens).isFile() || path.extname(args.colorTokens).toLowerCase() !== ".css") {
    console.error("--color-tokens must point to an existing CSS file.");
    process.exit(1);
  }
}
if (args.colorSystem === "custom" && !args.colorTokens) {
  console.error("--color-system custom requires --color-tokens <css-file>.");
  process.exit(1);
}
if (args.mediaMode === "talking-avatar" && args.presenterMode !== "on") {
  console.error("talking-avatar media requires --presenter on.");
  process.exit(1);
}

const projectRoot = path.resolve(args.project);
if (!fs.existsSync(projectRoot) || !fs.statSync(projectRoot).isDirectory()) {
  console.error(`Project directory does not exist: ${projectRoot}`);
  process.exit(1);
}
if (!fs.existsSync(path.join(projectRoot, "hyperframes.json")) || !fs.existsSync(path.join(projectRoot, "index.html"))) {
  console.error("The destination must be an existing HyperFrames project containing hyperframes.json and index.html.");
  process.exit(1);
}
if (args.install && !args.layoutIds.length) {
  console.error("--install requires at least one --layouts id so Registry items can be mapped deterministically.");
  process.exit(1);
}
if (args.contentFont) {
  args.contentFont = path.resolve(args.contentFont);
  const extension = path.extname(args.contentFont).toLowerCase();
  if (!fs.existsSync(args.contentFont) || !fs.statSync(args.contentFont).isFile()) {
    console.error(`Content font does not exist: ${args.contentFont}`);
    process.exit(1);
  }
  if (![".woff2", ".woff", ".ttf", ".otf", ".ttc"].includes(extension)) {
    console.error("--content-font must be WOFF2, WOFF, TTF, OTF, or TTC.");
    process.exit(1);
  }
}
const existingContentFontCss = path.join(projectRoot, "assets/video-composition/content-font.css");
if (/^(?:zh|ja|ko)(?:-|$)/i.test(args.language) && !args.contentFont && !fs.existsSync(existingContentFontCss)) {
  console.error(`Visible language ${args.language} requires a licensed --content-font during first staging.`);
  process.exit(1);
}

const invalidLayouts = args.layoutIds.filter(id => !layouts.has(id));
if (invalidLayouts.length) {
  console.error(`Unknown layout id(s): ${invalidLayouts.join(", ")}`);
  console.error(`Available: ${Array.from(layouts).join(", ")}`);
  process.exit(1);
}

const copied = [];
const skipped = [];
const removed = [];
const installed = [];
const reusedInstalls = [];
const installResults = [];
const referenceRoot = ".style-reference/video-composition";
const previousReceiptPath = path.join(projectRoot, referenceRoot, "REGISTRY-INSTALLS.json");
let previousInstallResults = new Map();
if (fs.existsSync(previousReceiptPath)) {
  try {
    const previousReceipt = JSON.parse(fs.readFileSync(previousReceiptPath, "utf8"));
    previousInstallResults = new Map((previousReceipt.items || []).map(item => [item.name, item]));
  } catch {
    previousInstallResults = new Map();
  }
}

function alreadyInstalledRegistryItems() {
  try {
    const manifest = JSON.parse(fs.readFileSync(path.join(projectRoot, "hyperframes.json"), "utf8"));
    return new Set((manifest.registryItems || []).filter(item => {
      const target = item.target && path.join(projectRoot, item.target);
      return item.name && target && fs.existsSync(target);
    }).map(item => item.name));
  } catch {
    return new Set();
  }
}

function copy(relativeSource, relativeDestination) {
  const source = path.join(skillRoot, relativeSource);
  const destination = path.join(projectRoot, relativeDestination);
  if (!fs.existsSync(source) || !fs.statSync(source).isFile()) {
    throw new Error(`Missing kit source: ${relativeSource}`);
  }
  if (fs.existsSync(destination) && !args.force) {
    skipped.push(relativeDestination);
    return;
  }
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination);
  copied.push(relativeDestination);
}

function copyExternal(source, relativeDestination) {
  const destination = path.join(projectRoot, relativeDestination);
  if (fs.existsSync(destination) && !args.force) {
    skipped.push(relativeDestination);
    return;
  }
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination);
  copied.push(relativeDestination);
}

function writeReference(relativeDestination, content) {
  const destination = path.join(projectRoot, relativeDestination);
  if (fs.existsSync(destination) && !args.force) {
    skipped.push(relativeDestination);
    return;
  }
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, content);
  copied.push(relativeDestination);
}

function writeColorSystemReceipt() {
  const relativeDestination = `${referenceRoot}/COLOR-SYSTEM.json`;
  const destination = path.join(projectRoot, relativeDestination);
  const receipt = {
    schemaVersion: 1,
    scope: "project",
    name: args.colorSystem,
    appliedTo: "all-scenes",
    tokenPrefix: "--palette-",
    source: args.colorSystem === "custom" ? "custom-color-system.css" : "built-in",
  };
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, `${JSON.stringify(receipt, null, 2)}\n`);
  copied.push(relativeDestination);
}

function removeManaged(relativeDestination) {
  const destination = path.join(projectRoot, relativeDestination);
  if (!fs.existsSync(destination) || !fs.statSync(destination).isFile()) return;
  fs.unlinkSync(destination);
  removed.push(relativeDestination);
}

function removeEmptyParents(relativeDirectory, stopRelative) {
  let current = path.join(projectRoot, relativeDirectory);
  const stop = path.join(projectRoot, stopRelative);
  while (current.startsWith(stop) && current !== stop && fs.existsSync(current)) {
    if (fs.readdirSync(current).length) break;
    fs.rmdirSync(current);
    current = path.dirname(current);
  }
}

function cleanManagedReferences(referenceRoot) {
  const retired = [
    "AUTHORING.md", "AUTHORING.zh-CN.md",
    "LAYOUT-CATALOG.md", "LAYOUT-CATALOG.zh-CN.md",
    "HYPERFRAMES-LAYOUT-MAP.md", "HYPERFRAMES-LAYOUT-MAP.zh-CN.md",
    "MOTION.md", "MOTION.zh-CN.md",
    "MOTION-CATALOG.md", "MOTION-CATALOG.zh-CN.md",
    "STYLE.md", "stress-content.json", "layouts/contact-sheet.jpg",
    "VOICE-AVATAR.md",
    "REGISTRY-INSTALLS.json",
  ];
  for (const relative of retired) removeManaged(`${referenceRoot}/${relative}`);

  if (args.layoutIds.length) removeManaged(`${referenceRoot}/ROUTER.md`);
  if (args.presenterMode === "off") {
    removeManaged(`${referenceRoot}/PRESENTER-ADAPTATION.md`);
    for (const relative of [
      "compositions/vc-presenter-scene.html",
      "compositions/vc-presenter-scene.motion.json",
    ]) removeManaged(relative);
  }

  for (const id of layouts) {
    if (args.layoutIds.includes(id)) continue;
    const filename = layoutFilename(id);
    removeManaged(`${referenceRoot}/layouts/preview/${filename}.png`);
    removeManaged(`${referenceRoot}/layouts/source/${filename}.html`);
    removeManaged(`${referenceRoot}/layouts/source/${filename}.motion.json`);
  }
}

function parseJsonEnvelope(output) {
  for (let index = 0; index < output.length; index += 1) {
    if (output[index] !== "{") continue;
    try {
      return JSON.parse(output.slice(index).trim());
    } catch {
      // HyperFrames may print informational lines before its JSON result.
    }
  }
  throw new Error("HyperFrames add did not return a readable JSON result.");
}

function routerBinding(id) {
  const cells = routerRows.get(id).split("|").map(value => value.trim());
  const itemCell = cells[4] || "";
  return {
    layoutId: id,
    routerCode: itemCell.match(/^(C|B|M)\b/)?.[1] || "",
    items: [...itemCell.matchAll(/`([^`]+)`/g)].map(match => match[1]),
  };
}

function mappedRegistryItems() {
  const items = args.layoutIds.flatMap(id => routerBinding(id).items);
  return [...new Set(items)];
}

function installMappedRegistryItems() {
  const command = process.platform === "win32" ? "npx.cmd" : "npx";
  const hyperframesPackage = resolveHyperframesPackage(projectRoot);
  const existing = alreadyInstalledRegistryItems();
  for (const item of mappedRegistryItems()) {
    const previous = previousInstallResults.get(item);
    if (existing.has(item) && previous) {
      installResults.push({ ...previous, reused: true });
      installed.push(item);
      reusedInstalls.push(item);
      console.log(`Reused installed Registry item: ${item}`);
      continue;
    }
    const run = spawnSync(command, [
      "--yes", hyperframesPackage, "add", item,
      "--dir", projectRoot,
      "--json",
      "--no-clipboard",
    ], { cwd: projectRoot, encoding: "utf8" });
    if (run.error || run.status !== 0) {
      if (run.stdout) process.stdout.write(run.stdout);
      if (run.stderr) process.stderr.write(run.stderr);
      console.error(`Failed to install mapped Registry item: ${item}`);
      process.exit(run.status || 1);
    }
    let result;
    try {
      result = parseJsonEnvelope(run.stdout || "");
    } catch (error) {
      console.error(`${item}: ${error.message}`);
      process.exit(1);
    }
    const relativePath = value => path.isAbsolute(value) ? path.relative(projectRoot, value) : value;
    installResults.push({
      name: result.name || item,
      type: result.type || "unknown",
      integration: result.type === "hyperframes:block" ? "scene-copy-with-marked-content-slot" : "scene-fusion-with-baked-starter-defaults",
      snippet: result.snippet || "",
      written: (result.written || []).map(relativePath),
      preserved: (result.preserved || []).map(relativePath),
      installed: result.installed || [item],
      variablesApplied: result.variablesApplied || [],
      warnings: result.warnings || [],
    });
    installed.push(item);
    console.log(`Installed Registry item: ${item}`);
  }
}

function writeInstallReceipt(referenceRoot) {
  const receipt = {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    layouts: args.layoutIds.map(routerBinding),
    items: installResults,
  };
  const relative = `${referenceRoot}/REGISTRY-INSTALLS.json`;
  const destination = path.join(projectRoot, relative);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, `${JSON.stringify(receipt, null, 2)}\n`);
  copied.push(relative);
}

function writeContentFont() {
  if (!args.contentFont) {
    if (!fs.existsSync(existingContentFontCss)) {
      writeReference("assets/video-composition/content-font.css", [
        ".vc-frame {",
        "  --font-body: var(--stage-font-body);",
        "  --font-display: var(--stage-font-display);",
        "  --font-mono: var(--stage-font-mono);",
        "}",
        "",
      ].join("\n"));
    }
    return;
  }
  const extension = path.extname(args.contentFont).slice(1).toLowerCase();
  const format = { woff2: "woff2", woff: "woff", ttf: "truetype", otf: "opentype", ttc: "truetype" }[extension];
  const fontDestination = `assets/video-composition/fonts/content.${extension}`;
  for (const candidate of ["woff2", "woff", "ttf", "otf", "ttc"]) {
    if (candidate !== extension) removeManaged(`assets/video-composition/fonts/content.${candidate}`);
  }
  const absoluteFontDestination = path.join(projectRoot, fontDestination);
  fs.mkdirSync(path.dirname(absoluteFontDestination), { recursive: true });
  fs.copyFileSync(args.contentFont, absoluteFontDestination);
  copied.push(fontDestination);
  const contentFontCss = [
    "@font-face {",
    '  font-family: "VcContent";',
    `  src: url("fonts/content.${extension}") format("${format}");`,
    "  font-weight: 100 900;",
    "  font-style: normal;",
    "  font-display: block;",
    "}",
    "",
    ".vc-frame {",
    '  --stage-font-body: "VcContent", VcBody, Arial, sans-serif;',
    '  --stage-font-display: "VcContent", VcBody, Arial, sans-serif;',
    '  --stage-font-editorial: "VcContent", VcEditorial, Georgia, serif;',
    '  --stage-font-mono: "VcContent", VcMono, monospace;',
    "  --font-body: var(--stage-font-body);",
    "  --font-display: var(--stage-font-display);",
    "  --font-mono: var(--stage-font-mono);",
    "}",
    "",
  ].join("\n");
  fs.writeFileSync(existingContentFontCss, contentFontCss);
  copied.push("assets/video-composition/content-font.css");
}

function buildSelectionReference() {
  const lines = [
    "# Video composition selected reference",
    "",
    "This lean authoring reference is generated by the staging script. It is not a content manifest, runtime input, layout compiler, or renderer.",
    "",
    `- Presenter mode: \`${args.presenterMode}\`; media mode: \`${args.mediaMode}\`.`,
    "- Author real scenes directly with the selected official HyperFrames items; no content JSON or layout generator.",
    ...(args.mediaMode === "none"
      ? ["- No generated speech or talking-avatar wait is part of this build; fix scene durations before scaffolding."]
      : ["- Read `VOICE-AVATAR.md`; generate media and author draft scenes concurrently, then finalize timing from measured durations without rebuilding content."]),
    "- Center complete required content in its real available region. Omit title chrome unless source-required.",
    "- Keep a full presenter at the template standard size. If it does not fit, use the grounded soft-fade `head-shoulders` treatment, move it to a divider, or omit it from that scene.",
    "- Keep the background and presenter settled; use the mapped item's semantic content motion.",
    ...(args.install ? ["- Read `REGISTRY-INSTALLS.json` only when a starter dependency is missing. Scaffolding copies every official dependency per scene and marks its only editable content slot."] : []),
    "- Run Preflight through review-project.mjs; use review-job.mjs start/status for Static and Preview so checks survive tool-session interruption. Wait for each job before the next phase. Release reuses unchanged successful Preview QA.",
    "- Preflight includes deterministic contract checks and HyperFrames lint. An authorized creation request proceeds to rendering after QA; wait for preview approval only when the user requested that gate.",
    "",
    "## Selected layouts",
    "",
  ];

  if (args.layoutIds.length) {
    lines.push("| Layout ID | Choose when | Capacity | Default official item | Motion family | Presenter |");
    lines.push("| --- | --- | --- | --- | --- | --- |");
    for (const id of args.layoutIds) lines.push(routerRows.get(id));
    lines.push("");
    lines.push("Executable HTML starters and motion sidecars are under `layouts/source/`; the corresponding settled PNG proofs are under `layouts/preview/`. Edit the generated scene content slot instead of rebuilding its layout.");
  } else {
    lines.push("No layouts were selected at staging time. Use the compact `ROUTER.md` copied beside this file, then restage with the chosen IDs if proof images are useful.");
  }

  return lines.join("\n");
}

for (const font of ["body.woff2", "editorial.woff2", "condensed.woff2", "mono.woff2"]) {
  copy(`assets/fonts/${font}`, `assets/video-composition/fonts/${font}`);
}
if (args.cleanManaged) cleanManagedReferences(referenceRoot);

copy("assets/runtime/gsap.min.js", "assets/runtime/gsap.min.js");
copy("assets/runtime/stage.css", "assets/video-composition/stage.css");
copy("assets/runtime/color-system.css", "assets/video-composition/color-system.css");
if (args.colorTokens) copyExternal(args.colorTokens, "assets/video-composition/custom-color-system.css");
else copy("assets/runtime/custom-color-system.css", "assets/video-composition/custom-color-system.css");
writeColorSystemReceipt();
writeContentFont();
copy("scripts/review-project.mjs", "scripts/review-project.mjs");
copy("scripts/review-job.mjs", "scripts/review-job.mjs");
copy("scripts/scaffold-scenes.mjs", "scripts/scaffold-scenes.mjs");
copy("scripts/finalize-timing.mjs", "scripts/finalize-timing.mjs");
copy("scripts/set-color-system.mjs", "scripts/set-color-system.mjs");
copy("assets/starter/compositions/vc-scene.html", "compositions/vc-scene.html");
copy("assets/starter/compositions/vc-scene.motion.json", "compositions/vc-scene.motion.json");
if (args.presenterMode === "on") {
  copy("assets/starter/compositions/vc-presenter-scene.html", "compositions/vc-presenter-scene.html");
  copy("assets/starter/compositions/vc-presenter-scene.motion.json", "compositions/vc-presenter-scene.motion.json");
}

writeReference(`${referenceRoot}/SELECTION.md`, buildSelectionReference());
if (!args.layoutIds.length) copy("references/ROUTER.md", `${referenceRoot}/ROUTER.md`);
if (args.presenterMode === "on") copy("references/PRESENTER-ADAPTATION.md", `${referenceRoot}/PRESENTER-ADAPTATION.md`);
if (args.mediaMode !== "none") copy("references/VOICE-AVATAR.md", `${referenceRoot}/VOICE-AVATAR.md`);
copy("assets/starter/demo-index.html", `${referenceRoot}/demo-index.html`);
copy("assets/style-master-a.png", `${referenceRoot}/style-master-a.png`);
copy("assets/style-master-b.png", `${referenceRoot}/style-master-b.png`);

if (args.layoutIds.length) {
  for (const id of args.layoutIds) {
    const filename = layoutFilename(id);
    copy(`assets/layouts/preview/${filename}.png`, `${referenceRoot}/layouts/preview/${filename}.png`);
    copy(`assets/layouts/source/${filename}.html`, `${referenceRoot}/layouts/source/${filename}.html`);
    copy(`assets/layouts/source/${filename}.motion.json`, `${referenceRoot}/layouts/source/${filename}.motion.json`);
  }
}

const adapterLayouts = args.layoutIds.filter(id => fs.existsSync(path.join(skillRoot, "assets/layouts/adapters", `${layoutFilename(id)}.html`)));
if (adapterLayouts.length) {
  copy("assets/runtime/vc-layout-adapter.css", "assets/runtime/vc-layout-adapter.css");
  for (const id of adapterLayouts) {
    const filename = layoutFilename(id);
    copy(`assets/layouts/adapters/${filename}.html`, `compositions/vc-adapters/${filename}.html`);
  }
}

if (adapterLayouts.some(id => id.startsWith("media/"))) {
  copy("assets/style-master-a.png", "assets/video-composition/media/style-master-a.png");
  copy("assets/style-master-b.png", "assets/video-composition/media/style-master-b.png");
}

if (args.layoutIds.some(id => routerBinding(id).routerCode === "M")) {
  copy("assets/layouts/adapters/vc-text-evidence.html", "compositions/vc-text-evidence.html");
}


if (args.install) {
  installMappedRegistryItems();
  writeInstallReceipt(referenceRoot);
}

console.log(`Authoring kit staged in ${projectRoot}`);
console.log(`Copied ${copied.length} file(s); skipped ${skipped.length} existing file(s).`);
if (args.cleanManaged) console.log(`Removed ${removed.length} obsolete or unselected managed file(s); unknown files were preserved.`);
console.log(`Video presenter mode: ${args.presenterMode}`);
console.log(`Long media mode: ${args.mediaMode}`);
console.log(`Color system: ${args.colorSystem}`);
if (args.layoutIds.length) console.log(`Content-form layouts: ${args.layoutIds.join(", ")}`);
if (args.install) console.log(`Registry items ready: ${installed.join(", ")}`);
if (reusedInstalls.length) console.log(`Registry installs reused without network work: ${reusedInstalls.join(", ")}`);
console.log("Use the selected executable layout starters; after scaffolding edit only marked frame slots for components or marked compositions/official/ slots for blocks.");
if (!args.install) console.log("Open .style-reference/video-composition/SELECTION.md and install each mapped Registry item directly, or rerun with --install.");
console.log("Search the Registry only when a mapped item is missing, exceeds real capacity, or expresses the wrong relationship.");
console.log("Start every content fit pass without title chrome; center and fully display the installed HyperFrames item before adding anything else.");
if (args.presenterMode === "off") {
  console.log("Do not add presenter DOM or reserve presenter space in any scene.");
} else {
  console.log("Plan recurring but non-continuous presenter scenes. Keep full presenters at the template standard size; when one does not fit, use a grounded bottom-corner head-and-shoulders treatment, move the person to a divider, or omit the person from that scene.");
}
console.log("Use scaffold-scenes.mjs with --layout-map so IDs, durations, official mounts, and motion sidecars remain aligned.");
console.log("Finish all settled static scenes, then use review-project.mjs for Preflight and review-job.mjs start/status for Static and Preview. Follow each returned job ID before starting another phase.");
if (args.mediaMode !== "none") console.log("Keep media generation running while draft scenes are authored; finalize their timing once from measured media durations.");
console.log("Preflight includes HyperFrames lint; Preview performs the only full browser check and automatically narrows a correction rerun when safe.");
if (skipped.length) console.log("Use --force only when you intend to refresh the managed kit files.");
