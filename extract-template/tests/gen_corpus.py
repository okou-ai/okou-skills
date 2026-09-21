"""Build a corpus of realistic docx documents covering many style situations.
Each generator is a different real-world pattern the extraction skill must survive."""
import docx, copy
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ZH = ["本报告覆盖试点项目第一阶段的交付范围、进度与风险。第一阶段自三月启动，至六月底完成全部功能验收，期间共完成十二个迭代。",
      "在验收过程中，团队发现部分接口的响应时间在高并发下超出预期，已通过缓存策略与连接池调优解决，详见附录二。",
      "下一阶段的重点是把试点经验推广到其余三个业务线，并建立统一的运维监控看板，预计需要八周时间。",
      "风险方面，主要来自外部供应商的交付节奏与内部人员的调配；建议在启动前完成资源锁定，并设置每两周一次的联合评审。"]
EN = ["This report covers the scope, schedule and risks of the first phase of the pilot programme, which ran from March to the end of June across twelve iterations.",
      "During acceptance the team found that several interfaces exceeded their response budget under load; the fix combined caching with connection-pool tuning and is described in Appendix B.",
      "The next phase extends the pilot to the remaining three business lines and establishes a shared operations dashboard, an estimated eight weeks of work.",
      "The principal risks are vendor delivery cadence and internal staffing; we recommend locking resources before kickoff and holding a joint review every two weeks."]

def set_font(run_or_style, name, size=None, ea=None, bold=None, color=None):
    f = run_or_style.font
    f.name = name
    rpr = run_or_style.element.get_or_add_rPr() if hasattr(run_or_style.element, "get_or_add_rPr") else run_or_style.element.rPr
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    rf.set(qn("w:ascii"), name); rf.set(qn("w:hAnsi"), name)
    rf.set(qn("w:eastAsia"), ea or name)
    if size: f.size = Pt(size)
    if bold is not None: f.bold = bold
    if color: f.color.rgb = RGBColor.from_string(color)

def page_field(par, prefix="", suffix=""):
    if prefix: par.add_run(prefix)
    r = par.add_run()
    for tag, val in (("begin", None), (None, " PAGE "), ("end", None)):
        if tag:
            fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), tag); r._r.append(fc)
        else:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = val; r._r.append(it)
    if suffix: par.add_run(suffix)

def columns(section, n, gap_twips=720, widths=None):
    sectPr = section._sectPr
    cols = sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols"); sectPr.append(cols)
    cols.set(qn("w:num"), str(n)); cols.set(qn("w:space"), str(gap_twips))
    if widths:
        cols.set(qn("w:equalWidth"), "0")
        for w in widths:
            c = OxmlElement("w:col"); c.set(qn("w:w"), str(w)); c.set(qn("w:space"), str(gap_twips)); cols.append(c)

def body(doc, texts, style="Normal", n=4, heading_style=None, hn=None, first_style=None):
    for i, t in enumerate(texts[:n]):
        p = doc.add_paragraph(t, style=(first_style if i == 0 and first_style else style))

def add_table(doc, style=None):
    t = doc.add_table(rows=4, cols=3)
    if style: t.style = style
    for i, row in enumerate(t.rows):
        for j, c in enumerate(row.cells):
            c.text = ("阶段", "交付物", "状态")[j] if i == 0 else f"第{i}项-{j}"
    return t

def a4(sec, top=2.5, bottom=2.0, left=2.8, right=2.8):
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin, sec.bottom_margin = Cm(top), Cm(bottom)
    sec.left_margin, sec.right_margin = Cm(left), Cm(right)

