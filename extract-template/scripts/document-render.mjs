import { spawnSync } from "node:child_process";
import { mkdtemp, readdir, rm, stat } from "node:fs/promises";
import { extname, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

import {
  ensureLibreOfficeWriter,
  ensurePoppler,
} from "../presentation/scripts/libreoffice.mjs";

const WORD_EXTENSIONS = [".doc", ".docx"];
const MAX_SOURCE_BYTES = 100 * 1024 * 1024;
const PDF_FILTER = `pdf:writer_pdf_Export:${JSON.stringify({
  ExportFormFields: { type: "boolean", value: "false" },
  // Supplying filter data resets omitted options; preserve Writer's image quality.
  Quality: { type: "long", value: "90" },
})}`;

export function run(command, args) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    env: { ...process.env, LC_ALL: "C" },
    timeout: 180_000,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    throw new Error(`${command} failed (${result.status}): ${result.stderr?.trim() ?? ""}`);
  }
  return result.stdout;
}

export function describePdf(pdfinfo, pdf, word = false) {
  const info = run(pdfinfo, [pdf]);
  const pages = Number(info.match(/^Pages:\s+(\d+)/mu)?.[1]);
  if (!Number.isInteger(pages) || pages < 1) {
    throw new Error("pdfinfo reported no pages");
  }
  const form = info.match(/^Form:\s+(.*)$/mu)?.[1]?.trim();
  if (word && form !== "none") {
    throw new Error(`Word export must contain no form fields; pdfinfo Form: ${form ?? "missing"}`);
  }
  return { pages, form };
}

/** Keep the PDF alive until the caller has rendered or copied it. */
export async function withDocumentPdf(input, scratchRoot, consume) {
  const source = resolve(input);
  const extension = extname(source).toLowerCase();
  if (![...WORD_EXTENSIONS, ".pdf"].includes(extension)) {
    throw new Error(`Unsupported input extension: ${extension || "none"}`);
  }
  const info = await stat(source);
  if (!info.isFile() || info.size > MAX_SOURCE_BYTES) {
    throw new Error("Source must be a file of at most 100 MiB");
  }
  const word = WORD_EXTENSIONS.includes(extension);
  const setup = word
    ? await ensureLibreOfficeWriter({ scratchRoot })
    : await ensurePoppler({ scratchRoot });
  let scratch;
  try {
    let pdf = source;
    if (word) {
      scratch = await mkdtemp(join(scratchRoot, ".prt-document-"));
      run(setup.soffice, [
        "--headless",
        `-env:UserInstallation=${pathToFileURL(join(scratch, "profile")).href}`,
        "--convert-to", PDF_FILTER,
        "--outdir", scratch,
        source,
      ]);
      const produced = (await readdir(scratch)).find((name) => name.endsWith(".pdf"));
      if (!produced) throw new Error("soffice produced no PDF from the Word document");
      pdf = join(scratch, produced);
    }
    const { pages } = describePdf(setup.pdfinfo, pdf, word);
    return await consume({ pdf, pages, setup });
  } finally {
    if (scratch) await rm(scratch, { recursive: true, force: true });
  }
}

export function renderPage(pdftocairo, pdf, page, out, width = 1000) {
  run(pdftocairo, [
    "-png", "-f", String(page), "-l", String(page), "-singlefile",
    "-scale-to-x", String(width), "-scale-to-y", "-1",
    pdf, out.slice(0, -".png".length),
  ]);
}
