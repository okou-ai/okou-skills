#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const PHASES = new Set(["preflight", "static", "preview", "release"]);
const roundTime = value => Number(value.toFixed(3));

export function parseAttributes(tag) {
  const attributes = {};
  const pattern = /([:\w-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g;
  for (const match of tag.matchAll(pattern)) attributes[match[1]] = match[2] ?? match[3] ?? "";
  return attributes;
}

export function parseComposition(html) {
  const tags = [...html.matchAll(/<[^!][^>]*data-composition-id\s*=\s*(?:"[^"]+"|'[^']+')[^>]*>/g)]
    .map(match => parseAttributes(match[0]));
  const host = tags.find(attributes => !attributes["data-composition-src"]);
  const errors = [];
  if (!host) return { host: null, scenes: [], errors: ["No host composition was found in index.html."] };

  const hostStart = Number(host["data-start"] ?? 0);
  const hostDuration = Number(host["data-duration"]);
  if (!Number.isFinite(hostStart) || hostStart < 0) errors.push("Host data-start must be a finite non-negative number.");
  if (!Number.isFinite(hostDuration) || hostDuration <= 0) errors.push("Host data-duration must be a finite positive number.");
  const hostEnd = hostStart + hostDuration;

  const scenes = tags.filter(attributes => attributes["data-composition-src"]).map((attributes, index) => {
    const start = Number(attributes["data-start"]);
    const duration = Number(attributes["data-duration"]);
    const source = attributes["data-composition-src"];
    const sourceStem = path.basename(source, path.extname(source));
    const scene = {
      order: index + 1,
      domId: attributes.id || "",
      id: attributes.id || attributes["data-composition-id"] || sourceStem,
      compositionId: attributes["data-composition-id"] || "",
      source,
      sourceStem,
      start,
      duration,
      end: start + duration,
      midpoint: roundTime(start + duration / 2),
    };
    if (!Number.isFinite(start) || start < hostStart) errors.push(`${scene.id}: data-start must be finite and within the host.`);
    if (!Number.isFinite(duration) || duration <= 0) errors.push(`${scene.id}: data-duration must be a finite positive number.`);
    if (Number.isFinite(scene.end) && Number.isFinite(hostEnd) && scene.end > hostEnd + 0.001) {
      errors.push(`${scene.id}: scene end ${roundTime(scene.end)} exceeds host end ${roundTime(hostEnd)}.`);
    }
    return scene;
  });

  if (!scenes.length) errors.push("No scene with data-composition-src was found in index.html.");
  return {
    host: {
      id: host.id || host["data-composition-id"],
      compositionId: host["data-composition-id"],
      start: hostStart,
      duration: hostDuration,
      end: hostEnd,
    },
    scenes,
    errors,
  };
}

export function filterScenes(scenes, requestedIds = []) {
  if (!requestedIds.length) return { scenes, missing: [] };
  const requested = [...new Set(requestedIds)];
  const selected = [];
  const missing = [];
  for (const id of requested) {
    const match = scenes.find(scene => [scene.id, scene.compositionId, scene.source, scene.sourceStem].includes(id));
    if (!match) missing.push(id);
    else if (!selected.includes(match)) selected.push(match);
  }
  return { scenes: selected, missing };
}

export function dedupeFindings(report = {}) {
  const groups = ["lint", "runtime", "layout", "motion", "contrast"];
  const byKey = new Map();
  for (const group of groups) {
    for (const finding of report[group]?.findings || []) {
      const key = [
        finding.severity || "unknown",
        finding.code || "unknown",
        finding.message || "",
        finding.selector || "",
        finding.sourceFile || "",
      ].join("|");
      const existing = byKey.get(key);
      if (existing) {
        existing.occurrences += 1;
        if (Number.isFinite(finding.time) && !existing.times.includes(finding.time)) existing.times.push(finding.time);
        continue;
      }
      byKey.set(key, {
        group,
        severity: finding.severity || "unknown",
        code: finding.code || "unknown",
        message: finding.message || "",
        selector: finding.selector || "",
        sourceFile: finding.sourceFile || "",
        occurrences: 1,
        times: Number.isFinite(finding.time) ? [finding.time] : [],
      });
    }
  }
  return [...byKey.values()].map(finding => ({ ...finding, times: finding.times.sort((a, b) => a - b) }));
}

export function analyzeCoverage(selectedScenes, checkReport = {}) {
  const actual = checkReport.layout?.samples || [];
  const uncoveredScenes = selectedScenes
    .filter(scene => !actual.some(time => Math.abs(time - scene.midpoint) <= 0.002))
    .map(scene => scene.id);
  return {
    requestedTimes: selectedScenes.map(scene => scene.midpoint),
    sampledTimes: actual,
    uncoveredScenes,
    transitionSamplesDropped: checkReport.layout?.transitionSamplesDropped || 0,
  };
}

export function parseJsonEnvelope(output) {
  const starts = [];
  for (let index = 0; index < output.length; index += 1) if (output[index] === "{") starts.push(index);
  for (const start of starts) {
    try {
      return JSON.parse(output.slice(start).trim());
    } catch {
      // HyperFrames can write informational lines before the JSON envelope.
    }
  }
  throw new Error("HyperFrames did not return a readable JSON envelope.");
}

export function countMotionSidecars(projectRoot) {
  const found = [];
  function walk(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      if (entry.name === "node_modules" || entry.name === ".git" || entry.name === ".hyperframes") continue;
      const absolute = path.join(directory, entry.name);
      if (entry.isDirectory()) walk(absolute);
      else if (entry.isFile() && entry.name.endsWith(".motion.json")) found.push(path.relative(projectRoot, absolute));
    }
  }
  walk(projectRoot);
  return found.sort();
}

export function classifyMotion(sidecars, checkReport, phase = "preview") {
  if (phase === "static" || !checkReport) return "not-checked";
  if (sidecars.length && !checkReport.motion?.enabled) return "unverified";
  if (!checkReport.motion?.enabled) return "not-declared";
  return checkReport.motion.ok ? "verified" : "failed";
}

export function mapSnapshots(scenes, files, projectRoot) {
  const frames = files.filter(file => /frame-\d+-at-.*\.png$/i.test(file));
  return scenes.map((scene, index) => ({
    sceneId: scene.id,
    compositionId: scene.compositionId,
    source: scene.source,
    time: scene.midpoint,
    file: frames[index] ? path.relative(projectRoot, frames[index]) : null,
  }));
}

export function resolveHyperframesPackage(projectRoot) {
  const packagePath = path.join(projectRoot, "package.json");
  if (!fs.existsSync(packagePath)) return "hyperframes";
  try {
    const manifest = JSON.parse(fs.readFileSync(packagePath, "utf8"));
    const scripts = Object.values(manifest.scripts || {}).join("\n");
    const pinned = scripts.match(/\bhyperframes@([^\s"']+)/)?.[1];
    return pinned ? `hyperframes@${pinned}` : "hyperframes";
  } catch {
    return "hyperframes";
  }
}

export function buildCommand(phase, projectRoot, outputRoot, scenes, hyperframesPackage = "hyperframes") {
  const prefix = hyperframesPackage === "hyperframes" ? ["hyperframes"] : ["--yes", hyperframesPackage];
  if (phase === "preflight") return { command: "npx", args: [...prefix, "lint", projectRoot, "--json"] };
  const at = scenes.map(scene => scene.midpoint).join(",");
  if (phase === "static") {
    return {
      command: "npx",
      args: [...prefix, "snapshot", projectRoot, `--at=${at}`, "--no-end", "--describe=false", `--output=${path.join(outputRoot, "snapshots")}`],
    };
  }
  const args = [...prefix, "check", projectRoot, `--at=${at}`, "--json"];
  return { command: "npx", args };
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function readMotionSidecar(file, expectedDuration, label, errors) {
  if (!fs.existsSync(file)) {
    errors.push(`${label}: missing motion sidecar ${file}`);
    return;
  }
  try {
    const motion = JSON.parse(fs.readFileSync(file, "utf8"));
    if (!Number.isFinite(motion.duration) || Math.abs(motion.duration - expectedDuration) > 0.001) {
      errors.push(`${label}: motion duration ${motion.duration} does not match ${expectedDuration}.`);
    }
    if (!Array.isArray(motion.assertions) || !motion.assertions.length) errors.push(`${label}: motion assertions are empty.`);
  } catch (error) {
    errors.push(`${label}: unreadable motion sidecar (${error.message}).`);
  }
}

function projectTextFiles(projectRoot) {
  const files = [path.join(projectRoot, "index.html")];
  for (const relative of ["compositions", "assets/video-composition"]) {
    const start = path.join(projectRoot, relative);
    if (!fs.existsSync(start)) continue;
    const walk = directory => {
      for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
        const absolute = path.join(directory, entry.name);
        if (entry.isDirectory()) walk(absolute);
        else if (/\.(?:html|css)$/i.test(entry.name)) files.push(absolute);
      }
    };
    walk(start);
  }
  return [...new Set(files)].sort();
}

export function preflightProject(projectRoot, parsed) {
  const errors = [];
  const warnings = [];
  const domIds = parsed.scenes.map(scene => scene.domId).filter(Boolean);
  const compositionIds = parsed.scenes.map(scene => scene.compositionId).filter(Boolean);
  if (domIds.length !== parsed.scenes.length) errors.push("Every host scene mount must have a stable DOM id.");
  if (new Set(domIds).size !== domIds.length) errors.push("Host scene DOM ids must be unique.");
  if (new Set(compositionIds).size !== compositionIds.length) errors.push("Scene composition ids must be unique.");

  readMotionSidecar(path.join(projectRoot, "index.motion.json"), parsed.host.duration, "host", errors);
  for (const scene of parsed.scenes) {
    const sourcePath = path.resolve(projectRoot, scene.source);
    if (!sourcePath.startsWith(`${projectRoot}${path.sep}`) || !fs.existsSync(sourcePath)) {
      errors.push(`${scene.id}: missing or unsafe source ${scene.source}.`);
      continue;
    }
    const html = fs.readFileSync(sourcePath, "utf8");
    const idPattern = new RegExp(`data-composition-id\\s*=\\s*["']${escapeRegex(scene.compositionId)}["']`);
    const timelinePattern = new RegExp(`window\\.__timelines\\s*\\[\\s*["']${escapeRegex(scene.compositionId)}["']\\s*\\]`);
    if (!idPattern.test(html)) errors.push(`${scene.id}: source does not declare composition id ${scene.compositionId}.`);
    if (!timelinePattern.test(html)) errors.push(`${scene.id}: source does not register timeline ${scene.compositionId}.`);
    const sidecar = sourcePath.replace(/\.html$/i, ".motion.json");
    readMotionSidecar(sidecar, scene.duration, scene.id, errors);
  }

  let containsHan = false;
  let resolvedFontFiles = 0;
  let nonLatinFontDeclared = false;
  const tokenCss = fs.existsSync(path.join(projectRoot, "assets/video-composition/stage.css"))
    ? fs.readFileSync(path.join(projectRoot, "assets/video-composition/stage.css"), "utf8")
    : "";
  const allowedColors = new Set([...tokenCss.matchAll(/#[0-9a-f]{3,8}\b/gi)].map(match => match[0].toLowerCase()));
  for (const file of projectTextFiles(projectRoot)) {
    const source = fs.readFileSync(file, "utf8");
    if (/@font-face\s*\{[^}]*font-family\s*:\s*["']?(?:VcContent|[^;}]*CJK)/is.test(source)) nonLatinFontDeclared = true;
    if ([...source].some(character => {
      const point = character.codePointAt(0);
      return point >= 0x3400 && point <= 0x9fff;
    })) containsHan = true;
    for (const match of source.matchAll(/url\(\s*(["']?)([^"')]+)\1\s*\)/g)) {
      const target = match[2];
      if (!/\.(?:woff2?|ttf|otf|ttc)(?:[?#].*)?$/i.test(target) || /^(?:data:|https?:|\/\/)/i.test(target)) continue;
      const clean = target.split(/[?#]/)[0];
      const fontPath = path.resolve(path.dirname(file), clean);
      if (!fs.existsSync(fontPath)) errors.push(`${path.relative(projectRoot, file)}: missing font ${target}.`);
      else resolvedFontFiles += 1;
    }
    if (file.includes(`${path.sep}compositions${path.sep}frames${path.sep}`) && allowedColors.size) {
      const customColors = [...new Set([...source.matchAll(/#[0-9a-f]{3,8}\b/gi)].map(match => match[0].toLowerCase()))]
        .filter(color => !allowedColors.has(color));
      if (customColors.length) warnings.push(`${path.relative(projectRoot, file)} uses non-token colors: ${customColors.join(", ")}.`);
    }
  }
  if (containsHan && (!nonLatinFontDeclared || !resolvedFontFiles)) errors.push("CJK content is present but no explicit local CJK content font is resolved; stage a licensed font with --content-font.");
  return { ok: errors.length === 0, errors, warnings };
}

export function sourceFingerprint(projectRoot) {
  const hash = crypto.createHash("sha256");
  const files = [path.join(projectRoot, "index.motion.json"), ...projectTextFiles(projectRoot)]
    .filter(file => fs.existsSync(file))
    .sort();
  for (const file of files) {
    hash.update(path.relative(projectRoot, file));
    hash.update(fs.readFileSync(file));
  }
  for (const relative of ["assets/video-composition/fonts"]) {
    const directory = path.join(projectRoot, relative);
    if (!fs.existsSync(directory)) continue;
    for (const entry of fs.readdirSync(directory, { withFileTypes: true }).filter(entry => entry.isFile()).sort((a, b) => a.name.localeCompare(b.name))) {
      const file = path.join(directory, entry.name);
      const stat = fs.statSync(file);
      hash.update(`${path.relative(projectRoot, file)}:${stat.size}:${stat.mtimeMs}`);
    }
  }
  return hash.digest("hex");
}

function hashFiles(projectRoot, files) {
  const hash = crypto.createHash("sha256");
  for (const file of [...new Set(files)].filter(file => fs.existsSync(file)).sort()) {
    hash.update(path.relative(projectRoot, file));
    hash.update(fs.readFileSync(file));
  }
  return hash.digest("hex");
}

function sceneDependencyFiles(projectRoot, scene) {
  const sourcePath = path.resolve(projectRoot, scene.source);
  const files = [sourcePath, sourcePath.replace(/\.html$/i, ".motion.json")];
  if (!fs.existsSync(sourcePath)) return files;
  const html = fs.readFileSync(sourcePath, "utf8");
  for (const match of html.matchAll(/data-composition-src\s*=\s*["']([^"']+)["']/g)) {
    const dependency = path.resolve(projectRoot, match[1]);
    if (dependency.startsWith(`${projectRoot}${path.sep}`)) files.push(dependency, dependency.replace(/\.html$/i, ".motion.json"));
  }
  return files;
}

export function fingerprintState(projectRoot, parsed) {
  const shared = [path.join(projectRoot, "index.html"), path.join(projectRoot, "index.motion.json")];
  for (const relative of ["assets/video-composition", "assets/runtime/gsap.min.js"]) {
    const start = path.join(projectRoot, relative);
    if (!fs.existsSync(start)) continue;
    if (fs.statSync(start).isFile()) shared.push(start);
    else {
      const walk = directory => {
        for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
          const absolute = path.join(directory, entry.name);
          if (entry.isDirectory()) walk(absolute);
          else shared.push(absolute);
        }
      };
      walk(start);
    }
  }
  return {
    shared: hashFiles(projectRoot, shared),
    scenes: Object.fromEntries(parsed.scenes.map(scene => [scene.id, hashFiles(projectRoot, sceneDependencyFiles(projectRoot, scene))])),
  };
}

function loadPreviewReport(projectRoot) {
  const file = path.join(projectRoot, ".hyperframes/review-project/preview/report.json");
  if (!fs.existsSync(file)) return null;
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return null;
  }
}

export function incrementalPreviewSelection(projectRoot, parsed) {
  const previous = loadPreviewReport(projectRoot);
  const current = fingerprintState(projectRoot, parsed);
  const allSceneIds = parsed.scenes.map(scene => scene.id);
  const priorCoverage = previous?.qaCoverage?.sceneIds || previous?.composition?.selectedScenes?.map(scene => scene.id) || [];
  if (!previous?.ok || previous.fingerprintState?.shared !== current.shared || !allSceneIds.every(id => priorCoverage.includes(id))) {
    return { scenes: parsed.scenes, previous: null, state: current, mode: "full" };
  }
  const changedIds = allSceneIds.filter(id => previous.fingerprintState?.scenes?.[id] !== current.scenes[id]);
  if (!changedIds.length) return { scenes: [], previous, state: current, mode: "reuse" };
  if (changedIds.length === allSceneIds.length) return { scenes: parsed.scenes, previous: null, state: current, mode: "full" };
  return { scenes: parsed.scenes.filter(scene => changedIds.includes(scene.id)), previous, state: current, mode: "incremental" };
}

function reusablePreview(projectRoot, fingerprint, parsed) {
  const report = loadPreviewReport(projectRoot);
  if (!report?.ok || report.sourceFingerprint !== fingerprint) return null;
  const covered = report.qaCoverage?.sceneIds || report.composition?.selectedScenes?.map(scene => scene.id) || [];
  if (!parsed.scenes.every(scene => covered.includes(scene.id))) return null;
  return report;
}

function collectFiles(directory) {
  if (!fs.existsSync(directory)) return [];
  const files = [];
  function walk(current) {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const absolute = path.join(current, entry.name);
      if (entry.isDirectory()) walk(absolute);
      else files.push(absolute);
    }
  }
  walk(directory);
  return files.sort();
}

function shellDisplay(command) {
  return [command.command, ...command.args.map(value => /\s/.test(value) ? JSON.stringify(value) : value)].join(" ");
}

function usage(exitCode = 0) {
  const out = exitCode ? console.error : console.log;
  out([
    "Usage:",
    "  node review-project.mjs --project <dir> --phase <preflight|static|preview|release> [--scenes id,id] [--output <dir>] [--dry-run]",
    "",
    "Runs a deterministic preflight, then derives scene midpoints and orchestrates at most one HyperFrames snapshot or check.",
    "It never edits composition sources and never renders video.",
  ].join("\n"));
  process.exit(exitCode);
}

function parseArgs(argv) {
  const args = { sceneIds: [], dryRun: false };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") usage(0);
    if (token === "--dry-run") {
      args.dryRun = true;
      continue;
    }
    if (token === "--project" || token === "--phase" || token === "--scenes" || token === "--output") {
      const value = argv[index + 1];
      if (!value) usage(1);
      if (token === "--project") args.project = value;
      if (token === "--phase") args.phase = value;
      if (token === "--output") args.output = value;
      if (token === "--scenes") args.sceneIds = value.split(",").map(item => item.trim()).filter(Boolean);
      index += 1;
      continue;
    }
    console.error(`Unknown argument: ${token}`);
    usage(1);
  }
  return args;
}

function buildSummary(report) {
  const lines = [
    `# Video composition ${report.phase} review`,
    "",
    `- Status: **${report.dryRun ? "DRY RUN" : report.ok ? "PASS" : "FAIL"}**`,
    `- Project: \`${report.project}\``,
    `- Host: \`${report.composition.host.compositionId}\` (${report.composition.host.duration}s)`,
    `- Scenes: ${report.composition.selectedScenes.length}/${report.composition.allScenes.length}`,
    `- Sample times: ${report.coverage.requestedTimes.join(", ")}`,
    `- Command: \`${report.command.display}\``,
    `- Preflight: ${report.preflight.ok ? "PASS" : "FAIL"} (${report.preflight.warnings.length} warning(s))`,
  ];
  if (report.incremental?.mode === "incremental") lines.push(`- QA scope: automatic incremental check for ${report.incremental.changedSceneIds.join(", ")}.`);
  if (report.reusedPreview) lines.push("- QA: reused unchanged successful Preview coverage.");
  if (report.dryRun) lines.push("- Execution: dry run; HyperFrames was not started.");
  if (report.command.exitCode !== null) lines.push(`- Command exit: ${report.command.exitCode}`);
  if (report.coverage.uncoveredScenes.length) lines.push(`- Uncovered scenes: ${report.coverage.uncoveredScenes.join(", ")}`);
  if (report.coverage.transitionSamplesDropped) lines.push(`- Dropped transition samples: ${report.coverage.transitionSamplesDropped}`);
  lines.push(`- Motion: ${report.motion.status} (${report.motion.sidecars.length} sidecar file(s))`);
  if (report.snapshots.length) lines.push(`- Snapshot files: ${report.snapshots.length}`);
  if (report.findings.length) {
    lines.push("", "## Deduplicated findings", "");
    for (const finding of report.findings) {
      const location = finding.sourceFile ? ` in ${finding.sourceFile}` : "";
      const repeated = finding.occurrences > 1 ? ` ×${finding.occurrences}` : "";
      lines.push(`- [${finding.severity}] ${finding.code}${repeated}${location}: ${finding.message}`);
    }
  }
  if (report.preflight.warnings.length) {
    lines.push("", "## Preflight warnings", "", ...report.preflight.warnings.map(warning => `- ${warning}`));
  }
  if (report.errors.length) {
    lines.push("", "## Errors", "", ...report.errors.map(error => `- ${error}`));
  }
  lines.push("");
  return lines.join("\n");
}

export function createBaseReport({ phase, projectRoot, parsed, selectedScenes, command, dryRun, motionSidecars, preflight, fingerprint, state, incrementalMode }) {
  return {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    phase,
    project: projectRoot,
    dryRun,
    ok: true,
    sourceFingerprint: fingerprint,
    fingerprintState: state,
    reusedPreview: false,
    incremental: {
      mode: incrementalMode,
      changedSceneIds: incrementalMode === "incremental" ? selectedScenes.map(scene => scene.id) : [],
    },
    preflight,
    composition: {
      host: parsed.host,
      allScenes: parsed.scenes,
      selectedScenes,
    },
    command: {
      display: shellDisplay(command),
      exitCode: null,
    },
    coverage: {
      requestedTimes: selectedScenes.map(scene => scene.midpoint),
      sampledTimes: [],
      uncoveredScenes: [],
      transitionSamplesDropped: 0,
    },
    qaCoverage: {
      sceneIds: [],
    },
    motion: {
      status: dryRun ? "not-checked" : phase === "static" ? "not-checked" : motionSidecars.length ? "unverified" : "not-declared",
      sidecars: motionSidecars,
    },
    snapshots: [],
    snapshotMap: [],
    findings: [],
    errors: [],
    hyperframes: null,
  };
}

export function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  if (!args.project || !PHASES.has(args.phase)) usage(1);
  const projectRoot = path.resolve(args.project);
  const indexPath = path.join(projectRoot, "index.html");
  if (!fs.existsSync(indexPath)) throw new Error(`Missing HyperFrames host: ${indexPath}`);

  const parsed = parseComposition(fs.readFileSync(indexPath, "utf8"));
  if (parsed.errors.length) throw new Error(parsed.errors.join("\n"));
  let filtered = filterScenes(parsed.scenes, args.sceneIds);
  if (filtered.missing.length) throw new Error(`Unknown scene id(s): ${filtered.missing.join(", ")}`);
  if (!filtered.scenes.length) throw new Error("No scenes were selected.");

  let incremental = { scenes: filtered.scenes, previous: null, state: fingerprintState(projectRoot, parsed), mode: "explicit" };
  if (args.phase === "preview" && !args.sceneIds.length) {
    incremental = incrementalPreviewSelection(projectRoot, parsed);
    filtered = { scenes: incremental.scenes.length ? incremental.scenes : parsed.scenes, missing: [] };
  }

  const outputRoot = path.resolve(args.output || path.join(projectRoot, ".hyperframes", "review-project", args.phase));
  const hyperframesPackage = resolveHyperframesPackage(projectRoot);
  const command = buildCommand(args.phase, projectRoot, outputRoot, filtered.scenes, hyperframesPackage);
  const motionSidecars = countMotionSidecars(projectRoot);
  const preflight = preflightProject(projectRoot, parsed);
  const fingerprint = sourceFingerprint(projectRoot);
  const report = createBaseReport({
    phase: args.phase,
    projectRoot,
    parsed,
    selectedScenes: filtered.scenes,
    command,
    dryRun: args.dryRun,
    motionSidecars,
    preflight,
    fingerprint,
    state: incremental.state,
    incrementalMode: incremental.mode,
  });
  report.errors.push(...preflight.errors);

  fs.mkdirSync(outputRoot, { recursive: true });
  if (!args.dryRun && preflight.ok && args.phase === "release" && !args.sceneIds.length) {
    const cached = reusablePreview(projectRoot, fingerprint, parsed);
    if (cached) {
      report.reusedPreview = true;
      report.command.display = "reuse unchanged successful Preview coverage";
      report.command.exitCode = 0;
      report.coverage = cached.coverage;
      report.motion = cached.motion;
      report.findings = cached.findings;
      report.hyperframes = cached.hyperframes;
      report.qaCoverage = cached.qaCoverage || { sceneIds: parsed.scenes.map(scene => scene.id) };
    }
  }
  if (!args.dryRun && preflight.ok && args.phase === "preview" && incremental.mode === "reuse") {
    report.reusedPreview = true;
    report.command.display = "reuse unchanged successful Preview coverage";
    report.command.exitCode = 0;
    report.coverage = incremental.previous.coverage;
    report.motion = incremental.previous.motion;
    report.findings = incremental.previous.findings;
    report.hyperframes = incremental.previous.hyperframes;
    report.qaCoverage = incremental.previous.qaCoverage || { sceneIds: parsed.scenes.map(scene => scene.id) };
  }
  if (!args.dryRun && preflight.ok && args.phase === "preflight") {
    const execution = spawnSync(command.command, command.args, {
      cwd: projectRoot,
      encoding: "utf8",
      maxBuffer: 64 * 1024 * 1024,
    });
    report.command.exitCode = execution.status ?? 1;
    if (execution.error) report.errors.push(execution.error.message);
    try {
      report.hyperframes = parseJsonEnvelope(execution.stdout || "");
      report.findings = dedupeFindings({ lint: { findings: report.hyperframes.findings || [] } });
      if (report.command.exitCode !== 0 || !report.hyperframes.ok) report.errors.push("HyperFrames lint reported a failure.");
    } catch (error) {
      report.errors.push(error.message);
      const diagnostic = (execution.stderr || execution.stdout || "").trim();
      if (diagnostic) report.errors.push(diagnostic);
    }
  }
  if (!args.dryRun && preflight.ok && args.phase !== "preflight" && !report.reusedPreview) {
    const execution = spawnSync(command.command, command.args, {
      cwd: projectRoot,
      encoding: "utf8",
      maxBuffer: 64 * 1024 * 1024,
    });
    report.command.exitCode = execution.status ?? 1;
    if (execution.error) report.errors.push(execution.error.message);

    if (args.phase === "static") {
      const snapshotFiles = collectFiles(path.join(outputRoot, "snapshots"));
      report.snapshots = snapshotFiles.map(file => path.relative(projectRoot, file));
      report.snapshotMap = mapSnapshots(filtered.scenes, snapshotFiles, projectRoot);
      if (report.command.exitCode !== 0) report.errors.push((execution.stderr || execution.stdout || "HyperFrames snapshot failed.").trim());
    } else {
      try {
        report.hyperframes = parseJsonEnvelope(execution.stdout || "");
        report.coverage = analyzeCoverage(filtered.scenes, report.hyperframes);
        report.findings = dedupeFindings(report.hyperframes);
        report.motion.status = classifyMotion(motionSidecars, report.hyperframes, args.phase);
        if (report.motion.status === "unverified") {
          report.errors.push("Motion sidecars exist, but HyperFrames motion verification was disabled.");
        }
        if (report.coverage.uncoveredScenes.length) report.errors.push(`HyperFrames did not sample: ${report.coverage.uncoveredScenes.join(", ")}`);
        if (report.command.exitCode !== 0 || !report.hyperframes.ok) report.errors.push("HyperFrames check reported a failure.");
        if (!report.errors.length && args.phase === "preview") {
          report.qaCoverage.sceneIds = args.sceneIds.length
            ? filtered.scenes.map(scene => scene.id)
            : parsed.scenes.map(scene => scene.id);
        }
      } catch (error) {
        report.errors.push(error.message);
        const diagnostic = (execution.stderr || execution.stdout || "").trim();
        if (diagnostic) report.errors.push(diagnostic);
      }
    }
  }

  report.ok = report.errors.length === 0;
  fs.writeFileSync(path.join(outputRoot, "report.json"), JSON.stringify(report, null, 2) + "\n");
  fs.writeFileSync(path.join(outputRoot, "summary.md"), buildSummary(report) + "\n");
  console.log(buildSummary(report));
  if (!report.ok) process.exitCode = 1;
  return report;
}

const invokedPath = process.argv[1] ? pathToFileURL(path.resolve(process.argv[1])).href : "";
if (import.meta.url === invokedPath) {
  try {
    main();
  } catch (error) {
    console.error(`review failed: ${error.message}`);
    process.exitCode = 1;
  }
}
