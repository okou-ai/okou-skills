#!/usr/bin/env python3
"""Small ReportLab example; replace its sample content with approved material."""

import argparse
from html import escape
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--font", default="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
    )
    parser.add_argument(
        "--symbols-font", default="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    args = parser.parse_args()

    # This TTC contains TrueType outlines; CFF-based TTCs cannot use this route.
    pdfmetrics.registerFont(TTFont("Body", args.font, subfontIndex=0))
    pdfmetrics.registerFont(TTFont("Symbols", args.symbols_font))
    body = ParagraphStyle(
        "Body", fontName="Body", fontSize=11, leading=18,
        spaceAfter=12, wordWrap="CJK",
    )
    heading = ParagraphStyle(
        "Heading", parent=body, fontSize=22, leading=30,
        spaceAfter=16, keepWithNext=True,
    )
    bullet = ParagraphStyle(
        "Bullet", parent=body, leftIndent=16, bulletIndent=0,
        bulletFontName="Symbols", bulletFontSize=11,
    )
    story = [
        Paragraph(escape("季度经营回顾（示例）"), heading),
        Paragraph(escape("产品运营 · 中文示例 · 2026 年 9 月"), body),
        Paragraph(escape("交付总数：3428；增长率：12.5%。"), bullet, bulletText="•"),
        Paragraph(
            escape("核对中文标点：“引号”、（括号）、《书名号》以及 Latin ABC 123。"),
            bullet, bulletText="•",
        ),
        Paragraph(
            escape(
                "连续中文段落需要正确换行，句号、逗号和右括号不应孤立在行首。"
                "这段示例包含中文、全角标点和产品名称 Okou，"
                "用于检查长段落在页面边界内自然流动。"
                "请用实际批准的内容替换示例，并逐页检查文字、标点与项目符号。"
                "生成成功和文字能够提取，都不能替代对最终页面图像的复核。"
            ),
            body,
        ),
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(args.output), pagesize=A4, leftMargin=54, rightMargin=54,
        topMargin=54, bottomMargin=54, lang="zh-CN",
        title="季度经营回顾（示例）",
    )
    document.build(story)


if __name__ == "__main__":
    main()
