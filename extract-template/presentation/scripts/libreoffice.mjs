#!/usr/bin/env node
/**
 * libreoffice.mjs — install document tools on demand and convert legacy PPT.
 *
 * PDF rendering requires Poppler. PPTX rendering and legacy PPT conversion
 * additionally require LibreOffice 24.2.2.2 with Impress; rendering a Word
 * document needs the same LibreOffice with Writer. Missing tools are installed
 * through apt only when needed. apt downloads and temporary files use the
 * writable filesystem with the most free space rather than filling the
 * sandbox root filesystem.
 *
 *   node scripts/libreoffice.mjs --ensure
 *   node scripts/libreoffice.mjs --ensure-writer
 *   node scripts/libreoffice.mjs --ensure-poppler
 *   node scripts/libreoffice.mjs --input old.ppt --out converted.pptx
 */
import { accessSync, constants, realpathSync } from "node:fs";
import {
  chmod,
  copyFile,
  mkdir,
  mkdtemp,
  readdir,
  rename,
  rm,
  stat,
  statfs,
} from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

export const LIBREOFFICE_VERSION = "24.2.2.2";

const LIBREOFFICE_APT_SERIES = "24.2.2";
const MAX_SOURCE_BYTES = 100 * 1024 * 1024;
const MIN_SCRATCH_BYTES = 512 * 1024 * 1024;
const POPPLER_TOOLS = ["pdftocairo", "pdfinfo", "pdftohtml", "pdffonts"];

/**
 * The filter each document kind is converted by, and the file that proves it
 * is installed.
 *
 * `soffice` on PATH does not mean a given format can be converted: the launcher
 * ships with `libreoffice-core`, and each filter is a separate package that
 * drops its own library beside it. A sandbox with Impress and no Writer answers
 * every `soffice` probe and then converts a `.docx` to nothing, which is the
 * failure this map exists to turn into an install.
 */
const LIBREOFFICE_COMPONENTS = {
  impress: { package: "libreoffice-impress", library: "libsdlo.so" },
  writer: { package: "libreoffice-writer", library: "libswlo.so" },
};

/** Whether the filter library sits in the program directory `soffice` runs from. */
function hasComponent(soffice, component) {
  if (!soffice) return false;
  const { library } = LIBREOFFICE_COMPONENTS[component];
  try {
    accessSync(
      path.join(path.dirname(realpathSync(soffice)), library),
      constants.F_OK,
    );
    return true;
  } catch {
    return false;
  }
}

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    maxBuffer: 64 * 1024 * 1024,
    timeout: 5 * 60 * 1000,
    ...options,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    const detail = [result.stdout, result.stderr].filter(Boolean).join("\n").trim();
    throw new Error(`${command} failed (${result.status})${detail ? `: ${detail}` : ""}`);
  }
  return result.stdout.trim();
}

function findExecutable(command) {
  if (command.includes(path.sep)) {
    const resolved = path.resolve(command);
    try {
      accessSync(resolved, constants.X_OK);
      return resolved;
    } catch {
      return "";
    }
  }
  const searchPath = process.env.PRT_TOOL_PATH || process.env.PATH || "";
  for (const directory of searchPath.split(path.delimiter)) {
    if (!directory) continue;
    const candidate = path.join(directory, command);
    try {
      accessSync(candidate, constants.X_OK);
      return candidate;
    } catch {
      // Keep searching PATH.
    }
  }
  return "";
}

function assertPinnedVersion(soffice) {
  const output = run(soffice, ["--version"]);
  const reported = output.match(/LibreOffice\s+(\S+)/iu)?.[1] || "";
  if (reported !== LIBREOFFICE_VERSION) {
    throw new Error(`Expected LibreOffice ${LIBREOFFICE_VERSION}, got: ${output || "no version output"}`);
  }
  return output;
}

function resolvePopplerTools() {
  return Object.fromEntries(POPPLER_TOOLS.map((tool) => [tool, findExecutable(tool)]));
}

function missingPopplerTools(poppler) {
  return POPPLER_TOOLS.filter((tool) => !poppler[tool]);
}

