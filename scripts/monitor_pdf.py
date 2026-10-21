"""PDF de duas páginas (A4 paisagem) com os resultados do monitoramento diário da ARCAFLA.

Lê a planilha já recalculada (valores das fórmulas) e grava
monitoramento/Monitoramento_Diario_ARCAFLA_AAAA-MM-DD.pdf (data do último dia).

Página 1 – painel visual:
  cabeçalho; 6 cartões de destaque (valor do dia, seta de melhora/piora, média e minigráfico);
  gráficos: produção por vaca e ECM nos dias exibidos, produção por lote (média e desvio padrão),
  leite DairyPlan × vendido, vacas com leite < 20 kg, % de gestantes e vazias/não gestantes;
  quadro "Atenção hoje" com os indicadores que mais pioraram.
Página 2 – tabela completa por blocos, coluna "Melhor" (↑/↓/0), variação com seta colorida e
  legenda "Como ler".

Cores: tinta escura para textos; série 1 azul #2A78D6, série 2 laranja #EB6834, série 3
verde-água #1BAF7A (paleta validada com o validate_palette.js da skill dataviz; o verde-água tem
contraste baixo e por isso todo gráfico leva rótulos com os valores); verde/vermelho só para
melhorou/piorou, sempre com seta.

Uso:
    python3 scripts/monitor_pdf.py [planilha.xlsx]
"""
import os
import re
import sys
from datetime import datetime

from openpyxl import load_workbook
from reportlab.graphics.shapes import Circle, Drawing, Line, PolyLine, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

