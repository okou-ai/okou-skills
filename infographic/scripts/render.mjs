#!/usr/bin/env node
import { readFile, writeFile, mkdir, stat, access, rm } from 'node:fs/promises';
import { constants } from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { randomBytes } from 'node:crypto';
import { chromium } from 'playwright-core';

const require = createRequire(import.meta.url);
const AntV = require('@antv/infographic');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const usage = 'node scripts/render.mjs --input file.antv --out dir [--width 1600 --height 900 --scale 1] [--copy \'["Required text"]\'|copy.json] [--chromium /path/to/chromium] [--no-sandbox]';
const json = (value) => JSON.stringify(value).replace(/[<>&\u2028\u2029]/g, (c) => `\\u${c.charCodeAt(0).toString(16).padStart(4, '0')}`);
const fail = (message) => { throw new Error(message); };

async function argumentsFor(argv) {
  const opts = { width: 1600, height: 900, scale: 1, copy: [] };
  const values = new Set(['input', 'out', 'width', 'height', 'scale', 'copy', 'chromium']);
  const seen = new Set();
  for (let i = 0; i < argv.length; i++) {
    const key = argv[i].slice(2);
    if (!argv[i].startsWith('--') || (!values.has(key) && key !== 'no-sandbox')) fail(`Unknown argument: ${argv[i]}`);
    if (seen.has(key)) fail(`Duplicate argument: --${key}`);
    seen.add(key);
    if (key === 'no-sandbox') { opts.noSandbox = true; continue; }
    if (!argv[i + 1] || argv[i + 1].startsWith('--')) fail(`Missing value for --${key}`);
    opts[key] = argv[++i];
  }
  if (!opts.input || !opts.out) fail(`--input and --out are required.\n${usage}`);
  for (const key of ['width', 'height', 'scale']) {
    const n = Number(opts[key]);
    const valid = Number.isFinite(n) && (key === 'scale' ? n >= 0.25 && n <= 4 : Number.isInteger(n) && n >= 64 && n <= 8192);
    if (!valid) fail(`Invalid --${key}: expected ${key === 'scale' ? '0.25–4' : 'an integer 64–8192'}`);
    opts[key] = n;
  }
  if (opts.width * opts.height * opts.scale ** 2 > 64_000_000) fail('Output exceeds 64 million pixels');
  if (path.extname(opts.input).toLowerCase() !== '.antv') fail('--input must be a native .antv file, not HTML');
  if (!(await stat(opts.input)).isFile()) fail('--input must be a regular file');
  const bytes = await readFile(opts.input);
  if (!bytes.length || bytes.length > 1_000_000) fail('Input must contain 1–1,000,000 bytes');
  opts.source = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  if (!opts.source.trim()) fail('Input is empty');
  if (typeof opts.copy === 'string') {
    try { opts.copy = JSON.parse(opts.copy.trim().startsWith('[') ? opts.copy : await readFile(opts.copy, 'utf8')); }
    catch (error) { fail(`Invalid --copy: supply a JSON string array or its JSON file (${error.message})`); }
  }
  if (!Array.isArray(opts.copy) || opts.copy.some((s) => typeof s !== 'string' || !s.trim())) fail('--copy must be a JSON array of nonempty strings');
  const parsed = AntV.parseSyntax(opts.source);
  if (parsed.errors.length) fail(`AntV syntax error: ${parsed.errors.map((e) => `line ${e.line}: ${e.path}: ${e.message}`).join('; ')}`);
  if (!parsed.options.template || !AntV.getTemplate(parsed.options.template)) fail('Use an exact built-in AntV template name');
  opts.parsed = parsed;
  opts.out = path.resolve(opts.out);
  const target = await stat(opts.out).catch((e) => { if (e.code !== 'ENOENT') throw e; });
  if (target && !target.isDirectory()) fail('--out must be a directory');
  return opts;
}

