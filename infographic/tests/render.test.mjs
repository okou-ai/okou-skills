import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, existsSync, mkdirSync, mkdtempSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { chromium } from 'playwright-core';

const require = createRequire(import.meta.url);
const AntV = require('@antv/infographic');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const base = process.env.ANTV_TEST_OUT || tmpdir();
mkdirSync(base, { recursive:true });
const scratch = mkdtempSync(path.join(base, 'renderer-tests-'));
console.log(`Renderer test artifacts: ${scratch}`);
const fixture = path.join(root, 'tests/fixtures/minimal.antv');
const noSandbox = process.env.ANTV_TEST_NO_SANDBOX === '1';
const browserFlags = [
  ...(process.env.CHROMIUM_PATH ? ['--chromium', process.env.CHROMIUM_PATH] : []),
  ...(noSandbox ? ['--no-sandbox'] : []),
];
function run(args) {
  const result = spawnSync(process.execPath, ['scripts/render.mjs', ...args], { cwd:root, encoding:'utf8', timeout:45000 });
  if (result.error) throw result.error;
  return { ...result, text:result.stdout + result.stderr };
}
function input(name, source, extension = '.antv') {
  const target = path.join(scratch, name + extension);
  writeFileSync(target, source);
  return target;
}
function rejected(args, pattern) {
  const result = run(args);
  assert.equal(result.status, 1, result.text);
  assert.match(result.text, pattern);
  return result;
}
function render(name, source, more = []) {
  const out = path.join(scratch, name);
  const result = run(['--input', source, '--out', out, ...browserFlags, ...more]);
  assert.equal(result.status, 0, result.text);
  const qa = JSON.parse(readFileSync(path.join(out, 'qa.json'), 'utf8'));
  assert.equal(qa.status, 'passed');
  assert.equal(qa.automaticChecks.status, 'passed');
  assert.equal(qa.visualReview.status, 'required');
  for (const key of ['engineErrors', 'pageErrors', 'consoleErrors', 'blockedRequests']) assert.deepEqual(qa[key], []);
  assert.deepEqual(qa.automaticChecks.clippedText, []);
  assert.deepEqual(qa.automaticChecks.missingRequiredText, []);
  const png = readFileSync(path.join(out, 'infographic.png'));
  assert.equal(png.subarray(1, 4).toString(), 'PNG');
  assert.deepEqual(qa.png, { width:png.readUInt32BE(16), height:png.readUInt32BE(20) });
  const svg = readFileSync(path.join(out, 'infographic.svg'), 'utf8');
  assert.match(svg, /<svg\b/);
  assert.match(svg, /<(path|rect|circle|ellipse)\b/);
  assert.match(svg, /<(foreignObject|text)\b/);
  assert.doesNotMatch(svg, /<image[^>]+data:image\/png/);
  const html = readFileSync(path.join(out, 'infographic.html'), 'utf8');
  assert.match(html, /id="infographic-source"/);
  assert.match(html, /id="antv-license"/);
  assert.match(html, /Copyright \(c\) 2025 AntV/);
  assert.doesNotMatch(html, /<script[^>]+\bsrc=/);
  return { out, qa, html, svg };
}
function allCopy(data) {
  const strings = [];
  function visit(value) {
    if (!value || typeof value !== 'object') return;
    for (const [key, child] of Object.entries(value)) {
      if (['title', 'desc', 'label', 'value'].includes(key) && typeof child === 'string') strings.push(child);
      else if (child && typeof child === 'object') visit(child);
    }
  }
  visit(data);
  return strings;
}

test('argument validation happens before browser launch', () => {
  const common = ['--input', fixture, '--out', path.join(scratch, 'bad-arguments'), '--chromium', '/not/a/browser'];
  rejected([], /--input and --out are required/);
  rejected([...common, '--unknown'], /Unknown argument/);
  rejected([...common, '--width'], /Missing value/);
  rejected([...common, '--input', fixture], /Duplicate argument/);
  for (const [flag, value] of [['width', 'NaN'], ['width', '63'], ['height', '900.5'], ['height', '8193'], ['scale', '0'], ['scale', 'Infinity'], ['scale', '5']]) {
    rejected([...common, `--${flag}`, value], new RegExp(`Invalid --${flag}`));
  }
  rejected([...common, '--width', '8192', '--height', '8192', '--scale', '4'], /64 million pixels/);
  for (const copy of ['[1]', '[""]', '["unfinished"', '{}']) rejected([...common, '--copy', copy], /--copy/);
  assert.equal(existsSync(path.join(scratch, 'bad-arguments')), false);
});

