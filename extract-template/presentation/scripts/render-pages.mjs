/**
 * render-pages.mjs — turn a PPT, PPTX, or PDF into ordered page PNGs.
 *
 *   node scripts/render-pages.mjs --input <deck.ppt|deck.pptx|deck.pdf> --out <pages-dir>
 *
 * This produces the ordered source-page images an AI inspects and the template
 * publishing command uploads.
 *
 * Missing system tools are installed through apt only when the input needs
 * them: PDF needs Poppler; PPTX and PPT need LibreOffice 24.2.2.2 plus
 * Poppler. Every page lands on a fixed 1600x900 surface so pages stay
 * comparable.
 */
import { spawnSync } from "node:child_process";
import {
  mkdir,
  mkdtemp,
  readdir,
  rename,
  rm,
  stat,
} from "node:fs/promises";
import { basename, extname, join, resolve } from "node:path";

import {
  convertLegacyPpt,
  ensureLibreOffice,
  ensurePoppler,
} from "./libreoffice.mjs";

const WIDTH = 1600;
const HEIGHT = 900;
const MAX_PAGES = 100;
const MAX_SOURCE_BYTES = 100 * 1024 * 1024;

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i]?.replace(/^--/u, "");
    if (key) {
      args[key] = argv[i + 1];
    }
  }
  return args;
}

function run(command, commandArgs) {
  const result = spawnSync(command, commandArgs, { encoding: "utf8" });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    throw new Error(
      `${command} failed (${result.status}): ${result.stderr?.trim() ?? ""}`,
    );
  }
  return result.stdout;
}

async function renderWithSystemTools(input, outDir, kind, tools) {
  let pdf = input;
  let pdfDirectory = "";
  try {
    if (kind === "pptx") {
      pdfDirectory = await mkdtemp(join(outDir, ".prt-render-pdf-"));
      run(tools.soffice, [
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        pdfDirectory,
        input,
      ]);
      const produced = (await readdir(pdfDirectory)).find((name) => {
        return name.endsWith(".pdf");
      });
      if (!produced) {
        throw new Error("soffice produced no PDF");
      }
      pdf = join(pdfDirectory, produced);
    }
    run(tools.pdftocairo, [
      "-png",
      "-r",
      "150",
      "-scale-to-x",
      String(WIDTH),
      "-scale-to-y",
      String(HEIGHT),
      pdf,
      join(outDir, "page"),
    ]);
  } finally {
    if (pdfDirectory) await rm(pdfDirectory, { recursive: true, force: true });
  }
  const pages = (await readdir(outDir))
    .map((name) => ({
      name,
      page: Number(name.match(/^page-(\d+)\.png$/u)?.[1]),
    }))
    .filter((item) => Number.isInteger(item.page))
    .sort((left, right) => left.page - right.page);
  if (!pages.length) throw new Error("pdftocairo produced no page PNGs");
  for (let index = 0; index < pages.length; index += 1) {
    const staged = `.page-normalize-${process.pid}-${index}.png`;
    await rename(join(outDir, pages[index].name), join(outDir, staged));
    pages[index].staged = staged;
  }
  for (let index = 0; index < pages.length; index += 1) {
    const finalName = `page-${String(index + 1).padStart(3, "0")}.png`;
    await rename(join(outDir, pages[index].staged), join(outDir, finalName));
  }
  return { pages: pages.length, degraded: [], method: "system" };
}

const args = parseArgs(process.argv.slice(2));
if (!args.input || !args.out) {
  console.error(
    "Usage: node scripts/render-pages.mjs --input <deck.ppt|deck.pptx|deck.pdf> --out <pages-dir>",
  );
  process.exit(2);
}

const source = resolve(args.input);
const outDir = resolve(args.out);

const info = await stat(source);
if (info.size > MAX_SOURCE_BYTES) {
  console.error(`Source is ${info.size} bytes; the limit is ${MAX_SOURCE_BYTES}`);
  process.exit(1);
}

await mkdir(outDir, { recursive: true });
for (const name of await readdir(outDir)) {
  if (/^page-\d+\.png$/u.test(name)) await rm(join(outDir, name), { force: true });
}

let input = source;
let temporary = "";
let conversion = null;
let setup = null;
let result = null;
try {
  const sourceExtension = extname(source).toLowerCase();
  if (![".ppt", ".pptx", ".pdf"].includes(sourceExtension)) {
    throw new Error(`Unsupported input extension: ${sourceExtension || "none"}`);
  }
  if (sourceExtension === ".ppt") {
    temporary = await mkdtemp(join(outDir, ".prt-ppt-render-"));
    input = join(temporary, `${basename(source, sourceExtension)}.pptx`);
    conversion = await convertLegacyPpt(source, input);
    setup = {
      soffice: conversion.soffice,
      pdftocairo: conversion.pdftocairo,
      source: conversion.libreOfficeSource,
      packages: conversion.packages,
    };
  }
  const kind = extname(input).toLowerCase() === ".pdf" ? "pdf" : "pptx";
  if (!setup) {
    setup = kind === "pdf"
      ? await ensurePoppler({ scratchRoot: outDir })
      : await ensureLibreOffice({ scratchRoot: outDir });
  }
  result = await renderWithSystemTools(input, outDir, kind, setup);
} catch (error) {
  if (temporary) await rm(temporary, { recursive: true, force: true });
  console.error(`Render failed: ${error.message}`);
  process.exit(1);
}
if (temporary) await rm(temporary, { recursive: true, force: true });

if (result.pages > MAX_PAGES) {
  console.error(`Rendered ${result.pages} pages; the limit is ${MAX_PAGES}`);
  process.exit(1);
}

console.log(
  JSON.stringify(
    {
      pages: result.pages,
      width: WIDTH,
      height: HEIGHT,
      method: result.method,
      installedPackages: setup.packages ?? [],
      ...(conversion ? {
        convertedFrom: "ppt",
        libreOfficeVersion: conversion.libreOfficeVersion,
      } : {}),
      // System conversion cannot identify unsupported shapes individually.
      degraded: result.degraded,
    },
    null,
    2,
  ),
);
