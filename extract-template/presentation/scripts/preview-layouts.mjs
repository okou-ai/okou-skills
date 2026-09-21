#!/usr/bin/env node
import { readFile, writeFile, realpath, lstat } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const begin = "<!-- BEGIN SLIDES -->";
const end = "<!-- END SLIDES -->";

async function readPackageFile(root, relative) {
  const resolved = await realpath(path.join(root, relative));
  if (!resolved.startsWith(root + path.sep)) {
    throw new Error(`Package file resolves outside the package: ${relative}`);
  }
  return readFile(resolved, "utf8");
}

export async function previewLayouts(packageDir) {
  const root = await realpath(packageDir);
  const catalog = JSON.parse(await readPackageFile(root, "layouts/common/catalog.json"));
  if (catalog.version !== 1 || !Array.isArray(catalog.layouts) || !catalog.layouts.length) {
    throw new Error("Expected a version 1 common-layout catalog with layouts.");
  }
  const shell = await readPackageFile(root, "layouts/_shell.html");
  if (shell.split(begin).length !== 2 || shell.split(end).length !== 2 || shell.indexOf(begin) > shell.indexOf(end)) {
    throw new Error("The package shell must contain one ordered BEGIN SLIDES / END SLIDES marker pair.");
  }
  const chrome = await readPackageFile(root, "layouts/chrome.html");
  const slides = [];
  const seen = new Set();
  for (const layout of catalog.layouts) {
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(layout.id) || layout.file !== `${layout.id}.html` || seen.has(layout.id)) {
      throw new Error(`Invalid or duplicate common layout: ${layout.id}`);
    }
    seen.add(layout.id);
    const fragment = await readPackageFile(root, `layouts/common/${layout.file}`);
    slides.push(`<section class="slide" aria-label="${layout.id}"><div class="stage pl-stage" data-layout="${layout.id}">\n${chrome}\n${fragment}\n</div></section>`);
  }
  const html = shell.slice(0, shell.indexOf(begin) + begin.length) + "\n" + slides.join("\n") + "\n" + shell.slice(shell.indexOf(end));
  const layoutsDir = await realpath(path.join(root, "layouts"));
  if (!layoutsDir.startsWith(root + path.sep)) throw new Error("The layouts directory resolves outside the package.");
  const output = path.join(layoutsDir, "preview.html");
  const existing = await lstat(output).catch(error => {
    if (error.code !== "ENOENT") throw error;
    return null;
  });
  if (existing && !existing.isFile()) throw new Error("Refusing to replace a non-file or symlink at layouts/preview.html.");
  await writeFile(output, html);
  return { output, layouts: slides.length };
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const args = process.argv.slice(2);
  if (args.length === 1 && ["--help", "-h"].includes(args[0])) {
    console.log("Usage: node scripts/preview-layouts.mjs --package <template-dir>\nWrites layouts/preview.html using the package's common fragments, theme, shell and chrome. Source layouts remain separate.");
  } else if (args.length !== 2 || args[0] !== "--package" || !args[1]) {
    console.error("Usage: node scripts/preview-layouts.mjs --package <template-dir>");
    process.exitCode = 1;
  } else {
    try { console.log(JSON.stringify(await previewLayouts(args[1]))); }
    catch (error) { console.error(error.message); process.exitCode = 1; }
  }
}
