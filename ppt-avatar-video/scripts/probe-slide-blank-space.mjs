#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { existsSync, readdirSync, statSync } from "node:fs";
import path from "node:path";

function fail(message) {
  process.stderr.write(`probe-slide-blank-space: ${message}\n`);
  process.exit(1);
}

function option(name) {
  const prefix = `--${name}=`;
  const argument = process.argv
    .slice(2)
    .find((value) => value.startsWith(prefix));
  return argument?.slice(prefix.length);
}

function numberOption(name, fallback, { min, max }) {
  const raw = option(name);
  const value = raw === undefined ? fallback : Number(raw);
  if (!Number.isFinite(value) || value < min || value > max) {
    fail(`--${name} must be between ${min} and ${max}`);
  }
  return value;
}

const inputArgs = process.argv
  .slice(2)
  .filter((argument) => !argument.startsWith("--"));
const bboxArg = option("bbox");
const bboxMatch = bboxArg?.match(/^(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)$/u);
if (inputArgs.length === 0 || !bboxMatch) {
  fail(
    "usage: probe-slide-blank-space.mjs SLIDE_OR_DIR [...] --bbox=WIDTHxHEIGHT [--visible-width-fraction=0.14]",
  );
}

const bboxWidth = Number(bboxMatch[1]);
const bboxHeight = Number(bboxMatch[2]);
if (bboxWidth <= 0 || bboxHeight <= 0)
  fail("--bbox dimensions must be positive");

const visibleWidthFraction = numberOption("visible-width-fraction", 0.14, {
  min: 0.01,
  max: 0.5,
});
const paddingFraction = numberOption("padding-fraction", 0.02, {
  min: 0,
  max: 0.2,
});
const tieThreshold = numberOption("tie-threshold", 0.08, {
  min: 0,
  max: 1,
});
const sampleWidth = Math.round(
  numberOption("sample-width", 480, { min: 64, max: 1920 }),
);
const defaultAnchor = option("default-anchor") || "bottom-right";
if (!new Set(["bottom-left", "bottom-right"]).has(defaultAnchor)) {
  fail("--default-anchor must be bottom-left or bottom-right");
}

const imageExtension = /\.(?:jpe?g|png|webp)$/iu;
const inputPaths = inputArgs.flatMap((input) => {
  const absolute = path.resolve(input);
  if (!existsSync(absolute)) fail(`input not found: ${input}`);
  if (!statSync(absolute).isDirectory()) return [absolute];
  return readdirSync(absolute)
    .filter((name) => imageExtension.test(name))
    .map((name) => path.join(absolute, name));
});

const slides = [...new Set(inputPaths)]
  .filter((input) => imageExtension.test(input))
  .sort((left, right) =>
    left.localeCompare(right, undefined, {
      numeric: true,
      sensitivity: "base",
    }),
  );
if (slides.length === 0) fail("no PNG, JPEG, or WebP slide images found");

function probeDimensions(imagePath) {
  const probe = spawnSync(
    "ffprobe",
    [
      "-v",
      "error",
      "-select_streams",
      "v:0",
      "-show_entries",
      "stream=width,height",
      "-of",
      "json",
      imagePath,
    ],
    { encoding: "utf8" },
  );
  if (probe.error) fail(`unable to run ffprobe: ${probe.error.message}`);
  if (probe.status !== 0) {
    fail(probe.stderr.trim() || `ffprobe failed for ${imagePath}`);
  }
  let stream;
  try {
    stream = JSON.parse(probe.stdout).streams?.[0];
  } catch {
    fail(`ffprobe returned invalid JSON for ${imagePath}`);
  }
  if (!stream?.width || !stream?.height) {
    fail(`image dimensions were not found: ${imagePath}`);
  }
  return { width: Number(stream.width), height: Number(stream.height) };
}

