#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";

function fail(message) {
  process.stderr.write(`probe-alpha-bbox: ${message}\n`);
  process.exit(1);
}

const args = process.argv.slice(2);
const videoArg = args.find((arg) => !arg.startsWith("--"));
const limitArg = args.find((arg) => arg.startsWith("--limit="));
const limit = limitArg ? Number(limitArg.slice("--limit=".length)) : 0.01;

if (!videoArg) fail("usage: probe-alpha-bbox.mjs VIDEO [--limit=0.01]");
if (!Number.isFinite(limit) || limit < 0 || limit > 1)
  fail("--limit must be between 0 and 1");

const video = path.resolve(videoArg);
if (!existsSync(video)) fail(`video not found: ${videoArg}`);

const probe = spawnSync(
  "ffprobe",
  [
    "-v",
    "error",
    "-select_streams",
    "v:0",
    "-show_entries",
    "stream=codec_name,width,height:stream_tags=ALPHA_MODE",
    "-of",
    "json",
    video,
  ],
  { encoding: "utf8" },
);

if (probe.error) fail(`unable to run ffprobe: ${probe.error.message}`);
if (probe.status !== 0) fail(probe.stderr.trim() || "ffprobe failed");

let stream;
try {
  stream = JSON.parse(probe.stdout).streams?.[0];
} catch {
  fail("ffprobe returned invalid JSON");
}

if (!stream?.width || !stream?.height) fail("video dimensions were not found");

const ffmpegArgs = ["-hide_banner", "-loglevel", "info"];
if (stream.codec_name === "vp9") ffmpegArgs.push("-c:v", "libvpx-vp9");
ffmpegArgs.push(
  "-i",
  video,
  "-vf",
  `alphaextract,cropdetect=limit=${limit}:round=2:reset=0`,
  "-an",
  "-f",
  "null",
  "-",
);

const scan = spawnSync("ffmpeg", ffmpegArgs, {
  encoding: "utf8",
  maxBuffer: 32 * 1024 * 1024,
});

if (scan.error) fail(`unable to run ffmpeg: ${scan.error.message}`);
if (scan.status !== 0)
  fail(scan.stderr.trim().split("\n").slice(-8).join("\n") || "ffmpeg failed");

const crops = [...scan.stderr.matchAll(/crop=(\d+):(\d+):(\d+):(\d+)/g)];
if (crops.length === 0) {
  fail(
    "no alpha bounds detected; confirm that the video has a decodable alpha channel",
  );
}

const [, width, height, x, y] = crops.at(-1);
const result = {
  sourceWidth: Number(stream.width),
  sourceHeight: Number(stream.height),
  bbox: {
    x: Number(x),
    y: Number(y),
    width: Number(width),
    height: Number(height),
  },
  codec: stream.codec_name,
  alphaMode: stream.tags?.ALPHA_MODE ?? null,
  scannedFrames: crops.length,
};

if (
  result.bbox.x < 0 ||
  result.bbox.y < 0 ||
  result.bbox.width <= 0 ||
  result.bbox.height <= 0 ||
  result.bbox.x + result.bbox.width > result.sourceWidth ||
  result.bbox.y + result.bbox.height > result.sourceHeight
) {
  fail(`detected invalid bounds: ${JSON.stringify(result)}`);
}

process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
