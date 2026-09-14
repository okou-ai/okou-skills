import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import crypto from "node:crypto";
import { parseComposition, preflightProject, sourceFingerprint, incrementalPreviewSelection } from "../scripts/review-project.mjs";

const scripts = fileURLToPath(new URL("../scripts/", import.meta.url));
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "vc-production-"));
  const project = path.join(root, "project");
  const bin = path.join(root, "bin");
  fs.mkdirSync(path.join(project, "compositions/frames"), { recursive: true });
  fs.mkdirSync(path.join(project, "assets/media"), { recursive: true });
  fs.mkdirSync(bin);
  const host = '<div id="root" data-composition-id="demo" data-start="0" data-duration="4" data-width="1920" data-height="1080">' +
    '<div id="scene-cover" data-composition-id="demo-cover" data-composition-src="compositions/frames/cover.html" data-start="0" data-duration="4"></div>' +
    '<audio id="narration" src="assets/media/narration.wav" data-start="0" data-duration="4"></audio></div>';
  fs.writeFileSync(path.join(project, "index.html"), host);
  fs.writeFileSync(path.join(project, "compositions/frames/cover.html"), '<div data-composition-id="demo-cover">Title</div><script>window.__timelines["demo-cover"] = {};</script>');
  for (const file of ["index.motion.json", "compositions/frames/cover.motion.json"]) {
    fs.writeFileSync(path.join(project, file), JSON.stringify({ duration: 4, assertions: [{ selector: "#root" }] }));
  }
  fs.writeFileSync(path.join(project, "assets/media/narration.wav"), "first audio bytes");
  fs.writeFileSync(path.join(project, "package.json"), JSON.stringify({ scripts: { check: "npx --yes hyperframes@0.8.38 check" } }));
  fs.writeFileSync(path.join(bin, "npx"), `#!${process.execPath}
const fs = require('node:fs');
const path = require('node:path');
fs.appendFileSync(process.env.QA_CALLS_FILE, JSON.stringify(process.argv.slice(2)) + '\\n');
const at = process.argv.find(arg => arg.startsWith('--at='));
function finish() {
  if (process.env.QA_WAIT_FOR_FILE && !fs.existsSync(process.env.QA_WAIT_FOR_FILE)) return setTimeout(finish, 10);
  const fail = fs.existsSync(path.join(process.cwd(), 'fail-check'));
  console.log(JSON.stringify({ok:!fail, findings:[], layout:{samples:at ? at.slice(5).split(',').map(Number) : [], findings:[]}, motion:{enabled:true, ok:!fail, findings:[]}}));
  process.exitCode = fail ? 1 : 0;
}
setTimeout(finish, Number(process.env.QA_DELAY_MS || 100));
`, { mode: 0o755 });
  const env = { ...process.env, PATH: `${bin}${path.delimiter}${process.env.PATH}`, QA_CALLS_FILE: path.join(root, "calls.jsonl"), QA_DELAY_MS: "500" };
  const call = (command, extra = []) => spawnSync(process.execPath, [path.join(scripts, "review-job.mjs"), command, "--project", project, ...extra], { encoding: "utf8", env, timeout: 5000 });
  const begin = (phase = "preview", extra = []) => {
    const result = call("start", ["--phase", phase, ...extra]);
    assert.equal(result.status, 0, result.stderr);
    return JSON.parse(result.stdout);
  };
  const get = id => {
    const result = call("status", ["--job", id]);
    assert.ok(result.stdout, result.stderr);
    return JSON.parse(result.stdout);
  };
  const until = async (id, predicate) => {
    for (let count = 0; count < 120; count += 1) {
      const state = get(id);
      if (predicate(state)) return state;
      await pause(30);
    }
    throw new Error(`Review ${id} did not reach the expected state.`);
  };
  const finish = id => until(id, state => ["passed", "failed", "interrupted"].includes(state.status));
  t.after(() => {
    const active = path.join(project, ".hyperframes/review-project/active-job.json");
    if (fs.existsSync(active)) {
      const job = JSON.parse(fs.readFileSync(active));
      const state = get(job.jobId);
      if (state.pid) { try { process.kill(-state.pid, "SIGKILL"); } catch {} }
    }
    fs.rmSync(root, { recursive: true, force: true });
  });
  return { root, project, host, env, call, begin, get, until, finish };
}