async function browserPath(explicit) {
  const configured = explicit || process.env.CHROMIUM_PATH || process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
  const names = process.platform === 'win32' ? ['chrome.exe', 'chromium.exe'] : ['chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable'];
  const candidates = configured ? [configured] : [
    '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome',
    '/opt/google/chrome/chrome', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    ...['PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA'].flatMap((key) => process.env[key] ? [path.join(process.env[key], 'Google/Chrome/Application/chrome.exe')] : []),
    ...(process.env.PATH || '').split(path.delimiter).flatMap((dir) => names.map((name) => path.join(dir, name))),
  ];
  for (const candidate of candidates) {
    try { await access(candidate, constants.X_OK); if ((await stat(candidate)).isFile()) return path.resolve(candidate); } catch {}
  }
  fail(`Chromium not found${configured ? ` at ${configured}` : ''}. Install it separately or supply --chromium /path/to/chromium`);
}

function makeHTML(source, bundle, license, width, height) {
  const nonce = randomBytes(18).toString('base64');
  return `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-${nonce}'; style-src 'unsafe-inline'; img-src data: blob:; font-src data:; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>AntV infographic — editable source</title>
<style>html,body{margin:0;width:${width}px;height:${height}px;overflow:hidden;font-family:sans-serif}#stage{width:100%;height:100%}#stage>svg{display:block}</style></head><body><div id="stage"></div>
<script id="antv-license" type="text/plain">${license.replace(/<\/script/gi, '<\\/script')}</script>
<script id="infographic-source" type="application/json">${json(source)}</script>
<script nonce="${nonce}">${bundle.replace(/<\/script/gi, '<\\/script')}</script>
<script nonce="${nonce}">
window.__renderState = {done:false, errors:[], warnings:[]};
(async () => {
  const state = window.__renderState;
  const message = (e) => e instanceof Error ? e.message : JSON.stringify(e);
  let timer;
  try {
    const A = AntVInfographic;
    // AntV loads every registered webfont. Keep the registry offline via its public API.
    for (const font of A.getFonts()) A.registerFont({...font, fontFamily:font.fontFamily.replace(/^["']|["']$/g, ''), fontWeight:{}});
    A.setDefaultFont('sans-serif');
    const parsed = A.parseSyntax(JSON.parse(document.getElementById('infographic-source').textContent));
    if (parsed.errors.length) throw new Error(message(parsed.errors));
    const options = parsed.options;
    const base = options.themeConfig?.base || {};
    options.themeConfig = {...options.themeConfig, base:{...base, text:{'font-family':'sans-serif', ...base.text}}};
    const font = options.themeConfig.base.text['font-family'];
    await document.fonts.load('16px ' + font);
    await document.fonts.ready;
    const graphic = window.infographic = new A.Infographic({...options, container:'#stage', width:${width}, height:${height}, padding:24, editable:true});
    const loaded = new Promise((resolve, reject) => {
      graphic.on('loaded', resolve);
      graphic.on('error', (e) => { state.errors.push(message(e)); reject(new Error(message(e))); });
      graphic.on('warning', (e) => state.warnings.push(message(e)));
    });
    const timeout = new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('AntV load timeout (15s)')), 15000); });
    graphic.render();
    await Promise.race([loaded, timeout]);
    await document.fonts.ready;
    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  } catch (e) { state.errors.push(message(e)); }
  finally { clearTimeout(timer); state.done = true; }
})();
</script></body></html>`;
}

