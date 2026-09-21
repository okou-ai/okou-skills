/** Render every document page at its own aspect ratio, retaining the PDF for analysis. */
import { copyFile, mkdir, readdir, stat } from "node:fs/promises";
import { join, resolve } from "node:path";
import { renderPage, withDocumentPdf } from "./document-render.mjs";

const args = {};
for (let i = 2; i < process.argv.length; i += 2) {
  args[process.argv[i]] = process.argv[i + 1];
}
if (!args["--input"] || !args["--out"]) {
  console.error("Usage: node render-document.mjs --input <source.docx|source.doc|source.pdf> --out <new directory>");
  process.exit(2);
}

try {
  const out = resolve(args["--out"]);
  await mkdir(out, { recursive: true });
  if ((await readdir(out)).length) throw new Error("Output directory must be empty; use a new directory for this render");
  const result = await withDocumentPdf(args["--input"], out, async ({ pdf, pages, setup }) => {
    const retainedPdf = join(out, "document.pdf");
    await copyFile(pdf, retainedPdf);
    const images = [];
    for (let page = 1; page <= pages; page += 1) {
      const image = join(out, `page-${String(page).padStart(3, "0")}.png`);
      renderPage(setup.pdftocairo, pdf, page, image);
      await stat(image);
      images.push(image);
    }
    return { pdf: retainedPdf, images, pageCount: pages, width: 1000, installedPackages: setup.packages ?? [] };
  });
  console.log(JSON.stringify(result, null, 2));
} catch (error) {
  console.error(`Document render failed: ${error.message}`);
  process.exitCode = 1;
}
