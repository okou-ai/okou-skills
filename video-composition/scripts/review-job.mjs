#!/usr/bin/env node
// Detach read-only QA from the tool session. The cloud render has its own durable job.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { spawn } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";
import { main as review } from "./review-project.mjs";

const scriptPath = fileURLToPath(import.meta.url);
const phases = new Set(["preflight", "static", "preview", "release"]);
const terminal = new Set(["passed", "failed", "interrupted"]);
const readJson = file => JSON.parse(fs.readFileSync(file, "utf8"));
const writeJson = (file, value) => {
  const temporary = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(temporary, JSON.stringify(value, null, 2) + "\n");
  fs.renameSync(temporary, file);
};

function locations(project, jobId) {
  if (!/^[a-f0-9-]{36}$/.test(jobId)) throw new Error("Use the exact job ID returned by start.");
  const root = path.join(project, ".hyperframes/review-project");
  return { directory: path.join(root, "jobs", jobId), lock: path.join(root, "active-job.json") };
}

function unlock(project, jobId) {
  const { lock, directory } = locations(project, jobId);
  const marker = path.join(directory, "unlocked");
  // Only one process may clean up a given job, so a late cleanup cannot unlink a newer lock.
  try { fs.mkdirSync(marker); }
  catch (error) { if (error.code === "EEXIST") return; throw error; }
  try {
    if (fs.existsSync(lock) && readJson(lock).jobId === jobId) fs.unlinkSync(lock);
  } catch (error) {
    fs.rmdirSync(marker);
    throw error;
  }
}

function alive(pid) {
  try { process.kill(pid, 0); return true; }
  catch (error) { if (error.code === "ESRCH") return false; return true; }
}

function activeProcessGroup(pid) {
  if (process.platform !== "linux") return alive(pid) || alive(-pid);
  // Container PID 1 may leave dead workers as zombies; kill(pid, 0) alone says they are alive.
  try {
    for (const entry of fs.readdirSync("/proc").filter(name => /^\d+$/.test(name))) {
      let stat;
      try { stat = fs.readFileSync(`/proc/${entry}/stat`, "utf8"); }
      catch (error) { if (["ENOENT", "ESRCH"].includes(error.code)) continue; throw error; }
      const fields = stat.slice(stat.lastIndexOf(")") + 2).split(" ");
      if ((Number(entry) === pid || Number(fields[2]) === pid) && !["Z", "X"].includes(fields[0])) return true;
    }
    return false;
  } catch { return alive(pid) || alive(-pid); }
}

export function status(project, jobId) {
  const { directory, lock } = locations(project, jobId);
  const statePath = path.join(directory, "status.json");
  if (!fs.existsSync(statePath)) {
    const pending = fs.existsSync(lock) ? readJson(lock) : null;
    if (pending?.jobId === jobId) return { ...pending, status: "starting", log: path.join(directory, "run.log") };
    throw new Error(`No retained review job ${jobId} in this project.`);
  }
  let state = readJson(statePath);
  const pidFile = path.join(directory, "pid");
  const pid = state.pid || (fs.existsSync(pidFile) ? Number(fs.readFileSync(pidFile, "utf8")) : null);
  if (!terminal.has(state.status) && pid && !activeProcessGroup(pid)) {
    // Re-read after probing: the worker may just have committed its terminal result.
    state = readJson(path.join(directory, "status.json"));
    if (!terminal.has(state.status)) {
      state = { ...state, status: "interrupted", completedAt: new Date().toISOString(), error: "The review process and its process group exited without a terminal result. Inspect this job's log before explicitly starting another check." };
      writeJson(path.join(directory, "status.json"), state);
      unlock(project, jobId);
    }
  }
  return { ...state, pid, log: path.join(directory, "run.log") };
}

