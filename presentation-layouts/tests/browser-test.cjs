/* Run with an externally installed playwright-core and Chromium; no dev server. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const {parseArgs} = require('node:util');
const {chromium} = require('playwright-core');
const {values} = parseArgs({options: {input: {type:'string'}, out: {type:'string'}}});
if (!values.input || !values.out) throw new Error('--input and --out are required');
const fitter = fs.readFileSync(path.resolve(__dirname, '../scripts/fit-text.js'), 'utf8');
const checks = [];
const check = (name, test) => { test(); checks.push({name, passed:true}); };

(async () => {
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium', headless:true, args:['--no-sandbox']});
  try {
    const page = await browser.newPage({viewport:{width:1600,height:900}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(pathToFileURL(path.resolve(values.input)).href);
    await page.evaluate(() => window.fixtureReady);
    const fixtures = await page.evaluate(() => window.fixtureReports);
    check('12 synthetic pages preserve source-size baselines', () => {
      assert.equal(fixtures.length,12);
      for (const report of fixtures) for (const region of report.regions) {
        assert.equal(region.status,'unchanged');
        assert.deepEqual(region.finalSizesPx,region.baselineSizesPx);
      }
      assert.deepEqual(errors,[]);
    });
    const bindings = JSON.parse(fs.readFileSync(path.join(path.dirname(path.resolve(values.input)), 'bindings.json'), 'utf8'));
    const roleSizes = await page.evaluate(() => [...document.querySelectorAll('.stage [data-text-role]')].map(element => ({skin:element.closest('.stage').dataset.skin, role:element.dataset.textRole, size:parseFloat(getComputedStyle(element).fontSize)})));
    check('rendered role sizes match compiled token baselines',()=>{for(const row of roleSizes) assert.equal(row.size,bindings[row.skin].resolved[`type.${row.role}.font-size`].value)});
    const markup = `<!doctype html><html><meta charset="utf-8"><style>body{margin:0}#root{display:block;width:900px;height:400px;font-family:sans-serif}.title{height:80px;width:800px;font-size:48px;line-height:1.5}.body{height:180px;width:420px;font-size:32px;line-height:1.5}</style><div id="root" class="okp-layout"><div class="title" data-fit-region="title"><span data-text-role="title">Stable title</span></div><div class="body" data-fit-region="body"><span class="base" data-text-role="body">短内容 / Short content</span><span class="small" data-text-role="body" style="font-size:16px"> small run</span></div></div><script>${fitter}</script></html>`;
    await page.setContent(markup);
    const policy = {roleBounds:{title:{minScale:0.75},body:{minScale:0.55}}};
    const run = p => page.evaluate(policy => OkpFit.fit(document.querySelector('#root'),policy),p || policy);
    let report = await run();
    check('short content unchanged',()=>assert(report.regions.every(r=>r.status==='unchanged')));
    await page.locator('.base').evaluate(e=>e.textContent='中文内容需要自动适配'.repeat(9));
    report = await run();
    const fitted = report.regions.find(r=>r.regionId==='body');
    check('only overflowing body fitted',()=>{assert.equal(fitted.status,'fitted');assert(fitted.scale>=0.55&&fitted.scale<1);assert.equal(report.regions[0].status,'unchanged');assert.equal(report.regions[0].finalSizesPx[0],48)});
    check('mixed run proportions preserved',()=>assert(Math.abs(fitted.finalSizesPx[0]/fitted.finalSizesPx[1]-2)<0.001));
    const repeated = await run();
    check('repeat starts at immutable baseline',()=>{assert.deepEqual(repeated.regions[1].baselineSizesPx,[32,16]);assert(Math.abs(repeated.regions[1].scale-fitted.scale)<0.001)});
    const serialized = await page.content();
    await page.setContent(serialized);
    const reloaded = await run();
    check('serialized reload does not treat fitted size as source',()=>assert.deepEqual(reloaded.regions[1].baselineSizesPx,[32,16]));
    await page.locator('.base').evaluate(e=>e.textContent='短内容 / Short content');
    report = await run();
    check('short replacement restores source sizes',()=>{assert.equal(report.regions[1].status,'unchanged');assert.deepEqual(report.regions[1].finalSizesPx,[32,16])});
    await page.locator('.base').evaluate(e=>e.textContent='非常密集的内容'.repeat(800));
    report = await run();
    check('cannot-fit returns unresolved without violating floor',()=>{assert.equal(report.regions[1].status,'unresolved');assert.deepEqual(report.regions[1].finalSizesPx,[32,16])});
    await page.locator('.base').evaluate(e=>e.textContent='中文内容需要自动适配'.repeat(9));
    report = await run({roleBounds:{title:{minScale:0.75}}});
    check('missing bound is not invented',()=>assert.equal(report.regions[1].status,'unresolved'));
    report = await run({roleBounds:{body:{enabled:false,minScale:0.55}}});
    check('explicit no-shrink respected',()=>assert.equal(report.regions[1].status,'unresolved'));
    report = await run({roleBounds:{body:{minFontSizePx:40}}});
    check('conflicting bound reported',()=>assert.equal(report.regions[1].reason,'FIT_BOUND_CONFLICT'));
    const originalBody = await page.locator('.body').innerHTML();
    await page.locator('.body').evaluate(e=>e.innerHTML='<div style="width:200px;height:60px;overflow:hidden"><span data-text-role="body">中文内容中文内容中文内容中文内容中文内容</span></div>');
    report = await run();
    check('nested clipping box measured, not hidden as a pass',()=>assert.equal(report.regions[1].status,'fitted'));
    await page.locator('.body').evaluate((e,html)=>e.innerHTML=html,originalBody);
    await page.evaluate(() => {
      const root = document.querySelector('#root');
      const slide = document.createElement('div');slide.hidden=true;slide.dataset.slide='hidden';
      root.replaceWith(slide);slide.append(root);
      const deck=document.createElement('main');deck.id='hidden-deck';slide.replaceWith(deck);deck.append(slide);
    });
    report = await page.evaluate(policy => OkpFit.fit(document.querySelector('#hidden-deck'),policy),policy);
    check('initially hidden slide measured and kept hidden',()=>assert.equal(report.regions.find(r=>r.regionId==='body').status,'fitted'));
    assert(await page.locator('[data-slide="hidden"]').evaluate(e=>e.hidden));
    await page.evaluate(()=>{document.body.innerHTML='<div id="root" class="okp-layout" style="width:0;height:0"><div data-fit-region="zero" style="width:0;height:0"><span data-text-role="body">text</span></div></div>'});
    report = await run();
    check('zero geometry not a pass',()=>assert.equal(report.regions[0].status,'unmeasurable'));
    await page.setContent(markup.replace('</div><script>', '<img src="data:image/png;base64,aW52YWxpZA=="></div><script>'));
    report = await run();
    check('broken image readiness not a pass',()=>assert(report.regions.every(r=>r.status==='unmeasurable')));
    const result = {timestamp:new Date().toISOString(),chromium:browser.version(),fixturePages:12,fixtureRegions:fixtures.reduce((n,r)=>n+r.regions.length,0),checks,fixtureReports:fixtures,limitations:['Synthetic acceptance, not a real extracted template','No production first-pass rate or speed comparison','No source font availability guarantee']};
    fs.mkdirSync(path.dirname(path.resolve(values.out)),{recursive:true});
    fs.writeFileSync(values.out,JSON.stringify(result,null,2)+'\n');
    console.log(JSON.stringify({passed:checks.length,fixturePages:12,fixtureRegions:result.fixtureRegions,out:values.out}));
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1});