// Run against the exported SVG, not the embedded source string or hidden editor controls.
function inspectSVG(required) {
  const svg = document.querySelector('#stage > svg');
  if (!svg) throw new Error('No exported SVG');
  const viewport = svg.getBoundingClientRect();
  const texts = [], clippedText = [], outsideTextBoxes = [];
  const rect = (r) => ({ x:r.x, y:r.y, width:r.width, height:r.height });
  const outside = (a, b, axis) => axis === 'x' ? a.left < b.left - 1 || a.right > b.right + 1 : a.top < b.top - 1 || a.bottom > b.bottom + 1;
  for (const el of svg.querySelectorAll('foreignObject > span, text')) {
    if (el.closest('defs,symbol')) continue;
    const value = el.textContent;
    if (!value?.trim()) continue;
    let visible = true;
    for (let a = el; a; a = a.parentElement) {
      const style = getComputedStyle(a);
      if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) visible = false;
    }
    const style = getComputedStyle(el);
    if (/^rgba\(.*,[\s]*0\)$/.test(style.color) || (el.tagName === 'text' && (style.fill === 'none' || Number(style.fillOpacity) === 0))) visible = false;
    const range = document.createRange();
    range.selectNodeContents(el);
    const ranges = [...range.getClientRects()].filter((r) => r.width > 0 && r.height > 0);
    if (!visible || !ranges.length) continue;
    const reasons = new Set();
    for (const r of ranges) {
      if (outside(r, viewport, 'x') || outside(r, viewport, 'y')) reasons.add('SVG viewport');
      for (let a = el; a && a !== svg; a = a.parentElement) {
        const style = getComputedStyle(a), b = a.getBoundingClientRect();
        for (const axis of ['x', 'y']) {
          if (['hidden', 'clip', 'scroll', 'auto'].includes(style[axis === 'x' ? 'overflowX' : 'overflowY']) && outside(r, b, axis)) reasons.add('CSS overflow');
        }
      }
    }
    const box = el.closest('foreignObject')?.getBoundingClientRect();
    if (box && ranges.some((r) => outside(r, box, 'x') || outside(r, box, 'y'))) outsideTextBoxes.push(value);
    texts.push({ text:value, bounds:rect(range.getBoundingClientRect()), fontSize:getComputedStyle(el).fontSize });
    if (reasons.size) clippedText.push({ text:value, reasons:[...reasons] });
  }
  return {
    visibleText:texts, clippedText, outsideTextBoxes,
    missingRequiredText:required.filter((s) => !texts.some((t) => t.text.includes(s))),
    svg:{ width:svg.width.baseVal.value, height:svg.height.baseVal.value, viewBox:svg.getAttribute('viewBox'), viewport:rect(viewport) },
  };
}