test('file and native syntax validation happen before rendering', () => {
  const target = path.join(scratch, 'bad-input');
  const common = ['--out', target, '--chromium', '/not/a/browser'];
  rejected(['--input', input('not-html', '<script>throw Error("unsafe")</script>', '.html'), ...common], /native \.antv file/);
  rejected(['--input', input('raw-html', '<!doctype html><script>throw Error("unsafe")</script>'), ...common], /AntV syntax error/);
  rejected(['--input', path.join(scratch, 'not-found.antv'), ...common], /ENOENT/);
  rejected(['--input', input('empty', ''), ...common], /Input must contain/);
  rejected(['--input', input('whitespace', ' \n '), ...common], /Input is empty/);
  rejected(['--input', input('invalid-syntax', 'infographic list-grid-badge-card\nunknownRoot nonsense\n'), ...common], /AntV syntax error/);
  rejected(['--input', input('unknown-template', 'infographic list-grid-badge-cars\ndata\n  title No fuzzy matching\n'), ...common], /exact built-in/);
  rejected(['--input', fixture, '--out', fixture, '--chromium', '/not/a/browser'], /--out must be a directory/);
  rejected(['--input', fixture, '--out', target, '--chromium', '/not/a/browser'], /Chromium not found/);
  assert.equal(existsSync(target), false);
});

test('minimal real diagram, custom dimensions, scale and inline --copy', { timeout:60000 }, () => {
  const result = render('minimal', fixture, ['--width', '800', '--height', '450', '--scale', '2', '--copy', '["A minimal real diagram","Alpha","Beta"]']);
  assert.deepEqual(result.qa.png, { width:1600, height:900 });
  assert.equal(result.qa.automaticChecks.svg.width, 800);
  assert.equal(result.qa.automaticChecks.svg.height, 450);
  assert.equal(result.qa.engine.version, '0.2.20');
  assert.equal(result.qa.engine.playwright, '1.65.0');
});

for (const name of ['process', 'comparison', 'timeline', 'hierarchy', 'relation', 'list']) {
  test(`starter ${name}: all authored copy survives native SVG export`, { timeout:60000 }, () => {
    const source = path.join(root, 'templates', `${name}.antv`);
    const parsed = AntV.parseSyntax(readFileSync(source, 'utf8'));
    assert.deepEqual(parsed.errors, []);
    const copies = allCopy(parsed.options.data);
    assert.ok(copies.length >= 6);
    if (name === 'relation') {
      const { nodes, relations } = parsed.options.data;
      const ids = new Set(nodes.map((node) => node.id));
      assert.equal(ids.size, nodes.length);
      assert.ok(relations.every((edge) => ids.has(edge.from) && ids.has(edge.to)));
      assert.ok(nodes.some((node) => relations.filter((edge) => edge.to === node.id).length > 1), 'Exercise a converging graph, not just a chain');
    }
    const result = render(name, source, ['--copy', JSON.stringify(copies)]);
    assert.deepEqual(result.qa.png, { width:1600, height:900 });
  });
}

test('--copy also accepts a JSON file', { timeout:60000 }, () => {
  const copies = path.join(scratch, 'copy.json');
  writeFileSync(copies, '["Alpha","A second verified item."]');
  render('copy-file', fixture, ['--copy', copies]);
});

test('missing copy fails and removes stale successful output files', { timeout:60000 }, () => {
  const out = path.join(scratch, 'missing-copy');
  mkdirSync(out);
  for (const file of ['infographic.png', 'infographic.svg', 'infographic.html']) writeFileSync(path.join(out, file), 'stale');
  rejected(['--input', fixture, '--out', out, ...browserFlags, '--copy', '["alpha"]'], /Missing required copy/);
  const qa = JSON.parse(readFileSync(path.join(out, 'qa.json')));
  assert.equal(qa.status, 'failed');
  assert.deepEqual(qa.automaticChecks.missingRequiredText, ['alpha']);
  for (const file of ['infographic.png', 'infographic.svg', 'infographic.html']) assert.equal(existsSync(path.join(out, file)), false);
});

test('engine error is reported without waiting for the load timeout', { timeout:30000 }, () => {
  const broken = input('engine-error', 'infographic list-grid-badge-card\ndesign\n  item\n    type does-not-exist\ndata\n  lists\n    - label Broken\n');
  const out = path.join(scratch, 'engine-error');
  const started = Date.now();
  rejected(['--input', broken, '--out', out, ...browserFlags], /AntV render failed.*Incomplete options/);
  assert.ok(Date.now() - started < 15000);
  const qa = JSON.parse(readFileSync(path.join(out, 'qa.json')));
  assert.ok(qa.engineErrors.some((s) => s.includes('Incomplete options')));
});