export async function start(project, phase, scenes = "") {
  if (process.platform === "win32") throw new Error("Detached review jobs require POSIX process groups; use review-project.mjs in a persistent Windows session.");
  if (!phases.has(phase)) throw new Error("Choose preflight, static, preview, or release.");
  if (!fs.existsSync(path.join(project, "index.html"))) throw new Error("Missing project index.html.");
  const jobId = crypto.randomUUID();
  const { directory, lock } = locations(project, jobId);
  fs.mkdirSync(path.dirname(lock), { recursive: true });
  const request = { jobId, project, phase, scenes };
  const acquire = () => {
    const temporary = `${lock}.${jobId}.tmp`;
    fs.writeFileSync(temporary, JSON.stringify(request));
    try { fs.linkSync(temporary, lock); }
    finally { fs.unlinkSync(temporary); }
  };
  try { acquire(); }
  catch (error) {
    if (error.code !== "EEXIST") throw error;
    const existing = readJson(lock);
    const current = status(project, existing.jobId);
    if (!terminal.has(current.status)) {
      if (existing.phase === phase && existing.scenes === scenes) return { ...current, reused: true };
      throw new Error(`Review ${existing.jobId} (${existing.phase}) is still active. Read its status/log before starting ${phase}.`);
    }
    unlock(project, existing.jobId);
    acquire();
  }

  let logFd;
  try {
    fs.mkdirSync(directory, { recursive: true });
    writeJson(path.join(directory, "request.json"), request);
    writeJson(path.join(directory, "status.json"), { ...request, status: "starting", startedAt: new Date().toISOString() });
    logFd = fs.openSync(path.join(directory, "run.log"), "a");
    const child = spawn(process.execPath, [scriptPath, "worker", "--project", project, "--job", jobId], {
      cwd: project, detached: true, stdio: ["ignore", logFd, logFd],
    });
    await new Promise((resolve, reject) => { child.once("spawn", resolve); child.once("error", reject); });
    fs.writeFileSync(path.join(directory, "pid"), String(child.pid));
    child.unref();
    return status(project, jobId);
  } catch (error) {
    writeJson(path.join(directory, "status.json"), { ...request, status: "failed", completedAt: new Date().toISOString(), error: error.message });
    unlock(project, jobId);
    throw error;
  } finally {
    if (logFd !== undefined) fs.closeSync(logFd);
  }
}

function worker(project, jobId) {
  const { directory } = locations(project, jobId);
  const request = readJson(path.join(directory, "request.json"));
  const started = Date.now();
  const base = { ...request, pid: process.pid, startedAt: new Date(started).toISOString() };
  writeJson(path.join(directory, "status.json"), { ...base, status: "running" });
  try {
    const argv = ["--project", project, "--phase", request.phase];
    if (request.scenes) argv.push("--scenes", request.scenes);
    const report = review(argv);
    const reportFile = path.join(directory, "report.json");
    writeJson(reportFile, report);
    writeJson(path.join(directory, "status.json"), {
      ...base, status: report.ok ? "passed" : "failed", completedAt: new Date().toISOString(),
      durationMs: Date.now() - started, report: reportFile, errors: report.errors,
    });
  } catch (error) {
    console.error(error.stack || error.message);
    writeJson(path.join(directory, "status.json"), { ...base, status: "failed", completedAt: new Date().toISOString(), durationMs: Date.now() - started, error: error.message });
    process.exitCode = 1;
  } finally {
    unlock(project, jobId);
  }
}

async function cli(argv) {
  const [command, ...rest] = argv;
  if (command === "--help" || command === "-h" || !command) {
    console.log("Usage:\n  node review-job.mjs start --project DIR --phase preflight|static|preview|release [--scenes id,id]\n  node review-job.mjs status --project DIR --job JOB_ID\n\nStart returns a local job ID immediately. Repeated starts reuse the same active check; another phase must wait. Read status and the job log after interruption; no check or cloud render is retried automatically.");
    return;
  }
  const args = {};
  for (let index = 0; index < rest.length; index += 2) {
    if (!["--project", "--phase", "--scenes", "--job"].includes(rest[index]) || !rest[index + 1]) throw new Error("Invalid arguments; see --help.");
    args[rest[index].slice(2)] = rest[index + 1];
  }
  if (!args.project) throw new Error("--project is required.");
  const project = path.resolve(args.project);
  if (command === "worker") return worker(project, args.job);
  const result = command === "start" ? await start(project, args.phase, args.scenes) : command === "status" ? status(project, args.job) : null;
  if (!result) throw new Error("Choose start or status.");
  console.log(JSON.stringify(result, null, 2));
  if (["failed", "interrupted"].includes(result.status)) process.exitCode = 1;
}

if (import.meta.url === pathToFileURL(path.resolve(process.argv[1] || "")).href) {
  cli(process.argv.slice(2)).catch(error => { console.error(`review job failed: ${error.message}`); process.exitCode = 1; });
}
