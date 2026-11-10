#!/usr/bin/env python3
# Modified by Okou: local-only input, fail-closed PDF checks, full required-copy
# matching and advisory style guidance; based on the pinned Folio source.
"""
brochure-design preflight — check rendered layout, copy and PDF fonts.

Usage
  python preflight.py brochure.html                 # print target (300 ppi goal)
  python preflight.py brochure.html --target digital  # screen/email PDF thresholds
  python preflight.py brochure.html --pdf out/brochure.pdf   # also check embedded fonts
  python preflight.py brochure.html --json report.json

Exit code 1 if any ERROR. Every finding names the page and element so you can fix it.

Checks
  ERROR  hidden overflow (text cut off by overflow:hidden / page edge), missing images,
         text below 6.5 pt, placeholder copy (lorem, "Headline Here", [[TK]]),
         effective image resolution below the floor, fallback fonts in the PDF,
         kit sample text or slot photos still in place (kit-sample)
  WARN   text inside the safe zone, text-on-text collisions, long measures,
         low contrast, images below the target resolution, web-UI tells
         (card shadows, side-stripe borders, gradient text, emoji icons, reflex fonts),
         layout monotony (same page structure repeated), no page furniture
  INFO   text over photos (check visually), all-quiet rhythm, pages that look underfilled,
         generic marketing / AI words (unleash, seamless, vibrant, "where X meets Y" …), dash-heavy prose
  WARN   same photo or paragraph on two pages (dup-image, dup-copy)
  WARN   humanizer tells: not-X-but-Y contrasts, slogan rows of fragments ("Learn. Grow. Thrive.")
  --copy copy.txt  UTF-8 required copy, one complete required string per line;
                   full strings (including short names/contacts) must appear.
                   Copy tells that come from the client's own text are skipped
  Self-test: python -m doctest preflight.py
  Page fill: quiet text pages are measured for a ragged foot (content stopping far above the
  margin) and mid-page holes — set data-type="cover|opener|hero|closing" or data-intent="breathing"
  on pages where open space is the design.
"""
import argparse, json, math, re, subprocess, sys
sys.dont_write_bytecode = True
from pathlib import Path

REFLEX_FONTS = ["inter", "roboto", "open sans", "montserrat", "arial", "helvetica", "lato",
                "dm sans", "space grotesk", "plus jakarta sans", "outfit", "fraunces",
                "playfair display", "cormorant", "cormorant garamond", "ibm plex sans",
                "instrument sans", "instrument serif", "syne", "newsreader", "lora",
                "crimson pro", "crimson text", "dm serif display", "space mono", "ibm plex mono",
                "system-ui", "sans-serif", "serif", "times new roman", "times", "georgia", "calibri", "cambria", "verdana", "tahoma", "trebuchet ms", "comic sans ms", "comic sans", "segoe ui", "century gothic", "courier new", "garamond", "book antiqua", "poppins", "source sans pro", "source sans 3", "nunito", "raleway", "oswald", "anton", "bebas neue"]
FALLBACK_PDF_FONTS = ["DejaVu", "Liberation", "FreeSans", "FreeSerif", "Bitstream", "Nimbus", "Carlito", "Caladea"]

