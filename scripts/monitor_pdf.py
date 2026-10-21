"""PDF de uma página (A4 paisagem) com os resultados do monitoramento diário da ARCAFLA.

Lê a planilha já recalculada (valores das fórmulas) e grava
monitoramento/Monitoramento_Diario_ARCAFLA_AAAA-MM-DD.pdf (data do último dia).

Página:
  1. título;
  2. painel de destaques: 6 cartões com o valor do último dia, seta de melhora/piora em relação ao
     dia anterior (verde = melhorou, vermelho = piorou, cinza = sem sentido definido), média dos dias
     e um minigráfico com a evolução dos dias exibidos;
  3. tabela completa, dividida em blocos (coluna lateral), com a coluna "Melhor" (↑/↓/0) e a variação
     com seta colorida pelo mesmo critério;
  4. legenda "Como ler".

Uso:
    python3 scripts/monitor_pdf.py [planilha.xlsx]
"""
import os
import re
import sys
from datetime import datetime

from openpyxl import load_workbook
from reportlab.graphics.shapes import Circle, Drawing, PolyLine
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

XLSX = sys.argv[1] if len(sys.argv) > 1 else "monitoramento/Monitoramento_Diario_ARCAFLA.xlsx"
LIB = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("Lib", f"{LIB}/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LibB", f"{LIB}/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("LibI", f"{LIB}/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Sym", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

# cores: tinta (texto), superfícies, azul da marca, série dos minigráficos, status (bom/ruim) e neutro
TINTA = colors.HexColor("#1F2328")
TINTA2 = colors.HexColor("#5E6B63")
AZUL = colors.HexColor("#1F5F8B")
AZUL_CLARO = colors.HexColor("#E3ECF3")
SERIE = colors.HexColor("#2A78D6")
LINHA = colors.HexColor("#C9D1CB")
ZEBRA = colors.HexColor("#F6F8F7")
HOJE = colors.HexColor("#EAF2FB")
MEDIA = colors.HexColor("#F1F4F7")
INFILL = colors.HexColor("#FFF6D6")
BOM = colors.HexColor("#0B7A0B")
RUIM = colors.HexColor("#B42D2D")
NEUTRO = colors.HexColor("#8A8A85")
BOM_BG = colors.HexColor("#E3F4E3")
RUIM_BG = colors.HexColor("#FBE6E6")
FS = 6.1      # corpo da tabela
ALT = 7.3     # altura das linhas da tabela
MM = 2.835


def br(v, casas):
    s = f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt(v, nf, sinal=False):
    """Formata como o Excel (formatos usados na planilha), em pt-BR."""
    if v is None or v == "":
        return ""
    if isinstance(v, datetime):
        return v.strftime("%d/%m")
    if isinstance(v, str):  # "média (DP)": decimal com vírgula
        return v.replace(".", ",")
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


def num(v):
    """Valor numérico de uma célula (na linha "média (DP)" pega a média)."""
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        m = re.match(r"\s*(-?[\d.]+)", v)
        return float(m[1]) if m else None
    return None


def juizo(melhor, var):
    """'bom', 'ruim' ou None (sem sentido definido ou sem variação)."""
    if not isinstance(var, (int, float)) or abs(var) < 1e-9 or melhor not in ("↑", "↓", "0"):
        return None
    if melhor == "↑":
        return "bom" if var > 0 else "ruim"
    return "bom" if var < 0 else "ruim"  # ↓ e 0 (a variação já é da distância até zero)


def hexa(c):
    return "#" + c.hexval()[2:]


# ---------------------------------------------------------------- leitura da planilha
wb = load_workbook(XLSX, data_only=True)
ws = wb["Monitoramento"]
HR = 4
cab = [ws.cell(HR, j).value for j in range(1, ws.max_column + 1)]
dcols = [j + 1 for j, v in enumerate(cab) if isinstance(v, datetime)]
dias = [cab[j - 1] for j in dcols]
ND = len(dias)
mcol = dcols[-1] + 1                                  # Média 10 dias
vcol = mcol + 1 if ND >= 2 else None                  # Variação
ultimo = dias[-1]

linhas = []  # dicts: tipo secao/bloco/item
for r in range(HR + 1, ws.max_row + 1):
    rot = ws.cell(r, 1).value
    if rot is None:
        continue
    cor = (ws.cell(r, 1).fill.fgColor.rgb or "")[-6:].upper()
    if ws.cell(r, 2).value is None and cor == "1F5F8B":
        linhas.append({"tipo": "secao", "rot": rot})
    elif ws.cell(r, 2).value is None:
        linhas.append({"tipo": "bloco", "rot": rot})
    else:
        linhas.append({
            "tipo": "item", "rot": rot.strip(), "sub": rot.startswith("   "),
            "un": ws.cell(r, 2).value, "melhor": ws.cell(r, 3).value or "",
            "vals": [ws.cell(r, j).value for j in dcols], "fmts": [ws.cell(r, j).number_format for j in dcols],
            "media": ws.cell(r, mcol).value, "mfmt": ws.cell(r, mcol).number_format,
            "var": ws.cell(r, vcol).value if vcol else None,
            "vfmt": ws.cell(r, vcol).number_format if vcol else "0",
            "entrada": (ws.cell(r, dcols[0]).fill.fgColor.rgb or "")[-6:].upper() == "FFF6D6"})
itens = {l["rot"]: l for l in linhas if l["tipo"] == "item"}

# ---------------------------------------------------------------- estilos de texto
st_t = ParagraphStyle("t", fontName="LibB", fontSize=13, textColor=AZUL, leading=15)
st_d = ParagraphStyle("d", fontName="Lib", fontSize=7.5, textColor=TINTA2, leading=9, alignment=2)
st_k = ParagraphStyle("k", fontName="LibB", fontSize=6.3, textColor=TINTA2, leading=7.4)
st_kv = ParagraphStyle("kv", fontName="LibB", fontSize=14, textColor=TINTA, leading=15)
st_ks = ParagraphStyle("ks", fontName="Lib", fontSize=6.2, textColor=TINTA2, leading=7.4)
st_c = ParagraphStyle("c", fontName="Lib", fontSize=FS, textColor=TINTA, leading=FS + 0.3, alignment=2)
st_bl = ParagraphStyle("bl", fontName="LibB", fontSize=6.2, textColor=AZUL, leading=7, alignment=1)
st_leg = ParagraphStyle("leg", fontName="Lib", fontSize=6.0, textColor=TINTA2, leading=7.2)


def cor_juizo(j):
    return BOM if j == "bom" else RUIM if j == "ruim" else NEUTRO


def var_html(it, tam=FS):
    """Variação: seta colorida (▲/▼) + número em tinta escura."""
    v = it["var"]
    if not isinstance(v, (int, float)):
        return ""
    txt = fmt(v, it["vfmt"], sinal=True)
    if txt == "0":
        return f'<font name="Sym" size="{tam - 1}" color="#8A8A85">=</font> 0'
    j = juizo(it["melhor"], v)
    simb = "▲" if v > 0 else "▼"
    return f'<font name="Sym" size="{tam - 1}" color="{hexa(cor_juizo(j))}">{simb}</font> {txt}'


# ---------------------------------------------------------------- painel de destaques
def sparkline(vals, w, h, cor_ult):
    d = Drawing(w, h)
    pts = [(i, v) for i, v in enumerate(vals) if v is not None]
    if len(pts) < 2:
        return d
    vs = [v for _, v in pts]
    lo, hi = min(vs), max(vs)
    if hi - lo < 1e-9:
        lo, hi = lo - 1, hi + 1
    n = max(len(vals) - 1, 1)
    xy = []
    for i, v in pts:
        xy += [2 + (w - 6) * i / n, 2 + (h - 5) * (v - lo) / (hi - lo)]
    d.add(PolyLine(xy, strokeColor=SERIE, strokeWidth=1.3))
    d.add(Circle(xy[-2], xy[-1], 2.2, fillColor=cor_ult, strokeColor=colors.white, strokeWidth=0.6))
    return d


def ultimo_valor(it):
    k = next((i for i in range(ND - 1, -1, -1) if it["vals"][i] not in (None, "")), None)
    return k, (it["vals"][k] if k is not None else None)


def cartao(titulo, rot, extra, w):
    it = itens.get(rot)
    if not it:
        return Paragraph(titulo, st_k)
    k, ult = ultimo_valor(it)
    if isinstance(ult, str):  # "média (DP)"
        valor = fmt(num(ult), "0.0")
    else:
        valor = fmt(ult, it["fmts"][k]) if k is not None else "–"
    if k is not None and k != ND - 1:
        valor += f' <font size="7" color="#5E6B63">({dias[k]:%d/%m})</font>'
    j = juizo(it["melhor"], it["var"])
    linha2 = var_html(it, 7) or '<font color="#8A8A85">sem dia anterior</font>'
    if linha2 and isinstance(it["var"], (int, float)):
        linha2 += " vs dia anterior"
    if it["media"] not in (None, ""):
        linha2 += f' · média {fmt(it["media"], it["mfmt"])}'
    if extra:
        linha2 += f"<br/>{extra}"
    corpo = Table([[Paragraph(titulo.upper(), st_k)], [Paragraph(valor, st_kv)], [Paragraph(linha2, st_ks)],
                   [sparkline([num(v) for v in it["vals"]], w - 10, 11, cor_juizo(j))]],
                  colWidths=[w - 4], rowHeights=[8, 15, 15, 11])
    corpo.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                               ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return corpo


def v_ult(rot, nf):
    it = itens.get(rot)
    return fmt(ultimo_valor(it)[1], nf) if it else "–"


PAG = landscape(A4)
MARG = 9 * MM
LARG = PAG[0] - 2 * MARG
dp = itens.get("Leite Total dia DairyPlan")
vd = itens.get("Leite vendido no dia (coletas do laticínio)")
kv = next((i for i in range(ND - 1, -1, -1) if vd and vd["vals"][i] not in (None, "")), None)
dif_txt = (f'{fmt(dp["vals"][kv], "#,##0")} kg × {fmt(vd["vals"][kv], "#,##0")} L'
           if kv is not None else "aguardando coletas")
CW = LARG / 6
cards = [
    cartao("Vacas em lactação", "Vacas em lactação (lotes 1 a 6 e 10)",
           f'no tanque: {v_ult("Em lactação no tanque (lotes 1 a 6)", "0")}', CW),
    cartao("Produção média 24 h (kg/vaca)", "Produção média nas últimas 24 h (DP)",
           f'ECM: <b>{v_ult("Média de leite ECM (gordura e proteína do tanque)", "0.0")} kg</b>', CW),
    cartao("DairyPlan × leite vendido", "Diferença DairyPlan × vendido", dif_txt, CW),
    cartao("Vacas gestantes (sem DNB)", "% gestantes ÷ (adultas − DNB)",
           f'{v_ult("Vacas gestantes (DDP ≥ 1, sem DNB)", "0")} vacas gestantes', CW),
    cartao("Em tratamento (lote 10)", "Animais em tratamento (lote 10)",
           f'leite descartado: {v_ult("Leite descartado – lote 10", "#,##0")} kg', CW),
    cartao("Vazias com IA há > 35 dias", "Vazias com IA há > 35 dias",
           f'inseminadas há > 35 dias: {v_ult("Inseminadas (Bred) com IA há > 35 dias", "0")}', CW),
]
painel = Table([cards], colWidths=[CW] * 6, rowHeights=[51])
painel.setStyle(TableStyle([
    ("BOX", (0, 0), (-1, -1), 0.6, LINHA), ("INNERGRID", (0, 0), (-1, -1), 0.6, LINHA),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1),
    ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
]))

