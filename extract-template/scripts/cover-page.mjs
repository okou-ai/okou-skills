/** Render a document's first page for the Custom catalog and count all pages. */
import { mkdir, stat } from "node:fs/promises";
import { dirname, extname, resolve } from "node:path";
import { renderPage, withDocumentPdf } from "./document-render.mjs";

const args = {};
for (let i = 2; i < process.argv.length; i += 2) {
  args[process.argv[i]] = process.argv[i + 1];
}
if (!args["--input"] || !args["--out"]) {
  console.error("Usage: node cover-page.mjs --input <source.docx|source.doc|source.pdf> --out <cover.png>");
  process.exit(2);
}
if (extname(args["--out"]).toLowerCase() !== ".png") {
  console.error("--out must end in .png");
  process.exit(2);
}

try {
  const out = resolve(args["--out"]);
  await mkdir(dirname(out), { recursive: true });
  const result = await withDocumentPdf(args["--input"], dirname(out), async ({ pdf, pages, setup }) => {
    renderPage(setup.pdftocairo, pdf, 1, out);
    await stat(out);
    return { cover: args["--out"], pageCount: pages, width: 1000, installedPackages: setup.packages ?? [] };
  });
  console.log(JSON.stringify(result, null, 2));
} catch (error) {
  console.error(`Cover render failed: ${error.message}`);
  process.exitCode = 1;
}