XLSX = next((a for a in sys.argv[1:] if a.endswith(".xlsx")), None) or "monitoramento/Monitoramento_Diario_ARCAFLA.xlsx"
LIB = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("Lib", f"{LIB}/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LibB", f"{LIB}/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("LibI", f"{LIB}/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Sym", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

TINTA = colors.HexColor("#1F2328")
TINTA2 = colors.HexColor("#5E6B63")
TINTA3 = colors.HexColor("#8A8F8C")
AZUL = colors.HexColor("#2E3338")      # cor principal: cinza-escuro
AZUL_ESC = colors.HexColor("#1E2226")
AZUL_CLARO = colors.HexColor("#ECEEEF")
S1, S2, S3 = colors.HexColor("#2A78D6"), colors.HexColor("#EB6834"), colors.HexColor("#1BAF7A")
# cor de identidade de cada lote (escolhida pela fazenda; validada com validate_palette.js – sempre com o
# nome do lote escrito ao lado, porque verde × vermelho ficam próximos para daltônicos)
COR_LOTE = {1: colors.HexColor("#EDA100"), 2: colors.HexColor("#2A78D6"), 3: colors.HexColor("#E34948"),
            4: colors.HexColor("#008300"), 5: colors.HexColor("#6250D6"), 6: colors.HexColor("#EB6834")}
GRADE = colors.HexColor("#E4E7E5")
LINHA = colors.HexColor("#C9D1CB")
ZEBRA = colors.HexColor("#F6F8F7")
HOJE = colors.HexColor("#EAF2FB")
MEDIA = colors.HexColor("#F1F4F7")
INFILL = colors.HexColor("#FFF6D6")
FUNDO = colors.HexColor("#FAFBFA")
BOM = colors.HexColor("#0B7A0B")
RUIM = colors.HexColor("#B42D2D")
NEUTRO = colors.HexColor("#8A8A85")
BOM_BG = colors.HexColor("#E3F4E3")
RUIM_BG = colors.HexColor("#FBE6E6")
MM = 2.835
PAG = landscape(A4)
MARG = 10 * MM
LARG = PAG[0] - 2 * MARG
ALTP = PAG[1] - 2 * 7 * MM


# ---------------------------------------------------------------- formatação
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
    """Valor numérico (na célula "média (DP)" pega a média)."""
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        m = re.match(r"\s*(-?[\d.]+)", v)
        return float(m[1]) if m else None
    return None


def dp(v):
    """Desvio padrão de uma célula "média (DP)"."""
    m = re.search(r"\(([\d.]+)\)", v) if isinstance(v, str) else None
    return float(m[1]) if m else None


def juizo(melhor, var):
    if not isinstance(var, (int, float)) or abs(var) < 1e-9 or melhor not in ("↑", "↓", "0"):
        return None
    if melhor == "↑":
        return "bom" if var > 0 else "ruim"
    return "bom" if var < 0 else "ruim"


def cor_juizo(j):
    return BOM if j == "bom" else RUIM if j == "ruim" else NEUTRO


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
mcol = dcols[-1] + 1
vcol = mcol + 1 if ND >= 2 else None
ultimo = dias[-1]

linhas = []
for r in range(HR + 1, ws.max_row + 1):
    rot = ws.cell(r, 1).value
    if rot is None:
        continue
    cor = (ws.cell(r, 1).fill.fgColor.rgb or "")[-6:].upper()
    if ws.cell(r, 2).value is None and cor in ("1F5F8B", "2E3338"):  # faixa de seção
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


def serie(rot):
    it = itens.get(rot)
    return [num(v) for v in it["vals"]] if it else [None] * ND


def ultimo_valor(it):
    k = next((i for i in range(ND - 1, -1, -1) if it["vals"][i] not in (None, "")), None)
    return k, (it["vals"][k] if k is not None else None)


# ---------------------------------------------------------------- estilos de texto
def est(nome, fonte="Lib", tam=7, cor=TINTA, lead=None, al=0):
    return ParagraphStyle(nome, fontName=fonte, fontSize=tam, textColor=cor, leading=lead or tam * 1.2,
                          alignment=al)


st_cab = est("cab", "LibB", 17, colors.white, 19)
st_cab2 = est("cab2", "Lib", 8.5, colors.HexColor("#C9CDD1"), 10.5)
st_cabd = est("cabd", "LibB", 10, colors.white, 12, 2)
st_k = est("k", "LibB", 6.6, TINTA2, 7.8)
st_kv = est("kv", "LibB", 17, TINTA, 18.5)
st_ks = est("ks", "Lib", 6.5, TINTA2, 7.8)
st_gt = est("gt", "LibB", 8, TINTA, 9.5)
st_gs = est("gs", "Lib", 6.3, TINTA2, 7.5)
st_at = est("at", "Lib", 7.2, TINTA, 9.2)
st_ath = est("ath", "LibB", 8, RUIM, 9.5)
st_t2 = est("t2", "LibB", 11, AZUL, 13)
st_d2 = est("d2", "Lib", 7.5, TINTA2, 9, 2)
st_leg = est("leg", "Lib", 6.6, TINTA2, 8)
st_bl = est("bl", "LibB", 7, AZUL, 8, 1)


def var_html(it, tam):
    v = it["var"]
    if not isinstance(v, (int, float)):
        return ""
    txt = fmt(v, it["vfmt"], sinal=True)
    if txt == "0":
        return f'<font name="Sym" size="{tam - 1}" color="#8A8A85">=</font> 0'
    simb = "▲" if v > 0 else "▼"
    return f'<font name="Sym" size="{tam - 1}" color="{hexa(cor_juizo(juizo(it["melhor"], v)))}">{simb}</font> {txt}'


# ---------------------------------------------------------------- gráficos
def escala(vals, zero=False, folga=0.12):
    vs = [v for v in vals if v is not None]
    if not vs:
        return 0, 1
    lo, hi = min(vs), max(vs)
    if zero:
        lo = min(0, lo)
    if hi - lo < 1e-9:
        lo, hi = lo - 1, hi + 1
    f = (hi - lo) * folga
    return (lo if zero else lo - f), hi + f


def eixo_x(d, x0, y0, larg, n, rotulos):
    for i, r in enumerate(rotulos):
        x = x0 + (larg * (i + 0.5) / n)
        d.add(String(x, y0 - 9, r, fontName="Lib", fontSize=6, fillColor=TINTA3, textAnchor="middle"))


def grade_y(d, x0, y0, larg, alt, lo, hi, nf, ticks=3):
    for t in range(ticks + 1):
        v = lo + (hi - lo) * t / ticks
        y = y0 + alt * t / ticks
        d.add(Line(x0, y, x0 + larg, y, strokeColor=GRADE, strokeWidth=0.5))
        d.add(String(x0 - 3, y - 2, fmt(v, nf), fontName="Lib", fontSize=5.8, fillColor=TINTA3, textAnchor="end"))


def grafico_linhas(series, w, h, nf, nf_rot=None, zero=False):
    """series: [(nome, valores, cor)]. Rótulo direto no último ponto de cada série."""
    d = Drawing(w, h)
    x0, y0, larg, alt = 28, 14, w - 28 - 42, h - 22
    todos = [v for _, vs, _ in series for v in vs]
    lo, hi = escala(todos, zero)
    grade_y(d, x0, y0, larg, alt, lo, hi, nf)
    eixo_x(d, x0, y0, larg, ND, [x.strftime("%d/%m") for x in dias])
    rotulos = []
    for nome, vs, cor in series:
        pts = [(x0 + larg * (i + 0.5) / ND, y0 + alt * (v - lo) / (hi - lo)) for i, v in enumerate(vs) if v is not None]
        if len(pts) >= 2:
            d.add(PolyLine([c for p in pts for c in p], strokeColor=cor, strokeWidth=1.6))
        for x, y in pts:
            d.add(Circle(x, y, 1.8, fillColor=cor, strokeColor=colors.white, strokeWidth=0.6))
        if pts:
            rotulos.append([pts[-1][0], pts[-1][1], fmt([v for v in vs if v is not None][-1], nf_rot or nf)])
    # rótulos no fim das linhas sem sobreposição (afasta verticalmente os que ficam a < 8 pt)
    rotulos.sort(key=lambda r: r[1])
    for i in range(1, len(rotulos)):
        if rotulos[i][1] - rotulos[i - 1][1] < 8:
            rotulos[i][1] = rotulos[i - 1][1] + 8
    for x, y, txt in rotulos:
        d.add(String(x0 + larg + 4, y - 2, txt, fontName="LibB", fontSize=6.6, fillColor=TINTA))
    return d


def grafico_barras(rotulos, vals, w, h, nf, cor=S1, erros=None, destaque_ult=False, cores=None):
    d = Drawing(w, h)
    x0, y0, larg, alt = 26, 14, w - 26 - 6, h - 24
    topo = [(v or 0) + ((erros[i] or 0) if erros else 0) for i, v in enumerate(vals)]
    lo, hi = escala(topo + [0], zero=True, folga=0.16)
    grade_y(d, x0, y0, larg, alt, lo, hi, nf.replace(".0", "") if "%" not in nf else nf)
    n = len(vals)
    bw = larg / n * 0.56
    for i, v in enumerate(vals):
        cx = x0 + larg * (i + 0.5) / n
        d.add(String(cx, y0 - 9, rotulos[i], fontName="Lib", fontSize=6, fillColor=TINTA3, textAnchor="middle"))
        if v is None:
            continue
        c = (cores[i] if cores else cor)
        if destaque_ult and i < n - 1:
            c = colors.HexColor("#9EC5F4")
        hb = alt * (v - lo) / (hi - lo)
        d.add(Rect(cx - bw / 2, y0, bw, hb, fillColor=c, strokeColor=None, rx=1.5, ry=1.5))
        topo_txt = y0 + hb + 2
        if erros and erros[i]:
            e = alt * erros[i] / (hi - lo)
            d.add(Line(cx, y0 + hb - e, cx, y0 + hb + e, strokeColor=TINTA2, strokeWidth=0.7))
            d.add(Line(cx - 2.5, y0 + hb + e, cx + 2.5, y0 + hb + e, strokeColor=TINTA2, strokeWidth=0.7))
            topo_txt = y0 + hb + e + 2
        d.add(String(cx, topo_txt, fmt(v, nf), fontName="LibB", fontSize=6.4, fillColor=TINTA, textAnchor="middle"))
    return d


def grafico_pares(a, b, w, h, nf, nomes, cores):
    """Barras agrupadas por dia (duas séries com a mesma grandeza)."""
    d = Drawing(w, h)
    x0, y0, larg, alt = 30, 14, w - 30 - 6, h - 24
    lo, hi = escala([v for v in a + b if v is not None], folga=0.25)
    lo = max(0, lo)
    grade_y(d, x0, y0, larg, alt, lo, hi, nf)
    eixo_x(d, x0, y0, larg, ND, [x.strftime("%d/%m") for x in dias])
    bw = larg / ND * 0.3
    for i in range(ND):
        cx = x0 + larg * (i + 0.5) / ND
        for k, (vs, c) in enumerate(((a, cores[0]), (b, cores[1]))):
            v = vs[i]
            if v is None:
                continue
            x = cx - bw - 0.5 if k == 0 else cx + 0.5
            d.add(Rect(x, y0, bw, alt * (v - lo) / (hi - lo), fillColor=c, strokeColor=None, rx=1, ry=1))
    lx = x0
    for nome, c in zip(nomes, cores):
        d.add(Rect(lx, h - 7, 6, 6, fillColor=c, strokeColor=None))
        d.add(String(lx + 8, h - 6.5, nome, fontName="Lib", fontSize=6.2, fillColor=TINTA2))
        lx += 8 + pdfmetrics.stringWidth(nome, "Lib", 6.2) + 10
    return d


def caixa(titulo, sub, desenho, w):
    t = Table([[Paragraph(titulo, st_gt)], [Paragraph(sub, st_gs)], [desenho]], colWidths=[w])
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                           ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                           ("BOX", (0, 0), (-1, -1), 0.6, LINHA), ("BACKGROUND", (0, 0), (-1, -1), colors.white)]))
    return t


