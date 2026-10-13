import assert from "node:assert/strict";
import {execFileSync, spawnSync} from "node:child_process";
import {existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync} from "node:fs";
import os from "node:os";
import path from "node:path";
import {fileURLToPath} from "node:url";
import test from "node:test";

const guide = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const installer = path.join(guide, "scripts/install-qa.mjs");
const verifier = path.join(guide, "tools/verify-package.mjs");
const safeArea = {left: 0, right: 0, top: 0, bottom: 0};
const fragment = '<section class="slide"><div class="stage" data-layout="title"><div class="fit"><h1>Source title</h1></div></div></section>';
const shell = contents => `<!doctype html><html><head><link rel="stylesheet" href="../styles/template.css"></head><body><main class="deck">${contents}</main></body></html>`;

function fixture(t, examples = 0) {
  const root = mkdtempSync(path.join(os.tmpdir(), "presentation-package-"));
  t.after(() => rmSync(root, {recursive: true, force: true}));
  const write = (file, value) => {
    mkdirSync(path.dirname(path.join(root, file)), {recursive: true});
    writeFileSync(path.join(root, file), typeof value === "string" ? value : JSON.stringify(value));
  };
  write("SKILL.md", "---\nname: fixture\ndescription: Package contract fixture.\n---\nFollow the [generation workflow](references/generate/workflow.md).\n");
  write("design-system.md", "Source rules and safe area.\n");
  write("layouts/README.md", "Insert source fragments into _shell.html.\n");
  write("styles/template.css", ".stage { width: 1600px; height: 900px; }\n");
  write("layouts/_shell.html", shell(fragment.repeat(examples)));
  write("layouts/source/title.html", fragment);
  const index = {sourceFilename: "source.pptx", pageCount: 3, sourceAspectRatio: "16:9", layouts: [
    {id: "title", file: "source/title.html", sourcePages: [1, 2, 3], purpose: "Title", regions: ["title"], capacity: {title: 40}},
  ]};
  write("layouts/source-index.json", index);
  const config = {minFontSizePx: 11, safeArea, layoutSafeAreas: {}, requiredChrome: [], allowedFontFallbacks: [], minContrastRatio: 3};
  write("tools/qa-config.json", config);
  execFileSync(process.execPath, [installer, "--package", root]);
  const verify = (...args) => {
    const result = spawnSync(process.execPath, [verifier, "--package", root, ...args], {encoding: "utf8"});
    assert.equal(result.error, undefined);
    return {code: result.status, ...JSON.parse(result.stdout)};
  };
  return {root, write, config, index, verify};
}

function blocked(result, message) {
  assert.equal(result.code, 1);
  assert.equal(result.status, "BLOCKED");
  assert(result.errors.some(error => error.includes(message)), JSON.stringify(result.errors));
}

for (const examples of [0, 1, 3]) {
  test(`shared shell may hold ${examples} examples while the index covers all source pages`, t => {
    const {verify} = fixture(t, examples);
    assert.deepEqual(verify(), {code: 0, status: "PACKAGE_VALID", errors: []});
  });
}

test("empty shell still requires complete source-page coverage", t => {
  const {write, index, verify} = fixture(t);
  index.layouts[0].sourcePages = [1, 2];
  write("layouts/source-index.json", index);
  blocked(verify(), "Covered 2 of 3");
});

function sourceCaptures(t) {
  const dir = mkdtempSync(path.join(os.tmpdir(), "presentation-source-pages-"));
  t.after(() => rmSync(dir, {recursive: true, force: true}));
  const png = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jBz8AAAAASUVORK5CYII=", "base64");
  for (const name of ["page-001.png", "page-002.png", "page-003.png"]) writeFileSync(path.join(dir, name), png);
  return {dir, png};
}

test("source capture directory accepts only the original ordered page images", t => {
  const {verify} = fixture(t);
  const {dir} = sourceCaptures(t);
  assert.deepEqual(verify("--source-pages", dir), {code: 0, status: "PACKAGE_VALID", errors: []});
  rmSync(path.join(dir, "page-002.png"));
  blocked(verify("--source-pages", dir), "Original ordered page images must exactly match source pageCount");
});

test("source capture directory rejects a contact sheet before upload", t => {
  const {verify} = fixture(t);
  const {dir, png} = sourceCaptures(t);
  const contactSheet = path.join(dir, "contact-sheet.png");
  writeFileSync(contactSheet, png);
  blocked(verify("--source-pages", dir), "contact-sheet.png");
  rmSync(contactSheet);
  assert.deepEqual(verify("--source-pages", dir), {code: 0, status: "PACKAGE_VALID", errors: []});
});

test("source capture directory rejects a directory posing as a page image", t => {
  const {verify} = fixture(t);
  const {dir} = sourceCaptures(t);
  const page = path.join(dir, "page-002.png");
  rmSync(page); mkdirSync(page);
  blocked(verify("--source-pages", dir), "page-002.png");
});