# ---------------------------------------------------------------- tabela
cabec = (["", "Indicador", "Un.", "Melhor"] + [d.strftime("%d/%m") for d in dias]
         + ["Média 10 dias"] + (["Var. (dia)"] if vcol else []))
NC = len(cabec)
CDIA0, CMED = 4, 4 + ND
CVAR = CMED + 1 if vcol else None
dados = [cabec]
est = [
    ("FONT", (0, 0), (-1, -1), "Lib", FS),
    ("TEXTCOLOR", (0, 0), (-1, -1), TINTA),
    ("FONT", (0, 0), (-1, 0), "LibB", FS),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6ECE8")),
    ("ALIGN", (2, 0), (-1, -1), "CENTER"),
    ("ALIGN", (CDIA0, 1), (-1, -1), "RIGHT"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LINEBELOW", (0, 0), (-1, -1), 0.25, LINHA),
    ("BOX", (0, 0), (-1, -1), 0.5, LINHA),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0.6),
    ("LEFTPADDING", (0, 0), (-1, -1), 2.2),
    ("RIGHTPADDING", (0, 0), (-1, -1), 2.2),
    ("TEXTCOLOR", (2, 1), (2, -1), TINTA2),
    ("FONTSIZE", (2, 1), (2, -1), 5.6),
    ("FONT", (3, 1), (3, -1), "Sym", 6.2),
    ("TEXTCOLOR", (3, 1), (3, -1), AZUL),
    ("BACKGROUND", (CDIA0 + ND - 1, 1), (CDIA0 + ND - 1, -1), HOJE),
    ("BACKGROUND", (CMED, 1), (CMED, -1), MEDIA),
    ("FONT", (CDIA0 + ND - 1, 0), (CDIA0 + ND - 1, -1), "LibB", FS),
    ("FONT", (CMED, 0), (CMED, -1), "LibB", FS),
]
blocos = []  # (início, fim, rótulo)
bloco_ini, bloco_rot, n = None, None, 0