JS = r"""
(opts) => {
  const PX_PER_MM = 96 / 25.4, PT = 0.75;
  const out = [];
  const add = (level, page, code, msg, el) => out.push({level, page, code, msg,
      el: el ? describe(el) : null});
  function describe(el) {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    if (el.classList.length) s += '.' + [...el.classList].slice(0, 3).join('.');
    const t = (el.innerText || el.alt || '').trim().replace(/\s+/g, ' ').slice(0, 48);
    return t ? `${s} “${t}”` : s;
  }
  const pages = [...document.querySelectorAll('.page')];
  const safeMM = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--safe')) || 5;
  const safe = safeMM * PX_PER_MM;
  const spineMM = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--safe-spine')) || 9;
  const spineSafe = spineMM * PX_PER_MM;
  const sigs = [];
  const firstFams = new Map();   // first family of each text stack -> the stand-in after it
  const loud = [];

  const ownText = el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 0);
  const textRects = el => {
    const rs = [];
    for (const n of el.childNodes) if (n.nodeType === 3 && n.textContent.trim()) {
      const r = document.createRange(); r.selectNodeContents(n);
      for (const q of r.getClientRects()) if (q.width > 0.5 && q.height > 0.5) rs.push(q);
    }
    return rs;
  };
  const bgOf = el => {
    for (let e = el; e && e !== document.body; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
      const m = cs.backgroundColor.match(/rgba?\(([^)]+)\)/);
      if (m) { const v = m[1].split(',').map(Number); if (v.length < 4 || v[3] > 0.95) return v.slice(0, 3); }
    }
    return [255, 255, 255];
  };
  const opaque = s => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(',').map(Number);
    return v.length === 4 && v[3] < .9 ? null : v.slice(0, 3); };
  // what is visually underneath a text rect? walks the paint stack at its centre
  const layerUnder = (e, r) => {
    const own = opaque(getComputedStyle(e).backgroundColor);  // pills, chips, tags paint their own ground
    if (own) return { color: own };
    const stack = document.elementsFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    for (const s of stack) {
      if (s === e || e.contains(s) || s.closest('[data-texture]')) continue;
      if (s.tagName === 'IMG' || s.tagName === 'VIDEO' || s.tagName === 'CANVAS') return { img: s };
      const cs = getComputedStyle(s);
      if (cs.backgroundImage && cs.backgroundImage !== 'none' && !cs.backgroundImage.startsWith('repeating')) return { img: s };
      const c = opaque(cs.backgroundColor);
      if (c) return { color: c };
    }
    return { color: [255, 255, 255] };
  };
  const shrink = r => ({ left: r.left + 0.5, right: r.right - 0.5, top: r.top + r.height * 0.2, bottom: r.bottom - r.height * 0.22,
                         width: r.width, height: r.height * 0.58 });
  const lum = c => { const f = x => { x /= 255; return x <= .03928 ? x / 12.92 : Math.pow((x + .055) / 1.055, 2.4); };
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]); };
  const ratio = (a, b) => { const A = lum(a), B = lum(b); return (Math.max(A, B) + .05) / (Math.min(A, B) + .05); };
  const rgb = s => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(',').map(Number);
    return v.length === 4 && v[3] < .5 ? null : v.slice(0, 3); };
  const inter = (a, b) => Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left)) *
                          Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));

  pages.forEach((pg, pi) => {
    const P = pi + 1;
    pg.scrollIntoView({ block: 'start' });
    const spineLeft = P % 2 === 1;   // recto: spine on the left
    const single = pg.classList.contains('single');   // posters, flyers, fold panels: no spine
    const trimEl = pg.querySelector('.trim') || pg;
    const T = trimEl.getBoundingClientRect();
    const PR = pg.getBoundingClientRect();
    const area = T.width * T.height;
    const all = [...pg.querySelectorAll('*')];
    const texts = all.filter(e => ownText(e) && getComputedStyle(e).visibility !== 'hidden' && getComputedStyle(e).display !== 'none');
    const imgs = [...pg.querySelectorAll('img')].filter(i => !i.closest('[data-texture]'));  // textures are not photos

    // ---- overflow (clipped text) ----
    all.forEach(e => {
      const cs = getComputedStyle(e);
      const clips = ['hidden', 'clip', 'auto', 'scroll'].includes(cs.overflowY) || ['hidden', 'clip', 'auto', 'scroll'].includes(cs.overflowX);
      if (!clips || e === pg || e.tagName === 'IMG' || e.classList.contains('ph') || e.classList.contains('spread-img')) return;
      if (!e.innerText || !e.innerText.trim()) return;
      if (e.scrollHeight > e.clientHeight + 2 || e.scrollWidth > e.clientWidth + 2)
        add('ERROR', P, 'overflow', `text is cut off (${e.scrollHeight - e.clientHeight}px hidden) — shorten copy, reduce size or give the block more room`, e);
    });
    // multi-column overflow: columns spill sideways
    all.filter(e => { const c = getComputedStyle(e).columnCount; return c && c !== 'auto'; }).forEach(e => {
      if (e.scrollWidth > e.clientWidth + 2) add('ERROR', P, 'overflow', 'multi-column text overflows into an extra column', e);
    });

    // ---- text placement, size, contrast ----
    const boxes = [];
    texts.forEach(e => {
      const cs = getComputedStyle(e);
      const rs = textRects(e);
      if (!rs.length) return;
      const fsPt = parseFloat(cs.fontSize) * PT;
      const chars = e.textContent.trim().length;
      const allowEdge = e.closest('[data-allow-edge]');
      rs.forEach(r => {
        if (r.right < PR.left || r.left > PR.right || r.bottom < PR.top || r.top > PR.bottom) return;
        const g = shrink(r);
        if (g.left < T.left - 1 || g.right > T.right + 1 || g.top < T.top - 1 || g.bottom > T.bottom + 1) {
          if (!allowEdge) {
            if (fsPt >= 40) add('WARN', P, 'off-trim', 'display type runs off the page — fine if it is a deliberate bleed (add data-allow-edge)', e);
            else add('ERROR', P, 'off-trim', 'text runs past the trim edge and will be cut off', e);
          }
        } else if (!allowEdge && fsPt < 40) {
          const inL = !single && spineLeft ? spineSafe : safe, inR = !single && !spineLeft ? spineSafe : safe;
          const atSpine = !single && (spineLeft ? g.left < T.left + inL - 1 : g.right > T.right - inR + 1);
          if (g.left < T.left + inL - 1 || g.right > T.right - inR + 1)
            add('WARN', P, atSpine ? 'spine' : 'safe-zone',
                atSpine
                  ? `text within ${spineMM}mm of the spine — binding will swallow it` : `text within ${safeMM}mm of the trim — risky after cutting`, e);
          else if (g.top < T.top + safe - 1 || g.bottom > T.bottom - safe + 1)
            add('WARN', P, 'safe-zone', `text within ${safeMM}mm of the trim — risky after cutting`, e);
        }
      });
      if (fsPt < 6.5) add('ERROR', P, 'tiny-type', `${fsPt.toFixed(1)}pt text is unreadable in print (floor 6.5pt)`, e);
      else if (fsPt < 7.5 && chars > 90) add('WARN', P, 'small-type', `${chars} chars set at ${fsPt.toFixed(1)}pt — too small for running text`, e);
      if (!opts.digital && fsPt > 12.5 && chars > 350 && e.tagName === 'P')
        add('WARN', P, 'web-scale', `${fsPt.toFixed(1)}pt running text reads like a web page; brochure body is 8.5–10pt`, e);
      // measure
      if (e.tagName === 'P' && chars > 220) {
        const w = Math.max(...rs.map(r => r.width));
        const cpl = w / (parseFloat(cs.fontSize) * 0.5);
        if (cpl > 82) add('WARN', P, 'measure', `~${Math.round(cpl)} characters per line — split into columns (aim 40–70)`, e);
      }
      // centred paragraphs
      if (e.tagName === 'P' && cs.textAlign === 'center' && rs.length > 4)
        add('INFO', P, 'centered', `${rs.length}-line centred paragraph — centre only short display text`, e);
      // contrast
      const fg = rgb(cs.color);
      const layers = [rs[0], rs[rs.length - 1]].map(r => layerUnder(e, r));
      const onImg = layers.find(l => l.img);
      const decorative = chars <= 2 || !!e.closest('[aria-hidden="true"]');   // ghost words and ornaments are marked aria-hidden
      if (onImg) { if (!decorative) add('INFO', P, 'on-photo', 'text sits on a photograph — confirm legibility in the PNG preview', e); }
      else if (fg) {
        const bg = layers[0].color;
        const cr = ratio(fg, bg);
        const large = fsPt >= 18 || (fsPt >= 14 && parseInt(cs.fontWeight) >= 700);
        if (cr < (large ? 3 : 4.5))
          add(decorative ? 'INFO' : cr < 2.5 ? 'ERROR' : 'WARN', P, 'contrast', `contrast ${cr.toFixed(2)}:1 (${large ? 'needs 3' : 'needs 4.5'})${decorative ? ' — decorative glyph' : ''}`, e);
      }
      // placeholder copy
      const txt = e.textContent;
      if (/lorem ipsum|dolor sit amet|headline here|title goes here|your (title|text|logo) here|\[\[\s*TK|xxx|reallygreatsite|123 anywhere st|any city, st|\+123-456-7890|larana,? inc/i.test(txt))
        add('ERROR', P, 'placeholder', 'placeholder / to-come copy in the document', e);
      // emoji as icons in headings
      if (/^H[1-6]$/.test(e.tagName) && /\p{Extended_Pictographic}/u.test(txt))
        add('WARN', P, 'emoji', 'emoji used as a heading icon — reads as chat UI, not print', e);
      // Advisory font heuristic: posters use expressive faces throughout; brochures use them for
      // headings and on cover, back-cover and contents pages. Body text may use a common face. Tamil is exempt.
      const stack = cs.fontFamily.split(',').map(f => f.replace(/["']/g, '').trim());
      const fam = stack[0].toLowerCase();
      const display = /^H[1-3]$/.test(e.tagName) || fsPt >= 20 || single ||
        ['cover', 'closing', 'contents'].includes(pg.dataset.type || (pi === 0 ? 'cover' : ''));
      if (display && !e.closest('[lang="ta"]') && opts.reflex.includes(fam) && !opts.brandFonts.includes(fam))
        boxes.push({reflex: fam});
      if (!e.closest('[lang="ta"]')) firstFams.set(stack[0], stack[1] || '');
      rs.forEach(r => boxes.push({r: shrink(r), e}));
    });
    // reflex font summary (once per page)
    const rf = [...new Set(boxes.filter(b => b.reflex).map(b => b.reflex))];
    if (rf.length) add('WARN', P, 'reflex-font', `common font in a display role: ${rf.join(', ')} — posters, and brochure headings, covers, back covers and contents, use aesthetic faces (typography.md → Aesthetic roster)`);

    // ---- text collisions ----
    const tb = boxes.filter(b => b.r);
    let hits = 0;
    for (let a = 0; a < tb.length && hits < 6; a++) for (let b = a + 1; b < tb.length && hits < 6; b++) {
      const A = tb[a], B = tb[b];
      if (A.e === B.e || A.e.contains(B.e) || B.e.contains(A.e)) continue;
      if (A.e.closest('[data-allow-overlap]') || B.e.closest('[data-allow-overlap]')) continue;
      const o = inter(A.r, B.r);
      if (o > Math.min(A.r.width * A.r.height, B.r.width * B.r.height) * 0.12) { hits++; add('WARN', P, 'collision', `text overlaps “${(B.e.innerText || '').trim().slice(0, 30)}” — mark data-allow-overlap if intentional`, A.e); }
    }

    // ---- images ----
    const floor = opts.digital ? 96 : 150, target = opts.digital ? 144 : 250;
    imgs.forEach(im => {
      if (!im.complete || im.naturalWidth === 0) { add('ERROR', P, 'missing-image', `image failed to load: ${im.getAttribute('src')}`, im); return; }
      if (/\.svg([?#]|$)/i.test(im.currentSrc || im.src)) return;  // vector art has no ppi
      const r = im.getBoundingClientRect();
      const vis = inter(r, PR);
      if (vis < 4) return;
      const fit = getComputedStyle(im).objectFit;
      const sx = r.width / im.naturalWidth, sy = r.height / im.naturalHeight;
      const s = fit === 'cover' ? Math.max(sx, sy) : fit === 'contain' ? Math.min(sx, sy) : Math.max(sx, sy);
      const ppi = 96 / s;
      if (ppi < floor) add('ERROR', P, 'low-res', `image prints at ~${Math.round(ppi)} ppi (floor ${floor}) — use a larger original or a smaller frame`, im);
      else if (ppi < target) add('WARN', P, 'low-res', `image prints at ~${Math.round(ppi)} ppi (aim ≥ ${target})`, im);
    });

    // masked shapes (circles, arcs) sliced by the spine
    imgs.forEach(im => {
      const holder = im.closest('.ph') || im;
      const cs = getComputedStyle(holder);
      const masked = cs.clipPath !== 'none' || parseFloat(cs.borderTopLeftRadius) > 20;
      if (single || !masked || holder.closest('.spread-img')) return;
      const r = holder.getBoundingClientRect();
      const crosses = spineLeft ? (r.left < T.left - 2 * PX_PER_MM && r.right < T.right - 5) : (r.right > T.right + 2 * PX_PER_MM && r.left > T.left + 5);
      if (crosses) add('WARN', P, 'spine-mask', 'a masked shape is cut by the spine — it will disappear into the binding; move it to the outer edge', im);
    });

    // ---- advisory decorative-rule detector; intentional rules may be retained ----
    const rules = all.filter(e => { const cs = getComputedStyle(e), r = e.getBoundingClientRect();
      if (e.closest('table,[data-allow-rule]') || /^table|^inline$/.test(cs.display) || r.width < 10 * PX_PER_MM) return false;
      if (e.tagName === 'HR') return true;
      const b = s => parseFloat(cs[`border${s}Width`]) > 0 && cs[`border${s}Style`] !== 'none' && rgb(cs[`border${s}Color`]);
      if ((b('Top') || b('Bottom')) && !b('Left') && !b('Right') && !opaque(cs.backgroundColor)) return true;
      return r.height <= 1.2 * PX_PER_MM && !e.children.length && !e.textContent.trim() && (rgb(cs.backgroundColor) || cs.backgroundImage !== 'none'); });
    if (rules.length) add('WARN', P, 'rule-heavy', `${rules.length} decorative rule(s) — lines under or above text read as generated; separate with space, type size or a colour field (data-allow-rule for a real table rule)`, rules[0]);
    // sample facts written to fill a page must never reach print unnoticed
    pg.querySelectorAll('[data-sample]').forEach(e => add('INFO', P, 'sample-fact', `sample fact, not from the client — confirm before printing: “${e.textContent.trim().slice(0, 60)}”`, e));

    // ---- web-UI tells ----
    let shadows = 0, stripes = 0, rounded = 0, gradText = 0;
    all.forEach(e => {
      const cs = getComputedStyle(e);
      if (cs.boxShadow !== 'none' && !e.classList.contains('page')) shadows++;
      const bl = parseFloat(cs.borderLeftWidth), br = parseFloat(cs.borderRightWidth), bt = parseFloat(cs.borderTopWidth), bb = parseFloat(cs.borderBottomWidth);
      if ((bl > 1.5 && br === 0 && bt === 0 && bb === 0) || (br > 1.5 && bl === 0 && bt === 0 && bb === 0)) stripes++;
      const rad = parseFloat(cs.borderTopLeftRadius);
      if (rad > 6 && cs.clipPath === 'none' && !e.closest('[data-allow-round]') && (e.querySelector('img') || (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && e.innerText && e.innerText.length > 40))) rounded++;
      if ((cs.webkitBackgroundClip === 'text' || cs.backgroundClip === 'text') && cs.backgroundImage.includes('gradient')) gradText++;
    });
    if (shadows) add('WARN', P, 'web-shadow', `${shadows} element(s) with box-shadow — drop shadows on print pages read as web cards`);
    if (stripes) add('WARN', P, 'side-stripe', `${stripes} side-stripe border(s) — the #1 templated-callout tell; use a full rule, a tint field or a number`);
    if (rounded >= 3) add('WARN', P, 'rounded-cards', `${rounded} rounded boxes holding text/photos — a web card grid, not a page layout`);
    if (gradText) add('WARN', P, 'gradient-text', 'gradient-filled text');

    // ---- rotated headlines: readers must not tilt their heads (small rails and tabs are fine) ----
    // kit sample text or slot photos still in place (kit.py new marks them)
    const ks = pg.querySelectorAll('[data-kit-sample]');
    if (ks.length) add('ERROR', P, 'kit-sample', `${ks.length} kit sample element(s) still in place — write the client's text / place their photo, then remove data-kit-sample`, ks[0]);

    // 'upside' = upside-down or reading bottom-to-top (always wrong); 'vertical' = reads top to bottom (magazines may allow it)
    const turned = n => { let v = false; for (; n && n !== pg; n = n.parentElement) { const c = getComputedStyle(n);
      if (c.writingMode.startsWith('sideways-lr')) return 'upside';
      if (!c.writingMode.startsWith('horizontal')) v = true;
      if (c.transform !== 'none') { const m = new DOMMatrix(c.transform);
        if (m.a < -0.5 || m.b < -0.5) return 'upside';
        if (m.b > 0.5) v = true; } } return v && 'vertical'; };
    const big = texts.filter(e => parseFloat(getComputedStyle(e).fontSize) * 0.75 >= 30);
    const upside = big.filter(e => turned(e) === 'upside');
    const vertical = big.filter(e => turned(e) === 'vertical' && !e.closest('[data-allow-vertical]') && !document.documentElement.hasAttribute('data-allow-vertical'));
    if (upside.length) add('WARN', P, 'rotated-heading', 'a headline reads upside-down or bottom-to-top — readers have to turn the page; set it horizontally or top-to-bottom', upside[0]);
    else if (vertical.length) add('WARN', P, 'rotated-heading', 'a headline is set vertically — keep headlines horizontal (vertical only for small rails and tabs; magazines may mark the page data-allow-vertical)', vertical[0]);

    // ---- page signature for rhythm / monotony ----
    const G = 4, H = 6, grid = [];
    const cell = (x, y) => ({ left: T.left + x * T.width / G, right: T.left + (x + 1) * T.width / G,
                              top: T.top + y * T.height / H, bottom: T.top + (y + 1) * T.height / H });
    const svgs = [...pg.querySelectorAll('svg')].filter(v => { const r = v.getBoundingClientRect(); return r.width * r.height > area * 0.03; });
    const imgRects = imgs.map(i => i.getBoundingClientRect()).concat(svgs.map(v => v.getBoundingClientRect()));
    const fields = all.filter(e => { const c = rgb(getComputedStyle(e).backgroundColor); if (!c || e === pg) return false;
      const r = e.getBoundingClientRect(); return r.width * r.height > area * 0.06 && (lum(c) < 0.45 || Math.max(...c) - Math.min(...c) > 60); })
      .map(e => e.getBoundingClientRect());
    const pgBg = rgb(getComputedStyle(pg).backgroundColor) || [255, 255, 255];
    let imgCov = 0, fieldCov = 0;
    for (let y = 0; y < H; y++) for (let x = 0; x < G; x++) {
      const c = cell(x, y), ca = (c.right - c.left) * (c.bottom - c.top);
      const iv = Math.min(1, imgRects.reduce((s, r) => s + inter(r, c), 0) / ca);
      const fv = Math.min(1, fields.reduce((s, r) => s + inter(r, c), 0) / ca);
      imgCov += iv / (G * H); fieldCov += fv / (G * H);
      grid.push(iv > .5 ? 'I' : fv > .5 ? 'F' : '.');
    }
    const darkPage = lum(pgBg) < 0.35 || Math.max(...pgBg) - Math.min(...pgBg) > 60;
    const isLoud = darkPage || imgCov > 0.45 || fieldCov > 0.4;
    loud.push(isLoud);
    sigs.push(grid.join(''));
    const blocks = texts.filter(e => !texts.some(o => o !== e && o.contains(e))).map(e => e.getBoundingClientRect());
    const textArea = blocks.reduce((s, r) => s + inter(r, T), 0) / area;
    if (pi > 0 && !isLoud && imgCov < 0.05 && textArea < 0.12 && !pg.dataset.intent)
      add('INFO', P, 'underfilled', 'page is mostly empty — intentional breathing page? (set data-intent="breathing")');
    // ---- page fill: every page's bottom edge must be a decision (adapted from print-studio) ----
    const ptype = pg.dataset.type || (pi === 0 ? 'cover' : isLoud ? 'opener' : 'text');
    if (!['cover', 'opener', 'hero', 'closing'].includes(ptype) && !pg.dataset.intent) {
      const live = pg.querySelector('.live');
      const LR = live ? live.getBoundingClientRect() : T;
      const ink = [];
      texts.forEach(e => { if (!e.closest('.furniture')) { const r = e.getBoundingClientRect(); if (r.height > 0) ink.push([r.top, r.bottom]); } });
      imgRects.forEach(r => ink.push([r.top, r.bottom]));
      fields.forEach(r => { if (r.height < LR.height * 0.9) ink.push([r.top, r.bottom]); });
      const iv = ink.map(([a, b]) => [Math.max(a, LR.top), Math.min(b, LR.bottom)]).filter(([a, b]) => b > a).sort((x, y) => x[0] - y[0]);
      if (iv.length) {
        let gap = 0, cur = iv[0][1];
        for (const [a, b] of iv.slice(1)) { gap = Math.max(gap, a - cur); cur = Math.max(cur, b); }
        const trailing = (LR.bottom - cur) / LR.height, hole = gap / LR.height;
        if (trailing > 0.28) add('WARN', P, 'ragged-foot', `content stops ${Math.round(trailing * 100)}% above the bottom margin — resize/anchor/re-flow so the page ends on purpose (or data-intent="breathing")`);
        if (hole > 0.22) add('WARN', P, 'mid-hole', `a ${Math.round(hole * 100)}% empty band inside the page — reads as a layout accident`);
      }
    }
    // furniture
    if (pi > 0 && !pg.querySelector('.furniture, .folio-num, [data-folio]') && !pg.hasAttribute('data-no-folio'))  // bare attribute = "" (falsy)
      add('INFO', P, 'no-folio', 'no page number / running head on an interior page');
  });

  // ---- document-level rhythm ----
  const sim = (a, b) => { let s = 0; for (let i = 0; i < a.length; i++) if (a[i] === b[i]) s++; return s / a.length; };
  let run = 1;
  for (let i = 2; i < sigs.length; i++) {
    run = sim(sigs[i], sigs[i - 1]) > 0.86 ? run + 1 : 1;
    if (run === 3) add('WARN', i + 1, 'monotony', `pages ${i - 1}–${i + 1} share the same structure — vary the pattern (see FLATPLAN rhythm)`);
  }
  const counts = {}; sigs.slice(1).forEach(s => counts[s] = (counts[s] || 0) + 1);
  const top = Math.max(0, ...Object.values(counts));
  if (sigs.length > 5 && top / (sigs.length - 1) > 0.45)
    add('WARN', 0, 'monotony', `${Math.round(100 * top / (sigs.length - 1))}% of interior pages use one layout — the templated-PDF signature`);
  const interior = loud.slice(1);
  if (interior.length >= 6 && interior.filter(Boolean).length === 0)
    add('INFO', 0, 'all-quiet', 'no loud pages (colour field, dark page or dominant photo) — add openers/dividers for rhythm');
  // aesthetic fonts named first but not installed here render with their free stand-in (next in the stack)
  const cx2 = document.createElement('canvas').getContext('2d'), probe = 'mmmmwwwwiiii 0123 Thursday Service';
  const width = f => { cx2.font = `72px ${f}`; return cx2.measureText(probe).width; };
  for (const [f, next] of firstFams)
    if (width(`"${f}", monospace`) === width('monospace') && width(`"${f}", serif`) === width('serif'))
      add('INFO', 0, 'stand-in-font', `"${f}" is not available here; the preview may use ${next ? `"${next}"` : 'a fallback'}. Supply a licensed local font and recheck the rendered PDF.`);
  const pageText = pages.map(p => p.innerText);
  // spread-img repeats one photo on facing pages on purpose (it crosses the gutter); poster variants may share a speaker
  const pageImgs = pages.map(p => p.hasAttribute('data-variant') ? [] :
    [...p.querySelectorAll('img')].filter(i => !i.closest('.spread-img, .cross, [data-texture]')).map(i => i.currentSrc || i.src));
  // poster variants: the heading of each page (data-role="heading", else h1, else the largest text)
  const variants = pages.map((pg, pi) => {
    if (!pg.hasAttribute('data-variant')) return null;
    const T = (pg.querySelector('.trim') || pg).getBoundingClientRect();
    const cand = [...pg.querySelectorAll('*')].filter(e => ownText(e));
    const h = pg.querySelector('[data-role="heading"]') || pg.querySelector('h1') ||
      cand.sort((a, b) => parseFloat(getComputedStyle(b).fontSize) - parseFloat(getComputedStyle(a).fontSize))[0];
    if (!h) return null;
    const cs = getComputedStyle(h), r = h.getBoundingClientRect();
    const cx = Math.min(2, Math.max(0, Math.floor(3 * ((r.left + r.right) / 2 - T.left) / T.width)));
    const cy = Math.min(2, Math.max(0, Math.floor(3 * ((r.top + r.bottom) / 2 - T.top) / T.height)));
    return { page: pi + 1, font: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim().toLowerCase(),
             cell: cx + 3 * cy, vertical: !cs.writingMode.startsWith('horizontal') || cs.transform !== 'none',
             color: rgb(cs.color) || [0, 0, 0] };
  });
  // display type (20pt+) is a visible colour even when its pixel share is small (palette-thin)
  const displayColours = [...new Set(pages.flatMap(pg => [...pg.querySelectorAll('*')]).filter(e => ownText(e)
    && parseFloat(getComputedStyle(e).fontSize) * 0.75 >= 20 && getComputedStyle(e).visibility !== 'hidden').map(e => getComputedStyle(e).color))];
  return { issues: out, pages: pages.length, loud, sigs, pageText, pageImgs, variants, displayColours };
}
"""