def legenda_series(pares):
    return " ".join(f'<font name="Sym" color="{hexa(c)}">●</font> {n}' for n, c in pares)


# ---------------------------------------------------------------- página 1: cartões
def sparkline(vals, w, h, cor_ult):
    d = Drawing(w, h)
    pts = [(i, v) for i, v in enumerate(vals) if v is not None]
    if len(pts) < 2:
        return d
    lo, hi = escala([v for _, v in pts], folga=0)
    n = max(len(vals) - 1, 1)
    xy = [c for i, v in pts for c in (2 + (w - 6) * i / n, 2 + (h - 5) * (v - lo) / (hi - lo))]
    d.add(PolyLine(xy, strokeColor=S1, strokeWidth=1.3))
    d.add(Circle(xy[-2], xy[-1], 2.2, fillColor=cor_ult, strokeColor=colors.white, strokeWidth=0.6))
    return d


def cartao(titulo, rot, extra, w):
    it = itens.get(rot)
    if not it:
        return Paragraph(titulo, st_k)
    k, ult = ultimo_valor(it)
    valor = fmt(num(ult), "0.0") if isinstance(ult, str) else (fmt(ult, it["fmts"][k]) if k is not None else "–")
    if k is not None and k != ND - 1:
        valor += f' <font size="7" color="#5E6B63">({dias[k]:%d/%m})</font>'
    j = juizo(it["melhor"], it["var"])
    l2 = var_html(it, 7.5)
    l2 = (l2 + " vs dia anterior") if l2 else '<font color="#8A8A85">sem dia anterior</font>'
    if it["media"] not in (None, ""):
        l2 += f' · média {fmt(it["media"], it["mfmt"])}'
    if extra:
        l2 += f"<br/>{extra}"
    corpo = Table([[Paragraph(titulo.upper(), st_k)], [Paragraph(valor, st_kv)], [Paragraph(l2, st_ks)],
                   [sparkline([num(v) for v in it["vals"]], w - 12, 13, cor_juizo(j))]],
                  colWidths=[w - 4], rowHeights=[9, 19, 17, 14])
    corpo.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                               ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return corpo


