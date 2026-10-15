"""PDF de uma página (A4 retrato) com os resultados do monitoramento diário.

Lê a planilha já recalculada (valores das fórmulas) e grava
monitoramento/Monitoramento_Diario_ARKAFLA_AAAA-MM-DD.pdf (data do último dia).

Uso:
    python3 scripts/monitor_pdf.py [planilha.xlsx]
"""
import os
import sys
from datetime import datetime

from openpyxl import load_workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

XLSX = sys.argv[1] if len(sys.argv) > 1 else "monitoramento/Monitoramento_Diario_ARKAFLA.xlsx"
FONTES = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("Lib", f"{FONTES}/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LibB", f"{FONTES}/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("LibI", f"{FONTES}/LiberationSans-Italic.ttf"))

AZUL = colors.HexColor("#1F5F8B")
CINZA = colors.HexColor("#5E6B63")
HFILL = colors.HexColor("#E6ECE8")
ZEBRA = colors.HexColor("#F5F8F6")
INFILL = colors.HexColor("#FFF6D6")
LINHA = colors.HexColor("#C9D1CB")
VERDE = colors.HexColor("#1E7B45")
VERMELHO = colors.HexColor("#B03A2E")
FS = 6.2  # corpo da tabela


def br(v, casas, milhar=True):
    s = f"{v:,.{casas}f}" if milhar else f"{v:.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt(v, nf, sinal=False):
    """Formata como no Excel (formatos usados no script da planilha), em pt-BR."""
    if v is None or v == "":
        return ""
    if isinstance(v, str):
        return v
    base = nf.split(";")[0].lstrip("+")
    if base.endswith("%"):
        casas = len(base.split(".")[1]) - 1 if "." in base else 0
        s = br(v * 100, casas) + "%"
    else:
        casas = len(base.split(".")[1]) if "." in base else 0
        s = br(v, casas)
    if sinal and v > 0:
        s = "+" + s
    if s.lstrip("+-").strip("0,%") == "":
        s = "0"
    return s


wb = load_workbook(XLSX, data_only=True)
ws = wb["Monitoramento"]
HR = 4
ncol = ws.max_column
dias = [ws.cell(HR, j).value for j in range(3, ncol)]
dias = [d for d in dias if isinstance(d, datetime)]
ND = len(dias)
tem_var = ws.cell(HR, 3 + ND).value is not None
ultimo = dias[-1]

st_t = ParagraphStyle("t", fontName="LibB", fontSize=12.5, textColor=AZUL, leading=15)
st_s = ParagraphStyle("s", fontName="LibI", fontSize=7, textColor=CINZA, leading=9)
st_l = ParagraphStyle("l", fontName="LibB", fontSize=8, textColor=AZUL, leading=10)

# ---------------------------------------------------------------- tabela principal
cab = ["Indicador", "Un."] + [d.strftime("%d/%m") for d in dias] + (["Var."] if tem_var else [])
linhas = [cab]
estilo = [
    ("FONT", (0, 0), (-1, -1), "Lib", FS),
    ("FONT", (0, 0), (-1, 0), "LibB", FS),
    ("BACKGROUND", (0, 0), (-1, 0), HFILL),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("GRID", (0, 0), (-1, -1), 0.25, LINHA),
    ("TOPPADDING", (0, 0), (-1, -1), 0.6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0.9),
    ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ("TEXTCOLOR", (1, 1), (1, -1), CINZA),
]
n_item = 0
for r in range(HR + 1, ws.max_row + 1):
    rot = ws.cell(r, 1).value
    if rot is None:
        continue
    i = len(linhas)
    if ws.cell(r, 2).value is None:  # título de bloco
        linhas.append([rot] + [""] * (len(cab) - 1))
        estilo += [("SPAN", (0, i), (-1, i)), ("BACKGROUND", (0, i), (-1, i), AZUL),
                   ("TEXTCOLOR", (0, i), (-1, i), colors.white), ("FONT", (0, i), (-1, i), "LibB", FS)]
        n_item = 0
        continue
    vals = []
    for k in range(ND):
        c = ws.cell(r, 3 + k)
        vals.append(fmt(c.value, c.number_format))
    linha = [rot, ws.cell(r, 2).value] + vals
    if tem_var:
        c = ws.cell(r, 3 + ND)
        txt = fmt(c.value, c.number_format, sinal=True)
        linha.append(txt)
        if txt not in ("", "0"):
            estilo.append(("TEXTCOLOR", (-1, i), (-1, i), VERDE if c.value > 0 else VERMELHO))
        estilo.append(("FONT", (-1, i), (-1, i), "LibB", FS))
    if ws.cell(r, 3).fill.fgColor.rgb in ("00FFF6D6", "FFFFF6D6"):  # célula de entrada
        estilo.append(("BACKGROUND", (2, i), (1 + ND, i), INFILL))
    elif n_item % 2:
        estilo.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    estilo.append(("FONT", (2 + ND - 1, i), (2 + ND - 1, i), "LibB", FS))  # último dia em negrito
    linhas.append(linha)
    n_item += 1

LARG = A4[0] - 2 * 14 * 2.835  # margens de 14 mm
w_dia = 32
w_un = 30
w_var = 30 if tem_var else 0
w_rot = min(LARG - w_un - w_dia * ND - w_var, 200)
tab = Table(linhas, colWidths=[w_rot, w_un] + [w_dia] * ND + ([w_var] if tem_var else []),
            rowHeights=7.7, repeatRows=0)
tab.setStyle(TableStyle(estilo))
tab.hAlign = "LEFT"

# ---------------------------------------------------------------- produção por lote
wl = wb["Produção por lote"]
LH = 4
cab1 = ["Lote"] + sum([[d.strftime("%d/%m"), ""] for d in dias], [])
cab2 = [""] + ["Média", "DP"] * ND
pl = [cab1, cab2]
est2 = [
    ("FONT", (0, 0), (-1, -1), "Lib", FS),
    ("FONT", (0, 0), (-1, 1), "LibB", FS),
    ("BACKGROUND", (0, 0), (-1, 1), HFILL),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("GRID", (0, 0), (-1, -1), 0.25, LINHA),
    ("SPAN", (0, 0), (0, 1)),
    ("TOPPADDING", (0, 0), (-1, -1), 0.6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0.9),
    ("LEFTPADDING", (0, 0), (-1, -1), 1.5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 1.5),
]
for k in range(ND):
    est2.append(("SPAN", (1 + 2 * k, 0), (2 + 2 * k, 0)))
    est2.append(("TEXTCOLOR", (2 + 2 * k, 2), (2 + 2 * k, -1), CINZA))
r = LH + 2
while wl.cell(r, 1).value:
    i = len(pl)
    linha = [wl.cell(r, 1).value]
    for k in range(ND):
        for o in (0, 1):
            c = wl.cell(r, 2 + 2 * k + o)
            linha.append(fmt(c.value, c.number_format))
    pl.append(linha)
    if (i - 2) % 2:
        est2.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    r += 1
est2.append(("FONT", (0, len(pl) - 1), (-1, len(pl) - 1), "LibB", FS))
w_l = 98
w_c = min((LARG - w_l) / (2 * ND), 34)
tab2 = Table(pl, colWidths=[w_l] + [w_c] * (2 * ND), rowHeights=7.7)
tab2.setStyle(TableStyle(est2))
tab2.hAlign = "LEFT"

# ---------------------------------------------------------------- página
OUT = os.path.join(os.path.dirname(XLSX), f"Monitoramento_Diario_ARKAFLA_{ultimo:%Y-%m-%d}.pdf")
doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=14 * 2.835, rightMargin=14 * 2.835,
                        topMargin=10 * 2.835, bottomMargin=8 * 2.835,
                        title=f"ARKAFLA – Monitoramento diário {ultimo:%d/%m/%Y}")
