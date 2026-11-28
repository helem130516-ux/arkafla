"""Tabela de produção diária (pedido da usuária em 28/11/2026).

Para cada dia com relatório do BoviSync (já com as correções de pesagem/partos aplicadas):
  - vacas em ordenha (lactação: lotes 1 a 7 e 10; o 7 só desde 03/11/2026; 20/30 contam como 2/3);
  - vacas no tanque (lotes 1 a 7);
  - média por vaca/dia (Leite > 0 das vacas em lactação = "Produção média nas últimas 24 h" do relatório);
  - leite total do DairyPlan (soma do Leite das vacas do tanque) e leite comercializado (kg = L × 1,032).
Grava monitoramento/analises/Producao_Diaria_AAAA-MM-DD_a_AAAA-MM-DD.xlsx e .pdf, com a média do período embaixo.

Uso:
    python3 scripts/tabela_producao.py [AAAA-MM-DD início] [AAAA-MM-DD fim]
"""
import glob
import json
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

LOTE7_DESDE = pd.Timestamp("2026-11-03")
DENS = 1.032
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]

ini = pd.Timestamp(sys.argv[1]) if len(sys.argv) > 1 else pd.Timestamp("2026-11-01")
arqs = sorted(glob.glob("dados/zootecnico/Zootecnico_*.xlsx"))
fim = pd.Timestamp(sys.argv[2]) if len(sys.argv) > 2 else pd.Timestamp(os.path.basename(arqs[-1])[11:21])
vendido = json.load(open("dados/leite_vendido.json"))

linhas = []
for a in arqs:
    d = pd.Timestamp(os.path.basename(a)[11:21])
    if not ini <= d <= fim:
        continue
    t = pd.read_excel(a)
    t.columns = t.columns.str.strip()
    t = t[t.StatRepro != "Male"]
    lote = t.Lote.replace({20: 2, 30: 3})
    lot_tq = list(range(1, 7)) + ([7] if d >= LOTE7_DESDE else [])
    lac = t[(t.LACT > 0) & (lote.isin(lot_tq) | (lote == 10))]
    tq = lac[lote[lac.index] != 10]
    com = lac[lac.Leite > 0]
    v = vendido.get(d.strftime("%Y-%m-%d"))
    linhas.append({"Data": d, "Dia": DIAS[d.weekday()], "Vacas em ordenha": len(lac), "Vacas no tanque": len(tq),
                   "Média kg/vaca/dia": com.Leite.mean(), "Leite total DairyPlan (kg)": tq.Leite[tq.Leite > 0].sum(),
                   "Leite comercializado (kg)": v * DENS if v is not None else None})
df = pd.DataFrame(linhas)


def r(v, casas):
    if v is None or pd.isna(v):
        return None
    return float(Decimal(str(round(float(v), 9))).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP))


def br(v, casas):
    if v is None:
        return "–"
    s = f"{v:,.{casas}f}"
    return s.replace(",", "#").replace(".", ",").replace("#", ".")


media = {"Vacas em ordenha": df["Vacas em ordenha"].mean(), "Vacas no tanque": df["Vacas no tanque"].mean(),
         "Média kg/vaca/dia": df["Média kg/vaca/dia"].mean(),
         "Leite total DairyPlan (kg)": df["Leite total DairyPlan (kg)"].mean(),
         "Leite comercializado (kg)": df["Leite comercializado (kg)"].dropna().mean()}
base = f"monitoramento/analises/Producao_Diaria_{df.Data.min():%Y-%m-%d}_a_{df.Data.max():%Y-%m-%d}"
os.makedirs("monitoramento/analises", exist_ok=True)

# ---------------------------------------------------------------- planilha
with pd.ExcelWriter(base + ".xlsx") as w:
    out = df.copy()
    out.loc[len(out)] = {"Data": None, "Dia": "Média", **media}
    out.to_excel(w, sheet_name="Produção diária", index=False, startrow=2)
wb = load_workbook(base + ".xlsx")
ws = wb.active
ws["A1"] = (f"ARCAFLA – Produção diária de {df.Data.min():%d/%m/%Y} a {df.Data.max():%d/%m/%Y} "
            "(ordenha = lactação, lotes 1 a 7 e 10; média = Leite > 0)")
ws["A1"].font = Font(bold=True, size=12, color="2E3338")
fino = Side(style="thin", color="D0D4D8")
fmts = {"Data": "DD/MM/YYYY", "Vacas em ordenha": "#,##0", "Vacas no tanque": "#,##0", "Média kg/vaca/dia": "0.0",
        "Leite total DairyPlan (kg)": "#,##0", "Leite comercializado (kg)": "#,##0"}
for c in ws[3]:
    c.font = Font(bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor="2E3338")
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws.row_dimensions[3].height = 32
for row in ws.iter_rows(min_row=4):
    ult = row[0].row == ws.max_row
    for c in row:
        cab = ws.cell(3, c.column).value
        c.number_format = fmts.get(cab, "General")
        c.alignment = Alignment(horizontal="center")
        c.border = Border(bottom=fino)
        if ult:
            c.font = Font(bold=True)
            c.fill = PatternFill("solid", fgColor="E8F3EC")
            if cab in ("Vacas em ordenha", "Vacas no tanque"):
                c.number_format = "#,##0"
