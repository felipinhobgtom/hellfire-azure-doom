from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "docs/relatorio.md").read_text(encoding="utf-8").splitlines()
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCustom", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#a62c20"), spaceAfter=16))
styles.add(ParagraphStyle(name="BodyCustom", parent=styles["BodyText"], leading=15, spaceAfter=7))
styles.add(ParagraphStyle(name="SmallCustom", parent=styles["BodyText"], fontSize=8, leading=10))
story = []
code = False
buffer = []
for line in source:
    if line.startswith("```"):
        if code:
            story.append(Preformatted("\n".join(buffer), ParagraphStyle("Code", fontName="Courier", fontSize=7, leading=9, backColor=colors.HexColor("#f1f2f3"), borderPadding=6)))
            story.append(Spacer(1, 5))
            buffer = []
        code = not code
        continue
    if code:
        buffer.append(line)
        continue
    if not line.strip():
        continue
    if line.startswith("|"):
        continue
    heading = re.match(r"^(#{1,3})\s+(.*)", line)
    if heading:
        level, text = len(heading.group(1)), heading.group(2)
        if text.startswith("Relatório técnico"):
            story.append(Paragraph(escape(text), styles["TitleCustom"]))
        else:
            story.append(Paragraph(escape(text), styles["Heading1" if level == 1 else "Heading2" if level == 2 else "Heading3"]))
        continue
    if line.startswith("---"):
        story.append(Spacer(1, 6))
        continue
    if line.startswith("- ") or re.match(r"^\d+\.\s", line):
        text = re.sub(r"^(-|\d+\.)\s*", "• ", line)
    else:
        text = line
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    story.append(Paragraph(text, styles["BodyCustom"]))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#69716f"))
    canvas.drawString(18 * mm, 12 * mm, "HELLFIRE · Relatório acadêmico · Novembro 2026")
    canvas.drawRightString(192 * mm, 12 * mm, str(doc.page))
    canvas.restoreState()

output = ROOT / "docs/relatorio.pdf"
SimpleDocTemplate(str(output), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=20*mm, title="HELLFIRE — Relatório técnico").build(story, onFirstPage=footer, onLaterPages=footer)
print(output)