# 1. Chinese project report: built-in styles customised, header/footer, table, list, numbered headings
def c01():
    d = Document(); s = d.sections[0]; a4(s, 2.54, 2.2, 3.0, 3.0)
    st = d.styles
    set_font(st["Normal"], "Times New Roman", 10.5, ea="宋体")
    st["Normal"].paragraph_format.line_spacing = 1.5
    st["Normal"].paragraph_format.first_line_indent = Pt(21)
    set_font(st["Title"], "Arial", 22, ea="黑体", bold=True, color="1F3864")
    st["Title"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(st["Heading 1"], "Arial", 16, ea="黑体", bold=True, color="1F3864")
    st["Heading 1"].paragraph_format.space_before = Pt(18); st["Heading 1"].paragraph_format.space_after = Pt(6)
    set_font(st["Heading 2"], "Arial", 13, ea="黑体", bold=True, color="2E74B5")
    set_font(st["Heading 3"], "Arial", 11, ea="黑体", bold=True, color="000000")
    s.header.paragraphs[0].text = "试点项目阶段报告\t内部资料"
    set_font(s.header.paragraphs[0].runs[0], "宋体", 9, ea="宋体", color="808080")
    fp = s.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    page_field(fp, "第 ", " 页")
    d.add_paragraph("试点项目第一阶段总结报告", style="Title")
    sub = d.add_paragraph("项目管理办公室 · 2026 年 6 月", style="Subtitle")
    for h1 in ("一、项目概述", "二、验收结果", "三、下一步计划"):
        d.add_paragraph(h1, style="Heading 1")
        body(d, ZH, n=2)
        for h2 in ("范围", "进度"):
            d.add_paragraph(f"{h1[0]}.{h2}", style="Heading 2")
            body(d, ZH[2:], n=2)
            d.add_paragraph("要点说明", style="Heading 3")
            for it in ("完成功能验收", "完成性能压测", "完成安全审计"):
                d.add_paragraph(it, style="List Bullet")
    d.add_paragraph("四、交付清单", style="Heading 1")
    add_table(d, "Table Grid")
    body(d, ZH, n=4)
    d.save("c01_zh_report.docx")

# 2. English Letter-size memo, Calibri, 1in margins, no header, custom-named styles only
def c02():
    d = Document(); s = d.sections[0]
    s.page_width, s.page_height = Inches(8.5), Inches(11)
    for a in ("top_margin", "bottom_margin", "left_margin", "right_margin"): setattr(s, a, Inches(1))
    st = d.styles
    set_font(st["Normal"], "Calibri", 11)
    st["Normal"].paragraph_format.space_after = Pt(8); st["Normal"].paragraph_format.line_spacing = 1.08
    from docx.enum.style import WD_STYLE_TYPE
    for name, base, size, color, bold in (("Memo Title", "Normal", 20, "C00000", True),
                                          ("Section Head", "Normal", 13, "404040", True),
                                          ("Sub Head", "Normal", 11, "404040", True),
                                          ("Body Copy", "Normal", 11, None, False)):
        x = st.add_style(name, WD_STYLE_TYPE.PARAGRAPH); x.base_style = st[base]
        set_font(x, "Calibri", size, bold=bold, color=color)
        x.paragraph_format.space_before = Pt(12 if "Head" in name else 0)
    d.add_paragraph("Memorandum: Q2 Pilot Review", style="Memo Title")
    for h in ("Purpose", "Findings", "Recommendation"):
        d.add_paragraph(h, style="Section Head")
        body(d, EN, style="Body Copy", n=2)
        d.add_paragraph("Detail", style="Sub Head")
        body(d, EN[2:], style="Body Copy", n=2)
    add_table(d, "Light Grid Accent 1")
    d.save("c02_en_memo_custom_styles.docx")

# 3. Two-column Chinese newsletter, unequal columns, running head both sides, title in column
def c03():
    d = Document(); s = d.sections[0]; a4(s, 2.0, 2.0, 2.0, 2.0)
    columns(s, 2, 567, widths=[6200, 3200])
    st = d.styles
    set_font(st["Normal"], "Arial", 9.5, ea="微软雅黑", color="333333")
    st["Normal"].paragraph_format.space_after = Pt(4); st["Normal"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_font(st["Title"], "Arial", 26, ea="微软雅黑", bold=True, color="C0392B")
    set_font(st["Heading 1"], "Arial", 14, ea="微软雅黑", bold=True, color="C0392B")
    set_font(st["Heading 2"], "Arial", 11, ea="微软雅黑", bold=True, color="7F8C8D")
    s.header.paragraphs[0].text = "智能体交付月刊\t2026 年第 6 期"
    set_font(s.header.paragraphs[0].runs[0], "Arial", 8, ea="微软雅黑", color="999999")
    page_field(s.footer.paragraphs[0], "— ", " —"); s.footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    d.add_paragraph("六月简报", style="Title")
    for h in ("交付进展", "客户之声", "下月安排", "团队动态"):
        d.add_paragraph(h, style="Heading 1"); body(d, ZH, n=3)
        d.add_paragraph("要点", style="Heading 2"); body(d, ZH[1:], n=2)
    d.save("c03_zh_newsletter_2col.docx")

# 4. "Real user" doc: NO styles used — headings are bold/large runs of Normal, direct formatting everywhere
def c04():
    d = Document(); s = d.sections[0]; a4(s)
    set_font(d.styles["Normal"], "Calibri", 11, ea="等线")
    p = d.add_paragraph(); r = p.add_run("产品需求说明书"); set_font(r, "Calibri", 20, ea="等线", bold=True); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for h in ("1 背景", "2 目标用户", "3 功能需求", "4 非功能需求"):
        p = d.add_paragraph(); r = p.add_run(h); set_font(r, "Calibri", 14, ea="等线", bold=True, color="2F5496")
        p.paragraph_format.space_before = Pt(12)
        for t in ZH[:3]:
            p = d.add_paragraph(); r = p.add_run(t); set_font(r, "Calibri", 11, ea="等线")
            p.paragraph_format.first_line_indent = Pt(22); p.paragraph_format.line_spacing = 1.3
        p = d.add_paragraph(); r = p.add_run("3.1 子项"); set_font(r, "Calibri", 12, ea="等线", bold=True)
        for t in ZH[1:3]:
            p = d.add_paragraph(); r = p.add_run(t); set_font(r, "Calibri", 11, ea="等线")
    add_table(d, "Table Grid")
    d.save("c04_zh_direct_formatting_only.docx")

# 5. Cover page + different first page header + numbered headings + TOC field + footnote-like small text
def c05():
    d = Document(); s = d.sections[0]; a4(s, 3.0, 2.5, 2.5, 2.5)
    s.different_first_page_header_footer = True
    st = d.styles
    set_font(st["Normal"], "Georgia", 11, ea="宋体"); st["Normal"].paragraph_format.space_after = Pt(6)
    set_font(st["Title"], "Georgia", 28, bold=True, color="000000"); st["Title"].paragraph_format.space_before = Pt(200)
    set_font(st["Heading 1"], "Georgia", 18, bold=True, color="000000"); st["Heading 1"].paragraph_format.page_break_before = True
    set_font(st["Heading 2"], "Georgia", 14, bold=True, color="555555")
    set_font(st["Heading 3"], "Georgia", 12, bold=False, color="000000"); st["Heading 3"].font.italic = True
    s.header.paragraphs[0].text = "Technical Assessment — Confidential"; s.header.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_font(s.header.paragraphs[0].runs[0], "Georgia", 9, color="777777")
    page_field(s.footer.paragraphs[0], "Page "); s.footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    d.add_paragraph("Technical Assessment of the Agent Delivery Platform", style="Title")
    d.add_paragraph("Prepared for the Steering Committee", style="Subtitle")
    d.add_paragraph("Contents", style="Heading 1")
    p = d.add_paragraph(); r = p.add_run()
    for tag, val in (("begin", None), (None, ' TOC \\o "1-2" \\h '), ("separate", None), (None, None), ("end", None)):
        if tag: fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), tag); r._r.append(fc)
        elif val: it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = val; r._r.append(it)
        else: t = OxmlElement("w:t"); t.text = "1 Introduction ...... 3"; r._r.append(t)
    for i, h in enumerate(("Introduction", "Architecture", "Findings", "Appendix"), 1):
        d.add_paragraph(f"{i} {h}", style="Heading 1"); body(d, EN, n=3)
        for j in (1, 2):
            d.add_paragraph(f"{i}.{j} Detail", style="Heading 2"); body(d, EN[1:], n=2)
            d.add_paragraph(f"{i}.{j}.1 Note", style="Heading 3"); body(d, EN[2:], n=1)
    p = d.add_paragraph("¹ Figures are drawn from the June acceptance log."); set_font(p.runs[0], "Georgia", 8, color="777777")
    d.save("c05_en_cover_numbered_toc.docx")

