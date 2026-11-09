from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
lines = (ROOT / "docs/relatorio.md").read_text(encoding="utf-8").splitlines()
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCustom", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#a62c20"), spaceAfter=16))
styles.add(ParagraphStyle(name="BodyCustom", parent=styles["BodyText"], leading=15, spaceAfter=7))
styles.add(ParagraphStyle(name="TableCell", parent=styles["BodyText"], fontSize=7.5, leading=9))
styles.add(ParagraphStyle(name="TableHeader", parent=styles["BodyText"], fontSize=7.5, leading=9, textColor=colors.white))

class ArchitectureDiagram(Flowable):
    def wrap(self, width, height):
        self.width, self.height = min(width, 555), 150
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.scale(self.width / 550, self.width / 550)
        boxes = [(5, 82, 105, 43, "Browser", "Chocolate Doom\nWASM + HTML"),
                 (137, 82, 105, 43, "Internet", "IPv4 + NSG\nTCP/80"),
                 (270, 82, 135, 43, "Azure VM", "Ubuntu · Docker\nFlask + Gunicorn"),
                 (438, 82, 105, 43, "Persistence", "SQLite\n/data/doom.db")]
        for x, y, w, h, title, detail in boxes:
            c.setFillColor(colors.HexColor("#eef2f1")); c.setStrokeColor(colors.HexColor("#40534f")); c.roundRect(x, y, w, h, 5, fill=1, stroke=1)
            c.setFillColor(colors.HexColor("#a62c20")); c.setFont("Helvetica-Bold", 8); c.drawCentredString(x+w/2, y+h-13, title)
            c.setFillColor(colors.HexColor("#202725")); c.setFont("Helvetica", 7)
            for j, text in enumerate(detail.split("\n")): c.drawCentredString(x+w/2, y+h-25-j*9, text)
        c.setStrokeColor(colors.HexColor("#687773")); c.setFillColor(colors.HexColor("#687773")); c.setLineWidth(1)
        for x1, x2 in [(110, 137), (242, 270), (405, 438)]:
            y=103; c.line(x1, y, x2-5, y); c.line(x2-5, y, x2-9, y+3); c.line(x2-5, y, x2-9, y-3)
        c.setFillColor(colors.HexColor("#eef2f1")); c.setStrokeColor(colors.HexColor("#40534f")); c.roundRect(290, 15, 120, 40, 5, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#a62c20")); c.setFont("Helvetica-Bold", 8); c.drawCentredString(350, 43, "Storage Account")
        c.setFillColor(colors.HexColor("#202725")); c.setFont("Helvetica", 7); c.drawCentredString(350, 29, "Boot diagnostics · Blob privado")
        c.line(337, 82, 337, 55); c.line(337, 55, 334, 60); c.line(337, 55, 340, 60)
        c.setFillColor(colors.HexColor("#eef2f1")); c.setStrokeColor(colors.HexColor("#40534f")); c.roundRect(55, 15, 120, 40, 5, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#a62c20")); c.setFont("Helvetica-Bold", 8); c.drawCentredString(115, 43, "ARM + Azure CLI")
        c.setFillColor(colors.HexColor("#202725")); c.setFont("Helvetica", 7); c.drawCentredString(115, 29, "Provisiona rede, VM, disco")
        c.line(175, 35, 300, 35); c.line(300, 35, 295, 32); c.line(300, 35, 295, 38)
        c.setFillColor(colors.HexColor("#4d5b56")); c.setFont("Helvetica-Oblique", 7); c.drawString(5, 2, "HTTP público para a demo; SQLite no disco gerenciado da VM.")
        c.restoreState()

class SchemaDiagram(Flowable):
    def wrap(self, width, height):
        self.width, self.height = min(width, 555), 108
        return self.width, self.height

    def draw(self):
        c=self.canv; x=120; y=12; w=315
        c.setFillColor(colors.HexColor("#eef2f1")); c.setStrokeColor(colors.HexColor("#40534f")); c.roundRect(x,y,w,84,5,fill=1,stroke=1)
        c.setFillColor(colors.HexColor("#a62c20")); c.roundRect(x,y+63,w,21,5,fill=1,stroke=0)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 9); c.drawCentredString(x+w/2,y+70,"SCORES")
        c.setFillColor(colors.HexColor("#202725")); c.setFont("Courier",8)
        for i,text in enumerate(["id          INTEGER PRIMARY KEY AUTOINCREMENT", "player      TEXT (1–24 chars)", "kills       INTEGER (0–999999)", "created_at  TEXT · ISO-8601 UTC"]):
            c.drawString(x+18,y+49-i*13,text)
        c.setFillColor(colors.HexColor("#4d5b56")); c.setFont("Helvetica-Oblique",7); c.drawCentredString(x+w/2,1,"CHECK constraints + bound SQL parameters")

story=[]
index=0
while index < len(lines):
    line=lines[index]
    if line.startswith("```"):
        block=[]; index+=1
        while index < len(lines) and not lines[index].startswith("```"):
            block.append(lines[index]); index+=1
        if block and block[0].startswith("flowchart"):
            story += [ArchitectureDiagram(), Spacer(1,8)]
        elif block and block[0].startswith("erDiagram"):
            story += [SchemaDiagram(), Spacer(1,8)]
        else:
            story += [Preformatted("\n".join(block), ParagraphStyle("Code", fontName="Courier", fontSize=7, leading=9, backColor=colors.HexColor("#f1f2f3"), borderPadding=6)), Spacer(1,5)]
        index+=1; continue
    if line.startswith("|"):
        rows=[]
        while index < len(lines) and lines[index].startswith("|"):
            cells=[cell.strip() for cell in lines[index].strip().strip("|").split("|")]
            if not cells or all(re.fullmatch(r":?-{3,}:?",cell) for cell in cells):
                index+=1; continue
            rows.append(cells); index+=1
        if rows:
            n=max(map(len,rows)); data=[]
            for r,row in enumerate(rows):
                row += [""]*(n-len(row)); formatted=[]
                for cell in row:
                    cell=escape(cell)
                    cell=re.sub(r"\*\*(.*?)\*\*",r"<b>\1</b>",cell)
                    cell=re.sub(r"`([^`]+)`",r"<font name='Courier'>\1</font>",cell)
                    formatted.append(Paragraph(cell,styles["TableHeader" if r==0 else "TableCell"]))
                data.append(formatted)
            table=Table(data,colWidths=[(A4[0]-36*mm)/n for _ in range(n)],repeatRows=1,hAlign="LEFT")
            table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#31413d")),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#aeb9b5")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
            story += [table,Spacer(1,8)]
        continue
    if not line.strip(): index+=1; continue
    heading=re.match(r"^(#{1,3})\s+(.*)",line)
    if heading:
        level,text=len(heading.group(1)),heading.group(2)
        story.append(Paragraph(escape(text),styles["TitleCustom"] if text.startswith("Relatório técnico") else styles["Heading1" if level==1 else "Heading2" if level==2 else "Heading3"]))
        index+=1; continue
    if line.startswith("---"):
        story.append(Spacer(1,6)); index+=1; continue
    text=re.sub(r"^(-|\d+\.)\s*","• ",line) if line.startswith("- ") or re.match(r"^\d+\.\s",line) else line
    text=re.sub(r"\*\*(.*?)\*\*",r"<b>\1</b>",text)
    text=re.sub(r"`([^`]+)`",r"<font name='Courier'>\1</font>",text)
    text=re.sub(r"\[([^\]]+)\]\(([^)]+)\)",r"\1 (\2)",text)
    story.append(Paragraph(text,styles["BodyCustom"])); index+=1

def footer(canvas, doc):
    canvas.saveState(); canvas.setFont("Helvetica",8); canvas.setFillColor(colors.HexColor("#69716f"))
    canvas.drawString(18*mm,12*mm,"HELLFIRE · Relatório acadêmico · Novembro 2026")
    canvas.drawRightString(192*mm,12*mm,str(doc.page)); canvas.restoreState()

output=ROOT/"docs/relatorio.pdf"
SimpleDocTemplate(str(output),pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=20*mm,title="HELLFIRE — Relatório técnico").build(story,onFirstPage=footer,onLaterPages=footer)
print(output)