for col, wdt in zip("ABCDEFG", (12, 7, 12, 12, 12, 16, 16)):
    ws.column_dimensions[col].width = wdt
ws.freeze_panes = "A4"
wb.save(base + ".xlsx")

# ---------------------------------------------------------------- PDF
def fonte(nome):
    for p in (f"fontes/{nome}", f"/usr/share/fonts/truetype/liberation/{nome}"):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(nome)


pdfmetrics.registerFont(TTFont("Lib", fonte("LiberationSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("LibB", fonte("LiberationSans-Bold.ttf")))
TINTA, TINTA2, BORDA = colors.HexColor("#2E3338"), colors.HexColor("#5F6870"), colors.HexColor("#D0D4D8")
dados = [["Data", "Dia", "Vacas em\nordenha", "Vacas no\ntanque", "Média\nkg/vaca/dia", "Leite total\nDairyPlan (kg)",
          "Leite\ncomercializado (kg)"]]
for _, x in df.iterrows():
    dados.append([x.Data.strftime("%d/%m"), x.Dia, br(x["Vacas em ordenha"], 0), br(x["Vacas no tanque"], 0),
                  br(r(x["Média kg/vaca/dia"], 1), 1), br(r(x["Leite total DairyPlan (kg)"], 0), 0),
                  br(r(x["Leite comercializado (kg)"], 0), 0)])
dados.append(["Média", "", br(r(media["Vacas em ordenha"], 0), 0), br(r(media["Vacas no tanque"], 0), 0),
              br(r(media["Média kg/vaca/dia"], 1), 1), br(r(media["Leite total DairyPlan (kg)"], 0), 0),
              br(r(media["Leite comercializado (kg)"], 0), 0)])
n = len(dados)
LARG = A4[0] - 28 * mm
tab = Table(dados, colWidths=[LARG * f for f in (0.10, 0.08, 0.13, 0.13, 0.15, 0.20, 0.21)], repeatRows=1)
est = [("FONTNAME", (0, 0), (-1, 0), "LibB"), ("FONTSIZE", (0, 0), (-1, -1), 8.6),
       ("BACKGROUND", (0, 0), (-1, 0), TINTA), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
       ("FONTNAME", (0, 1), (-1, -1), "Lib"), ("TEXTCOLOR", (0, 1), (-1, -1), TINTA),
       ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
       ("LINEBELOW", (0, 1), (-1, -2), 0.4, BORDA), ("TOPPADDING", (0, 0), (-1, -1), 2.6),
       ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
       ("BACKGROUND", (0, n - 1), (-1, n - 1), colors.HexColor("#E8F3EC")),
       ("FONTNAME", (0, n - 1), (-1, n - 1), "LibB"), ("LINEABOVE", (0, n - 1), (-1, n - 1), 1, TINTA)]
for i, x in enumerate(df.itertuples(), start=1):  # fim de semana em cinza claro
    if x.Dia in ("sáb", "dom"):
        est.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F3F4F6")))
tab.setStyle(TableStyle(est))
s_tit = ParagraphStyle("t", fontName="LibB", fontSize=16, textColor=TINTA, leading=20)
s_sub = ParagraphStyle("s", fontName="Lib", fontSize=9, textColor=TINTA2, leading=12)
s_nota = ParagraphStyle("n", fontName="Lib", fontSize=7.5, textColor=TINTA2, leading=10)
cab = [Paragraph("Produção diária", s_tit),
       Paragraph(f"Fazenda ARCAFLA · Castro – PR · {df.Data.min():%d/%m/%Y} a {df.Data.max():%d/%m/%Y}", s_sub)]
topo = Table([[Image("dados/logo_arcafla.png", width=26 * mm, height=18 * mm, kind="proportional"), cab]],
             colWidths=[30 * mm, LARG - 30 * mm]) if os.path.exists("dados/logo_arcafla.png") else cab
if isinstance(topo, Table):
    topo.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
doc = SimpleDocTemplate(base + ".pdf", pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm,
                        bottomMargin=12 * mm, title="Produção diária – ARCAFLA")
doc.build([topo, Spacer(1, 5 * mm), tab, Spacer(1, 3 * mm),
           Paragraph("Vacas em ordenha = lactação (lotes 1 a 7 e 10; o 7 desde 03/11). Vacas no tanque = lotes 1 a 7. "
                     "Média kg/vaca/dia = média do Leite das vacas em ordenha com pesagem (Leite > 0). "
                     "Leite total DairyPlan = soma do Leite das vacas do tanque. Leite comercializado = coletas do "
                     "laticínio (L × 1,032); “–” = coleta ainda não recebida. Fim de semana em cinza. Dias de 18 a "
                     "20/11 com queda real por calor. Fonte: BoviSync/DairyPlan e coletas Castrolanda.", s_nota)])
print(base + ".xlsx")
print(base + ".pdf")
print(df.assign(**{"Média kg/vaca/dia": df["Média kg/vaca/dia"].round(1)}).to_string(index=False))
print("média:", {k: round(v, 1) for k, v in media.items()})