def v_ult(rot, nf):
    it = itens.get(rot)
    return fmt(ultimo_valor(it)[1], nf) if it else "–"


dpl = itens.get("Leite Total dia DairyPlan")
vdd = itens.get("Leite vendido no dia (coletas do laticínio)")
kv = next((i for i in range(ND - 1, -1, -1) if vdd and vdd["vals"][i] not in (None, "")), None)
dif_txt = (f'{fmt(dpl["vals"][kv], "#,##0")} kg × {fmt(vdd["vals"][kv], "#,##0")} L'
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
painel = Table([cards], colWidths=[CW] * 6, rowHeights=[64])
painel.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, LINHA), ("INNERGRID", (0, 0), (-1, -1), 0.6, LINHA),
                            ("BACKGROUND", (0, 0), (-1, -1), colors.white), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1),
                            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))

# ---------------------------------------------------------------- página 1: gráficos
G1W, G2W = LARG * 0.58 - 3, LARG * 0.42 - 3
GH1 = 150
g_prod = caixa("Produção por vaca nos últimos dias",
               legenda_series([("Produção média 24 h", S1), ("Leite ECM (gordura e proteína do tanque)", S2)])
               + " · kg/vaca",
               grafico_linhas([("prod", serie("Produção média nas últimas 24 h (DP)"), S1),
                               ("ecm", serie("Média de leite ECM (gordura e proteína do tanque)"), S2)],
                              G1W - 10, GH1, "0.0"), G1W)
