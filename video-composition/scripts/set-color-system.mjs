#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const PACKAGE_ID = "video-composition";
const DEFAULT_COLOR_SYSTEM = "navy-cobalt";
const LIGHT_COLOR_SYSTEMS = new Set(["monumental-minimal", "parchment-oxblood", "porcelain-carbon"]);

function usage(exitCode = 0) {
  const out = exitCode ? console.error : console.log;
  out([
    "Usage:",
    "  node scripts/set-color-system.mjs --project <dir> --color-system <built-in-name|custom> [--color-tokens file]",
    "",
    "Updates the project-level Palette palette without rebuilding scenes or changing content/layout geometry.",
  ].join("\n"));
  process.exit(exitCode);
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

function parseArgs(argv) {
  const args = { colorSystem: DEFAULT_COLOR_SYSTEM };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") usage(0);
    if (["--project", "--color-system", "--color-tokens"].includes(token)) {
      const value = argv[index + 1];
      if (!value) usage(1);
      if (token === "--project") args.project = value;
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

function setRootColorSystem(source, name) {
  const root = /<(main|div)\b[^>]*\bid="root"[^>]*>/;
  if (!root.test(source)) return null;
  return source.replace(root, opening => {
    if (/\bdata-color-system="[^"]*"/.test(opening)) {
      return opening.replace(/\bdata-color-system="[^"]*"/, `data-color-system="${name}"`);
    }
    return opening.replace(/>$/, ` data-color-system="${name}">`);
  });
}

function setColorSystem(source, name) {
  const rooted = setRootColorSystem(source, name) ?? source;
  const scheme = LIGHT_COLOR_SYSTEMS.has(name) ? "light" : "dark";
  return rooted.replace(/scheme:\s*"(?:light|dark)"/g, `scheme: "${scheme}"`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const colorSystem = normalizeColorSystem(args.colorSystem);
  if (!args.project || !colorSystem) usage(1);
  const projectRoot = path.resolve(args.project);
  const indexPath = path.join(projectRoot, "index.html");
  if (!fs.existsSync(indexPath)) throw new Error(`Missing HyperFrames host: ${indexPath}`);

  const customPath = path.join(projectRoot, `assets/${PACKAGE_ID}/custom-color-system.css`);
  if (args.colorTokens) {
    const source = path.resolve(args.colorTokens);
    if (!fs.existsSync(source) || path.extname(source).toLowerCase() !== ".css") {
      throw new Error("--color-tokens must point to an existing CSS file.");
    }
    fs.mkdirSync(path.dirname(customPath), { recursive: true });
    fs.copyFileSync(source, customPath);
  }
  if (colorSystem === "custom" && !fs.existsSync(customPath)) {
    throw new Error("custom requires --color-tokens <css-file> on first use.");
  }

  const targets = [indexPath];
  const framesRoot = path.join(projectRoot, "compositions/frames");
  if (fs.existsSync(framesRoot)) {
    for (const name of fs.readdirSync(framesRoot).filter(name => name.endsWith(".html"))) {
      targets.push(path.join(framesRoot, name));
    }
  }
  const officialRoot = path.join(projectRoot, "compositions/official");
  if (fs.existsSync(officialRoot)) {
    for (const name of fs.readdirSync(officialRoot).filter(name => name.endsWith(".html"))) {
      targets.push(path.join(officialRoot, name));
    }
  }

  let updated = 0;
  for (const target of targets) {
    const source = fs.readFileSync(target, "utf8");
    const next = setColorSystem(source, colorSystem);
    if (next === source) continue;
    fs.writeFileSync(target, next);
    updated += 1;
  }

  const referenceRoot = path.join(projectRoot, `.style-reference/${PACKAGE_ID}`);
  fs.mkdirSync(referenceRoot, { recursive: true });
  fs.writeFileSync(path.join(referenceRoot, "COLOR-SYSTEM.json"), `${JSON.stringify({
    schemaVersion: 1,
    scope: "project",
    name: colorSystem,
    appliedTo: "all-scenes",
    tokenPrefix: "--palette-",
    source: colorSystem === "custom" ? "custom-color-system.css" : "built-in",
  }, null, 2)}\n`);
  console.log(`Palette color system set to ${colorSystem}; updated ${updated} host/frame file(s).`);
}

try {
  main();
} catch (error) {
  console.error(`Color system update failed: ${error.message}`);
  process.exitCode = 1;
}
