#!/usr/bin/env node
import fs from "node:fs";
import crypto from "node:crypto";
import path from "node:path";

function usage(exitCode = 0) {
  const out = exitCode ? console.error : console.log;
  out([
    "Usage:",
    "  node scripts/scaffold-scenes.mjs --project <dir> --host-id <id> --presenter <off|on> --scenes id:<seconds|auto>,id:<seconds|auto> [--layout-map id=family/layout,id=family/layout] [--color-system <built-in-name|custom>] [--presenter-scenes id,id] [--language tag] [--force]",
    "",
    "Creates the mechanical multi-scene contract from selected executable starters. Use auto to author scenes concurrently with media generation; finalize exact timing later without rebuilding content.",
    "It never chooses layouts or writes content.",
  ].join("\n"));
  process.exit(exitCode);
}

function parseArgs(argv) {
  const args = { hostId: "navy-cobalt", language: "en", colorSystem: "navy-cobalt", presenterScenes: [], force: false };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") usage(0);
    if (token === "--force") {
      args.force = true;
      continue;
    }
    if (["--project", "--host-id", "--presenter", "--scenes", "--layout-map", "--presenter-scenes", "--language", "--color-system"].includes(token)) {
      const value = argv[index + 1];
      if (!value) usage(1);
      if (token === "--project") args.project = value;
      if (token === "--host-id") args.hostId = value;
      if (token === "--presenter") args.presenterMode = value;
      if (token === "--scenes") args.sceneSpec = value;
      if (token === "--layout-map") args.layoutSpec = value;
      if (token === "--presenter-scenes") args.presenterScenes = value.split(",").map(item => item.trim()).filter(Boolean);
      if (token === "--language") args.language = value;
      if (token === "--color-system") args.colorSystem = value;
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

function validId(value) {
  return /^[a-z][a-z0-9-]*$/.test(value);
}

function parseScenes(value = "") {
  return value.split(",").filter(Boolean).map(entry => {
    const split = entry.lastIndexOf(":");
    const id = entry.slice(0, split).trim();
    const durationToken = entry.slice(split + 1).trim();
    const provisional = durationToken === "auto";
    const duration = provisional ? 6 : Number(durationToken);
    if (split < 1 || !validId(id) || !Number.isFinite(duration) || duration <= 0) {
      throw new Error(`Invalid scene specification: ${entry}. Use kebab-id:positive-seconds or kebab-id:auto.`);
    }
    return { id, duration, provisional };
  });
}

function parseLayoutMap(value = "") {
  const map = new Map();
  for (const entry of value.split(",").map(item => item.trim()).filter(Boolean)) {
    const split = entry.indexOf("=");
    const sceneId = entry.slice(0, split).trim();
    const layoutId = entry.slice(split + 1).trim();
    if (split < 1 || !validId(sceneId) || !/^[a-z]+\/[a-z0-9-]+$/.test(layoutId)) {
      throw new Error(`Invalid layout mapping: ${entry}. Use scene-id=family/layout-id.`);
    }
    if (map.has(sceneId)) throw new Error(`Duplicate layout mapping for ${sceneId}.`);
    map.set(sceneId, layoutId);
  }
  return map;
}

function htmlEscape(value) {
  return value.replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function adaptStarter(source, sourceId, compositionId, sceneId, duration, language, colorSystem, presenter) {
  let adapted = source
    .replaceAll(sourceId, compositionId)
    .replace(/<html lang="[^"]+"/, `<html lang="${htmlEscape(language)}"`)
    .replace(/data-composition-duration="[^"]+"/g, `data-composition-duration="${duration}"`)
    .replace(/data-duration="[^"]+"/g, `data-duration="${duration}"`)
    .replace(/data-color-system="[^"]+"/g, `data-color-system="${colorSystem}"`)
    .replace(/id="vc-layout-stage"/, 'id="root"')
    .replace(/(<main id="root"[^>]*data-presenter=")(?:off|on)(")/, `$1${presenter ? "on" : "off"}$2`)
    .replace(/<main\s+class="vc-frame/, `<main id="scene-${sceneId}-stage" class="vc-frame`);
  if (!presenter) adapted = adapted.replace(/\s*<!-- PRESENTER_SLOT_BEGIN -->[\s\S]*?<!-- PRESENTER_SLOT_END -->/, "");
  return adapted;
}

function adaptMotion(source, duration) {
  const motion = JSON.parse(source);
  motion.duration = duration;
  for (const assertion of motion.assertions || []) {
    if (Number.isFinite(assertion.bySec) && assertion.bySec >= duration) {
      assertion.bySec = Number(Math.max(0.05, duration * 0.5).toFixed(3));
    }
  }
  return `${JSON.stringify(motion, null, 2)}\n`;
}

function parseVariableValues(html) {
  const raw = html.match(/data-variable-values='([^']*)'/)?.[1];
  return raw ? JSON.parse(raw.replaceAll("&quot;", '"').replaceAll("&#39;", "'").replaceAll("&amp;", "&")) : {};
}

function bakeVariableDefaults(source, values, sceneId) {
  const match = source.match(/data-composition-variables='([\s\S]*?)'/);
  if (!match) return source;
  const variables = JSON.parse(match[1]);
  for (const variable of variables) {
    if (Object.prototype.hasOwnProperty.call(values, variable.id)) variable.default = values[variable.id];
  }
  const encoded = JSON.stringify(variables).replaceAll("&", "&amp;").replaceAll("'", "&#39;");
  const baked = source.replace(match[0], `data-composition-variables='${encoded}'`);
  const htmlOpeningTag = /<html(?:[^<>"']|"[^"]*"|'[^']*')*>/;
  return baked.replace(htmlOpeningTag, opening => [
    `<!-- CONTENT_SLOT_BEGIN (${sceneId}): edit only default values in data-composition-variables. -->`,
    opening,
    "<!-- CONTENT_SLOT_END -->",
  ].join("\n"));
}

function markBlockContent(source, sceneId) {
  if (!source.includes("<body") || !source.includes("</body>")) return source;
  return source
    .replace(/(<body[^>]*>)/, `$1\n<!-- CONTENT_SLOT_BEGIN (${sceneId}): edit visible literals or data only; preserve official structure. -->`)
    .replace("</body>", "<!-- CONTENT_SLOT_END -->\n</body>");
}

function applyStageContrast(source, colorSystem) {
  const contrastStyle = `    <style data-vc-contrast>
      :root, body, [data-composition-id] {
        --bg: var(--palette-field) !important;
        --fg: var(--palette-ink) !important;
        --surface: var(--palette-surface) !important;
        --border: var(--palette-line) !important;
        --muted: var(--palette-muted) !important;
        --brand: var(--palette-accent) !important;
        --accent: var(--palette-accent) !important;
        --accent-2: var(--palette-signal) !important;
        --mk-ink: var(--palette-ink) !important;
        --mk-ink-dim: var(--palette-muted) !important;
        --mk-ink-dark: var(--palette-ink) !important;
        --mk-ink-dim-dark: var(--palette-muted) !important;
        --mk-accent: var(--palette-accent) !important;
        --mk-accent-dark: var(--palette-line) !important;
      }
    </style>`;
  const scheme = colorSystem === "monumental-minimal" ? "light" : "dark";
  return source
    .replace(/<script src="https?:\/\/[^\"]*gsap[^\"]*"><\/script>/, '<script src="assets/runtime/gsap.min.js"></script>')
    .replace(/scheme:\s*"(?:light|dark)"/, `scheme: "${scheme}"`)
    .replace("</head>", `${contrastStyle}\n  </head>`);
}

function synchronizeFullWindowDurations(source, duration) {
  const declared = Number(
    source.match(/data-composition-duration="([^"]+)"/)?.[1]
      ?? source.match(/data-composition-id="[^"]+"[^>]*data-duration="([^"]+)"/)?.[1],
  );
  let synchronized = source.replace(/data-composition-duration="[^"]+"/g, `data-composition-duration="${duration}"`);
  if (!Number.isFinite(declared)) return synchronized;
  return synchronized.replace(/data-duration="([^"]+)"/g, (attribute, value) => (
    Number(value) === declared ? `data-duration="${duration}"` : attribute
  ));
}

function normalizeOfficialEnvelope(source, duration) {
  let normalized = source.replace(/data-composition-duration="[^"]+"/g, `data-composition-duration="${duration}"`);
  normalized = normalized.replace(/(<[^>]+data-composition-id="[^"]+"[^>]*data-duration=")[^"]+("[^>]*>)/, (match, before, after) => {
    let root = `${before}${duration}${after}`;
    if (!/data-width="/.test(root)) root = root.replace(/>$/, ' data-width="1920">');
    if (!/data-height="/.test(root)) root = root.replace(/>$/, ' data-height="1080">');
    return root;
  });
  return normalized;
}

function extractFusedContent(source) {
  const template = source.match(/<body[^>]*>[\s\S]*?<template[^>]*>([\s\S]*?)<\/template>/)?.[1]?.trim();
  if (template) {
    const root = template.match(/^<[^>]+id="root"[^>]*>([\s\S]*)<\/[^>]+>\s*$/);
    if (!root) throw new Error("Official component template has no #root envelope.");
    return root[1];
  }
  const body = source.match(/<body[^>]*>([\s\S]*?)<\/body>/)?.[1] || "";
  const root = body.match(/<[^>]+id="root"[^>]*>([\s\S]*?)<\/div>\s*(?:<script|$)/);
  if (!root) throw new Error("Merged official adapter has no #root envelope.");
  const styles = [...source.matchAll(/<style[^>]*>[\s\S]*?<\/style>/g)].map(match => match[0]);
  const scripts = [...source.matchAll(/<script(?![^>]*\bsrc=)[^>]*>[\s\S]*?<\/script>/g)].map(match => match[0]);
  return [...styles, root[1], ...scripts].join("\n");
}

function retokenStageSource(source) {
  return source
    .replace(/html\s*,\s*body\s*\{[^}]*\}/g, "")
    .replaceAll("#f8fafc", "var(--palette-contrast-field)")
    .replaceAll("#0b0c0e", "var(--palette-field)")
    .replaceAll("#71f5a7", "var(--palette-accent)")
    .replaceAll("#61a8ff", "var(--palette-accent)")
    .replaceAll("#c5a3ff", "var(--palette-signal)")
    .replace(/#fff(?![0-9a-f])/gi, "var(--palette-contrast-field)");
}

function fuseOfficialComponent(html, source, officialId, compositionId, values, duration, sceneId) {
  const synchronizedSource = synchronizeFullWindowDurations(source, duration);
  const baked = bakeVariableDefaults(synchronizedSource, values, sceneId).replaceAll(officialId, compositionId);
  const variableAttribute = baked.match(/data-composition-variables='[\s\S]*?'/)?.[0];
  if (!variableAttribute) throw new Error(`${sceneId}: official component has no variable contract.`);
  let extracted;
  try {
    extracted = extractFusedContent(baked);
  } catch (error) {
    throw new Error(`${sceneId}: ${error.message}`);
  }
  let content = retokenStageSource(extracted)
    .replace(/<script src="https?:\/\/[^\"]*gsap[^\"]*"><\/script>/g, "")
    .replaceAll("#root", "#vc-official-mount")
    .replaceAll('getElementById("root")', 'getElementById("vc-official-mount")')
    .replaceAll("getElementById('root')", "getElementById('vc-official-mount')");
  const mount = html.match(/<div[\s\S]*?id="vc-official-mount"[\s\S]*?>\s*<\/div>/)?.[0];
  if (!mount) throw new Error(`${sceneId}: component starter has no empty official mount.`);
  const opening = mount.match(/^([\s\S]*?>)\s*<\/div>$/)?.[1]
    .replace(/\s+data-composition-id="[^"]+"/, "")
    .replace(/\s+data-composition-src="[^"]+"/, "")
    .replace(/\s+data-variable-values='[^']*'/, "")
    .replace(/\s+data-start="[^"]+"/, "")
    .replace(/\s+data-track-index="[^"]+"/, "");
  if (!opening) throw new Error(`${sceneId}: component mount cannot be normalized.`);
  content = `${opening}\n${content}\n      </div>`;
  let fused = html
    .replace(mount, content)
    .replace("CONTENT_SLOT_BEGIN", "AUTHORITY_BEHAVIOR_BEGIN")
    .replace("CONTENT_SLOT_END", "AUTHORITY_BEHAVIOR_END")
    .replace(/<html((?:[^<>"']|"[^"]*"|'[^']*')*)>/, (_, attributes) => [
      `<!-- CONTENT_SLOT_BEGIN (${sceneId}): edit only default values in data-composition-variables. -->`,
      `<html${attributes} data-composition-duration="${duration}" ${variableAttribute}>`,
      "<!-- CONTENT_SLOT_END -->",
    ].join("\n"));
  fused = fused.replace(
    `window.__timelines["${compositionId}"] = gsap.timeline({ paused: true });`,
    `window.__timelines["${compositionId}"] = window.__timelines["${compositionId}"] || gsap.timeline({ paused: true });`,
  );
  return fused;
}

function applyPresenterGeometry(html, presenter) {
  if (!presenter) return html;
  const side = html.match(/<main id="root"[^>]*data-presenter-side="(left|right)"/)?.[1] || "right";
  const geometry = side === "left"
    ? "left:auto;right:0;width:1340px"
    : "left:0;right:auto;width:1340px";
  return html.replace('id="vc-official-mount"', `id="vc-official-mount" style="${geometry}"`);
}

function isBlankScaffold(html, projectRoot) {
  const receiptPath = path.join(projectRoot, ".hyperframes/video-composition/bootstrap.json");
  if (fs.existsSync(receiptPath)) {
    const receipt = JSON.parse(fs.readFileSync(receiptPath, "utf8"));
    return receipt.blankIndexSha256 === crypto.createHash("sha256").update(html).digest("hex");
  }
  return !/data-composition-src\s*=/.test(html) && /Add your clips here\. Example:/.test(html);
}

function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  args.colorSystem = normalizeColorSystem(args.colorSystem);
  if (!args.project || !args.sceneSpec || !["off", "on"].includes(args.presenterMode) || !validId(args.hostId)) usage(1);
  if (!args.colorSystem) throw new Error("Unknown --color-system. Use a built-in name from the Gallery or custom.");
  const scenes = parseScenes(args.sceneSpec);
  const provisionalTiming = scenes.some(scene => scene.provisional);
  const layoutMap = parseLayoutMap(args.layoutSpec);
  if (!scenes.length) throw new Error("At least one scene is required.");
  if (new Set(scenes.map(scene => scene.id)).size !== scenes.length) throw new Error("Scene ids must be unique.");
  const unknownPresenterScenes = args.presenterScenes.filter(id => !scenes.some(scene => scene.id === id));
  if (unknownPresenterScenes.length) throw new Error(`Unknown presenter scene id(s): ${unknownPresenterScenes.join(", ")}`);
  if (args.presenterMode === "off" && args.presenterScenes.length) throw new Error("Presenter scenes require --presenter on.");
  const unknownLayoutScenes = [...layoutMap.keys()].filter(id => !scenes.some(scene => scene.id === id));
  if (unknownLayoutScenes.length) throw new Error(`Unknown layout-map scene id(s): ${unknownLayoutScenes.join(", ")}`);
  if (layoutMap.size && scenes.some(scene => !layoutMap.has(scene.id))) throw new Error("--layout-map must provide one selected layout for every scene.");

  const projectRoot = path.resolve(args.project);
  const indexPath = path.join(projectRoot, "index.html");
  if (!fs.existsSync(path.join(projectRoot, "hyperframes.json")) || !fs.existsSync(indexPath)) {
    throw new Error("The destination must be an initialized HyperFrames project.");
  }
  const existingIndex = fs.readFileSync(indexPath, "utf8");
  if (!args.force && !isBlankScaffold(existingIndex, projectRoot)) {
    throw new Error("index.html is not the untouched blank HyperFrames scaffold; use --force only when replacement is intentional.");
  }

  const starterRoot = path.join(projectRoot, "compositions");
  const readStarter = name => {
    const starterPath = path.join(starterRoot, name);
    if (!fs.existsSync(starterPath)) {
      throw new Error(`Missing staged starter: ${path.relative(projectRoot, starterPath)}. Run the authoring-kit staging command first.`);
    }
    return fs.readFileSync(starterPath, "utf8");
  };
  const plainStarter = readStarter("vc-scene.html");
  const plainMotion = readStarter("vc-scene.motion.json");
  const needsPresenterStarter = args.presenterMode === "on" && args.presenterScenes.length > 0;
  const presenterStarter = needsPresenterStarter ? readStarter("vc-presenter-scene.html") : null;
  const presenterMotion = needsPresenterStarter ? readStarter("vc-presenter-scene.motion.json") : null;
  const targets = [indexPath, path.join(projectRoot, "index.motion.json")];
  for (const scene of scenes) {
    targets.push(path.join(projectRoot, "compositions/frames", `${scene.id}.html`));
    targets.push(path.join(projectRoot, "compositions/frames", `${scene.id}.motion.json`));
  }
  const conflicts = targets.filter(target => target !== indexPath && fs.existsSync(target));
  if (conflicts.length && !args.force) throw new Error(`Refusing to overwrite existing scaffold file(s): ${conflicts.map(file => path.relative(projectRoot, file)).join(", ")}`);

  const mounts = [];
  const rootAssertions = [];
  const presenterOmissions = [];
  let cursor = 0;
  for (const scene of scenes) {
    const compositionId = `${args.hostId}-${scene.id}`;
    let presenter = args.presenterMode === "on" && args.presenterScenes.includes(scene.id);
    const layoutId = layoutMap.get(scene.id);
    const layoutStem = layoutId ? layoutId.replace("/", "--") : null;
    const layoutRoot = path.join(projectRoot, ".style-reference/video-composition/layouts/source");
    const selectedStarter = layoutId ? fs.readFileSync(path.join(layoutRoot, `${layoutStem}.html`), "utf8") : presenter ? presenterStarter : plainStarter;
    const selectedMotion = layoutId ? fs.readFileSync(path.join(layoutRoot, `${layoutStem}.motion.json`), "utf8") : presenter ? presenterMotion : plainMotion;
    const sourceId = layoutId
      ? selectedStarter.match(/data-composition-id="([^"]+)"/)?.[1]
      : presenter ? "vc-presenter-scene" : "vc-scene";
    if (!sourceId) throw new Error(`${scene.id}: selected starter has no composition id.`);
    const registryCode = selectedStarter.match(/data-registry-code="([CBM])"/)?.[1];
    if (presenter && registryCode === "B") {
      presenter = false;
      presenterOmissions.push(`${scene.id} (full-canvas block)`);
    }
    let html = adaptStarter(selectedStarter, sourceId, compositionId, scene.id, scene.duration, args.language, args.colorSystem, presenter);
    if (layoutId && registryCode) {
      const sourceMatch = html.match(/data-vc-content-slot="official"[\s\S]*?data-composition-id="([^"]+)"[\s\S]*?data-composition-src="([^"]+)"/);
      if (!sourceMatch) throw new Error(`${scene.id}: executable starter has no official mount contract.`);
      const [, officialId, officialSource] = sourceMatch;
      const sourcePath = path.join(projectRoot, officialSource);
      if (!fs.existsSync(sourcePath)) throw new Error(`${scene.id}: installed official source is missing: ${officialSource}`);
      const isolatedId = `${compositionId}-official`;
      const isolatedRelative = `compositions/official/${scene.id}-${path.basename(officialSource)}`;
      const isolatedPath = path.join(projectRoot, isolatedRelative);
      const values = parseVariableValues(html);
      if (registryCode === "B") {
        fs.mkdirSync(path.dirname(isolatedPath), { recursive: true });
        let isolatedSource = synchronizeFullWindowDurations(fs.readFileSync(sourcePath, "utf8"), scene.duration).replaceAll(officialId, isolatedId);
        isolatedSource = normalizeOfficialEnvelope(applyStageContrast(markBlockContent(isolatedSource, scene.id), args.colorSystem), scene.duration);
        fs.writeFileSync(isolatedPath, isolatedSource);
        const originalMount = html.match(/<div[\s\S]*?<\/div>/)?.[0] || "";
        html = html
          .replace(/<!-- CONTENT_SLOT_BEGIN:[\s\S]*?<!-- CONTENT_SLOT_END -->/, `<!-- AUTHORITY_OFFICIAL_SOURCE: edit the protected content slot in ${isolatedRelative}. -->\n      ${originalMount}`)
          .replace(`data-composition-id="${officialId}"`, `data-composition-id="${isolatedId}"`)
          .replace(`data-composition-src="${officialSource}"`, `data-composition-src="${isolatedRelative}"`)
          .replace(/\s+data-variable-values='[^']*'/, "");
      } else {
        html = fuseOfficialComponent(html, fs.readFileSync(sourcePath, "utf8"), officialId, compositionId, values, scene.duration, scene.id);
      }
    }
    html = applyPresenterGeometry(html, presenter);
    const motion = adaptMotion(selectedMotion, scene.duration);
    const frameRoot = path.join(projectRoot, "compositions/frames");
    fs.mkdirSync(frameRoot, { recursive: true });
    fs.writeFileSync(path.join(frameRoot, `${scene.id}.html`), html);
    fs.writeFileSync(path.join(frameRoot, `${scene.id}.motion.json`), motion);
    mounts.push({ ...scene, compositionId, start: cursor });
    rootAssertions.push({
      kind: "appearsBy",
      selector: `#scene-${scene.id}`,
      bySec: Number((cursor + Math.min(1, scene.duration * 0.5)).toFixed(3)),
    });
    cursor += scene.duration;
  }

  const contentFontLink = fs.existsSync(path.join(projectRoot, "assets/video-composition/content-font.css"))
    ? '    <link rel="stylesheet" href="assets/video-composition/content-font.css" />\n'
    : "";
  const mountHtml = mounts.map(scene => [
    `      <div id="scene-${scene.id}" class="clip"`,
    `        data-composition-id="${scene.compositionId}"`,
    `        data-composition-src="compositions/frames/${scene.id}.html"`,
    `        data-start="${scene.start}" data-duration="${scene.duration}" data-track-index="1"`,
    '        data-width="1920" data-height="1080"></div>',
  ].join("\n")).join("\n");
  const index = `<!doctype html>
<html lang="${htmlEscape(args.language)}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="assets/runtime/gsap.min.js"></script>
    <link rel="stylesheet" href="assets/video-composition/stage.css" />
${contentFontLink}    <style>
      * { box-sizing: border-box; }
      html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #000; }
      #root { position: relative; width: 1920px; height: 1080px; overflow: hidden; }
      #root > [data-composition-src] { position: absolute; inset: 0; width: 1920px; height: 1080px; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="${args.hostId}" data-color-system="${args.colorSystem}" data-width="1920" data-height="1080" data-duration="${cursor}" data-video-presenter="${args.presenterMode}" data-vc-timing="${provisionalTiming ? "provisional" : "final"}">
${mountHtml}
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      window.__timelines["${args.hostId}"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
`;
  fs.writeFileSync(indexPath, index);
  fs.writeFileSync(path.join(projectRoot, "index.motion.json"), `${JSON.stringify({ duration: cursor, assertions: rootAssertions }, null, 2)}\n`);
  console.log(`scene contract created: ${scenes.length} scene(s), ${cursor}s, presenter ${args.presenterMode}, global color system ${args.colorSystem}.`);
  if (provisionalTiming) console.log("Scene HTML is ready for content authoring; run finalize-timing.mjs with measured durations before review.");
  console.log(layoutMap.size
    ? "Executable official starters are active; edit only CONTENT_SLOT values in fused component scenes or scene-specific block files under compositions/official/."
    : "Generic technical envelopes were generated; integrate selected items next.");
  if (presenterOmissions.length) console.log(`Presenter omitted where full-canvas blocks require the complete stage: ${presenterOmissions.join(", ")}.`);
}

try {
  main();
} catch (error) {
  console.error(`scaffold failed: ${error.message}`);
  process.exitCode = 1;
}