def pdf_checks(pdf, issues, expected_fonts=()):
    """Embedding is checked only with pdffonts; unavailable/failed is not a pass."""
    def error(code, msg):
        issues.append({"level": "ERROR", "page": 0, "code": code, "msg": msg, "el": None})
    try:
        res = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        error("pdf-font-check", f"PDF font verification unavailable: {type(exc).__name__}; provide local Poppler pdffonts")
        return {"status": "failed", "backend": "pdffonts"}
    lines = res.stdout.splitlines()
    valid_header = (len(lines) >= 2 and " ".join(lines[0].split()) == "name type encoding emb sub uni object ID"
                    and len(lines[1].split()) == 7 and all(set(part) == {"-"} for part in lines[1].split()))
    if res.returncode or not valid_header:
        error("pdf-font-check", f"pdffonts failed or returned an invalid report (exit {res.returncode})")
        return {"status": "failed", "backend": "pdffonts"}
    before, fonts = len(issues), []
    expected = [re.sub(r"[^a-z0-9]", "", f.lower()) for f in expected_fonts if f.strip()]
    for line in res.stdout.splitlines()[2:]:
        parts = line.split()
        if not parts:
            continue
        if (len(parts) < 8 or any(value not in {"yes", "no"} for value in parts[-5:-2])
                or not all(value.isdigit() for value in parts[-2:])):
            error("pdf-font-check", "Cannot parse pdffonts row; embedding was not verified")
            continue
        name, embedded = parts[0], parts[-5] == "yes"
        fonts.append({"name": name, "embedded": embedded})
        normalized = re.sub(r"[^a-z0-9]", "", name.lower())
        allowed = any(f in normalized for f in expected)
        if not allowed and any(f.lower() in name.lower() for f in FALLBACK_PDF_FONTS):
            error("fallback-font", f"Unexpected PDF fallback font {name}; supply the intended licensed font (or explicitly declare an intended brand font)")
        if not embedded:
            error("font-not-embedded", f"font not embedded: {name}")
    return {"status": "passed" if len(issues) == before else "failed", "backend": "pdffonts", "fonts": fonts}