function aptCandidate(output, packageName) {
  const candidate = output.match(/^\s*Candidate:\s*(\S+)/imu)?.[1] || "";
  if (!candidate || candidate === "(none)") {
    throw new Error(`apt has no ${packageName} candidate`);
  }
  return candidate;
}

function isPinnedAptCandidate(candidate) {
  const version = candidate.replace(/^\d+:/u, "");
  const prefixes = [LIBREOFFICE_VERSION, LIBREOFFICE_APT_SERIES];
  return prefixes.some(
    (prefix) => version === prefix
      || version.startsWith(`${prefix}-`)
      || version.startsWith(`${prefix}+`)
      || version.startsWith(`${prefix}~`),
  );
}

async function selectScratchRoot(hint = "") {
  const forced = process.env.PRT_SYSTEM_SCRATCH;
  const rawCandidates = forced
    ? [forced]
    : [hint, process.cwd(), os.tmpdir()];
  const candidates = [
    ...new Set(rawCandidates.filter(Boolean).map((item) => path.resolve(item))),
  ];
  let selected = null;
  for (const directory of candidates) {
    try {
      await mkdir(directory, { recursive: true });
      const filesystem = await statfs(directory);
      const available = Number(filesystem.bavail) * Number(filesystem.bsize);
      if (!selected || available > selected.available) selected = { directory, available };
    } catch {
      // Try the next writable candidate.
    }
  }
  if (!selected) throw new Error("No writable scratch filesystem is available for document tool setup");
  if (selected.available < MIN_SCRATCH_BYTES) {
    throw new Error(
      `Only ${Math.floor(selected.available / 1048576)} MiB is free at ${selected.directory}; document tool setup needs at least 512 MiB`,
    );
  }
  return selected.directory;
}

function aptTools() {
  const aptGetOverride = process.env.PRT_APT_GET_BIN || "";
  const aptCacheOverride = process.env.PRT_APT_CACHE_BIN || "";
  if (Boolean(aptGetOverride) !== Boolean(aptCacheOverride)) {
    throw new Error("PRT_APT_GET_BIN and PRT_APT_CACHE_BIN must be provided together");
  }
  const aptGet = aptGetOverride
    ? path.resolve(aptGetOverride)
    : findExecutable("apt-get");
  const aptCache = aptCacheOverride
    ? path.resolve(aptCacheOverride)
    : findExecutable("apt-cache");
  if (!aptGet || !aptCache) throw new Error("apt-get and apt-cache are required to install document tools");

  const mocked = Boolean(aptGetOverride);
  const isRoot = typeof process.getuid === "function" && process.getuid() === 0;
  let sudo = "";
  if (!mocked && !isRoot) {
    sudo = findExecutable("sudo");
    if (!sudo || spawnSync(sudo, ["-n", "true"], { encoding: "utf8" }).status !== 0) {
      throw new Error("Document tool setup requires root or passwordless sudo for apt");
    }
  }
  return { aptGet, aptCache, sudo };
}

function runApt(binary, args, environment, sudo = "") {
  if (!sudo) return run(binary, args, { env: environment });
  return run(sudo, [
    "-n",
    "env",
    `DEBIAN_FRONTEND=${environment.DEBIAN_FRONTEND}`,
    `TMPDIR=${environment.TMPDIR}`,
    binary,
    ...args,
  ], { env: environment });
}

async function makeAptScratch(scratchRoot) {
  const directory = await mkdtemp(path.join(scratchRoot, ".prt-apt-"));
  const archives = path.join(directory, "archives");
  const lists = path.join(directory, "lists");
  const temporary = path.join(directory, "tmp");
  const directories = [
    archives,
    path.join(archives, "partial"),
    lists,
    path.join(lists, "partial"),
    path.join(lists, "auxfiles"),
    temporary,
  ];
  for (const item of directories) {
    await mkdir(item, { recursive: true });
    await chmod(item, 0o700);
  }
  return { directory, archives, lists, temporary };
}

