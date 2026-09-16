#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function usage(exitCode = 0) {
  const out = exitCode ? console.error : console.log;
  out([
    "Usage:",
    "  node scripts/finalize-timing.mjs --project <dir> --scenes id:seconds,id:seconds",
    "",
    "Replaces provisional scene timing with measured media durations without rebuilding or overwriting scene content.",
  ].join("\n"));
  process.exit(exitCode);
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") usage(0);
    if (["--project", "--scenes"].includes(token)) {
      const value = argv[index + 1];
      if (!value) usage(1);
      if (token === "--project") args.project = value;
      else args.sceneSpec = value;
      index += 1;
      continue;
    }
    console.error(`Unknown argument: ${token}`);
    usage(1);
  }
  return args;
}

function parseScenes(value = "") {
  const durations = new Map();
  for (const entry of value.split(",").map(item => item.trim()).filter(Boolean)) {
    const split = entry.lastIndexOf(":");
    const id = entry.slice(0, split).trim();
    const duration = Number(entry.slice(split + 1));
    if (split < 1 || !/^[a-z][a-z0-9-]*$/.test(id) || !Number.isFinite(duration) || duration <= 0) {
      throw new Error(`Invalid measured scene duration: ${entry}. Use kebab-id:positive-seconds.`);
    }
    if (durations.has(id)) throw new Error(`Duplicate measured duration for ${id}.`);
    durations.set(id, duration);
  }
  if (!durations.size) throw new Error("At least one measured scene duration is required.");
  return durations;
}

function parseAttributes(tag) {
  const attributes = {};
  for (const match of tag.matchAll(/([:\w-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g)) {
    attributes[match[1]] = match[2] ?? match[3] ?? "";
  }
  return attributes;
}

function setAttribute(tag, name, value) {
  const pattern = new RegExp(`(\\s${name}\\s*=\\s*)(?:"[^"]*"|'[^']*')`);
  if (pattern.test(tag)) return tag.replace(pattern, `$1"${value}"`);
  return tag.replace(/>$/, ` ${name}="${value}">`);
}

function retimeHtml(source, oldDuration, newDuration) {
  let output = source.replace(/data-composition-duration="[^"]+"/g, `data-composition-duration="${newDuration}"`);
  output = output.replace(/data-duration="([^"]+)"/g, (attribute, value) => (
    Number.isFinite(Number(value)) && Math.abs(Number(value) - oldDuration) <= 0.001
      ? `data-duration="${newDuration}"`
      : attribute
  ));
  return output;
}

function retimeMotion(file, duration) {
  if (!fs.existsSync(file)) throw new Error(`Missing motion sidecar: ${file}`);
  const motion = JSON.parse(fs.readFileSync(file, "utf8"));
  motion.duration = duration;
  for (const assertion of motion.assertions || []) {
    if (Number.isFinite(assertion.bySec) && assertion.bySec >= duration) {
      assertion.bySec = Number(Math.max(0.05, duration * 0.5).toFixed(3));
    }
  }
  fs.writeFileSync(file, `${JSON.stringify(motion, null, 2)}\n`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.project || !args.sceneSpec) usage(1);
  const projectRoot = path.resolve(args.project);
  const indexPath = path.join(projectRoot, "index.html");
  if (!fs.existsSync(indexPath)) throw new Error(`Missing HyperFrames host: ${indexPath}`);
  const durations = parseScenes(args.sceneSpec);
  let index = fs.readFileSync(indexPath, "utf8");
  const matches = [...index.matchAll(/<div\b[^>]*\bid="scene-([a-z][a-z0-9-]*)"[^>]*>/g)];
  if (!matches.length) throw new Error("No scene mounts were found in index.html.");
  const sceneIds = matches.map(match => match[1]);
  const missing = sceneIds.filter(id => !durations.has(id));
  const unknown = [...durations.keys()].filter(id => !sceneIds.includes(id));
  if (missing.length || unknown.length) {
    throw new Error(`Measured durations must cover the existing scene set exactly. Missing: ${missing.join(", ") || "none"}; unknown: ${unknown.join(", ") || "none"}.`);
  }

  const hostMatch = index.match(/<div\b[^>]*\bid="root"[^>]*\bdata-composition-id="[^"]+"[^>]*>/);
  if (!hostMatch) throw new Error("host root was not found in index.html.");
  const hostMotionPath = path.join(projectRoot, "index.motion.json");
  if (!fs.existsSync(hostMotionPath)) throw new Error("Missing index.motion.json.");

  const hostAssertions = [];
  let cursor = 0;
  for (const match of matches) {
    const sceneId = match[1];
    const attributes = parseAttributes(match[0]);
    const oldDuration = Number(attributes["data-duration"]);
    const duration = durations.get(sceneId);
    const source = attributes["data-composition-src"];
    if (!Number.isFinite(oldDuration) || !source) throw new Error(`${sceneId}: existing mount timing or source is invalid.`);

    let updatedTag = setAttribute(match[0], "data-start", cursor);
    updatedTag = setAttribute(updatedTag, "data-duration", duration);
    index = index.replace(match[0], updatedTag);

    const framePath = path.resolve(projectRoot, source);
    if (!framePath.startsWith(`${projectRoot}${path.sep}`) || !fs.existsSync(framePath)) throw new Error(`${sceneId}: missing or unsafe frame source ${source}.`);
    let frame = fs.readFileSync(framePath, "utf8");
    const dependencies = [...frame.matchAll(/data-composition-src="(compositions\/official\/[^"]+)"/g)].map(item => item[1]);
    frame = retimeHtml(frame, oldDuration, duration);
    fs.writeFileSync(framePath, frame);
    retimeMotion(framePath.replace(/\.html$/i, ".motion.json"), duration);

    for (const dependency of dependencies) {
      const dependencyPath = path.resolve(projectRoot, dependency);
      if (!dependencyPath.startsWith(`${projectRoot}${path.sep}`) || !fs.existsSync(dependencyPath)) throw new Error(`${sceneId}: missing or unsafe official source ${dependency}.`);
      fs.writeFileSync(dependencyPath, retimeHtml(fs.readFileSync(dependencyPath, "utf8"), oldDuration, duration));
    }

    hostAssertions.push({
      kind: "appearsBy",
      selector: `#scene-${sceneId}`,
      bySec: Number((cursor + Math.min(0.5, duration * 0.5)).toFixed(3)),
    });
    cursor = Number((cursor + duration).toFixed(6));
  }

  let updatedHost = setAttribute(hostMatch[0], "data-duration", cursor);
  updatedHost = setAttribute(updatedHost, "data-vc-timing", "final");
  index = index.replace(hostMatch[0], updatedHost);
  fs.writeFileSync(indexPath, index);
  fs.writeFileSync(hostMotionPath, `${JSON.stringify({ duration: cursor, assertions: hostAssertions }, null, 2)}\n`);
  console.log(`timing finalized: ${sceneIds.length} scene(s), ${cursor}s. Authored scene content was preserved.`);
}

try {
  main();
} catch (error) {
  console.error(`timing finalization failed: ${error.message}`);
  process.exitCode = 1;
}