def fecha_bloco(fim):
    if bloco_ini is not None and fim >= bloco_ini:
        blocos.append((bloco_ini, fim, bloco_rot))


for l in linhas:
    i = len(dados)
    if l["tipo"] == "secao":
        fecha_bloco(i - 1)
        bloco_ini, bloco_rot = None, None
        dados.append([l["rot"]] + [""] * (NC - 1))
        est += [("SPAN", (0, i), (-1, i)), ("BACKGROUND", (0, i), (-1, i), AZUL),
                ("TEXTCOLOR", (0, i), (-1, i), colors.white), ("FONT", (0, i), (-1, i), "LibB", FS + 0.4),
                ("ALIGN", (0, i), (-1, i), "LEFT")]
        if "jovens" in l["rot"].lower():  # sem blocos internos: um bloco só
            bloco_ini, bloco_rot = i + 1, "Recria"
        n = 0
        continue
    if l["tipo"] == "bloco":
        fecha_bloco(i - 1)
        bloco_ini, bloco_rot = i, l["rot"]
        n = 0
        continue
    vals = [fmt(v, f) for v, f in zip(l["vals"], l["fmts"])]
    rot = ("    " if l["sub"] else "") + l["rot"]
    linha = ["", rot, l["un"], l["melhor"]] + vals + [fmt(l["media"], l["mfmt"])]
    if vcol:
        linha.append(Paragraph(var_html(l), st_c))
        j = juizo(l["melhor"], l["var"])
        if j:
            est.append(("BACKGROUND", (CVAR, i), (CVAR, i), BOM_BG if j == "bom" else RUIM_BG))
    dados.append(linha)
    if l["entrada"]:
        est.append(("BACKGROUND", (CDIA0, i), (CDIA0 + ND - 1, i), INFILL))
    elif n % 2:
        est.append(("BACKGROUND", (1, i), (CDIA0 + ND - 2, i), ZEBRA))
    if l["sub"]:
        est.append(("TEXTCOLOR", (1, i), (1, i), TINTA2))
    for k, v in enumerate(l["vals"]):  # "média (DP)" em letra menor para caber
        if isinstance(v, str):
            est.append(("FONTSIZE", (CDIA0 + k, i), (CDIA0 + k, i), 5.6))
    n += 1