test("shared shell requires one deck insertion point", t => {
  const {write, verify} = fixture(t);
  write("layouts/_shell.html", "<html><body></body></html>");
  blocked(verify(), "one .deck");
});

test("shell structure uses HTML attributes rather than comments or script strings", t => {
  const {write, verify} = fixture(t);
  write("layouts/_shell.html", '<html><body><!-- <main class="deck"> --><main class=deck></main><script>const example = \'<main class="deck">\';</script></body></html>');
  assert.deepEqual(verify(), {code: 0, status: "PACKAGE_VALID", errors: []});
});

for (const [label, contents, message] of [
  ["missing fit", fragment.replace('class="fit"', 'class="content"'), "one .fit content root"],
  ["duplicate fit", fragment.replace('<h1>', '<div class="fit"></div><h1>'), "one .fit content root"],
  ["fit outside stage", '<section class="slide"><div class="stage"></div><div class="fit">Title</div></section>', "one .fit content root"],
  ["fit on stage itself", '<section class="slide"><div class="stage fit">Title</div></section>', "one .fit content root"],
  ["missing stage", '<section class="slide"><div class="fit">Title</div></section>', "one .stage"],
  ["duplicate stage", fragment.replace('</section>', '<div class="stage"><div class="fit"></div></div></section>'), "one .stage"],
  ["nested stage", fragment.replace('<div class="stage"', '<div><div class="stage"').replace('</section>', '</div></section>'), "direct child of .slide"],
  ["multiple slides", fragment.repeat(2), "one .slide"],
  ["extra outer wrapper", `<div>${fragment}</div>`, "top-level fragment"],
]) {
  test(`source package catches ${label} before generation`, t => {
    const {write, verify} = fixture(t);
    write("layouts/source/title.html", contents);
    blocked(verify(), message);
  });
}

test("each shell example needs its own content root", t => {
  const {write, verify} = fixture(t);
  write("layouts/_shell.html", shell(fragment + fragment.replace('class="fit"', 'class="content"')));
  blocked(verify(), "layouts/_shell.html: each .stage needs exactly one .fit");
});

test("shell examples must be direct deck children", t => {
  const {write, verify} = fixture(t);
  write("layouts/_shell.html", shell(`<div>${fragment}</div>`));
  blocked(verify(), "direct children of .deck");
});

test("structure ignores comments and script strings and accepts unquoted classes and SVG", t => {
  const {write, verify} = fixture(t);
  write("layouts/source/title.html", '<section class=slide><div class=stage data-layout=title><div class=fit><img src="data:,a"><svg><path d="M0 0" /></svg>Title</div></div></section><!-- <div class=fit> --><script>const example = "<div class=fit>";</script>');
  assert.deepEqual(verify(), {code: 0, status: "PACKAGE_VALID", errors: []});
});

for (const file of ["references/generate/workflow.md", "references/generate/qa.md", "references/generate/runtime-contract.md", "references/generate/layout-reuse.md", "references/generate/typography-fit.md", "scripts/viewport.js", "scripts/navigation.js", "tools/capture.mjs", "tools/prepare-web.py", "library/README.md", "library/styles/geometry.css"]) {
  test(`required package file cannot be missing: ${file}`, t => {
    const {root, verify} = fixture(t);
    rmSync(path.join(root, file));
    blocked(verify(), file);
  });
}

test("a directory cannot stand in for the QA guide", t => {
  const {root, verify} = fixture(t);
  const file = path.join(root, "references/generate/qa.md");
  rmSync(file); mkdirSync(file);
  blocked(verify(), "references/generate/qa.md");
});

test("installed generation package works without extraction references or helpers", t => {
  const {root, verify} = fixture(t);
  for (const file of ["references/extract", "scripts/prepare-pdf.py", "scripts/inspect-pdf.mjs", "scripts/assemble-pdf.py", "scripts/inventory-html.py", "scripts/source-derivatives.py", "scripts/install-qa.mjs", "tools/verify-package.mjs", "tests"]) {
    assert.equal(existsSync(path.join(root, file)), false, file);
  }
  assert.deepEqual(verify(), {code: 0, status: "PACKAGE_VALID", errors: []});
});

for (const file of ["references/extract/layout-inventory.md", "scripts/prepare-pdf.py", "scripts/inspect-pdf.mjs", "scripts/assemble-pdf.py", "scripts/inventory-html.py", "scripts/source-derivatives.py", "scripts/install-qa.mjs", "tools/verify-package.mjs"]) {
  test(`rejects extraction files mixed into a generation package: ${file}`, t => {
    const {write, verify} = fixture(t);
    write(file, "Extraction-only content.");
    blocked(verify(), file.startsWith("references/") ? "references/extract" : file);
  });
}

test("generation entrypoint must route to the bundled workflow", t => {
  const {write, verify} = fixture(t);
  write("SKILL.md", "# Template\nUse the [design system](design-system.md).\n");
  blocked(verify(), "must link to references/generate/workflow.md");
});

