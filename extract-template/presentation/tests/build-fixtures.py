#!/usr/bin/env python3
"""Controlled style/data probes, never source uploads or extraction evidence."""
from copy import deepcopy
from pathlib import Path
import base64
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
CATALOG = json.loads((ROOT / 'library/references/catalog.json').read_text())
IMAGE = 'data:image/svg+xml;base64,' + base64.b64encode(b'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="160"><rect width="256" height="160" fill="#8298ac"/></svg>').decode()

def fill_tree(element, locale, index=0):
    for child in list(element):
        repeat = child.get('data-repeat')
        if repeat:
            position = list(element).index(child)
            element.remove(child)
            count = 3 if repeat not in ('quotes', 'risks', 'references', 'benefits', 'limitations', 'edges') else 2
            for number in range(count):
                clone = deepcopy(child)
                clone.attrib.pop('data-repeat')
                element.insert(position + number, clone)
                fill_tree(clone, locale, number)
        else:
            fill_tree(child, locale, index)
    for key, value in list(element.attrib.items()):
        element.set(key, re.sub(r'\{\{([^{}]+)\}\}', lambda m: slot(m[1], locale, index), value))
    if element.text:
        element.text = re.sub(r'\{\{([^{}]+)\}\}', lambda m: slot(m[1], locale, index), element.text)
    if element.tag == 'text':
        element.set('data-source-size', '20')

def slot(name, locale, i):
    numeric = {
        'mark-x':70+i*140, 'mark-y':210-i*20, 'mark-width':60, 'mark-height':50+i*20,
        'label-x':70+i*140, 'label-y':278, 'point-x':90+i*140, 'point-y':200-i*40,
        'point-radius':5, 'bubble-radius':12+i*3, 'interval-x':100+i*40,
        'interval-y':60+i*65, 'interval-width':160+i*40, 'interval-height':24,
        'task-label-x':40, 'task-label-y':105+i*65, 'node-x':40+i*180,
        'node-y':90, 'node-width':130, 'node-height':90,
        'node-label-x':52+i*180, 'node-label-y':140,
        'cell-intensity':(i+1)/4,
    }
    if name in numeric: return str(numeric[name])
    if name == 'image-src': return IMAGE
    if name == 'line-path': return 'M90 200L230 160L370 120'
    if name == 'edge-path': return f'M{170+i*180} 135H{220+i*180}'
    if name == 'slice-path': return ['M260 145L260 45A100 100 0 0 1 346.6 195Z','M260 145L346.6 195A100 100 0 0 1 173.4 195Z','M260 145L173.4 195A100 100 0 0 1 260 45Z'][i%3]
    if name == 'funnel-path': return f'M{60+i*35} {30+i*60}H{520-i*35}L{485-i*35} {75+i*60}H{95+i*35}Z'
    if name == 'radar-axis-points': return '300,30 450,145 390,265 210,265 150,145'
    if name == 'radar-value-points': return '300,60 400,145 365,220 250,210 200,145'
    if name.endswith('number'): return str(i+1)
    if 'value' in name or name in ('change','variance','plan-price'): return str((i+1)*12)
    if name in ('mark-label','node-label','task-label'): return ('项' if locale=='zh' else 'Item') + str(i+1)
    if name in ('title','header','cell'): return ('示例内容' if locale=='zh' else 'Test content') + str(i+1)
    if any(part in name for part in ('heading','name','period','horizon','label','state')): return ('示例主题' if locale=='zh' else 'Test theme') + str(i+1)
    return '受控测试内容，保留原意与语言。' if locale=='zh' else 'Controlled test content, retaining meaning and language.'

geometry = (ROOT / 'library/styles/geometry.css').read_text()
for skin in ('sans-light','serif-dark'):
    for locale in ('en','zh'):
        pages=[]
        for entry in CATALOG['layouts']:
            tree=ET.fromstring((ROOT / 'library/references' / entry['file']).read_text())
            fill_tree(tree,locale)
            pages.append(f'<section class="slide"><div class="stage" data-layout="{entry["id"]}"><main class="fit">{ET.tostring(tree,encoding="unicode")}</main></div></section>')
        font='Arial, "Noto Sans CJK SC", sans-serif' if skin=='sans-light' else 'Georgia, "Noto Serif CJK SC", serif'
        ink,paper=('#172535','#f7f4ec') if skin=='sans-light' else ('#f7f4ec','#172535')
        css=f'''*{{box-sizing:border-box}}html,body{{margin:0;height:100%;font-family:{font};font-size:24px;line-height:1.2}}.deck{{height:100vh;overflow-y:auto}}.slide{{height:900px}}.stage{{width:1600px;height:900px;position:relative;color:{ink};background:{paper}}}.fit{{position:absolute;inset:70px 80px}}[data-text-role="title"]{{font-size:48px;font-weight:700}}[data-text-role="heading"]{{font-size:28px;font-weight:700}}[data-text-role="metric-value"]{{font-size:56px}}[data-text-role="body"]{{font-size:24px}}[data-text-role="caption"]{{font-size:15px}}[data-text-role="label"],[data-text-role="table-cell"]{{font-size:20px}}[data-text-role="table-header"]{{font-size:22px;font-weight:700}}blockquote{{margin:0}}'''
        (OUT / f'{skin}-{locale}.html').write_text('<!doctype html><html><head><meta charset="utf-8"><style>'+geometry+css+'</style></head><body><div class="deck">'+''.join(pages)+'</div></body></html>')
print(f'Wrote four controlled 54-layout probes to {OUT}')