fecha_bloco(len(dados) - 1)
for ini, fim, rot in blocos:  # coluna lateral com o nome do bloco
    dados[ini][0] = Paragraph(rot, st_bl)
    est += [("SPAN", (0, ini), (0, fim)), ("BACKGROUND", (0, ini), (0, fim), AZUL_CLARO),
            ("LINEBELOW", (0, fim), (-1, fim), 0.8, AZUL)]

w_bl, w_un, w_mel, w_med = 50, 26, 22, 40
w_var = 40 if vcol else 0
w_rot = 168
w_dia = min((LARG - w_bl - w_rot - w_un - w_mel - w_med - w_var) / ND, 58)
tab = Table(dados, colWidths=[w_bl, w_rot, w_un, w_mel] + [w_dia] * ND + [w_med] + ([w_var] if vcol else []),
            rowHeights=[9] + [ALT] * (len(dados) - 1))
tab.setStyle(TableStyle(est))
tab.hAlign = "LEFT"

# ---------------------------------------------------------------- página
legenda = Paragraph(
    "<b>Como ler.</b> <b>Melhor</b>: <font name='Sym'>↑</font> bom quando sobe · <font name='Sym'>↓</font> "
    "bom quando desce · <b>0</b> bom perto de zero · vazio = sem sentido definido. "
    "<b>Var.</b>: último dia − dia anterior; <font name='Sym' color='#0B7A0B'>▲▼</font> verde = melhorou, "
    "<font name='Sym' color='#B42D2D'>▲▼</font> vermelho = piorou, <font name='Sym' color='#8A8A85'>▲▼</font> "
    "cinza = sem sentido definido. Coluna azul-clara = último dia; cinza = média dos dias exibidos. "
    "Produção: média (desvio padrão). Só fêmeas; adultas = LACT &gt; 0; lactação = lotes 1 a 6 e 10 "
    "(10 = tratamento, leite descartado; lotes 20/30 contam como 2/3); DNB fora da reprodução. "
    "Leite vendido (amarelo) = coletas do laticínio, em litros.", st_leg)
titulo = Table([[Paragraph("ARCAFLA · Monitoramento diário do rebanho", st_t),
                 Paragraph(f"Dados de <b>{ultimo:%d/%m/%Y}</b> · {ND} dia(s): {dias[0]:%d/%m} a "
                           f"{ultimo:%d/%m}", st_d)]], colWidths=[LARG * 0.6, LARG * 0.4])
titulo.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                            ("LINEBELOW", (0, 0), (-1, 0), 1.2, AZUL)]))

OUT = os.path.join(os.path.dirname(XLSX), f"Monitoramento_Diario_ARCAFLA_{ultimo:%Y-%m-%d}.pdf")
doc = SimpleDocTemplate(OUT, pagesize=PAG, leftMargin=MARG, rightMargin=MARG, topMargin=5 * MM,
                        bottomMargin=4 * MM, title=f"ARCAFLA – Monitoramento diário {ultimo:%d/%m/%Y}")
doc.build([titulo, Spacer(1, 3), painel, Spacer(1, 3), tab, Spacer(1, 2), legenda])
from pypdf import PdfReader  # noqa: E402

npag = len(PdfReader(OUT).pages)
print(f"{OUT}: {npag} página(s)")
if npag != 1:
    raise SystemExit("O PDF passou de uma página")