lotes = [itens.get(f"Produção média do lote {lt} (DP)") for lt in range(1, 7)]
v_lote = [num(it["vals"][-1]) if it else None for it in lotes]
e_lote = [dp(it["vals"][-1]) if it else None for it in lotes]
g_lote = caixa(f"Produção por lote em {ultimo:%d/%m}",
               "Média em kg/vaca · traço = ± desvio padrão (quanto maior, mais desigual o lote)",
               grafico_barras([f"Lote {i}" for i in range(1, 7)], v_lote, G2W - 10, GH1, "0.0", erros=e_lote,
                              cores=[COR_LOTE[i] for i in range(1, 7)]),
               G2W)

G3W = LARG / 4 - 4.5
GH2 = 122
dp_s, vd_s = serie("Leite Total dia DairyPlan"), serie("Leite vendido no dia (coletas do laticínio)")
dif = itens.get("Diferença DairyPlan × vendido")
dif_med = fmt(dif["media"], dif["mfmt"]) if dif and dif["media"] not in (None, "") else "–"
g_leite = caixa("Leite DairyPlan × vendido",
                legenda_series([("DairyPlan (kg)", S1), ("Vendido (L)", S2)]) + f" · dif. média <b>{dif_med}</b>",
                grafico_linhas([("dp", dp_s, S1), ("vd", vd_s, S2)], G3W - 10, GH2, "#,##0"),
                G3W)
m20 = serie("Vacas com leite < 20 kg (tanque)")
g_20 = caixa("Vacas com leite abaixo de 20 kg",
             "Lotes 1 a 6 · 20 kg ≈ 19,4 L · bom quando cai",
             grafico_barras([x.strftime("%d/%m") for x in dias], m20, G3W - 10, GH2, "0", destaque_ult=True),
             G3W)
g_gest = caixa("Vacas gestantes (% sem DNB)", "Gestantes ÷ (adultas − DNB) · bom quando sobe",
               grafico_linhas([("gest", serie("% gestantes ÷ (adultas − DNB)"), S1)], G3W - 10, GH2, "0.0%"), G3W)