async function removeAptScratch(directory, sudo) {
  if (!path.basename(directory).startsWith(".prt-apt-")) {
    throw new Error(`Refusing to remove unexpected apt scratch path: ${directory}`);
  }
  try {
    await rm(directory, { recursive: true, force: true });
  } catch (error) {
    if (!sudo) throw error;
    run(sudo, ["-n", "rm", "-rf", "--", directory]);
  }
}

async function ensureDocumentTools({ component, scratchRoot = "" }) {
  const libreOffice = Boolean(component);
  let soffice = "";
  let version = "";
  let source = "system";
  if (libreOffice) {
    if (process.env.PRT_SOFFICE) {
      soffice = path.resolve(process.env.PRT_SOFFICE);
      source = "PRT_SOFFICE";
    } else {
      soffice = findExecutable("soffice");
    }
    if (soffice) version = assertPinnedVersion(soffice);
  }
  // The filter, not the launcher, is what decides whether this conversion can
  // run, so a `soffice` that cannot open the format still needs an install.
  const libreOfficeNeedsInstall =
    libreOffice && (!soffice || !hasComponent(soffice, component));
  let poppler = resolvePopplerTools();
  let missingPoppler = missingPopplerTools(poppler);
  if (!libreOfficeNeedsInstall && !missingPoppler.length) {
    return {
      soffice,
      version,
      ...poppler,
      installed: false,
      source,
      packages: [],
    };
  }
  if (process.platform !== "linux") {
    throw new Error(`Automatic document tool setup requires Linux; found ${process.platform}/${process.arch}`);
  }

  const tools = aptTools();
  const root = await selectScratchRoot(scratchRoot);
  const scratch = await makeAptScratch(root);
  const aptOptions = [
    "-o", `Dir::Cache::archives=${scratch.archives}`,
    "-o", `Dir::State::lists=${scratch.lists}`,
    "-o", "APT::Keep-Downloaded-Packages=false",
    "-o", "APT::Sandbox::User=root",
  ];
  const environment = {
    ...process.env,
    DEBIAN_FRONTEND: "noninteractive",
    TMPDIR: scratch.temporary,
  };

  try {
    process.stderr.write("document tool helper: refreshing apt metadata\n");
    runApt(tools.aptGet, [...aptOptions, "update"], environment, tools.sudo);
    const packages = [];
    if (libreOfficeNeedsInstall) {
      const componentPackage = LIBREOFFICE_COMPONENTS[component].package;
      const policy = runApt(
        tools.aptCache,
        [...aptOptions, "policy", componentPackage],
        environment,
      );
      const candidate = aptCandidate(policy, componentPackage);
      if (!isPinnedAptCandidate(candidate)) {
        throw new Error(
          `apt ${componentPackage} candidate ${candidate} does not provide LibreOffice ${LIBREOFFICE_VERSION}`,
        );
      }
      packages.push(`${componentPackage}=${candidate}`);
    }
    if (missingPoppler.length) packages.push("poppler-utils");

    if (packages.length) {
      process.stderr.write(`document tool helper: apt installing ${packages.join(" ")}\n`);
      runApt(tools.aptGet, [
        ...aptOptions,
        "install",
        "-y",
        "--no-install-recommends",
        ...packages,
      ], environment, tools.sudo);
    }

    if (libreOfficeNeedsInstall && !soffice) soffice = findExecutable("soffice");
    if (libreOffice && !soffice) throw new Error("apt completed but soffice is still unavailable");
    if (libreOfficeNeedsInstall && !hasComponent(soffice, component)) {
      throw new Error(
        `apt completed but LibreOffice ${component} is still unavailable`,
      );
    }
    if (libreOffice) version = assertPinnedVersion(soffice);
    poppler = resolvePopplerTools();
    missingPoppler = missingPopplerTools(poppler);
    if (missingPoppler.length) {
      throw new Error(`apt completed but Poppler tools are still unavailable: ${missingPoppler.join(", ")}`);
    }
    return {
      soffice,
      version,
      ...poppler,
      installed: packages.length > 0,
      source: libreOffice
        ? (libreOfficeNeedsInstall ? "apt" : source)
        : (packages.length ? "apt" : "system"),
      packages,
    };
  } finally {
    await removeAptScratch(scratch.directory, tools.sudo);
  }
}