QUOTES = str.maketrans("‘’“”", "''\"\"")


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[\u00ad\u200b]", "", t.replace("-\n", ""))).strip().lower().translate(QUOTES)


# Advisory humanizer-derived copy heuristics; see licenses/humanizer-MIT.txt.
# innerText applies text-transform, so fragments match ALL CAPS too.
GENERIC = (r"\b(unleash\w*|elevate[sd]?|elevating|revolutioni[sz]\w*|next[- ]gen|seamless(?:ly)?|cutting[- ]edge|world[- ]class"
           r"|synerg\w+|state[- ]of[- ]the[- ]art|best[- ]in[- ]class|game[- ]changer|empower\w*|unlock\w*|redefin\w+|holistic"
           r"|one[- ]stop|tailored solutions?|trusted partner|committed to excellence|delve\w*|tapestry|testament|pivotal|vibrant"
           r"|nestled|in the heart of|showcas\w+|meticulous\w*|breathtaking|renowned|where \w+(?: \w+)? meets \w+"
           r"|unforgettable (?:evening|night|experience)|a night to remember|don.t miss (?:out|it)|get ready to|a divine encounter awaits"
           r"|experience the power of|come together as one)\b")
TELLS = [
    ("WARN", "ai-contrast", r"(?i:\b(?:not (?:just|only|merely|simply)|more than just)\b[^.!?\n]*|\bit'?s not\b[^.!?\n]{1,60}?[,;—–]\s*it'?s\b[^.!?\n]*)",
     "not-X-but-Y contrast (humanizer §1) — state the point directly"),
    ("WARN", "ai-fragments", r"(?:\b[A-Z][A-Za-z']{2,}(?: [A-Za-z']+)?[.!]\s+){2,}[A-Z][A-Za-z']{2,}(?: [A-Za-z']+)?[.!]",
     "slogan row of fragments (humanizer §2) — one sentence that carries a fact"),
]