test('an empty drawing is not a successful infographic', { timeout:60000 }, () => {
  const source = input('no-text', 'infographic list-grid-badge-card\ndata\n  lists\n    - id empty\n');
  rejected(['--input', source, '--out', path.join(scratch, 'no-text'), ...browserFlags], /No visible text/);
});

test('external resources fail closed instead of producing silently missing icons', { timeout:30000 }, () => {
  const source = input('remote-icon', 'infographic list-grid-badge-card\ndata\n  lists\n    - label Remote\n      icon https://example.invalid/icon.svg\n');
  const out = path.join(scratch, 'remote-icon');
  const started = Date.now();
  rejected(['--input', source, '--out', out, ...browserFlags], /Browser error|Outgoing request blocked/);
  assert.ok(Date.now() - started < 15000);
  const qa = JSON.parse(readFileSync(path.join(out, 'qa.json')));
  assert.ok(qa.blockedRequests.length || qa.consoleErrors.length);
  assert.equal(qa.status, 'failed');
});

test('safe inline SVG resources work without any network requests', { timeout:60000 }, () => {
  const icon = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40"><path fill="#3F6655" d="M4 4h32v32H4z"/></svg>';
  const source = input('inline-icon', `infographic list-grid-badge-card\ndata\n  title Inline vector resource\n  lists\n    - label Local icon\n      desc No remote asset service.\n      icon data:image/svg+xml,${encodeURIComponent(icon)}\n`);
  render('inline-icon', source, ['--copy', '["Inline vector resource","Local icon","No remote asset service."]']);
});

test('active attributes in supplied inline SVG are rejected before export', { timeout:60000 }, () => {
  const icon = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40"><path onmouseover="window.__PWNED=1" d="M4 4h32v32H4z"/></svg>';
  const source = input('unsafe-icon', `infographic list-grid-badge-card\ndata\n  lists\n    - label Unsafe icon\n      icon data:image/svg+xml,${encodeURIComponent(icon)}\n`);
  const out = path.join(scratch, 'unsafe-icon');
  rejected(['--input', source, '--out', out, ...browserFlags], /Unsafe SVG attribute|Browser error/);
  assert.equal(existsSync(path.join(out, 'infographic.html')), false);
});

test('HTML preserves exact source safely and renders offline, including CJK and script-like copy', { timeout:60000 }, async () => {
  const special = 'Literal < > & "quotes" </script><script>window.__PWNED=1</script>';
  const source = `infographic list-grid-badge-card\ndata\n  title 精确信息 · 2026\n  desc ${special}\n  lists\n    - label 清晰中文\n      desc Names, values and units: 12 kg.\ntheme\n  colorBg #FFFFFF\n  base\n    text\n      font-family Noto Sans CJK SC\n// Exact-source separators: <!-- \u2028 \u2029\n`;
  const result = render('safe-source', input('safe-source', source), ['--copy', JSON.stringify(['精确信息 · 2026', special, '清晰中文', '12 kg.'])]);
  assert.doesNotMatch(result.html, /<script>window\.__PWNED/);
  const browser = await chromium.launch({ executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium', headless:true, chromiumSandbox:!noSandbox });
  try {
    const context = await browser.newContext({ viewport:{ width:1600, height:900 }, serviceWorkers:'block' });
    const requests = [], errors = [];
    await context.route('**/*', async (route) => { requests.push(route.request().url()); await route.abort(); });
    const page = await context.newPage();
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    await page.setContent(result.html);
    await page.waitForFunction(() => window.__renderState?.done, null, { timeout:20000 });
    const actual = await page.evaluate(() => ({ source:JSON.parse(document.getElementById('infographic-source').textContent), state:window.__renderState, injected:window.__PWNED, text:document.getElementById('stage').textContent, editor:typeof window.infographic?.render }));
    assert.equal(actual.source, source);
    assert.equal(actual.injected, undefined);
    assert.deepEqual(actual.state.errors, []);
    assert.ok(actual.text.includes(special));
    assert.ok(actual.text.includes('清晰中文'));
    assert.equal(actual.editor, 'function');
    assert.deepEqual(requests, []);
    assert.deepEqual(errors, []);
  } finally { await browser.close(); }
});
