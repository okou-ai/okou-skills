import assert from 'node:assert/strict';
import {after, before, test} from 'node:test';
import {chromium} from 'playwright';
import {inspectPDF} from '../scripts/inspect-pdf.mjs';

let browser;
before(async () => { browser = await chromium.launch({executablePath: process.env.PRESENTATION_CHROMIUM_PATH, headless: true}); });
after(async () => { await browser?.close(); });

test('computed visibility distinguishes flattened, mixed and editable candidates without a DOM dump', async t => {
  const page = await browser.newPage();
  t.after(() => page.close());
  await page.setContent(`<style>.pf{width:792px;height:445.5px}.pc{display:none}.hidden{visibility:hidden}</style>
    <div class="pf" id="pf1" data-page-no="1"><div class="pc"><div class="t hidden">Hidden glyphs</div></div></div>
    <div class="pf" id="pf24" data-page-no="24"><div class="pc">
      <div class="t">Visible text</div><div class="t" style="color:transparent">Transparent glyphs</div>
      <div style="opacity:0"><div class="t">Transparent ancestor</div></div>
      <div class="t" style="-webkit-text-fill-color:transparent">Transparent fill</div>
      <div class="t hidden"><span style="visibility:visible">Visible override</span></div>
    </div></div>`);
  const result = await page.evaluate(inspectPDF);
  assert.equal(result.pageCount, 2);
  assert.equal(result.pages[0].status, 'reference-only');
  assert.equal(result.pages[0].text.hidden, 1);
  assert.equal(result.pages[1].sourceId, 'pf24');
  assert.equal(result.pages[1].text.visible, 2);
  assert.equal(result.pages[1].text.hidden, 3);
  assert.equal(result.pages[1].status, 'visible-text-needs-slot-review');
  assert.deepEqual([result.pages[1].width, result.pages[1].height], [792, 445.5]);
  assert.equal(await page.locator('.pc').first().evaluate(node => getComputedStyle(node).display), 'none');
});

test('source samples remain bounded and failed background loads remain explicit', async t => {
  const page = await browser.newPage();
  t.after(() => page.close());
  await page.setContent(`<div class="pf" style="width:792px;height:445.5px"><div class="pc">
    <img class="bi" src="data:image/png;base64,invalid"><div class="t">${'x'.repeat(100000)}</div></div></div>`);
  const result = await page.evaluate(inspectPDF);
  assert.equal(result.pages[0].text.visibleSample.length, 120);
  assert.equal(result.pages[0].backgrounds[0].loaded, false);
  assert.ok(JSON.stringify(result).length < 2000);
});