def copy_tells(pages, src=""):
    """Humanizer tells in the laid-out text; anything also found in the client's copy (src) is skipped.
    >>> [i["code"] for i in copy_tells(["It's not just a school, it's a family.", "LEARN. GROW. THRIVE."])]
    ['ai-contrast', 'ai-fragments']
    >>> copy_tells(["It's not just a school, it's a family."], src="It’s not just a school, it’s a family.")
    []
    >>> [i["code"] for i in copy_tells(["Where tradition meets innovation — a vibrant campus — for all — since 1990."])]
    ['ai-dashes', 'generic-copy']
    >>> copy_tells(["Dr. R. K. Sharma, Principal. Founded in 1990, more than a decade ago. Front elevation, 2025–26."])
    []
    """
    out, nsrc = [], norm(src)
    add = lambda level, i, code, msg: out.append({"level": level, "page": i + 1, "code": code, "msg": msg, "el": None})
    for i, t in enumerate(pages):
        t = t.translate(QUOTES)
        dashes = len(re.findall(r"—|\s–\s|\s--\s", t))
        if dashes >= 3 and not re.search(r"—|\s–\s", src):  # client writes with dashes → their voice, leave it
            add("INFO", i, "ai-dashes", f"{dashes} dashes joining clauses (humanizer §8) — if newly authored, consider a comma, colon or full stop")
        for level, code, rx, msg in TELLS:
            for m in re.finditer(rx, t):
                if norm(m.group(0)) not in nsrc:
                    add(level, i, code, f"{msg}: “{m.group(0).strip()[:70]}”")
        hits = sorted({m.group(0).lower() for m in re.finditer(GENERIC, t, re.I) if norm(m.group(0)) not in nsrc})
        if hits:
            add("INFO", i, "generic-copy", f"generic copy: {', '.join(hits)} — review for a specific factual statement")
    return out