test("a detached review survives its launching CLI, deduplicates starts, and blocks overlapping phases", async t => {
  const f = fixture(t);
  f.env.QA_DELAY_MS = "1";
  f.env.QA_WAIT_FOR_FILE = path.join(f.root, "allow-completion");
  const first = f.begin();
  assert.ok(["starting", "running"].includes(first.status), "start must return while the check is waiting on its completion barrier");
  const repeated = f.begin();
  assert.equal(repeated.jobId, first.jobId);
  assert.equal(repeated.reused, true);
  assert.notEqual(f.call("start", ["--phase", "release"]).status, 0);
  fs.writeFileSync(f.env.QA_WAIT_FOR_FILE, "continue");
  const done = await f.finish(first.jobId);
  assert.equal(done.status, "passed");
  const report = JSON.parse(fs.readFileSync(done.report));
  assert.ok(report.completedAt >= report.startedAt);
  assert.ok(report.durationMs >= 0);
  assert.equal(fs.readFileSync(path.join(f.root, "calls.jsonl"), "utf8").trim().split("\n").length, 1);
  const release = await f.finish(f.begin("release").jobId);
  assert.equal(JSON.parse(fs.readFileSync(release.report)).reusedPreview, true);
  assert.equal(fs.readFileSync(path.join(f.root, "calls.jsonl"), "utf8").trim().split("\n").length, 1);
});

test("an interrupted attempt cannot borrow an old PASS and is not restarted automatically", async t => {
  const f = fixture(t);
  assert.equal((await f.finish(f.begin().jobId)).status, "passed");
  // A changed source makes the second attempt run the engine rather than reuse the first result.
  fs.appendFileSync(path.join(f.project, "compositions/frames/cover.html"), "<!-- revised -->");
  f.env.QA_DELAY_MS = "4000";
  const next = f.begin();
  const running = await f.until(next.jobId, state => state.status === "running");
  process.kill(-running.pid, "SIGTERM");
  const interrupted = await f.finish(next.jobId);
  assert.equal(interrupted.status, "interrupted");
  assert.equal(JSON.parse(fs.readFileSync(path.join(f.project, ".hyperframes/review-project/preview/report.json"))).ok, true);
  assert.equal(f.get(next.jobId).status, "interrupted");
  f.env.QA_DELAY_MS = "100";
  const explicitRetry = f.begin();
  assert.notEqual(explicitRetry.jobId, next.jobId);
  assert.equal((await f.finish(explicitRetry.jobId)).status, "passed");
});

test("failed checks retain failure evidence and input changes during a check fail closed", async t => {
  const f = fixture(t);
  fs.writeFileSync(path.join(f.project, "fail-check"), "fail");
  const failure = await f.finish(f.begin().jobId);
  assert.equal(failure.status, "failed");
  assert.ok(failure.errors.length);
  fs.unlinkSync(path.join(f.project, "fail-check"));
  f.env.QA_DELAY_MS = "1200";
  const next = f.begin();
  await f.until(next.jobId, state => fs.existsSync(path.join(f.root, "calls.jsonl")) && fs.readFileSync(path.join(f.root, "calls.jsonl"), "utf8").trim().split("\n").length === 2);
  fs.writeFileSync(path.join(f.project, "assets/media/narration.wav"), "replacement during review");
  const changed = await f.finish(next.jobId);
  assert.equal(changed.status, "failed");
  assert.ok(changed.errors.some(error => error.includes("inputs changed")));
});