sub = (f"Relatório zootécnico diário · {ND} dia(s): {dias[0]:%d/%m/%Y} a {ultimo:%d/%m/%Y} · "
       "Var. = último dia − dia anterior · Adultos: LACT &gt; 0 · Lactação: lotes 1 a 6 e 10 "
       "(10 = tratamento, leite descartado) · DP = desvio padrão")
partes = [Paragraph(f"ARKAFLA – Monitoramento diário do rebanho · {ultimo:%d/%m/%Y}", st_t),
          Paragraph(sub, st_s), Spacer(1, 4), tab, Spacer(1, 5),
          Paragraph("Produção por lote (kg/vaca, adultas com leite &gt; 0)", st_l), Spacer(1, 2), tab2]


def rodape(c, d):
    c.saveState()
    c.setFont("LibI", 6)
    c.setFillColor(CINZA)
    c.drawRightString(A4[0] - 14 * 2.835, 5 * 2.835,
                      "Definições completas na aba Notas da planilha Monitoramento_Diario_ARKAFLA.xlsx")
    c.restoreState()


doc.build(partes, onFirstPage=rodape)
from pypdf import PdfReader  # noqa: E402

n = len(PdfReader(OUT).pages)
print(f"{OUT}: {n} página(s)")
if n != 1:
    raise SystemExit("O PDF passou de uma página")