function decodeSample(imagePath, width, height) {
  const sampleHeight = Math.max(2, Math.round((sampleWidth * height) / width));
  const decode = spawnSync(
    "ffmpeg",
    [
      "-hide_banner",
      "-loglevel",
      "error",
      "-i",
      imagePath,
      "-frames:v",
      "1",
      "-vf",
      `scale=${sampleWidth}:${sampleHeight}:flags=area,format=rgb24`,
      "-pix_fmt",
      "rgb24",
      "-f",
      "rawvideo",
      "-",
    ],
    { maxBuffer: 64 * 1024 * 1024 },
  );
  if (decode.error) fail(`unable to run ffmpeg: ${decode.error.message}`);
  if (decode.status !== 0) {
    fail(decode.stderr.toString().trim() || `ffmpeg failed for ${imagePath}`);
  }
  const expected = sampleWidth * sampleHeight * 3;
  if (decode.stdout.length !== expected) {
    fail(
      `decoded ${decode.stdout.length} bytes for ${imagePath}; expected ${expected}`,
    );
  }
  return { pixels: decode.stdout, width: sampleWidth, height: sampleHeight };
}

function regionComplexity(pixels, frameWidth, region) {
  let edgeCount = 0;
  let edgeTotal = 0;
  let strongEdges = 0;

  function colorDifference(first, second) {
    return (
      (Math.abs(pixels[first] - pixels[second]) +
        Math.abs(pixels[first + 1] - pixels[second + 1]) +
        Math.abs(pixels[first + 2] - pixels[second + 2])) /
      3
    );
  }

  for (let y = region.y; y < region.y + region.height; y += 1) {
    for (let x = region.x; x < region.x + region.width; x += 1) {
      const offset = (y * frameWidth + x) * 3;
      if (x + 1 < region.x + region.width) {
        const difference = colorDifference(offset, offset + 3);
        edgeTotal += difference;
        strongEdges += difference >= 18 ? 1 : 0;
        edgeCount += 1;
      }
      if (y + 1 < region.y + region.height) {
        const difference = colorDifference(offset, offset + frameWidth * 3);
        edgeTotal += difference;
        strongEdges += difference >= 18 ? 1 : 0;
        edgeCount += 1;
      }
    }
  }

  const meanGradient = edgeCount === 0 ? 0 : edgeTotal / edgeCount / 255;
  const edgeDensity = edgeCount === 0 ? 0 : strongEdges / edgeCount;
  return {
    score: edgeDensity * 0.75 + meanGradient * 0.25,
    edgeDensity,
    meanGradient,
  };
}

function rounded(value) {
  return Number(value.toFixed(6));
}

let previousAnchor = defaultAnchor;
const results = slides.map((slidePath) => {
  const dimensions = probeDimensions(slidePath);
  const sample = decodeSample(slidePath, dimensions.width, dimensions.height);
  const visibleWidth = sample.width * visibleWidthFraction;
  const visibleHeight = visibleWidth * (bboxHeight / bboxWidth);
  const horizontalPadding = sample.width * paddingFraction;
  const verticalPadding = sample.height * paddingFraction;
  const regionWidth = Math.min(
    sample.width,
    Math.max(2, Math.ceil(visibleWidth + horizontalPadding * 2)),
  );
  const regionHeight = Math.min(
    sample.height,
    Math.max(2, Math.ceil(visibleHeight + verticalPadding)),
  );
  const y = sample.height - regionHeight;
  const leftRegion = { x: 0, y, width: regionWidth, height: regionHeight };
  const rightRegion = {
    x: sample.width - regionWidth,
    y,
    width: regionWidth,
    height: regionHeight,
  };
  const left = regionComplexity(sample.pixels, sample.width, leftRegion);
  const right = regionComplexity(sample.pixels, sample.width, rightRegion);
  const difference = Math.abs(left.score - right.score);
  const denominator = Math.max(left.score, right.score, 1e-9);
  const relativeDifference = difference / denominator;
  const anchor =
    relativeDifference <= tieThreshold
      ? previousAnchor
      : left.score < right.score
        ? "bottom-left"
        : "bottom-right";
  previousAnchor = anchor;

  return {
    path: slidePath,
    presenterAnchor: anchor,
    scores: {
      bottomLeft: rounded(left.score),
      bottomRight: rounded(right.score),
      relativeDifference: rounded(relativeDifference),
    },
  };
});

process.stdout.write(
  `${JSON.stringify(
    {
      strategy: "lowest-bottom-corner-complexity",
      bbox: { width: bboxWidth, height: bboxHeight },
      visibleWidthFraction,
      paddingFraction,
      tieThreshold,
      defaultAnchor,
      slides: results,
    },
    null,
    2,
  )}\n`,
);
