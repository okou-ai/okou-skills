#!/usr/bin/env node
// One bounded, computed-style inventory of pdf2htmlEX output; no page HTML dump.
import {execFileSync} from 'node:child_process';
import {readFileSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

export async function inspectPDF() {
  await document.fonts.ready;
  const style = document.createElement('style');
  style.textContent = '.pc{display:block!important}*{animation:none!important;transition:none!important}';
  document.head.append(style);
  await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
  const transparent = color => color === 'transparent' || /rgba\([^)]*,\s*0(?:\.0+)?\)$/.test(color);
  const pages = [...document.querySelectorAll('.pf')].map((page, index) => {
    const fonts = new Map(), colors = new Set(), visible = [], hidden = [];
    const walker = document.createTreeWalker(page, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const text = node.textContent.replace(/\s+/g, ' ').trim();
      if (!text || !node.parentElement.closest('.t')) continue;
      const computed = getComputedStyle(node.parentElement);
      let shown = computed.visibility === 'visible' && !transparent(computed.color) &&
        !transparent(computed.webkitTextFillColor || computed.color);
      for (let parent = node.parentElement; parent && page.contains(parent); parent = parent.parentElement) {
        const css = getComputedStyle(parent);
        if (css.display === 'none' || Number(css.opacity) === 0) shown = false;
      }
      (shown ? visible : hidden).push(text);
      if (shown) {
        const key = `${computed.fontFamily} | ${computed.fontSize} | ${computed.lineHeight}`;
        fonts.set(key, (fonts.get(key) || 0) + 1);
        colors.add(computed.color);
      }
    }
    const css = getComputedStyle(page);
    return {
      page: index + 1, sourceId: page.id, converterPage: page.dataset.pageNo,
      width: parseFloat(css.width), height: parseFloat(css.height),
      backgrounds: [...page.querySelectorAll('img.bi')].map(img => ({
        file: img.getAttribute('src'), loaded: img.complete && img.naturalWidth > 0,
      })),
      text: {visible: visible.length, hidden: hidden.length,
        visibleSample: visible.join(' ').slice(0, 120), hiddenSample: hidden.join(' ').slice(0, 120)},
      visibleStyles: [...fonts].sort((a, b) => b[1] - a[1]).slice(0, 8),
      visibleColors: [...colors].slice(0, 8),
      status: visible.length ? 'visible-text-needs-slot-review' : 'reference-only',
    };
  });
  style.remove();
  return {pageCount: pages.length, pages,
    notes: ['Visibility is a computed-style observation, not proof of editable text or a reading order.',
      'Pages with hidden text and backgrounds need source-image review for flattened lettering.']};
}

export function main(args) {
  if (args.length !== 2 || args[0] !== '--work-dir') throw new Error('Usage: node inspect-pdf.mjs --work-dir <work-dir>');
  const work = path.resolve(args[1]);
  const receipt = JSON.parse(readFileSync(path.join(work, 'pdf-html/conversion.json'), 'utf8'));
  const session = `pdf-inventory-${process.pid}`;
  const browser = (...command) => execFileSync('agent-browser', ['--session', session, ...command], {
    encoding: 'utf8', timeout: 60000, maxBuffer: 2 * 1024 * 1024,
  });
  const start = Date.now();
  let report;
  try {
    browser('set', 'viewport', '1600', '900');
    browser('open', pathToFileURL(path.join(work, 'pdf-html/source.html')).href);
    let result = JSON.parse(browser('eval', '-b', Buffer.from(`(${inspectPDF.toString()})()`).toString('base64')).trim());
    if (typeof result === 'string') result = JSON.parse(result);
    report = result;
    if (report.pageCount !== receipt.pageCount || report.pages.some(page => !(page.width > 0 && page.height > 0)))
      throw new Error('Rendered page count/geometry differs from the conversion inventory');
    if (report.pages.some(page => page.backgrounds.some(image => !image.loaded)))
      throw new Error('Converted source has an unloaded background');
  } finally {
    try { browser('close'); } catch {}
  }
  report.elapsedSeconds = (Date.now() - start) / 1000;
  report.sourceSha256 = receipt.sourceSha256;
  const target = path.join(work, 'pdf-html/inspection.json');
  writeFileSync(target, JSON.stringify(report, null, 2) + '\n');
  const summary = path.join(work, 'pdf-html/inspection-summary.json');
  const overview = {pageCount: report.pageCount,
    dimensions: [...new Set(report.pages.map(page => `${page.width}x${page.height}`))],
    visibleStyles: [...new Set(report.pages.flatMap(page => page.visibleStyles.map(([style]) => style)))],
    columns: ['page', 'sourceId', 'backgroundFiles', 'visibleTextNodes', 'hiddenTextNodes', 'sourceTextSample'],
    pages: report.pages.map(page => [page.page, page.sourceId, page.backgrounds.map(image => image.file),
      page.text.visible, page.text.hidden, (page.text.visibleSample || page.text.hiddenSample).slice(0, 80)]),
    notes: report.notes};
  writeFileSync(summary, JSON.stringify(overview, null, 2) + '\n');
  console.log(JSON.stringify({inspection: target, summary, pageCount: report.pageCount,
    referenceOnlyPages: report.pages.filter(page => page.status === 'reference-only').map(page => page.page),
    visibleTextPages: report.pages.filter(page => page.text.visible).map(page => page.page),
    elapsedSeconds: report.elapsedSeconds}));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main(process.argv.slice(2));