def dup_checks(pages, imgs):
    """Same photo or same paragraph on two pages: a template habit that reads as filler.
    >>> [i["code"] for i in dup_checks(["A long paragraph about our crab grades and how buyers read them.", "A long paragraph about our crab grades and how buyers read them."], [["a.jpg"], ["b.jpg", "a.jpg"]])]
    ['dup-image', 'dup-copy']
    >>> dup_checks(["Short.", "Short."], [["logo.svg"], ["logo.svg"]])
    []
    """
    out, seen_img, seen_par = [], {}, {}
    for i, srcs in enumerate(imgs):
        for src in dict.fromkeys(srcs):
            if not re.search(r"logo|mark|icon|\.svg", src, re.I):  # logos and marks repeat on purpose
                seen_img.setdefault(src, []).append(i + 1)
    for i, t in enumerate(pages):
        for par in dict.fromkeys(norm(x) for x in t.splitlines()):
            if len(par) >= 60:
                seen_par.setdefault(par, []).append(i + 1)
    for src, pgs in seen_img.items():
        if len(pgs) > 1:
            out.append({"level": "WARN", "page": pgs[1], "code": "dup-image", "msg": f"same photo on pages {', '.join(map(str, pgs))}: {src.rsplit('/', 1)[-1][:60]}", "el": None})
    for par, pgs in seen_par.items():
        if len(pgs) > 1:
            out.append({"level": "WARN", "page": pgs[1], "code": "dup-copy", "msg": f"same paragraph on pages {', '.join(map(str, pgs))}: “{par[:60]}…”", "el": None})
    return out