test("same-name audio replacements invalidate review, and runtime audio rates fail preflight", async t => {
  const f = fixture(t);
  assert.equal((await f.finish(f.begin().jobId)).status, "passed");
  const parsed = parseComposition(f.host);
  assert.equal(incrementalPreviewSelection(f.project, parsed).mode, "reuse");
  const before = sourceFingerprint(f.project);
  fs.writeFileSync(path.join(f.project, "assets/media/narration.wav"), "new same-name audio");
  assert.notEqual(sourceFingerprint(f.project), before);
  assert.equal(incrementalPreviewSelection(f.project, parsed).mode, "full");
  fs.writeFileSync(path.join(f.project, "index.html"), f.host.replace('<audio ', '<audio data-playback-rate="0.88" '));
  const preflight = preflightProject(f.project, parsed);
  assert.equal(preflight.ok, false);
  assert.ok(preflight.errors.some(error => error.includes("runtime playback rate")));
});

test("a recorded blank host survives template changes but edited or authored hosts are preserved", t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "vc-bootstrap-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const blank = '<!doctype html><html><body><div id="root" data-composition-id="main"><h1 id="title">Title</h1></div></body></html>';
  fs.writeFileSync(path.join(root, "index.html"), blank);
  fs.writeFileSync(path.join(root, "hyperframes.json"), "{}");
  const receiptDir = path.join(root, ".hyperframes/video-composition");
  fs.mkdirSync(receiptDir, { recursive: true });
  fs.writeFileSync(path.join(receiptDir, "bootstrap.json"), JSON.stringify({ hyperframesVersion: "0.8.38", blankIndexSha256: crypto.createHash("sha256").update(blank).digest("hex") }));
  const run = (script, extra) => spawnSync(process.execPath, [path.join(scripts, script), "--project", root, ...extra], { encoding: "utf8" });
  const stage = run("stage-authoring-kit.mjs", ["--presenter", "off", "--language", "en"]);
  assert.equal(stage.status, 0, stage.stderr);
  const scaffold = () => run("scaffold-scenes.mjs", ["--host-id", "demo", "--presenter", "off", "--scenes", "cover:4"]);
  const edited = blank.replace("Title</h1>", "Approved copy</h1>");
  fs.writeFileSync(path.join(root, "index.html"), edited);
  assert.notEqual(scaffold().status, 0);
  assert.equal(fs.readFileSync(path.join(root, "index.html"), "utf8"), edited);
  fs.writeFileSync(path.join(root, "index.html"), blank);
  const created = scaffold();
  assert.equal(created.status, 0, created.stderr);
  const authored = fs.readFileSync(path.join(root, "index.html"), "utf8");
  assert.match(authored, /demo-cover/);
  assert.notEqual(scaffold().status, 0);
  assert.equal(fs.readFileSync(path.join(root, "index.html"), "utf8"), authored);
});

test("font preparation retains full coverage by default and refuses a missing-glyph subset", t => {
  const deps = spawnSync("python3", ["-c", "import fontTools, brotli"], { encoding: "utf8" });
  if (deps.status !== 0) return t.skip("FontTools and Brotli are optional font-preparation dependencies.");
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "vc-font-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const source = path.resolve(scripts, "../assets/fonts/body.woff2");
  const output = path.join(root, "content.woff2");
  const run = extra => spawnSync("python3", [path.join(scripts, "prepare-content-font.py"), "--input", source, "--output", output, ...extra], { encoding: "utf8" });
  const full = run([]);
  assert.equal(full.status, 0, full.stderr);
  assert.equal(JSON.parse(full.stdout).subset, false);
  const comparison = spawnSync("python3", ["-c", "from fontTools.ttLib import TTFont; import sys; assert TTFont(sys.argv[1]).getBestCmap() == TTFont(sys.argv[2]).getBestCmap()", source, output], { encoding: "utf8" });
  assert.equal(comparison.status, 0, comparison.stderr);
  const before = fs.readFileSync(output);
  const textFile = path.join(root, "visible.txt");
  fs.writeFileSync(textFile, "Hello " + String.fromCodePoint(0x10ffff));
  const missing = run(["--text-file", textFile, "--overwrite"]);
  assert.notEqual(missing.status, 0);
  assert.match(missing.stderr, /lacks visible glyphs/);
  assert.deepEqual(fs.readFileSync(output), before);
});
