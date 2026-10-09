const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const metrics = read('scripts/dom-metrics.js');
const fitter = read('scripts/fit-text.js');
const navigation = read('scripts/navigation.js');
const audit = read('tools/audit.js');
const config = {minFontSizePx: 10, expectedPages: 3, safeArea: {left:.05, right:.05, top:.07, bottom:.07}, requiredChrome: [], allowedFontFallbacks: [], minContrastRatio:3};
const css = `*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;font-family:Arial,sans-serif}.deck{height:100vh;overflow-y:auto}.slide{height:900px;position:relative}.stage{width:1600px;height:900px;position:relative;background:white;color:#18212f}.fit{position:absolute;inset:70px 80px;display:flex;flex-direction:column;gap:24px}h1{font-size:48px;line-height:1.2;margin:0}.body{flex:1;min-height:0;font-size:28px;line-height:1.2}p{margin:0}footer{position:absolute;bottom:20px;left:80px;font-size:18px}`;
const slide = body => `<section class="slide"><div class="stage"><main class="fit"><header data-fit-region="title"><h1 data-text-role="title">Source title</h1></header><div class="body" data-fit-region="body">${body}</div></main><footer data-chrome="footer">Source footer</footer></div></section>`;
const html = (body='<p>Visible source content</p>', count=3, extra='') => `<!doctype html><html><head><meta charset="utf-8"><style>${css}${extra}</style></head><body><div class="deck">${Array.from({length:count},()=>slide(body)).join('')}</div></body></html>`;
const results = [];
(async () => {
  const browser = await chromium.launch({headless:true, ...(process.env.CHROMIUM_PATH ? {executablePath:process.env.CHROMIUM_PATH} : {}), args:['--no-sandbox']});
  const page = await browser.newPage({viewport:{width:1600,height:900}, reducedMotion:'reduce'});
  async function setup(source=html(), fit=false, overrides={}) {
    await page.setContent(source);
    await page.evaluate(cfg => {window.PRESENTATION_QA_CONFIG=cfg}, {...config,...overrides});
    await page.addScriptTag({content:metrics});
    await page.evaluate(()=>{for(const element of document.querySelectorAll('text[data-source-size]'))element.style.fontSize=`${Number(element.dataset.sourceSize)/window.PresentationMetrics.fontFactor(element)}px`});
    await page.addScriptTag({content:navigation});
    if (fit) {
      await page.addScriptTag({content:fitter});
      await page.evaluate(async()=>{await window.PresentationFit.ready;});
    } else await page.evaluate(()=>{window.PresentationFit={report:{status:'READY',regions:[],errors:[]}}});
  }
  async function inspect() {return JSON.parse(await page.evaluate(audit));}
  async function test(name, run) {
    await run(); results.push({name,status:'passed'}); console.log(`PASS ${name}`);
  }
  async function blocked(name, source, code, mutate, overrides={}) {
    await test(name, async()=>{
      await setup(source,false,overrides); if(mutate) await page.evaluate(mutate);
      const report=await inspect();
      assert.equal(report.status,'BLOCKED',JSON.stringify(report)); assert.ok(report.blocking[code],JSON.stringify(report));
    });
  }
  await test('positive reference and real four-key navigation',async()=>{await setup(html());assert.equal((await inspect()).status,'READY_TO_PUBLISH');});
  await blocked('8px cannot pass final QA',html('<p style="font-size:8px">Small text</p>'),'smallText');
  await blocked('9.99px boundary is rejected',html('<p style="font-size:9.99px">Small text</p>'),'smallText');
  await test('10px boundary is accepted',async()=>{await setup(html('<p style="font-size:10px">Readable text</p>'));assert.equal((await inspect()).status,'READY_TO_PUBLISH');});
  await blocked('zero pages cannot publish',html('',0),'deckStructure');
  await blocked('requested count cannot be inferred from output',html(),'pageCount',null,{expectedPages:4});
  await blocked('indirect slides are unreachable',html().replace('<div class="deck">','<div class="deck"><div>').replace('</div></body>','</div></div></body>'),'deckStructure');
  await blocked('same foreground and background',html('<p style="color:white">Invisible ink</p>'),'lowContrast');
  await blocked('same ink over a filled SVG shape',html('<svg width="200" height="120" viewBox="0 0 200 120"><rect width="200" height="120" fill="black"/><text x="20" y="80" style="font-size:24px;fill:black">Hidden SVG</text></svg>'),'lowContrast');
  await blocked('negative margin crosses the source safe area',html('<p style="margin-left:-110px">Outside source margin</p>'),'textOverflow');
  await blocked('ancestor clipping is blocking',html('<div style="height:18px;overflow:hidden"><p>One line<br>Another line</p></div>'),'textOverflow');
  await blocked('hidden text cannot clear an overflow',html('<p style="opacity:0">Hidden content</p>'),'hiddenText');
  await blocked('unresolved fit-floor flag is blocking',html('<p data-overflow="fit-floor">Unresolved text</p>'),'unresolvedFit');
  await blocked('an image outside a photocell is still checked',html('<img src="data:image/png;base64,AAAA" alt="broken">'),'brokenImage');
  await blocked('required source chrome must be present',html(),'requiredChrome',null,{requiredChrome:[{role:'logo',min:1,max:1}]});
  await blocked('no foreign default safe area',html(),'invalidConfig',null,{safeArea:null});
  await blocked('text-bearing pseudo-element below floor',html('<p class="tiny">Source</p>',3,'.tiny:after{content:"caption";font-size:8px}'),'smallText');
  await blocked('SVG viewBox scaling counts toward the floor',html('<svg width="100" height="100" viewBox="0 0 1000 1000"><text x="10" y="100" style="font-size:40px;fill:currentColor">Small SVG</text></svg>'),'smallText');
  await blocked('collapsed positive plot is blocking',html('<div data-plot-mark data-value="3" style="height:0px;width:40px"></div><p>Three</p>'),'collapsedChart');
  await blocked('title and body ink collision',html('<p style="position:absolute;top:5px">Over title</p>'),'titleBodyOverlap');
  await blocked('disabled left, up and down are all rejected',html().replace('</body>','<script>window.addEventListener("keydown",event=>{if(["ArrowLeft","ArrowUp","ArrowDown"].includes(event.key))event.stopImmediatePropagation()},true)</script></body>'),'keyboardNavigation');
  await blocked('failed used webfont despite loaded set',html('<p style="font-family:BrokenProbe,Arial">Font probe</p>'),'fontLoad',async()=>{
    const face=new FontFace('BrokenProbe','url(data:font/woff2;base64,AAAA)');document.fonts.add(face);await face.load().catch(()=>{});await document.fonts.ready;
  });
  await test('gradient ground is explicitly review-required',async()=>{await setup(html('<p style="background-image:linear-gradient(white,#eee)">Review the ground</p>'));assert.equal((await inspect()).status,'NEEDS_VISUAL_REVIEW');});
  await test('automatic floor applies even without overflow',async()=>{
    await setup(html('<p style="font-size:8px">Originally eight</p>'),true);
    const sizes=await page.evaluate(()=>[...document.querySelectorAll('.body p')].map(window.PresentationMetrics.logicalFontSize));
    assert.ok(sizes.every(size=>size>=9.999));assert.equal((await inspect()).status,'READY_TO_PUBLISH');
  });
  await test('measured search goes below the old 80% cutoff',async()=>{
    await setup(html(`<p style="font-size:80px">${'A meaningful finding with supporting evidence. '.repeat(60)}</p>`),true);
    const fit=await page.evaluate(()=>window.PresentationFit.report);
    assert.equal(fit.status,'READY',JSON.stringify(fit)); assert.ok(fit.regions.some(region=>region.status==='fitted' && region.scale<.8));
    assert.equal((await inspect()).status,'READY_TO_PUBLISH');
  });
  await test('CJK and mixed runs fit without losing content',async()=>{
    const content='中文内容与 English evidence 保持完整。'.repeat(100);
    await setup(html(`<p style="font-size:70px">${content}<strong>重点</strong><span style="font-size:12px">脚注</span></p>`),true);
    const state=await page.evaluate(()=>window.PresentationFit.report);
    assert.equal(state.status,'READY',JSON.stringify(state));
    assert.equal(await page.locator('.body p').first().textContent(),content+'重点脚注');
    assert.equal((await inspect()).status,'READY_TO_PUBLISH');
  });
  await test('unfit-at-10px remains blocked without clipping',async()=>{
    await setup(html('<p>'+('Too much factual content '.repeat(2500))+'</p>'),true);
    const report=await page.evaluate(()=>window.PresentationFit.report);assert.equal(report.status,'BLOCKED');
    assert.ok(report.regions.some(region=>region.status==='unresolved'));
    assert.ok((await inspect()).blocking.unresolvedFit);
  });
  await test('rerun, edit and serialized reload restore immutable styles',async()=>{
    await setup(html(`<p style="font-size:80px">${'A meaningful finding. '.repeat(180)}</p>`),true);
    const initial=await page.locator('.body p').first().evaluate(el=>getComputedStyle(el).fontSize);
    await page.evaluate(async()=>{await window.PresentationFit.fit()});
    assert.equal(await page.locator('.body p').first().evaluate(el=>getComputedStyle(el).fontSize),initial);
    const serialized=await page.content();await setup(serialized,true);
    assert.equal(await page.locator('.body p').first().evaluate(el=>getComputedStyle(el).fontSize),initial);
    await page.evaluate(async()=>{for(const el of document.querySelectorAll('.body p'))el.textContent='Short';await window.PresentationFit.fit()});
    assert.equal(await page.locator('.body p').first().evaluate(el=>getComputedStyle(el).fontSize),'80px');
  });
  await test('viewport stage zoom does not change the logical floor',async()=>{
    await setup(html('<p style="font-size:10px">Logical ten</p>',3,'.stage{transform:scale(.5);transform-origin:top left}'));
    assert.equal((await inspect()).status,'READY_TO_PUBLISH');
  });
  await test('hidden-page display is measured and restored',async()=>{
    const source=html().replaceAll('class="slide"','class="slide" data-fit-display="block" hidden');
    await setup(source,true);assert.equal((await page.evaluate(()=>window.PresentationFit.report)).status,'READY');
    assert.ok((await inspect()).blocking.keyboardNavigation);assert.equal(await page.locator('.slide[hidden]').count(),3);
  });
  await test('explicit fallback handles a failed used font',async()=>{
    await setup(html('<p style="font-family:BrokenProbe,Arial">Font fallback</p>'),false,{allowedFontFallbacks:['BrokenProbe']});
    await page.evaluate(async()=>{const face=new FontFace('BrokenProbe','url(data:font/woff2;base64,AAAA)');document.fonts.add(face);await face.load().catch(()=>{})});
    assert.equal((await inspect()).status,'READY_TO_PUBLISH');
  });
  await test('all background image failures block shared readiness',async()=>{
    await setup(html('<p>Background asset</p>',3,'.body{background-image:url(data:image/png;base64,AAAA)}'),true);
    const state=await page.evaluate(()=>window.PresentationFit.report);assert.equal(state.status,'BLOCKED');
    assert.ok(state.errors.some(error=>error.includes('background image failed')));assert.equal((await inspect()).status,'BLOCKED');
  });
  await test('SVG effective floor is applied automatically',async()=>{
    await setup(html('<svg width="100" height="100" viewBox="0 0 1000 1000"><text x="10" y="300" style="font-size:40px;fill:currentColor">SVG</text></svg>'),true);
    assert.ok(await page.locator('svg text').first().evaluate(el=>window.PresentationMetrics.logicalFontSize(el)>=10));
    assert.equal((await inspect()).status,'READY_TO_PUBLISH');
  });
  await test('nested fit regions fail closed',async()=>{
    await setup(html('<div data-fit-region="nested"><p>Nested region</p></div>'),true);
    assert.equal((await page.evaluate(()=>window.PresentationFit.report)).status,'BLOCKED');
  });
  await test('font families, weights and palette survive fitting',async()=>{
    await setup(html(`<p style="font-size:70px;font-weight:700;color:#172535">${'Preserved source style. '.repeat(160)}</p>`),true);
    const style=await page.locator('.body p').first().evaluate(el=>{const s=getComputedStyle(el);return[s.fontFamily,s.fontWeight,s.color]});
    assert.deepEqual(style,['Arial, sans-serif','700','rgb(23, 37, 53)']);assert.equal((await inspect()).status,'READY_TO_PUBLISH');
  });
  await test('visual-review coverage is not silently capped at 30 pages',async()=>{
    await setup(html('<p style="background-image:linear-gradient(white,#eee)">Review each page</p>',35),false,{expectedPages:35});
    const report=await inspect();assert.equal(report.status,'NEEDS_VISUAL_REVIEW');assert.equal(new Set(report.reviewRequired.map(item=>item.page)).size,35);
  });
  if(process.env.FIXTURE_DIR) {
    for(const filename of fs.readdirSync(process.env.FIXTURE_DIR).filter(name=>name.endsWith('.html')).sort()) {
      await test(`all 54 local references: ${filename}`,async()=>{
        await setup(fs.readFileSync(path.join(process.env.FIXTURE_DIR,filename),'utf8'),true,{expectedPages:54});
        const report=await inspect();assert.equal(report.status,'READY_TO_PUBLISH',JSON.stringify(report));
        assert.equal(report.pages,54);assert.equal(report.navigableSlides,54);
      });
    }
  }
  await browser.close();
  const out=process.env.BROWSER_REPORT || path.join(__dirname,'browser-report.json');
  fs.writeFileSync(out,JSON.stringify({status:'passed',checks:results.length,results},null,2)+'\n');
})().catch(error=>{console.error(error);process.exit(1)});