def variant_clash(vs):
    """Poster variants must differ on every axis: heading font, heading position, heading colour, ground colour.
    >>> a = {"page": 1, "font": "anton", "cell": 0, "vertical": False, "color": [255, 255, 255], "ground": [0, 35, 78]}
    >>> b = dict(a, page=2, font="marcellus", cell=8, color=[14, 42, 71], ground=[237, 227, 211])
    >>> variant_clash([a, b])
    []
    >>> [i["msg"] for i in variant_clash([a, dict(b, font="Anton", ground=[2, 36, 80])])]
    ['variants p1 and p2 share: heading font, ground colour — every variant needs its own']
    """
    sys.path.insert(0, str(Path(__file__).parent))
    from colors import rgb2oklch
    def lab(c):
        L, C, h = rgb2oklch([v / 255 for v in c]); return L, C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    near = lambda c1, c2: math.dist(lab(c1), lab(c2)) < 0.08
    out, vs = [], [v for v in vs if v]
    for i, a in enumerate(vs):
        for b in vs[i + 1:]:
            same = [k for k, hit in (("heading font", a["font"].lower() == b["font"].lower()),
                                     ("header position", a["cell"] == b["cell"] and a["vertical"] == b["vertical"]),
                                     ("heading colour", near(a["color"], b["color"])),
                                     ("ground colour", "ground" in a and "ground" in b and near(a["ground"], b["ground"]))) if hit]
            if same:
                out.append({"level": "WARN", "page": b["page"], "code": "variant-clash",
                            "msg": f"variants p{a['page']} and p{b['page']} share: {', '.join(same)} — every variant needs its own", "el": None})
    return out