async function render(opts) {
  const executablePath = await browserPath(opts.chromium);
  const library = path.resolve(path.dirname(require.resolve('@antv/infographic')), '..');
  const [bundle, license] = await Promise.all([
    readFile(path.join(library, 'dist/infographic.min.js'), 'utf8'),
    readFile(path.join(library, 'LICENSE'), 'utf8'),
  ]);
  const html = makeHTML(opts.source, bundle, license, opts.width, opts.height);
  const qa = {
    status:'failed', engine:{ name:'@antv/infographic', version:AntV.VERSION, playwright:require('playwright-core/package.json').version },
    input:path.resolve(opts.input), template:opts.parsed.options.template,
    requested:{ width:opts.width, height:opts.height, scale:opts.scale, requiredCopy:opts.copy },
    automaticChecks:{ status:'not-run', scope:'Exact visible text substrings and browser text-range/viewport/CSS-overflow geometry; not semantic or visual approval' },
    visualReview:{ status:'required', checks:['Read all copy in the PNG', 'Inspect overlap, small text, contrast, arrows and factual meaning at delivery size'] },
    warnings:opts.parsed.warnings, engineErrors:[], pageErrors:[], consoleErrors:[], blockedRequests:[],
  };
  await mkdir(opts.out, { recursive:true });
  for (const name of ['infographic.png', 'infographic.svg', 'infographic.html']) await rm(path.join(opts.out, name), { force:true });
  let browser, abort;
  const fatal = new Promise((_, reject) => { abort = (message) => reject(new Error(message)); });
  fatal.catch(() => {});
  const guarded = async (operation) => {
    let timer;
    try { return await Promise.race([operation, fatal, new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('Browser operation timeout (20s)')), 20000); })]); }
    finally { clearTimeout(timer); }
  };
  try {
    browser = await chromium.launch({ executablePath, headless:true, chromiumSandbox:!opts.noSandbox, args:['--disable-dev-shm-usage'], timeout:20000 });
    qa.engine.chromium = browser.version();
    const context = await browser.newContext({ viewport:{ width:opts.width, height:opts.height }, deviceScaleFactor:opts.scale, serviceWorkers:'block' });
    await context.route('**/*', async (route) => { qa.blockedRequests.push(route.request().url()); await route.abort(); abort('Outgoing request blocked; use local fonts and inline resources only'); });
    const page = await context.newPage();
    page.on('pageerror', (error) => { qa.pageErrors.push(error.message); abort(`Page error: ${error.message}`); });
    page.on('console', (message) => { if (message.type() === 'error') { qa.consoleErrors.push(message.text()); abort(`Browser error: ${message.text()}`); } });
    page.setDefaultTimeout(20000);
    await guarded(page.setContent(html, { waitUntil:'load', timeout:20000 }));
    await guarded(page.waitForFunction(() => window.__renderState?.done, null, { timeout:20000 }));
    const state = await page.evaluate(() => window.__renderState);
    qa.engineErrors = state.errors;
    qa.warnings.push(...state.warnings);
    if (state.errors.length) fail(`AntV render failed: ${state.errors.join('; ')}`);
    const svg = await guarded(page.evaluate(async ({ width, height }) => {
      const url = await window.infographic.toDataURL({ type:'svg', embedResources:false });
      const xml = decodeURIComponent(url.slice(url.indexOf(',') + 1));
      const doc = new DOMParser().parseFromString(xml, 'image/svg+xml');
      if (doc.querySelector('parsererror') || doc.documentElement.localName !== 'svg') throw new Error('Invalid SVG export');
      const svg = doc.documentElement;
      // Never export active content or external resource references from inline assets.
      if (svg.querySelector('script,iframe,object,embed,a,link,style,animate,animateMotion,animateTransform,set,discard')) throw new Error('Unsafe active SVG content');
      for (const el of [svg, ...svg.querySelectorAll('*')]) for (const attr of el.attributes) {
        if (/^on/i.test(attr.localName) || ((attr.localName === 'href' || attr.localName === 'src') && !/^(#|data:image\/)/i.test(attr.value))) throw new Error('Unsafe SVG attribute');
        for (const match of attr.value.matchAll(/url\(([^)]*)\)/gi)) if (!/^(#|data:image\/)/i.test(match[1].trim().replace(/^["']|["']$/g, ''))) throw new Error('External CSS resource in SVG');
      }
      svg.setAttribute('width', width);
      svg.setAttribute('height', height);
      document.getElementById('stage').replaceChildren(document.importNode(svg, true));
      await document.fonts.ready;
      await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      return new XMLSerializer().serializeToString(svg);
    }, { width:opts.width, height:opts.height }));
    qa.automaticChecks = { ...qa.automaticChecks, ...await page.evaluate(inspectSVG, opts.copy), status:'failed' };
    const checks = qa.automaticChecks;
    if (!checks.visibleText.length) fail('No visible text in exported SVG');
    if (checks.missingRequiredText.length) fail(`Missing required copy: ${JSON.stringify(checks.missingRequiredText)}`);
    if (checks.clippedText.length) fail(`Clipped text: ${JSON.stringify(checks.clippedText)}`);
    if (qa.blockedRequests.length || qa.pageErrors.length || qa.consoleErrors.length) fail('Browser errors occurred');
    await guarded(page.locator('#stage').screenshot({ path:path.join(opts.out, 'infographic.png'), animations:'disabled', timeout:20000 }));
    const png = await readFile(path.join(opts.out, 'infographic.png'));
    qa.png = { width:png.readUInt32BE(16), height:png.readUInt32BE(20) };
    await writeFile(path.join(opts.out, 'infographic.svg'), svg);
    await writeFile(path.join(opts.out, 'infographic.html'), html);
    qa.automaticChecks.status = 'passed';
    qa.status = 'passed';
    console.log(JSON.stringify({ status:qa.status, out:opts.out, png:qa.png, visualReview:'required' }));
  } catch (error) { qa.error = error.message; throw error; }
  finally {
    await browser?.close();
    await writeFile(path.join(opts.out, 'qa.json'), JSON.stringify(qa, null, 2) + '\n');
  }
}

if (process.argv.length === 3 && process.argv[2] === '--help') console.log(usage);
else {
  try { await render(await argumentsFor(process.argv.slice(2))); }
  catch (error) { console.error(`render: ${error.message}`); process.exitCode = 1; }
}
