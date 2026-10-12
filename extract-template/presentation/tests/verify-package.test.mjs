import assert from "node:assert/strict";
import {execFileSync, spawnSync} from "node:child_process";
import {mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync} from "node:fs";
import os from "node:os";
import path from "node:path";
import {fileURLToPath} from "node:url";
import test from "node:test";

const guide = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const installer = path.join(guide, "scripts/install-qa.mjs");
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
  write("SKILL.md", "---\nname: fixture\ndescription: Package contract fixture.\n---\nSee references/qa.md.\n");
  write("design-system.md", "Source rules and safe area.\n");
  write("layouts/README.md", "Insert source fragments into _shell.html.\n");
  write("styles/template.css", ".stage { width: 1600px; height: 900px; }\n");
  write("layouts/_shell.html", shell(fragment.repeat(examples)));
  write("layouts/source/title.html", fragment);
  const index = {sourceFilename: "source.pptx", pageCount: 3, sourceAspectRatio: "16:9", layouts: [
    {id: "title", file: "source/title.html", sourcePages: [1, 2, 3], purpose: "Title", regions: ["title"], capacity: {title: 40}},
  ]};
  write("layouts/source-index.json", index);
  const config = {minFontSizePx: 10, safeArea, layoutSafeAreas: {}, requiredChrome: [], allowedFontFallbacks: [], minContrastRatio: 3};
  write("tools/qa-config.json", config);
  execFileSync(process.execPath, [installer, "--package", root]);
  const verify = () => {
    const result = spawnSync(process.execPath, [path.join(root, "tools/verify-package.mjs"), "--package", root], {encoding: "utf8"});
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

for (const file of ["references/qa.md", "references/layout-reuse.md", "references/typography-fit.md", "scripts/navigation.js", "library/README.md", "library/styles/geometry.css"]) {
  test(`required package file cannot be missing: ${file}`, t => {
    const {root, verify} = fixture(t);
    rmSync(path.join(root, file));
    blocked(verify(), file);
  });
}

test("a directory cannot stand in for the QA guide", t => {
  const {root, verify} = fixture(t);
  const file = path.join(root, "references/qa.md");
  rmSync(file); mkdirSync(file);
  blocked(verify(), "references/qa.md");
});

for (const [label, change, message] of [
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