def palette_count(images, share=0.02, dist=0.05, display=()):
    """How many distinct colours are visible across the pages (images hidden): colours are grouped in
    OKLab and a group counts when it covers at least `share` of all pixels; display-type colours (20pt+)
    count too, however little area they cover.
    >>> from PIL import Image
    >>> two = [Image.new("RGB", (10, 10), (246, 241, 231)), Image.new("RGB", (10, 10), (59, 42, 32))]
    >>> palette_count(two)
    2
    >>> palette_count(two + [Image.new("RGB", (10, 10), (125, 139, 106))])
    3
    >>> palette_count(two, display=[(217, 72, 15), (60, 43, 33)])
    3
    """
    sys.path.insert(0, str(Path(__file__).parent))
    from colors import rgb2oklch
    def lab(c):
        L, C, h = rgb2oklch([v / 255 for v in c]); return L, C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    counts = {}
    for im in images:
        for n, c in im.convert("RGB").getcolors(im.width * im.height):
            q = tuple(v // 8 * 8 for v in c); counts[q] = counts.get(q, 0) + n
    total, groups = sum(counts.values()), []
    for c, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        L = lab(c)
        g = next((g for g in groups if math.dist(g[0], L) < dist), None)
        if g: g[1] += n
        else: groups.append([L, n])
    seen = [g[0] for g in groups if g[1] / total >= share]
    for c in display:
        L = lab(c)
        if all(math.dist(s, L) >= dist for s in seen): seen.append(L)
    return len(seen)


def copy_coverage(source, document):
    """Full required strings; no prefix matching or minimum-length exemption."""
    required = list(dict.fromkeys(norm(line) for line in source.splitlines() if line.strip()))
    if not required:
        raise ValueError("Approved copy is empty; provide one required string per line")
    laid_out = norm(document)
    missing = [line for line in required if line not in laid_out]
    return {"status": "passed" if not missing else "failed", "required": len(required),
            "found": len(required) - len(missing), "coverage_pct": 100 * (1 - len(missing) / len(required)), "missing": missing}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("--target", choices=["print", "digital"], default="print")
    ap.add_argument("--pdf")
    ap.add_argument("--brand-fonts", default="", help="comma list of fonts that are the client's brand (exempt from reflex check)")
    ap.add_argument("--copy", help="approved UTF-8 text: one complete required string per line")
    ap.add_argument("--source", help="the client's original text: copy tells found in it are theirs and skipped (default: --copy)")
    ap.add_argument("--json")
    a = ap.parse_args()
    from document import add_style, open_document, output_path
    if a.json:
        a.json = str(output_path(a.json, Path(a.html).resolve().parent))
    with open_document(a.html) as p:
        res = p.evaluate(JS, {"digital": a.target == "digital", "reflex": REFLEX_FONTS,
                              "brandFonts": [f.strip().lower() for f in a.brand_fonts.split(",") if f.strip()]})
        if any(res["variants"]):  # grounds are gradients or SVG, so take the dominant colour from pixels
            import io
            from PIL import Image
            for v in filter(None, res["variants"]):
                q = Image.open(io.BytesIO(p.locator(".page").nth(v["page"] - 1).screenshot())).convert("RGB").resize((90, 127)).quantize(6)
                idx = max(q.getcolors())[1]
                v["ground"] = q.getpalette()[idx * 3: idx * 3 + 3]
        import io
        from PIL import Image
        # count the design's colours, not the photos' — unless the style is photo-led (white pages whose colour lives in
        # big photographs, e.g. the minimal e-book kit): <html data-palette-photos> counts the photos too
        if not p.evaluate("document.documentElement.hasAttribute('data-palette-photos')"):
            add_style(p, "img, svg image { visibility: hidden !important }")
        shots = [Image.open(io.BytesIO(p.locator(".page").nth(i).screenshot())).convert("RGB").resize((60, 85), Image.NEAREST)
                 for i in range(res["pages"])]
    disp = [tuple(int(float(v)) for v in re.findall(r"[\d.]+", c)[:3]) for c in res.get("displayColours", []) if not c.startswith("rgba(0, 0, 0, 0")]
    n_col = palette_count(shots, display=disp)
    if n_col < 3:
        res["issues"].append({"level": "WARN", "page": 0, "code": "palette-thin", "el": None,
                              "msg": f"only {n_col} colours are visible; review whether a limited/monochrome palette is intentional"})
    issues = res["issues"]
    src = Path(a.copy).read_text(encoding="utf-8") if a.copy else ""
    doc = norm(" ".join(res["pageText"]))
    issues += copy_tells(res["pageText"], Path(a.source).read_text(encoding="utf-8") if a.source else src)
    issues += dup_checks(res["pageText"], res["pageImgs"])
    issues += variant_clash(res["variants"])
    coverage = copy_coverage(src, doc) if a.copy else {"status": "not_checked"}
    if a.copy:
        for missing in coverage["missing"]:
            issues.append({"level": "ERROR", "page": 0, "code": "copy-missing", "msg": f"Required copy missing/altered: “{missing[:140]}”", "el": None})
        issues.append({"level": "INFO", "page": 0, "code": "copy-coverage", "msg": f"{coverage['found']}/{coverage['required']} full required strings present", "el": None})
    pdf_result = pdf_checks(a.pdf, issues, a.brand_fonts.split(",")) if a.pdf else {"status": "not_checked"}
    # de-duplicate identical messages on the same element
    seen, uniq = set(), []
    for i in issues:
        k = (i["level"], i["page"], i["code"], i["el"], i["msg"][:40])
        if k not in seen:
            seen.add(k); uniq.append(i)
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    uniq.sort(key=lambda i: (order[i["level"]], i["page"]))
    n = {k: sum(1 for i in uniq if i["level"] == k) for k in order}
    print(f"brochure-design preflight · {res['pages']} pages · target={a.target} · "
          f"{n['ERROR']} errors, {n['WARN']} warnings, {n['INFO']} notes")
    rhythm = "".join("■" if l else "□" for l in res["loud"])
    print(f"rhythm (■ loud / □ quiet): {rhythm}")
    for i in uniq:
        where = f"p{i['page']}" if i["page"] else "doc"
        el = f"  [{i['el']}]" if i["el"] else ""
        print(f"{i['level']:5} {where:>4} {i['code']:<15} {i['msg']}{el}")
    if a.json:
        Path(a.json).write_text(json.dumps({"summary": n, "rhythm": res["loud"], "copy": coverage, "pdf_fonts": pdf_result, "issues": uniq}, indent=2), encoding="utf-8")
    sys.exit(1 if n["ERROR"] else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252 and crash on ■ — “
    main()
