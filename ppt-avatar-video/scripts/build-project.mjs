#!/usr/bin/env node

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

function fail(message) {
  process.stderr.write(`build-project: ${message}\n`);
  process.exit(1);
}

function parseFlag(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

function finiteNumber(value, label, { min = -Infinity, max = Infinity } = {}) {
  const number = Number(value);
  if (!Number.isFinite(number) || number < min || number > max) {
    fail(`${label} must be a finite number between ${min} and ${max}`);
  }
  return number;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function formatSeconds(value) {
  return Number(value.toFixed(6)).toString();
}

const PRESENTER_ANCHORS = new Set(["bottom-left", "bottom-right"]);
const PRESENTER_PLACEMENTS = new Set(["left", "overlay", "right"]);

function optionalPresenterAnchor(value, label) {
  if (value === undefined || value === null || value === "") return null;
  const anchor = String(value);
  if (!PRESENTER_ANCHORS.has(anchor)) {
    fail(`${label} must be bottom-left or bottom-right`);
  }
  return anchor;
}

const manifestArg = parseFlag("--manifest");
const outArg = parseFlag("--out");
if (!manifestArg || !outArg) {
  fail(
    "usage: build-project.mjs --manifest composition-input.json --out PROJECT_DIR",
  );
}

const manifestPath = path.resolve(manifestArg);
const outDir = path.resolve(outArg);
if (!existsSync(manifestPath)) fail(`manifest not found: ${manifestArg}`);

let manifest;
try {
  manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
} catch (error) {
  fail(`invalid manifest JSON: ${error.message}`);
}

const id = String(manifest.id || "deck-video");
if (!/^[a-z0-9][a-z0-9-]{0,62}$/.test(id)) {
  fail("id must be a lowercase kebab-case identifier of at most 63 characters");
}

const width = finiteNumber(manifest.width ?? 1920, "width", {
  min: 16,
  max: 7680,
});
const height = finiteNumber(manifest.height ?? 1080, "height", {
  min: 16,
  max: 7680,
});
const fps = finiteNumber(manifest.fps ?? 30, "fps", { min: 1, max: 240 });
const background = String(manifest.background || "#000000");
const hyperframesVersion = String(manifest.hyperframesVersion || "0.8.26");

if (!Array.isArray(manifest.slides) || manifest.slides.length === 0) {
  fail("slides must be a non-empty array");
}

mkdirSync(outDir, { recursive: true });
const outPrefix = `${outDir}${path.sep}`;

function validateAsset(relativePath, label) {
  if (
    typeof relativePath !== "string" ||
    !relativePath ||
    path.isAbsolute(relativePath)
  ) {
    fail(`${label} must be a project-relative path`);
  }
  const absolute = path.resolve(outDir, relativePath);
  if (!absolute.startsWith(outPrefix) || !existsSync(absolute)) {
    fail(`${label} is missing or outside the project: ${relativePath}`);
  }
  return relativePath.split(path.sep).join("/");
}

let slideCursor = 0;
const slides = manifest.slides.map((slide, index) => {
  const duration = finiteNumber(slide.duration, `slides[${index}].duration`, {
    min: 0.1,
    max: 3600,
  });
  const result = {
    path: validateAsset(slide.path, `slides[${index}].path`),
    duration,
    start: slideCursor,
    presenterAnchor: optionalPresenterAnchor(
      slide.presenterAnchor,
      `slides[${index}].presenterAnchor`,
    ),
  };
  slideCursor += duration;
  return result;
});

const totalDuration = slideCursor;

const presenterInput = manifest.presenter;
if (
  presenterInput !== undefined &&
  presenterInput !== null &&
  typeof presenterInput !== "object"
) {
  fail("presenter must be an object when provided");
}

let presenter = null;
if (presenterInput) {
  const presenterPath = validateAsset(presenterInput.path, "presenter.path");
  const sourceWidth = finiteNumber(
    presenterInput.sourceWidth,
    "presenter.sourceWidth",
    { min: 1 },
  );
  const sourceHeight = finiteNumber(
    presenterInput.sourceHeight,
    "presenter.sourceHeight",
    { min: 1 },
  );
  const bbox = presenterInput.bbox || {};
  const bboxX = finiteNumber(bbox.x, "presenter.bbox.x", { min: 0 });
  const bboxY = finiteNumber(bbox.y, "presenter.bbox.y", { min: 0 });
  const bboxWidth = finiteNumber(bbox.width, "presenter.bbox.width", {
    min: 1,
  });
  const bboxHeight = finiteNumber(bbox.height, "presenter.bbox.height", {
    min: 1,
  });
  if (bboxX + bboxWidth > sourceWidth || bboxY + bboxHeight > sourceHeight) {
    fail("presenter.bbox exceeds the source video dimensions");
  }

  const visibleWidthFraction = finiteNumber(
    presenterInput.visibleWidthFraction ?? 0.14,
    "presenter.visibleWidthFraction",
    { min: 0.01, max: 1 },
  );
  const placement = String(presenterInput.placement || "overlay");
  if (!PRESENTER_PLACEMENTS.has(placement)) {
    fail("presenter.placement must be left, overlay, or right");
  }
  if (
    placement !== "overlay" &&
    slides.some((slide) => slide.presenterAnchor)
  ) {
    fail("slides[].presenterAnchor is only valid for overlay placement");
  }

  const requestedAnchor = optionalPresenterAnchor(
    presenterInput.anchor,
    "presenter.anchor",
  );
  const anchor =
    placement === "left"
      ? "bottom-left"
      : placement === "right"
        ? "bottom-right"
        : requestedAnchor || "bottom-right";
  const horizontalInsetFraction = placement === "overlay" ? 0 : 0.03;
  const bottomInsetFraction = placement === "overlay" ? 0 : 0.115;

  const targetVisibleWidth = width * visibleWidthFraction;
  const scale = targetVisibleWidth / bboxWidth;
  const renderedWidth = sourceWidth * scale;
  const renderedHeight = sourceHeight * scale;
  const bottomOffset =
    height * bottomInsetFraction - (sourceHeight - bboxY - bboxHeight) * scale;
  const leftOffset = width * horizontalInsetFraction - bboxX * scale;
  const rightOffset =
    width * horizontalInsetFraction - (sourceWidth - bboxX - bboxWidth) * scale;

  presenter = {
    path: presenterPath,
    placement,
    anchor,
    visibleWidthFraction,
    targetVisibleWidth,
    scale,
    renderedWidth,
    renderedHeight,
    bottomOffset,
    leftOffset,
    rightOffset,
    clipTop: (bboxY / sourceHeight) * 100,
    clipRight: ((sourceWidth - bboxX - bboxWidth) / sourceWidth) * 100,
    clipBottom: ((sourceHeight - bboxY - bboxHeight) / sourceHeight) * 100,
    clipLeft: (bboxX / sourceWidth) * 100,
  };
}

const narrationInput = manifest.narration;
if (
  narrationInput !== undefined &&
  narrationInput !== null &&
  typeof narrationInput !== "object"
) {
  fail("narration must be an object when provided");
}

let audioPath;
if (narrationInput) {
  audioPath = validateAsset(narrationInput.path, "narration.path");
} else if (presenterInput) {
  audioPath = validateAsset(
    presenterInput.audioPath || presenterInput.path,
    "presenter.audioPath",
  );
} else {
  fail("narration.path is required when presenter is omitted");
}

const slideTags = slides
  .map((slide, index) => {
    return `      <img id="slide-${String(index + 1).padStart(3, "0")}" class="clip slide" src="${escapeHtml(slide.path)}" alt="Slide ${index + 1}" data-start="${formatSeconds(slide.start)}" data-duration="${formatSeconds(slide.duration)}" />`;
  })
  .join("\n");

const slideStyle =
  presenter?.placement === "left"
    ? `left: 20%; top: 11.5%; width: 77%; height: 77%;`
    : presenter?.placement === "right"
      ? `left: 3%; top: 11.5%; width: 77%; height: 77%;`
      : `inset: 0; width: ${width}px; height: ${height}px;`;

const presenterAnchors = presenter
  ? slides.map((slide) => {
      if (presenter.placement === "left") return "bottom-left";
      if (presenter.placement === "right") return "bottom-right";
      return slide.presenterAnchor || presenter.anchor;
    })
  : [];

const presenterSegments = [];
for (const [index, slide] of slides.entries()) {
  if (!presenter) break;
  const anchor = presenterAnchors[index];
  const previous = presenterSegments.at(-1);
  if (previous?.anchor === anchor) {
    previous.duration += slide.duration;
  } else {
    presenterSegments.push({
      anchor,
      start: slide.start,
      duration: slide.duration,
    });
  }
}

const presenterStyle = presenter
  ? `
      .presenter-video {
        z-index: 20;
        bottom: ${formatSeconds(presenter.bottomOffset)}px;
        width: ${formatSeconds(presenter.renderedWidth)}px;
        height: ${formatSeconds(presenter.renderedHeight)}px;
        clip-path: inset(${formatSeconds(presenter.clipTop)}% ${formatSeconds(presenter.clipRight)}% ${formatSeconds(presenter.clipBottom)}% ${formatSeconds(presenter.clipLeft)}%);
        pointer-events: none;
      }
      .presenter-bottom-left {
        left: ${formatSeconds(presenter.leftOffset)}px;
      }
      .presenter-bottom-right {
        right: ${formatSeconds(presenter.rightOffset)}px;
      }`
  : "";
const presenterTags = presenter
  ? `${presenterSegments
      .map((segment, index) => {
        const id =
          index === 0
            ? "presenter-video"
            : `presenter-video-${String(index + 1).padStart(3, "0")}`;
        return `      <video id="${id}" class="clip presenter-video presenter-${segment.anchor}" src="${escapeHtml(presenter.path)}" data-start="${formatSeconds(segment.start)}" data-duration="${formatSeconds(segment.duration)}" data-media-start="${formatSeconds(segment.start)}" data-track-index="20" data-layout-allow-overlap data-layout-allow-overflow muted playsinline preload="auto" aria-label="Presenter"></video>`;
      })
      .join("\n")}\n`
  : "";

const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=${width}, height=${height}" />
    <title>${escapeHtml(id)}</title>
    <style>
      * { box-sizing: border-box; }
      html, body { margin: 0; width: ${width}px; height: ${height}px; overflow: hidden; background: ${escapeHtml(background)}; }
      #root { position: relative; width: ${width}px; height: ${height}px; overflow: hidden; isolation: isolate; background: ${escapeHtml(background)}; }
      .clip { position: absolute; }
      .slide { z-index: 1; ${slideStyle} object-fit: contain; background: ${escapeHtml(background)}; }
${presenterStyle}
      .narration-audio { width: 0; height: 0; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-no-timeline data-start="0" data-duration="${formatSeconds(totalDuration)}" data-width="${width}" data-height="${height}">
${slideTags}
${presenterTags}      <audio id="narration-audio" class="clip narration-audio" src="${escapeHtml(audioPath)}" data-start="0" data-duration="${formatSeconds(totalDuration)}" data-track-index="30" data-volume="1" preload="auto"></audio>
    </div>
  </body>
</html>
`;

const packageJson = {
  name: id,
  private: true,
  type: "module",
  scripts: {
    dev: `npx --yes hyperframes@${hyperframesVersion} preview`,
    check: `npx --yes hyperframes@${hyperframesVersion} check`,
    render: `npx --yes hyperframes@${hyperframesVersion} render`,
    publish: `npx --yes hyperframes@${hyperframesVersion} publish`,
  },
};

const hyperframesJson = {
  $schema: "https://hyperframes.heygen.com/schema/hyperframes.json",
  paths: {
    blocks: "compositions",
    components: "compositions/components",
    assets: "assets",
  },
  media: { autoProxy: true },
  authoringSkill: "ppt-avatar-video",
  registryItems: [],
};

writeFileSync(path.join(outDir, "index.html"), html);
writeFileSync(
  path.join(outDir, "index.motion.json"),
  `${JSON.stringify(
    {
      duration: totalDuration,
      assertions: [{ kind: "appearsBy", selector: "#slide-001", bySec: 0.1 }],
    },
    null,
    2,
  )}\n`,
);
writeFileSync(
  path.join(outDir, "package.json"),
  `${JSON.stringify(packageJson, null, 2)}\n`,
);
writeFileSync(
  path.join(outDir, "hyperframes.json"),
  `${JSON.stringify(hyperframesJson, null, 2)}\n`,
);
writeFileSync(
  path.join(outDir, "meta.json"),
  `${JSON.stringify({ id, name: id, createdAt: new Date().toISOString() }, null, 2)}\n`,
);

process.stdout.write(
  `${JSON.stringify(
    {
      project: outDir,
      slides: slides.length,
      duration: totalDuration,
      fps,
      mode: presenter ? "avatar" : "voice-only",
      narration: { path: audioPath },
      presenter: presenter
        ? {
            placement: presenter.placement,
            anchor: presenter.anchor,
            slideAnchors: presenterAnchors,
            segments: presenterSegments,
            visibleWidthFraction: presenter.visibleWidthFraction,
            targetVisibleWidth: presenter.targetVisibleWidth,
            scale: presenter.scale,
            renderedWidth: presenter.renderedWidth,
            renderedHeight: presenter.renderedHeight,
          }
        : null,
    },
    null,
    2,
  )}\n`,
);
