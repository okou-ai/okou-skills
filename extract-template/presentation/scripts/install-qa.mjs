#!/usr/bin/env node
/* Copy QA into a user package and inline the common runtime exactly once. */
import {copyFileSync, cpSync, existsSync, mkdirSync, readFileSync, writeFileSync} from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length; i += 2) options[args[i]?.replace(/^--/, "")] = args[i + 1];
if (!options.package) { console.error("Usage: node scripts/install-qa.mjs --package <template-dir> [--config <source-qa.json>]"); process.exit(2); }
const target = path.resolve(options.package);
const shell = path.join(target, "layouts/_shell.html");
if (!existsSync(shell)) throw new Error("Create layouts/_shell.html before installing QA");
const configPath = options.config ? path.resolve(options.config) : path.join(target, "tools/qa-config.json");
const config = JSON.parse(readFileSync(existsSync(configPath) ? configPath : path.join(here, "../tools/qa-config.json"), "utf8"));
config.minFontSizePx = 10;
mkdirSync(path.join(target, "scripts"), {recursive: true});
mkdirSync(path.join(target, "tools"), {recursive: true});
for (const name of ["dom-metrics.js", "fit-text.js", "navigation.js"]) copyFileSync(path.join(here, name), path.join(target, "scripts", name));
for (const name of ["audit.js", "qa.mjs", "run.sh", "verify-package.mjs"]) copyFileSync(path.join(here, "../tools", name), path.join(target, "tools", name));
writeFileSync(path.join(target, "tools/qa-config.json"), JSON.stringify(config, null, 2) + "\n");
cpSync(path.join(here, "../library"), path.join(target, "library"), {recursive: true});
mkdirSync(path.join(target, "references"), {recursive: true});
for (const name of ["qa.md", "typography-fit.md", "layout-reuse.md"]) copyFileSync(path.join(here, "../references", name), path.join(target, "references", name));
const runtime = ["dom-metrics.js", "fit-text.js", "navigation.js"].map(name => readFileSync(path.join(here, name), "utf8")).join("\n");
const json = JSON.stringify(config).replaceAll("<", "\\u003c");
const block = `<!-- BEGIN PRESENTATION RUNTIME -->\n<script data-presentation-runtime>\nwindow.PRESENTATION_QA_CONFIG=${json};\n${runtime}\n</script>\n<!-- END PRESENTATION RUNTIME -->`;
let html = readFileSync(shell, "utf8");
const marker = /<!-- BEGIN PRESENTATION RUNTIME -->[\s\S]*?<!-- END PRESENTATION RUNTIME -->/g;
const matches = [...html.matchAll(marker)];
if (matches.length > 1) throw new Error("Duplicate runtime markers");
if (matches.length) html = html.replace(marker, block);
else {
  if (!/<\/body\s*>/i.test(html)) throw new Error("Shell needs a closing body tag");
  html = html.replace(/<\/body\s*>/i, `${block}\n</body>`);
}
writeFileSync(shell, html);
console.log(JSON.stringify({package: target, shell, minFontSizePx: 10, runtime: "inlined", sourceSafeAreaConfigured: Boolean(config.safeArea || Object.keys(config.layoutSafeAreas || {}).length)}));
