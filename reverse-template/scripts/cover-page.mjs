/**
 * cover-page.mjs — render a document's first page and count its pages.
 *
 *   node ../scripts/cover-page.mjs --input <source.docx|source.doc|source.pdf> --out cover.png
 *
 * This produces the picture the Custom catalog shows for a document template
 * and the page count that decides whether it draws a stack of sheets behind
 * it. Both are passed to `okou user-template publish` as `--cover` and
 * `--page-count`.
 *
 * Shared by the `docx/` and `pdf/` branches because both answer the same two
 * questions about their source, and because the apt provisioning it reuses
 * from `presentation/scripts/libreoffice.mjs` should exist once.
 *
 * Missing system tools are installed through apt only when the input needs
 * them: PDF needs Poppler; Word needs LibreOffice 24.2.2.2 with Writer, which
 * a sandbox carrying only Impress does not have.
 */
import { spawnSync } from "node:child_process";
import { mkdtemp, readdir, rm, stat } from "node:fs/promises";
import { dirname, extname, join, resolve } from "node:path";

import {
  ensureLibreOfficeWriter,
  ensurePoppler,
} from "../presentation/scripts/libreoffice.mjs";

// Wide enough that the catalog tile, which draws the page at about 190 CSS
// pixels, still has a full retina pixel budget and room to spare. Larger only
// buys bytes: nothing renders this picture bigger than a tile.
const WIDTH = 1000;
const MAX_SOURCE_BYTES = 100 * 1024 * 1024;
const WORD_EXTENSIONS = [".doc", ".docx"];

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

/** Convert a Word document to PDF so one renderer answers for both inputs. */
async function wordToPdf(source, soffice, scratch) {
  run(soffice, [
    "--headless",
    "--convert-to",
    "pdf",
    "--outdir",
    scratch,
    source,
  ]);
  const produced = (await readdir(scratch)).find((name) => {
    return name.endsWith(".pdf");
  });
  if (!produced) {
    // Writer converts to nothing rather than failing when its filter is
    // absent, so a silent success is the shape this error has to catch.
    throw new Error("soffice produced no PDF from the Word document");
  }
  return join(scratch, produced);
}

function pageCountOf(pdfinfo, pdf) {
  const pages = Number(run(pdfinfo, [pdf]).match(/^Pages:\s+(\d+)/mu)?.[1]);
  if (!Number.isInteger(pages) || pages < 1) {
    throw new Error("pdfinfo reported no pages");
  }
  return pages;
}

const args = parseArgs(process.argv.slice(2));
if (!args.input || !args.out) {
  console.error(
    "Usage: node ../scripts/cover-page.mjs --input <source.docx|source.doc|source.pdf> --out <cover.png>",
  );
  process.exit(2);
}

const source = resolve(args.input);
const out = resolve(args.out);
if (extname(out).toLowerCase() !== ".png") {
  console.error(`--out must end in .png; got ${args.out}`);
  process.exit(2);
}

const extension = extname(source).toLowerCase();
if (![...WORD_EXTENSIONS, ".pdf"].includes(extension)) {
  console.error(`Unsupported input extension: ${extension || "none"}`);
  process.exit(1);
}

const info = await stat(source).catch(() => null);
if (!info) {
  console.error(`Source not found: ${source}`);
  process.exit(1);
}
if (info.size > MAX_SOURCE_BYTES) {
  console.error(`Source is ${info.size} bytes; the limit is ${MAX_SOURCE_BYTES}`);
  process.exit(1);
}

const word = WORD_EXTENSIONS.includes(extension);
const outDir = dirname(out);
let scratch = "";
let result = null;
let setup = null;
try {
  setup = word
    ? await ensureLibreOfficeWriter({ scratchRoot: outDir })
    : await ensurePoppler({ scratchRoot: outDir });
  let pdf = source;
  if (word) {
    scratch = await mkdtemp(join(outDir, ".prt-cover-pdf-"));
    pdf = await wordToPdf(source, setup.soffice, scratch);
  }
  const pageCount = pageCountOf(setup.pdfinfo, pdf);
  // `-scale-to-y -1` keeps the page's own proportions, so a Letter source is
  // not squared into A4 and the catalog crops it rather than distorting it.
  run(setup.pdftocairo, [
    "-png",
    "-f", "1",
    "-l", "1",
    "-singlefile",
    "-scale-to-x", String(WIDTH),
    "-scale-to-y", "-1",
    pdf,
    out.slice(0, -".png".length),
  ]);
  await stat(out);
  result = { cover: args.out, pageCount };
} catch (error) {
  console.error(`Cover render failed: ${error.message}`);
  process.exit(1);
} finally {
  if (scratch) await rm(scratch, { recursive: true, force: true });
}

console.log(
  JSON.stringify(
    {
      ...result,
      width: WIDTH,
      installedPackages: setup.packages ?? [],
    },
    null,
    2,
  ),
);