# 6. Three equal columns, tiny type, Letter landscape (brochure)
def c06():
    d = Document(); s = d.sections[0]
    from docx.enum.section import WD_ORIENT
    s.orientation = WD_ORIENT.LANDSCAPE; s.page_width, s.page_height = Inches(11), Inches(8.5)
    for a in ("top_margin", "bottom_margin", "left_margin", "right_margin"): setattr(s, a, Inches(0.6))
    columns(s, 3, 500)
    st = d.styles
    set_font(st["Normal"], "Verdana", 8.5, color="222222"); st["Normal"].paragraph_format.space_after = Pt(5)
    set_font(st["Title"], "Verdana", 18, bold=True, color="00695C")
    set_font(st["Heading 1"], "Verdana", 11, bold=True, color="00695C"); st["Heading 1"].paragraph_format.space_before = Pt(10)
    set_font(st["Heading 2"], "Verdana", 9, bold=True, color="222222")
    d.add_paragraph("Agent Delivery Platform — Product Brief", style="Title")
    for h in ("Why", "What", "How", "Pricing", "Support", "Roadmap"):
        d.add_paragraph(h, style="Heading 1"); body(d, EN, n=3)
        d.add_paragraph("At a glance", style="Heading 2"); body(d, EN[3:], n=1)
    d.save("c06_en_brochure_3col_landscape.docx")

