"""PDF com o resumo das análises do tanque (pedido da usuária em 12/11/2026).

Duas tabelas, com a média embaixo de cada uma:
  1. média dos tanques de cada grupo de coletas (gordura, proteína, CPP, ureia, CCS) + média de todas as análises;
  2. o último grupo, tanque a tanque.
Lê dados/analise_tanque.json e grava monitoramento/analises/Resumo_Analises_Tanque_AAAA-MM-DD.pdf
(data = última coleta analisada).

Uso:
    python3 scripts/resumo_analises_pdf.py
"""
import json
import os
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def fonte(nome):
    for p in (f"fontes/{nome}", f"/usr/share/fonts/truetype/liberation/{nome}", f"/usr/share/fonts/truetype/dejavu/{nome}"):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(nome)


pdfmetrics.registerFont(TTFont("Lib", fonte("LiberationSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("LibB", fonte("LiberationSans-Bold.ttf")))

TINTA, TINTA2, ESCURO, BORDA = colors.HexColor("#2E3338"), colors.HexColor("#5F6870"), colors.HexColor("#2E3338"), colors.HexColor("#D0D4D8")
FUNDO_MEDIA = colors.HexColor("#E8F3EC")
class Fmt(str):
    """Formato com arredondamento "meio para cima", como no Excel (13,45 → 13,5)."""
    def format(self, v):
        casas = int(self[3]) if self[3].isdigit() else 0
        q = Decimal(1).scaleb(-casas)
        return f"{Decimal(str(round(float(v), 9))).quantize(q, rounding=ROUND_HALF_UP):.{casas}f}"


COLS = [("gordura", "Gordura\n%", Fmt("{:.2f}")), ("proteina", "Proteína\n%", Fmt("{:.2f}")), ("cpp", "CPP\n(mil UFC/mL)", Fmt("{:.1f}")),
        ("ureia", "Ureia\n(mg/dL)", Fmt("{:.1f}")), ("ccs", "CCS\n(mil cél./mL)", Fmt("{:.0f}"))]


def br(txt):
    return txt.replace(".", "#").replace(",", ".").replace("#", ",")


def periodo(x):
    ds = sorted(x.data.dt.strftime("%d").unique())
    mes = x.data.max().strftime("%m")
    return (f"{ds[0]}/{mes}" if len(ds) == 1 else f"{ds[0]}–{ds[-1]}/{mes}") + \
        (f" ({x.tanque.nunique()} tanques)" if x.tanque.nunique() != 4 else "")


d = pd.DataFrame(json.load(open("dados/analise_tanque.json")))
d["data"] = pd.to_datetime(d.data)
d = d.sort_values(["data", "tanque"])
grupos = list(dict.fromkeys(d.grupo))

# tabela 1: média de cada grupo de coletas
t1 = [["Coletas"] + [c[1] for c in COLS]]
for g in grupos:
    x = d[d.grupo == g]
    t1.append([periodo(x)] + [br(f.format(x[c].mean())) for c, _, f in COLS])
t1.append([f"Média ({len(d)} análises)"] + [br(f.format(d[c].mean())) for c, _, f in COLS])

# tabela 2: último grupo, tanque a tanque
ult = d[d.grupo == grupos[-1]]
t2 = [["Tanque", "Data"] + [c[1] for c in COLS]]
for _, r in ult.iterrows():
    t2.append([str(r.tanque), r.data.strftime("%d/%m")] + [br(f.format(r[c])) for c, _, f in COLS])
t2.append(["Média", ""] + [br(f.format(ult[c].mean())) for c, _, f in COLS])


def estilo(n):
    return TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "LibB"), ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("BACKGROUND", (0, 0), (-1, 0), ESCURO), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 1), (-1, -1), "Lib"), ("TEXTCOLOR", (0, 1), (-1, -1), TINTA),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, BORDA),
        ("BACKGROUND", (0, n - 1), (-1, n - 1), FUNDO_MEDIA), ("FONTNAME", (0, n - 1), (-1, n - 1), "LibB"),
        ("LINEABOVE", (0, n - 1), (-1, n - 1), 1, TINTA),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])


os.makedirs("monitoramento/analises", exist_ok=True)
saida = f"monitoramento/analises/Resumo_Analises_Tanque_{d.data.max():%Y-%m-%d}.pdf"
doc = SimpleDocTemplate(saida, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm,
                        bottomMargin=14 * mm, title="Resumo das análises do tanque – ARCAFLA")
LARG = A4[0] - 32 * mm
s_tit = ParagraphStyle("t", fontName="LibB", fontSize=17, textColor=TINTA, leading=21)
s_sub = ParagraphStyle("s", fontName="Lib", fontSize=9.5, textColor=TINTA2, leading=13)
s_sec = ParagraphStyle("h", fontName="LibB", fontSize=12, textColor=TINTA, leading=15, spaceBefore=4)
s_nota = ParagraphStyle("n", fontName="Lib", fontSize=8, textColor=TINTA2, leading=11)

cab = [Paragraph("Resumo das análises do tanque", s_tit),
       Paragraph(f"Fazenda ARCAFLA · Castro – PR · coletas de {d.data.min():%d/%m/%Y} a {d.data.max():%d/%m/%Y}", s_sub)]
if os.path.exists("dados/logo_arcafla.png"):
    topo = Table([[Image("dados/logo_arcafla.png", width=30 * mm, height=21 * mm, kind="proportional"), cab]],
                 colWidths=[34 * mm, LARG - 34 * mm])
    topo.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
else:
    topo = cab

w1 = [LARG * 0.30] + [LARG * 0.14] * 5
w2 = [LARG * 0.12, LARG * 0.13] + [LARG * 0.15] * 5
story = [topo, Spacer(1, 8 * mm),
         Paragraph("Média dos tanques de cada coleta", s_sec), Spacer(1, 2 * mm),
         Table(t1, colWidths=w1, style=estilo(len(t1)), repeatRows=1), Spacer(1, 2 * mm),
         Paragraph(f"A média de baixo junta as {len(d)} análises individuais (todos os tanques e coletas).", s_nota),
         Spacer(1, 8 * mm),
         Paragraph(f"Última análise por tanque ({periodo(ult).split(' (')[0]})", s_sec), Spacer(1, 2 * mm),
         Table(t2, colWidths=w2, style=estilo(len(t2))), Spacer(1, 6 * mm),
         Paragraph("Fonte: análises do laticínio (Castrolanda / PARLPR), em dados/analise_tanque.json. "
                   f"Gerado em {pd.Timestamp.now():%d/%m/%Y}.", s_nota)]
doc.build(story)
print(saida)