test("checks nested local guidance links while allowing provenance and code examples", t => {
  const {root, write, verify} = fixture(t);
  const file = "references/generate/qa.md";
  const guide = readFileSync(path.join(root, file), "utf8");
  write(file, guide + '\n[Source](https://example.com/deck)\n`[example](unused.md)`\n```md\n[example](unused.md)\n```\n[Notes][notes]\n[notes]: <Usage notes.md>\n');
  write("references/generate/Usage notes.md", "Extra generation guidance.\n");
  assert.deepEqual(verify(), {code: 0, status: "PACKAGE_VALID", errors: []});
  write("references/generate/Usage notes.md", "See [missing guide](missing.md).\n");
  blocked(verify(), "missing.md");
});

test("refresh removes legacy mixed guides and catches stale entrypoint links", t => {
  const {root, write, verify} = fixture(t);
  write("references/layout-reuse.md", "Old mixed guidance.\n");
  write("tools/verify-package.mjs", "Old bundled extraction helper.\n");
  const skill = readFileSync(path.join(root, "SKILL.md"), "utf8");
  write("SKILL.md", skill + "[Layouts](references/layout-reuse.md)\n");
  execFileSync(process.execPath, [installer, "--package", root]);
  assert.equal(existsSync(path.join(root, "references/layout-reuse.md")), false);
  assert.equal(existsSync(path.join(root, "tools/verify-package.mjs")), false);
  blocked(verify(), "Missing package resource: SKILL.md -> references/layout-reuse.md");
  write("SKILL.md", skill + "[Layouts](references/generate/layout-reuse.md)\n");
  assert.deepEqual(verify(), {code: 0, status: "PACKAGE_VALID", errors: []});
});

for (const [label, change, message] of [
  ["legacy 10px minimum", {minFontSizePx: 10}, "The fixed minimum is 11px"],
  ["missing safe area", {safeArea: null}, "Record a source safeArea"],
  ["overlapping safe insets", {safeArea: {...safeArea, left: 0.7, right: 0.4}}, "Invalid source safeArea"],
  ["malformed layout map", {layoutSafeAreas: []}, "layoutSafeAreas must be an object"],
  ["invalid per-layout override", {layoutSafeAreas: {title: {left: 0}}}, "Invalid layoutSafeAreas entry"],
  ["uncovered source profile", {safeArea: null, layoutSafeAreas: {other: safeArea}}, "Missing source safe area for title"],
  ["invalid fallback list", {allowedFontFallbacks: "Arial"}, "allowedFontFallbacks must be an array"],
  ["invalid chrome count", {requiredChrome: [{role: "footer", min: 2, max: 1}]}, "Invalid source requiredChrome rule"],
  ["invalid contrast", {minContrastRatio: 2}, "minContrastRatio must be within"],
]) {
  test(`rejects source configuration with ${label}`, t => {
    const {write, config, verify} = fixture(t);
    write("tools/qa-config.json", {...config, ...change});
    blocked(verify(), message);
  });
}

test("refresh upgrades a legacy 10px package configuration and embedded runtime together", t => {
  const {root, write, config, verify} = fixture(t);
  write("tools/qa-config.json", {...config, minFontSizePx: 10});
  const installed = JSON.parse(execFileSync(process.execPath, [installer, "--package", root], {encoding: "utf8"}));
  assert.equal(installed.minFontSizePx, 11);
  assert.equal(JSON.parse(readFileSync(path.join(root, "tools/qa-config.json"), "utf8")).minFontSizePx, 11);
  assert.deepEqual(verify(), {code: 0, status: "PACKAGE_VALID", errors: []});
});

test("per-profile safe areas can replace a global safe area", t => {
  const {write, config, verify} = fixture(t);
  write("layouts/source/title.html", fragment.replace('data-layout="title"', 'data-source-profile="title"'));
  write("tools/qa-config.json", {...config, safeArea: null, layoutSafeAreas: {title: safeArea}});
  assert.deepEqual(verify(), {code: 0, status: "PACKAGE_VALID", errors: []});
});

test("installation requires source configuration instead of silently using an empty default", t => {
  const {root} = fixture(t);
  rmSync(path.join(root, "tools/qa-config.json"));
  const before = readFileSync(path.join(root, "layouts/_shell.html"), "utf8");
  const result = spawnSync(process.execPath, [installer, "--package", root], {encoding: "utf8"});
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /source-specific qa-config.json/);
  assert.equal(readFileSync(path.join(root, "layouts/_shell.html"), "utf8"), before);
});

test("shared-shell support retains recursive local-resource checks", t => {
  const {write, verify} = fixture(t);
  write("styles/template.css", '@import "nested.css";');
  write("styles/nested.css", '.stage { background-image: url("../assets/missing.png"); }');
  blocked(verify(), "assets/missing.png");
});