g_rep = caixa("Atrasos reprodutivos",
              legenda_series([("Vazias com IA > 35 dias", S2), ("DEL > 150 não gestantes", S1)]) + " · cab",
              grafico_linhas([("vaz", serie("Vazias com IA há > 35 dias"), S2),
                              ("ng", serie("DEL > 150 não gestantes (sem DNB)"), S1)], G3W - 10, GH2, "0"), G3W)


# ---------------------------------------------------------------- página 1: atenção hoje
def atencao(max_n=6):
    pior = []
    for it in itens.values():
        v = it["var"]
        if juizo(it["melhor"], v) != "ruim":
            continue
        base = num(it["vals"][-2]) if ND >= 2 else None
        rel = abs(v) / abs(base) if base not in (None, 0) else abs(v)
        if "%" in it["vfmt"]:
            rel = abs(v) * 5  # pontos percentuais
        pior.append((rel, it))
    pior.sort(key=lambda x: -x[0])
    out = []
    for _, it in pior[:max_n]:
        k, ult = ultimo_valor(it)
        val = fmt(num(ult), "0.0") if isinstance(ult, str) else fmt(ult, it["fmts"][k])
        out.append(f'<font name="Sym" color="#B42D2D">▼</font> <b>{it["rot"]}</b>: {val} '
                   f'({fmt(it["var"], it["vfmt"], sinal=True)} vs dia anterior)')
    return out


at = atencao()
txt_at = "<br/>".join(at) if at else "Nenhum indicador piorou em relação ao dia anterior."
quadro_at = Table([[Paragraph("Atenção hoje – o que mais piorou", st_ath)], [Paragraph(txt_at, st_at)]],
                  colWidths=[LARG])
quadro_at.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FDF3F3")),
                               ("LINEBEFORE", (0, 0), (0, -1), 3, RUIM), ("LEFTPADDING", (0, 0), (-1, -1), 8),
                               ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))

linha1 = Table([[g_prod, g_lote]], colWidths=[G1W + 6, G2W + 6])
linha2 = Table([[g_leite, g_20, g_gest, g_rep]], colWidths=[G3W + 6] * 4)
for t in (linha1, linha2):
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                           ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))


# ---------------------------------------------------------------- página 2: tabela
cabec = (["", "Indicador", "Un.", "Melhor"] + [d.strftime("%d/%m") for d in dias]
         + ["Média 10 dias"] + (["Var. (dia)"] if vcol else []))
NC = len(cabec)
CDIA0, CMED = 4, 4 + ND
CVAR = CMED + 1 if vcol else None
n_linhas = 1 + sum(1 for l in linhas if l["tipo"] != "bloco")
ALT = min(10.5, (ALTP - 22 - 40 - 14) / n_linhas)
FS = min(7.8, ALT - 1.0)
st_c = est("c", "Lib", FS, TINTA, FS + 0.3, 2)
dados = [cabec]
estilo = [
    ("FONT", (0, 0), (-1, -1), "Lib", FS), ("TEXTCOLOR", (0, 0), (-1, -1), TINTA),
    ("FONT", (0, 0), (-1, 0), "LibB", FS), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6ECE8")),
    ("ALIGN", (2, 0), (-1, -1), "CENTER"), ("ALIGN", (CDIA0, 1), (-1, -1), "RIGHT"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, -1), 0.25, LINHA),
    ("BOX", (0, 0), (-1, -1), 0.5, LINHA),
    ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0.8),
    ("LEFTPADDING", (0, 0), (-1, -1), 2.5), ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
    ("TEXTCOLOR", (2, 1), (2, -1), TINTA2), ("FONTSIZE", (2, 1), (2, -1), FS - 1),
    ("FONT", (3, 1), (3, -1), "Sym", FS), ("TEXTCOLOR", (3, 1), (3, -1), AZUL),
    ("BACKGROUND", (CDIA0 + ND - 1, 1), (CDIA0 + ND - 1, -1), HOJE),
    ("BACKGROUND", (CMED, 1), (CMED, -1), MEDIA),
    ("FONT", (CDIA0 + ND - 1, 0), (CDIA0 + ND - 1, -1), "LibB", FS), ("FONT", (CMED, 0), (CMED, -1), "LibB", FS),
]
blocos, bloco_ini, bloco_rot, n = [], None, None, 0


