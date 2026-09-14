#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const hyperframesVersion = "0.8.38";

function usage(exitCode = 0) {
  const out = exitCode ? console.error : console.log;
  out([
    "Usage:",
    "  node scripts/bootstrap-project.mjs --project <dir> --host-id <id> --presenter <off|on> --media-mode <none|voice|talking-avatar> --language <tag> --scenes id:<seconds|auto>,id:<seconds|auto> --layout-map id=family/layout,id=family/layout [--color-system <built-in-name|custom>] [--color-tokens file] [--presenter-scenes id,id] [--content-font file] [--force]",
    "  node scripts/bootstrap-project.mjs --prepare-only --project <dir> --presenter <off|on> --media-mode <voice|talking-avatar> --language <tag> --layout-map id=family/layout,id=family/layout [--color-system <built-in-name|custom>] [--color-tokens file] [--content-font file] [--force]",
    "",
    `Initializes new projects with HyperFrames ${hyperframesVersion} and stages/installs selected official items once. Existing projects keep their pin.`,
    "Full mode creates executable scene starters; auto uses provisional authoring windows, while prepare-only leaves timing and the host untouched.",
    "It never researches the subject, chooses layouts, writes content, or renders video.",
  ].join("\n"));
  process.exit(exitCode);
}

function parseArgs(argv) {
  const args = { presenterScenes: [], force: false, prepareOnly: false, mediaMode: "none", colorSystem: "navy-cobalt" };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") usage(0);
    if (token === "--force") {
      args.force = true;
      continue;
    }
    if (token === "--prepare-only") {
      args.prepareOnly = true;
      continue;
    }
    if (["--project", "--host-id", "--presenter", "--media-mode", "--language", "--scenes", "--layout-map", "--presenter-scenes", "--content-font", "--color-system", "--color-tokens"].includes(token)) {
      const value = argv[index + 1];
      if (!value) usage(1);
      if (token === "--project") args.project = value;
      if (token === "--host-id") args.hostId = value;
      if (token === "--presenter") args.presenter = value;
      if (token === "--media-mode") args.mediaMode = value;
      if (token === "--language") args.language = value;
      if (token === "--scenes") args.scenes = value;
      if (token === "--layout-map") args.layoutMap = value;
      if (token === "--presenter-scenes") args.presenterScenes = value.split(",").map(item => item.trim()).filter(Boolean);
      if (token === "--content-font") args.contentFont = value;
      if (token === "--color-system") args.colorSystem = value;
      if (token === "--color-tokens") args.colorTokens = value;
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

function run(command, args, cwd, label) {
  const started = performance.now();
  const result = spawnSync(command, args, { cwd, encoding: "utf8", stdio: "inherit" });
  const seconds = ((performance.now() - started) / 1000).toFixed(2);
  if (result.error || result.status !== 0) throw new Error(`${label} failed after ${seconds}s.`);
  console.log(`${label}: ${seconds}s`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.project || !args.layoutMap || !args.language || !["off", "on"].includes(args.presenter)) usage(1);
  if (!["none", "voice", "talking-avatar"].includes(args.mediaMode)) usage(1);
  args.colorSystem = normalizeColorSystem(args.colorSystem);
  if (!args.colorSystem) throw new Error("Unknown --color-system. Use a built-in name from the Gallery or custom.");
  if (args.colorSystem === "custom" && !args.colorTokens) throw new Error("--color-system custom requires --color-tokens <css-file>.");
  if (args.mediaMode === "talking-avatar" && args.presenter !== "on") throw new Error("talking-avatar media requires --presenter on.");
  if (!args.prepareOnly && (!args.hostId || !args.scenes)) usage(1);
  const projectRoot = path.resolve(args.project);
  const layoutEntries = args.layoutMap.split(",").map(item => item.trim()).filter(Boolean);
  const layouts = [...new Set(layoutEntries.map(entry => entry.slice(entry.indexOf("=") + 1)))];
  if (layoutEntries.some(entry => !/^[a-z][a-z0-9-]*=[a-z]+\/[a-z0-9-]+$/.test(entry))) {
    throw new Error("--layout-map entries must use scene-id=family/layout-id.");
  }
  const existingFontCss = path.join(projectRoot, "assets/video-composition/content-font.css");
  if (args.contentFont && (!fs.existsSync(args.contentFont) || !fs.statSync(args.contentFont).isFile())) {
    throw new Error(`Content font does not exist: ${args.contentFont}`);
  }
  if (/^(?:zh|ja|ko)(?:-|$)/i.test(args.language) && !args.contentFont && !fs.existsSync(existingFontCss)) {
    throw new Error(`${args.language} requires --content-font on the first bootstrap.`);
  }

  const npx = process.platform === "win32" ? "npx.cmd" : "npx";
  if (!fs.existsSync(path.join(projectRoot, "hyperframes.json"))) {
    if (fs.existsSync(path.join(projectRoot, "index.html"))) {
      throw new Error("Refusing to initialize over an existing index.html without a HyperFrames project. Restore its project configuration first.");
    }
    fs.mkdirSync(path.dirname(projectRoot), { recursive: true });
    run(npx, ["--yes", `hyperframes@${hyperframesVersion}`, "init", projectRoot, "--non-interactive", "--example=blank"], path.dirname(projectRoot), "HyperFrames init");
    // Trust only the exact blank host created by this invocation, not a changing template comment.
    const receiptDir = path.join(projectRoot, ".hyperframes", "video-composition");
    fs.mkdirSync(receiptDir, { recursive: true });
    fs.writeFileSync(path.join(receiptDir, "bootstrap.json"), JSON.stringify({
      hyperframesVersion,
      blankIndexSha256: crypto.createHash("sha256").update(fs.readFileSync(path.join(projectRoot, "index.html"))).digest("hex"),
    }, null, 2) + "\n");
  }

  const stageArgs = [
    path.join(skillRoot, "scripts/stage-authoring-kit.mjs"),
    "--project", projectRoot,
    "--presenter", args.presenter,
    "--media-mode", args.mediaMode,
    "--language", args.language,
    "--layouts", layouts.join(","),
    "--color-system", args.colorSystem,
    "--install",
    "--clean-managed",
  ];
  if (args.contentFont) stageArgs.push("--content-font", path.resolve(args.contentFont));
  if (args.colorTokens) stageArgs.push("--color-tokens", path.resolve(args.colorTokens));
  if (args.force) stageArgs.push("--force");
  run(process.execPath, stageArgs, projectRoot, "stage/install");

  if (args.prepareOnly) {
    console.log(`media-parallel preparation complete: ${projectRoot}`);
    console.log("After media finishes, measure exact durations and run scripts/scaffold-scenes.mjs once.");
    return;
  }

  const scaffoldArgs = [
    path.join(projectRoot, "scripts/scaffold-scenes.mjs"),
    "--project", projectRoot,
    "--host-id", args.hostId,
    "--presenter", args.presenter,
    "--language", args.language,
    "--color-system", args.colorSystem,
    "--scenes", args.scenes,
    "--layout-map", args.layoutMap,
  ];
  if (args.presenterScenes.length) scaffoldArgs.push("--presenter-scenes", args.presenterScenes.join(","));
  if (args.force) scaffoldArgs.push("--force");
  run(process.execPath, scaffoldArgs, projectRoot, "scene scaffold");
  console.log(`bootstrap complete: ${projectRoot}`);
}

try {
  main();
} catch (error) {
  console.error(`bootstrap failed: ${error.message}`);
  process.exitCode = 1;
}