# 7. Theme fonts only (no explicit rFonts anywhere) — inspect must resolve theme slots; heading inversion H2 > H1
def c07():
    d = Document(); s = d.sections[0]; a4(s)
    st = d.styles
    for name in ("Normal", "Title", "Heading 1", "Heading 2"):
        rpr = st[name].element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is not None: rpr.remove(rf)
    st["Heading 1"].font.size = Pt(12); st["Heading 2"].font.size = Pt(15)   # inverted on purpose
    st["Normal"].font.size = Pt(12)
    d.add_paragraph("Inverted hierarchy sample", style="Title")
    for h in ("Alpha", "Beta"):
        d.add_paragraph(h, style="Heading 1"); body(d, EN, n=2)
        d.add_paragraph("Sub", style="Heading 2"); body(d, EN, n=2)
    d.save("c07_theme_fonts_inverted.docx")

# 8. Contract: fixed clauses, numbered list style, 'Block Text' quotes, signature table, small caps title
def c08():
    d = Document(); s = d.sections[0]; a4(s, 2.5, 2.5, 3.2, 3.2)
    st = d.styles
    set_font(st["Normal"], "Times New Roman", 12, ea="仿宋"); st["Normal"].paragraph_format.line_spacing = Pt(20); st["Normal"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_font(st["Title"], "Times New Roman", 16, ea="黑体", bold=True, color="000000"); st["Title"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(st["Heading 1"], "Times New Roman", 12, ea="黑体", bold=True, color="000000")
    s.footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER; page_field(s.footer.paragraphs[0], "第 ", " 页  共 [总页数] 页")
    s.header.paragraphs[0].text = "合同编号：[合同编号]"
    d.add_paragraph("技术服务合同", style="Title")
    d.add_paragraph("甲方：[甲方名称]\n乙方：[乙方名称]")
    for i, h in enumerate(("第一条 服务内容", "第二条 服务期限", "第三条 费用与支付", "第四条 违约责任", "第五条 争议解决"), 1):
        d.add_paragraph(h, style="Heading 1")
        for t in ZH[:2]:
            d.add_paragraph(f"{i}.{ZH.index(t)+1} " + t)
        d.add_paragraph("双方确认：本条款为本合同不可分割的一部分。", style="Intense Quote")
    add_table(d, "Table Grid")
    d.save("c08_zh_contract_placeholders.docx")

# 9. header with a logo picture (left) and text (right), Light Grid table
def c09():
    import pymupdf
    d = pymupdf.open(); pg = d.new_page(width=120, height=40)
    pg.draw_rect(pymupdf.Rect(0, 0, 40, 40), color=None, fill=(0.93, 0.31, 0))
    pg.insert_text((48, 28), "OKOU", fontsize=20, fontname="helv", color=(0.07, 0.08, 0.09))
    pg.get_pixmap(dpi=144).save("logo.png"); d.close()
    d = Document(); s = d.sections[0]; a4(s, 3.0, 2.5, 2.5, 2.5)
    st = d.styles
    set_font(st["Normal"], "Calibri", 10.5, ea="微软雅黑"); st["Normal"].paragraph_format.space_after = Pt(6)
    set_font(st["Title"], "Calibri", 24, ea="微软雅黑", bold=True, color="ED4E01")
    set_font(st["Heading 1"], "Calibri", 15, ea="微软雅黑", bold=True, color="111418")
    set_font(st["Heading 2"], "Calibri", 12, ea="微软雅黑", bold=True, color="444444")
    hp = s.header.paragraphs[0]; hp.add_run().add_picture("logo.png", height=Cm(0.7)); hp.add_run("\t\t客户成功部 · 内部资料")
    for r in hp.runs[1:]: r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string("888888")
    fp = s.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT; page_field(fp)
    d.add_paragraph("客户成功季度回顾", style="Title")
    for h in ("一、客户健康度", "二、续约与扩展", "三、下季度重点"):
        d.add_paragraph(h, style="Heading 1"); body(d, ZH, n=3)
        d.add_paragraph("要点", style="Heading 2"); body(d, ZH[1:], n=1)
        t = d.add_table(rows=4, cols=3); t.style = "Light Grid Accent 1"
        for i, row in enumerate(t.rows):
            for j, c in enumerate(row.cells): c.text = ("客户", "健康分", "状态")[j] if i == 0 else f"第{i}项-{j}"
    d.save("c09_zh_header_logo_lightgrid.docx")


for f in (c01, c02, c03, c04, c05, c06, c07, c08, c09):
    f(); print("ok", f.__name__)