def fecha_bloco(fim):
    if bloco_ini is not None and fim >= bloco_ini:
        blocos.append((bloco_ini, fim, bloco_rot))


for l in linhas:
    i = len(dados)
    if l["tipo"] == "secao":
        fecha_bloco(i - 1)
        bloco_ini, bloco_rot = None, None
        dados.append([l["rot"]] + [""] * (NC - 1))
        estilo += [("SPAN", (0, i), (-1, i)), ("BACKGROUND", (0, i), (-1, i), AZUL),
                   ("TEXTCOLOR", (0, i), (-1, i), colors.white), ("FONT", (0, i), (-1, i), "LibB", FS + 0.4),
                   ("ALIGN", (0, i), (-1, i), "LEFT")]
        if "jovens" in l["rot"].lower():
            bloco_ini, bloco_rot = i + 1, "Recria"
        n = 0
        continue
    if l["tipo"] == "bloco":
        fecha_bloco(i - 1)
        bloco_ini, bloco_rot, n = i, l["rot"], 0
        continue
    vals = [fmt(v, f) for v, f in zip(l["vals"], l["fmts"])]
    linha = ["", ("    " if l["sub"] else "") + l["rot"], l["un"], l["melhor"]] + vals + [fmt(l["media"], l["mfmt"])]
    if vcol:
        linha.append(Paragraph(var_html(l, FS), st_c))
        j = juizo(l["melhor"], l["var"])
        if j:
            estilo.append(("BACKGROUND", (CVAR, i), (CVAR, i), BOM_BG if j == "bom" else RUIM_BG))
    dados.append(linha)
    if l["entrada"]:
        estilo.append(("BACKGROUND", (CDIA0, i), (CDIA0 + ND - 1, i), INFILL))
    elif n % 2:
        estilo.append(("BACKGROUND", (1, i), (CDIA0 + ND - 2, i), ZEBRA))
    if l["sub"]:
        estilo.append(("TEXTCOLOR", (1, i), (1, i), TINTA2))
    m_lote = re.search(r"lote (\d+)", l["rot"])
    if m_lote and int(m_lote[1]) in COR_LOTE and "Produção" in l["rot"]:  # marca colorida do lote
        c_l = COR_LOTE[int(m_lote[1])]
        estilo += [("LINEBEFORE", (1, i), (1, i), 4, c_l), ("TEXTCOLOR", (1, i), (1, i), TINTA),
                   ("FONT", (1, i), (1, i), "LibB", FS)]
    for k, v in enumerate(l["vals"]):
        if isinstance(v, str):
            estilo.append(("FONTSIZE", (CDIA0 + k, i), (CDIA0 + k, i), FS - 0.6))
    n += 1
fecha_bloco(len(dados) - 1)
for ini, fim, rot in blocos:
    dados[ini][0] = Paragraph(rot, st_bl)
    estilo += [("SPAN", (0, ini), (0, fim)), ("BACKGROUND", (0, ini), (0, fim), AZUL_CLARO),
               ("LINEBELOW", (0, fim), (-1, fim), 0.8, AZUL)]

w_bl, w_un, w_mel, w_med, w_rot = 66, 30, 26, 46, 180
w_var = 46 if vcol else 0
w_dia = min((LARG - w_bl - w_rot - w_un - w_mel - w_med - w_var) / ND, 60)
tab = Table(dados, colWidths=[w_bl, w_rot, w_un, w_mel] + [w_dia] * ND + [w_med] + ([w_var] if vcol else []),
            rowHeights=[ALT + 1] + [ALT] * (len(dados) - 1))
tab.setStyle(TableStyle(estilo))
tab.hAlign = "LEFT"