export async function ensurePoppler({ scratchRoot = "" } = {}) {
  return ensureDocumentTools({ component: "", scratchRoot });
}

export async function ensureLibreOffice({ scratchRoot = "" } = {}) {
  return ensureDocumentTools({ component: "impress", scratchRoot });
}

export async function ensureLibreOfficeWriter({ scratchRoot = "" } = {}) {
  return ensureDocumentTools({ component: "writer", scratchRoot });
}

async function assertPptx(file) {
  const listing = run("unzip", ["-Z1", file]);
  if (!/^ppt\/presentation\.xml$/mu.test(listing)) {
    throw new Error(`LibreOffice did not produce a readable PPTX: ${file}`);
  }
}

export async function convertLegacyPpt(inputFile, outputFile) {
  const input = path.resolve(inputFile);
  const output = path.resolve(outputFile);
  if (path.extname(output).toLowerCase() !== ".pptx") {
    throw new Error(`Legacy conversion output must end in .pptx: ${output}`);
  }
  const info = await stat(input);
  if (!info.isFile()) throw new Error(`Legacy PPT is not a file: ${input}`);
  if (info.size > MAX_SOURCE_BYTES) {
    throw new Error(`Legacy PPT is ${info.size} bytes; the limit is ${MAX_SOURCE_BYTES}`);
  }

  await mkdir(path.dirname(output), { recursive: true });
  const scratchRoot = await selectScratchRoot(path.dirname(output));
  const office = await ensureLibreOffice({ scratchRoot });
  const conversionDir = await mkdtemp(path.join(scratchRoot, ".prt-ppt-convert-"));
  const profileDir = await mkdtemp(path.join(scratchRoot, ".prt-lo-profile-"));
  const partialOutput = `${output}.part-${process.pid}`;
  try {
    run(office.soffice, [
      `-env:UserInstallation=${pathToFileURL(profileDir).href}`,
      "--headless",
      "--convert-to", "pptx",
      "--outdir", conversionDir,
      input,
    ], {
      env: { ...process.env, TMPDIR: scratchRoot },
    });
    const produced = (await readdir(conversionDir))
      .find((name) => path.extname(name).toLowerCase() === ".pptx");
    if (!produced) throw new Error("LibreOffice produced no PPTX");
    const converted = path.join(conversionDir, produced);
    await assertPptx(converted);
    await copyFile(converted, partialOutput);
    await rename(partialOutput, output);
    return {
      input,
      output,
      libreOfficeVersion: LIBREOFFICE_VERSION,
      libreOfficeSource: office.source,
      installed: office.installed,
      packages: office.packages,
      soffice: office.soffice,
      pdftocairo: office.pdftocairo,
    };
  } finally {
    await rm(partialOutput, { force: true });
    await rm(conversionDir, { recursive: true, force: true });
    await rm(profileDir, { recursive: true, force: true });
  }
}

function parseArgs(argv) {
  const args = { ensure: "", input: "", out: "" };
  for (let index = 2; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--ensure") args.ensure = "libreoffice";
    else if (arg === "--ensure-writer") args.ensure = "writer";
    else if (arg === "--ensure-poppler") args.ensure = "poppler";
    else if (arg === "--input") args.input = argv[++index];
    else if (arg === "--out") args.out = argv[++index];
    else if (arg === "--help" || arg === "-h") {
      console.log("Usage: node scripts/libreoffice.mjs --ensure | --ensure-writer | --ensure-poppler | --input <deck.ppt> --out <deck.pptx>");
      process.exit(0);
    } else throw new Error(`Unknown argument: ${arg}`);
  }
  if (!args.ensure && (!args.input || !args.out)) {
    throw new Error("Legacy conversion requires both --input and --out");
  }
  return args;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  const args = parseArgs(process.argv);
  try {
    const result = args.ensure === "libreoffice"
      ? await ensureLibreOffice()
      : args.ensure === "writer"
        ? await ensureLibreOfficeWriter()
        : args.ensure === "poppler"
          ? await ensurePoppler()
          : await convertLegacyPpt(args.input, args.out);
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error(error.stack || error.message);
    process.exit(1);
  }
}