legenda = Paragraph(
    "<b>Como ler.</b> <b>Melhor</b>: <font name='Sym'>↑</font> bom quando sobe · <font name='Sym'>↓</font> "
    "bom quando desce · <b>0</b> bom perto de zero · vazio = sem sentido definido. "
    "<b>Var.</b>: último dia − dia anterior; <font name='Sym' color='#0B7A0B'>▲▼</font> verde = melhorou, "
    "<font name='Sym' color='#B42D2D'>▲▼</font> vermelho = piorou, <font name='Sym' color='#8A8A85'>▲▼</font> "
    "cinza = sem sentido definido. Coluna azul-clara = último dia; cinza = média dos dias exibidos. "
    "Produção: média (desvio padrão). Só fêmeas; adultas = LACT &gt; 0; lactação = lotes 1 a 6 e 10 "
    "(10 = tratamento, leite descartado; lotes 20/30 contam como 2/3); DNB fora da reprodução. "
    "Leite vendido (amarelo) = coletas do laticínio, em litros.", st_leg)


# ---------------------------------------------------------------- cabeçalhos e montagem
def cabecalho_p1():
    t = Table([[Paragraph("ARCAFLA", st_cab), Paragraph(f"Dados de {ultimo:%d/%m/%Y}", st_cabd)],
               [Paragraph(f"Monitoramento diário do rebanho · {ND} dia(s): {dias[0]:%d/%m} a {ultimo:%d/%m}",
                          st_cab2), Paragraph("", st_cab2)]],
              colWidths=[LARG * 0.65, LARG * 0.35])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), AZUL), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, 0), 5),
                           ("BOTTOMPADDING", (0, -1), (-1, -1), 5), ("TOPPADDING", (0, 1), (-1, 1), 0),
                           ("BOTTOMPADDING", (0, 0), (-1, 0), 0), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("LINEBELOW", (0, -1), (-1, -1), 2, S2)]))
    return t


def cabecalho_p2():
    t = Table([[Paragraph("ARCAFLA · Tabela completa dos indicadores", st_t2),
                Paragraph(f"Dados de <b>{ultimo:%d/%m/%Y}</b> · página 2 de 2", st_d2)]],
              colWidths=[LARG * 0.6, LARG * 0.4])
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                           ("LINEBELOW", (0, 0), (-1, 0), 1.2, AZUL)]))
    return t


def rodape(c, d):
    c.saveState()
    c.setFont("LibI", 6.2)
    c.setFillColor(TINTA3)
    c.drawString(MARG, 4.5 * MM, "ARCAFLA · Monitoramento diário · fonte: relatório zootécnico (BoviSync/DairyPlan), "
                                 "coletas e análises do laticínio")
    c.drawRightString(PAG[0] - MARG, 4.5 * MM, f"página {d.page} de 2")
    c.restoreState()


OUT = os.path.join(os.path.dirname(XLSX), f"Monitoramento_Diario_ARCAFLA_{ultimo:%Y-%m-%d}.pdf")
doc = SimpleDocTemplate(OUT, pagesize=PAG, leftMargin=MARG, rightMargin=MARG, topMargin=7 * MM,
                        bottomMargin=7 * MM, title=f"ARCAFLA – Monitoramento diário {ultimo:%d/%m/%Y}")
doc.build([cabecalho_p1(), Spacer(1, 6), painel, Spacer(1, 7), linha1, Spacer(1, 7), linha2, Spacer(1, 7),
           quadro_at, PageBreak(), cabecalho_p2(), Spacer(1, 4), tab, Spacer(1, 3), legenda],
          onFirstPage=rodape, onLaterPages=rodape)
from pypdf import PdfReader  # noqa: E402

npag = len(PdfReader(OUT).pages)
print(f"{OUT}: {npag} página(s)")
if npag != 2 and "--sem-checar" not in sys.argv:
    raise SystemExit("O PDF deveria ter 2 páginas")
