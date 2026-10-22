"""PDF de duas páginas (A4 paisagem) com os resultados do monitoramento diário da ARCAFLA.

Lê a planilha já recalculada (valores das fórmulas) e grava
monitoramento/Monitoramento_Diario_ARCAFLA_AAAA-MM-DD.pdf (data do último dia).

Página 1 – painel visual:
  cabeçalho; 6 cartões de destaque (valor do dia, seta de melhora/piora, média e minigráfico);
  gráficos: produção por vaca e ECM nos dias exibidos, produção por lote (média e desvio padrão),
  leite DairyPlan × comercializado, vacas com leite < 20 kg, % de gestantes e vazias/não gestantes;
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
import math
import os
import re
import sys
from datetime import datetime

from openpyxl import load_workbook
from reportlab.graphics.shapes import Circle, Drawing, Line, Path, PolyLine, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

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
BORDA = colors.HexColor("#DADDE0")
FUNDO_PAG = colors.HexColor("#F3F4F5")
ZEBRA = colors.HexColor("#F7F8F9")
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
MARG = 6 * MM
LARG = PAG[0] - 2 * MARG
ALTP = PAG[1] - 2 * 5 * MM


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


def clarear(c, f=0.80):
    """Tom claro de uma cor (mistura com branco)."""
    return colors.Color(c.red + (1 - c.red) * f, c.green + (1 - c.green) * f, c.blue + (1 - c.blue) * f)


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


st_cab = est("cab", "LibB", 18, colors.white, 19)
st_cab2 = est("cab2", "Lib", 9.5, colors.HexColor("#C9CDD1"), 10.5)
st_cabd = est("cabd", "LibB", 12, colors.white, 14, 2)
st_k = est("k", "LibB", 7.6, TINTA2, 8.8)
st_kv = est("kv", "LibB", 25, TINTA, 26)
st_ks = est("ks", "Lib", 7.4, TINTA2, 8.6)
st_gt = est("gt", "LibB", 9.5, TINTA, 11)
st_gs = est("gs", "Lib", 7.3, TINTA2, 8.6)
st_at = est("at", "Lib", 9, TINTA, 11)
st_ath = est("ath", "LibB", 9.5, RUIM, 11)
st_t2 = est("t2", "LibB", 11, AZUL, 13)
st_d2 = est("d2", "Lib", 7.5, TINTA2, 9, 2)
st_leg = est("leg", "Lib", 7, TINTA2, 8.4)
st_bl = est("bl", "LibB", 7.8, AZUL, 9, 1)


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
    # em gráficos estreitos pula datas (sempre mantendo a última) para os rótulos não se encostarem
    passo = max(1, math.ceil((pdfmetrics.stringWidth("00/00", "Lib", 7.6) + 6) / (larg / n)))
    for i, r in enumerate(rotulos):
        if (n - 1 - i) % passo:
            continue
        x = x0 + (larg * (i + 0.5) / n)
        d.add(String(x, y0 - 10, r, fontName="Lib", fontSize=7.6, fillColor=TINTA2, textAnchor="middle"))


def grade_y(d, x0, y0, larg, alt, lo, hi, nf, ticks=3):
    for t in range(ticks + 1):
        v = lo + (hi - lo) * t / ticks
        y = y0 + alt * t / ticks
        d.add(Line(x0, y, x0 + larg, y, strokeColor=GRADE, strokeWidth=0.6, strokeDashArray=[2, 2.5]))
        d.add(String(x0 - 3, y - 2, fmt(v, nf), fontName="Lib", fontSize=7.6, fillColor=TINTA2, textAnchor="end"))


def curva(pts, cor, area_y=None, largura=2.2):
    """Linha suave que passa exatamente pelos pontos sem ultrapassá-los (interpolação monotônica de
    Fritsch–Carlson): não cria picos nem vales que não existem nos dados. Com area_y, área clara até essa altura."""
    p = Path(strokeColor=None if area_y is not None else cor, strokeWidth=largura,
             fillColor=colors.Color(cor.red, cor.green, cor.blue, alpha=0.10) if area_y is not None else None,
             strokeLineCap=1, strokeLineJoin=1)
    n = len(pts)
    dx = [pts[k + 1][0] - pts[k][0] for k in range(n - 1)]
    dl = [(pts[k + 1][1] - pts[k][1]) / dx[k] for k in range(n - 1)]
    m = [dl[0]] + [0 if dl[k - 1] * dl[k] <= 0 else 2 / (1 / dl[k - 1] + 1 / dl[k]) for k in range(1, n - 1)] + [dl[-1]]
    p.moveTo(*pts[0])
    for k in range(n - 1):
        (x1, y1), (x2, y2), h = pts[k], pts[k + 1], dx[k]
        p.curveTo(x1 + h / 3, y1 + m[k] * h / 3, x2 - h / 3, y2 - m[k + 1] * h / 3, x2, y2)
    if area_y is not None:
        p.lineTo(pts[-1][0], area_y)
        p.lineTo(pts[0][0], area_y)
        p.closePath()
    return p


def grafico_linhas(series, w, h, nf, nf_rot=None, zero=False, area=False, valores=False, faixa=None):
    """series: [(nome, valores, cor)]. Rótulo direto no último ponto de cada série.
    faixa: (título, [texto por dia]) – linha de valores abaixo das datas (ex.: diferença %)."""
    d = Drawing(w, h)
    larg = w - 34 - 52
    # faixa: se os textos não cabem lado a lado, alterna em duas linhas (um dia em cima, outro embaixo)
    larg_txt = max((pdfmetrics.stringWidth(t, "LibB", 7.4) for t in (faixa[1] if faixa else []) if t), default=0)
    duas = bool(faixa) and larg_txt + 3 > larg / ND
    extra = (20 if duas else 12) if faixa else 0
    x0, y0, alt = 34, 14 + extra, h - 22 - extra
    if faixa:
        d.add(String(x0 - 3, 7 if duas else 3, faixa[0], fontName="LibB", fontSize=7, fillColor=TINTA2,
                     textAnchor="end"))
        for i, t in enumerate(faixa[1]):
            if t:
                y = (11 if (ND - 1 - i) % 2 else 3) if duas else 3
                d.add(String(x0 + larg * (i + 0.5) / ND, y, t, fontName="LibB", fontSize=7.4, fillColor=TINTA,
                             textAnchor="middle"))
    todos = [v for _, vs, _ in series for v in vs]
    lo, hi = escala(todos, zero)
    grade_y(d, x0, y0, larg, alt, lo, hi, nf)
    eixo_x(d, x0, y0, larg, ND, [x.strftime("%d/%m") for x in dias])
    rotulos = []
    for k, (nome, vs, cor) in enumerate(series):
        pts = [(x0 + larg * (i + 0.5) / ND, y0 + alt * (v - lo) / (hi - lo)) for i, v in enumerate(vs) if v is not None]
        if len(pts) >= 2:
            if area is True and k == 0 or area == "todas":  # área clara sob a(s) série(s)
                d.add(curva(pts, cor, area_y=y0))
            d.add(curva(pts, cor))
        vals_ok = [v for v in vs if v is not None]
        for idx, (x, y) in enumerate(pts[:-1]):
            d.add(Circle(x, y, 2.2 if valores else 1.3, fillColor=cor, strokeColor=colors.white,
                         strokeWidth=0.8 if valores else 0))
            if valores:  # valor de cada dia, do lado de fora: acima se a série está por cima naquele dia
                i_dia = [i for i, v in enumerate(vs) if v is not None][idx]
                outros = [o[1][i_dia] for o in series if o[1] is not vs and o[1][i_dia] is not None]
                por_cima = all(vs[i_dia] >= o for o in outros) if outros else True
                dy = 6 if por_cima else -11
                d.add(String(x, y + dy, fmt(vals_ok[idx], nf_rot or nf), fontName="LibB", fontSize=7.4,
                             fillColor=TINTA2, textAnchor="middle"))
        if pts:
            d.add(Circle(pts[-1][0], pts[-1][1], 3.4, fillColor=cor, strokeColor=colors.white, strokeWidth=1.4))
            rotulos.append([pts[-1][0], pts[-1][1], fmt([v for v in vs if v is not None][-1], nf_rot or nf)])
    # rótulos no fim das linhas sem sobreposição (afasta verticalmente os que ficam a < 8 pt)
    rotulos.sort(key=lambda r: r[1])
    for i in range(1, len(rotulos)):
        if rotulos[i][1] - rotulos[i - 1][1] < 11:
            rotulos[i][1] = rotulos[i - 1][1] + 11
    for x, y, txt in rotulos:
        d.add(String(x0 + larg + 4, y - 3, txt, fontName="LibB", fontSize=10, fillColor=TINTA))
    return d


def grafico_barras(rotulos, vals, w, h, nf, cor=S1, erros=None, destaque_ult=False, cores=None):
    d = Drawing(w, h)
    x0, y0, larg, alt = 30, 14, w - 30 - 6, h - 28
    topo = [(v or 0) + ((erros[i] or 0) if erros else 0) for i, v in enumerate(vals)]
    lo, hi = escala(topo + [0], zero=True, folga=0.16)
    grade_y(d, x0, y0, larg, alt, lo, hi, nf.replace(".0", "") if "%" not in nf else nf)
    n = len(vals)
    bw = larg / n * 0.56
    for i, v in enumerate(vals):
        cx = x0 + larg * (i + 0.5) / n
        if larg / n >= 30 or (n - 1 - i) % 2 == 0:  # em gráficos estreitos, um rótulo sim, outro não
            d.add(String(cx, y0 - 10, rotulos[i], fontName="Lib", fontSize=7.6, fillColor=TINTA2, textAnchor="middle"))
        if v is None:
            continue
        c = (cores[i] if cores else cor)
        if destaque_ult and i < n - 1:
            c = colors.HexColor("#9EC5F4")
        hb = alt * (v - lo) / (hi - lo)
        d.add(Rect(cx - bw / 2, y0, bw, hb, fillColor=c, strokeColor=None, rx=3.5, ry=3.5))
        topo_txt = y0 + hb + 2
        if erros and erros[i]:
            e = alt * erros[i] / (hi - lo)
            d.add(Line(cx, y0 + hb - e, cx, y0 + hb + e, strokeColor=TINTA2, strokeWidth=0.7))
            d.add(Line(cx - 2.5, y0 + hb + e, cx + 2.5, y0 + hb + e, strokeColor=TINTA2, strokeWidth=0.7))
            topo_txt = y0 + hb + e + 2
        d.add(String(cx, topo_txt, fmt(v, nf), fontName="LibB", fontSize=10, fillColor=TINTA, textAnchor="middle"))
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
                           ("TOPPADDING", (0, 0), (0, 0), 5),
                           ("BOX", (0, 0), (-1, -1), 0.5, BORDA), ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                           ("ROUNDEDCORNERS", [7, 7, 7, 7])]))
    return t


def legenda_series(pares):
    return " ".join(f'<font name="Sym" color="{hexa(c)}">●</font> {n}' for n, c in pares)


# ---------------------------------------------------------------- página 1: cartões
def sparkline(d, vals, x, y, w, h, cor_ult):
    """Linha dos últimos dias no rodapé do cartão (área suave, ponto final na cor do juízo)."""
    pts = [(i, v) for i, v in enumerate(vals) if v is not None]
    if len(pts) < 2:
        return
    lo, hi = escala([v for _, v in pts], folga=0)
    n = max(len(vals) - 1, 1)
    xy = [(x + (w - 4) * i / n, y + 2 + (h - 4) * (v - lo) / (hi - lo)) for i, v in pts]
    d.add(curva(xy, S1, area_y=y, largura=1.6))
    d.add(curva(xy, S1, largura=1.6))
    d.add(Circle(xy[-1][0], xy[-1][1], 2.8, fillColor=cor_ult, strokeColor=colors.white, strokeWidth=1))


def texto(d, x, y, partes, tam):
    """Escreve (texto, negrito, cor) em sequência na mesma linha."""
    for t, neg, cor in partes:
        f = "LibB" if neg else "Lib"
        d.add(String(x, y, t, fontName=f, fontSize=tam, fillColor=cor))
        x += pdfmetrics.stringWidth(t, f, tam)


def cartao(titulo, rot, extra, w, h, tv=None):
    """Cartão-resumo: título, valor grande, selo da variação, média, linha extra e sparkline."""
    d = Drawing(w, h)
    it = itens.get(rot)
    if not it:
        return d
    k, ult = ultimo_valor(it)
    valor = fmt(num(ult), "0.0") if isinstance(ult, str) else (fmt(ult, it["fmts"][k]) if k is not None else "–")
    j = juizo(it["melhor"], it["var"])
    cj = cor_juizo(j)
    d.add(Rect(0, 6, 3, h - 12, fillColor=cj, strokeColor=None, rx=1.5, ry=1.5))  # faixa do juízo
    x, dir_ = 10, w - 6  # margens: o texto começa em x e tudo termina em dir_
    y_tit, y_val, y_med, y_ext = h - 13, h - 40, h - 51, h - 61  # linhas de base iguais em todos os cartões
    d.add(String(x, y_tit, titulo.upper(), fontName="LibB", fontSize=TIT_TAM, fillColor=TINTA2))
    # selo da variação vs ontem: mesma largura e posição em todos os cartões
    v = it["var"]
    pw = 0
    if isinstance(v, (int, float)):
        txt = fmt(v, it["vfmt"], sinal=True)
        simb = "=" if txt == "0" else "▲" if v > 0 else "▼"
        txt = txt.lstrip("+-") if txt != "0" else "0"
        ws_, wt_ = pdfmetrics.stringWidth(simb, "Sym", 7), pdfmetrics.stringWidth(txt, "LibB", 8.6)
        pw = max(44, ws_ + wt_ + 10)
        fundo = BOM_BG if j == "bom" else RUIM_BG if j == "ruim" else AZUL_CLARO
        px, cx = dir_ - pw, dir_ - pw / 2
        d.add(Rect(px, y_val + 2.5, pw, 15, fillColor=fundo, strokeColor=None, rx=7.5, ry=7.5))
        x0 = cx - (ws_ + 2 + wt_) / 2
        d.add(String(x0, y_val + 7, simb, fontName="Sym", fontSize=7, fillColor=cj))
        d.add(String(x0 + ws_ + 2, y_val + 6.8, txt, fontName="LibB", fontSize=8.6, fillColor=cj))
        d.add(String(cx, y_med, "vs ontem", fontName="Lib", fontSize=6.2, fillColor=TINTA3, textAnchor="middle"))
    livre = dir_ - x - (pw + 6 if pw else 0)  # o valor encolhe se não couber ao lado do selo
    TAM_VALOR.append(min(27, livre / pdfmetrics.stringWidth(valor, "LibB", 1)))
    tv = tv or TAM_VALOR[-1]
    d.add(String(x, y_val, valor, fontName="LibB", fontSize=tv, fillColor=TINTA))
    linha = []
    if k is not None and k != ND - 1:
        linha.append((f"dado de {dias[k]:%d/%m} · ", True, RUIM))
    if it["media"] not in (None, ""):
        rot_med = "média 10 dias " if k == ND - 1 else "méd. "
        linha += [(rot_med, False, TINTA2), (fmt(it["media"], it["mfmt"]), True, TINTA2)]
    texto(d, x, y_med, linha, 7.4)
    if extra:
        texto(d, x, y_ext, [(extra[0] + " " if extra[0] else "", False, TINTA2), (extra[1], True, TINTA)], 7.4)
    # sparkline de x até dir_ (o ponto final fica alinhado à borda direita do selo)
    sparkline(d, [num(v) for v in it["vals"]], x, 4, dir_ - x + 1, 13, cj)
    return d


def v_ult(rot, nf):
    it = itens.get(rot)
    return fmt(ultimo_valor(it)[1], nf) if it else "–"


dpl = itens.get("Leite Total dia DairyPlan")
vdd = itens.get("Leite comercializado no dia (coletas do laticínio)")
kv = next((i for i in range(ND - 1, -1, -1) if vdd and vdd["vals"][i] not in (None, "")), None)
dif_txt = (("", f'{fmt(dpl["vals"][kv], "#,##0")} kg × {fmt(vdd["vals"][kv], "#,##0")} kg')
           if kv is not None else ("aguardando coletas", ""))
CW = LARG / 6
CH = 82  # altura dos cartões
TITULOS = ["Vacas em lactação", "Produção 24 h (kg/vaca)", "DairyPlan × comercializado", "Gestantes (sem DNB)",
           "Em tratamento (lote 10)", "Vazias com IA há > 35 dias"]
# um só tamanho de título para os 6 cartões: o maior que faz o título mais comprido caber
TIT_TAM = min(7.4, min((CW - 7 - 16) / pdfmetrics.stringWidth(t.upper(), "LibB", 1) for t in TITULOS))
def monta_cartoes(tv=None):
    return [
        cartao("Vacas em lactação", "Vacas em lactação (lotes 1 a 6 e 10)",
               ("no tanque:", v_ult("Em lactação no tanque (lotes 1 a 6)", "0")), CW - 7, CH - 2, tv),
        cartao("Produção 24 h (kg/vaca)", "Produção média nas últimas 24 h (DP)",
               ("ECM:", v_ult("Média de leite ECM (gordura e proteína do tanque)", "0.0") + " kg"), CW - 7, CH - 2, tv),
        cartao("DairyPlan × comercializado", "Diferença DairyPlan × comercializado", dif_txt, CW - 7, CH - 2, tv),
        cartao("Gestantes (sem DNB)", "% gestantes ÷ (adultas − DNB)",
               ("vacas gestantes:", v_ult("Vacas gestantes (DDP ≥ 1, sem DNB)", "0")), CW - 7, CH - 2, tv),
        cartao("Em tratamento (lote 10)", "Animais em tratamento (lote 10)",
               ("leite descartado:", v_ult("Leite descartado – lote 10", "#,##0") + " kg"), CW - 7, CH - 2, tv),
        cartao("Vazias com IA há > 35 dias", "Vazias com IA há > 35 dias",
               ("inseminadas > 35 d:", v_ult("Inseminadas (Bred) com IA há > 35 dias", "0")), CW - 7, CH - 2, tv),
    ]


TAM_VALOR = []
monta_cartoes()  # 1ª passada: tamanho que cada valor precisa
cards = monta_cartoes(min(TAM_VALOR))  # todos os valores no mesmo tamanho


def embrulha(conteudo, w, h):
    t = Table([[conteudo]], colWidths=[w], rowHeights=[h])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.white), ("BOX", (0, 0), (-1, -1), 0.5, BORDA),
                           ("ROUNDEDCORNERS", [7, 7, 7, 7]), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1),
                           ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return t


painel = Table([[embrulha(c, CW - 5, CH) for c in cards]], colWidths=[CW] * 6)
painel.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))

# ---------------------------------------------------------------- página 1: gráficos
G1W, G2W = LARG * 0.58 - 3, LARG * 0.42 - 3
GH1 = 158
g_prod = caixa("Produção por vaca nos últimos dias",
               legenda_series([("Produção média 24 h", S1), ("Leite ECM (gordura e proteína do tanque)", S3)])
               + " · kg/vaca",
               grafico_linhas([("prod", serie("Produção média nas últimas 24 h (DP)"), S1),
                               ("ecm", serie("Média de leite ECM (gordura e proteína do tanque)"), S3)],
                              G1W - 10, GH1, "0.0", area="todas", valores=True), G1W)
lotes = [itens.get(f"Produção média do lote {lt} (DP)") for lt in range(1, 7)]
v_lote = [num(it["vals"][-1]) if it else None for it in lotes]
e_lote = [dp(it["vals"][-1]) if it else None for it in lotes]
g_lote = caixa(f"Produção por lote em {ultimo:%d/%m}",
               "Média em kg/vaca · traço = ± desvio padrão (quanto maior, mais desigual o lote)",
               grafico_barras([f"Lote {i}" for i in range(1, 7)], v_lote, G2W - 10, GH1, "0.0", erros=e_lote,
                              cores=[COR_LOTE[i] for i in range(1, 7)]),
               G2W)

G3W = LARG * 0.22 - 6      # gráficos menores da 2ª fileira
GLW = LARG * 0.34 - 6      # leite DairyPlan × comercializado (kg), mais largo (dois conjuntos de valores)
GH2 = 134
dp_s, vd_s = serie("Leite Total dia DairyPlan"), serie("Leite comercializado no dia (coletas do laticínio)")
dp_s, vd_s = [[v / 1000 if v is not None else None for v in x] for x in (dp_s, vd_s)]  # em mil
dif = itens.get("Diferença DairyPlan × comercializado")
dif_med = fmt(dif["media"], dif["mfmt"]) if dif and dif["media"] not in (None, "") else "–"
g_leite = caixa("Leite DairyPlan × comercializado",
                legenda_series([("DairyPlan (mil kg)", S1), ("Comercializado (mil kg)", S3)]) + f" · dif. méd. <b>{dif_med}</b>",
                grafico_linhas([("dp", dp_s, S1), ("vd", vd_s, S3)], GLW - 10, GH2, "0.0",
                               area="todas", valores=True,
                               faixa=("dif.", [fmt(v, "+0.0%;-0.0%;0.0%", sinal=True) if isinstance(v, (int, float))
                                               else "" for v in (dif["vals"] if dif else [])])),
                GLW)
m20 = serie("Vacas com leite < 20 kg (tanque)")
g_20 = caixa("Vacas com leite abaixo de 20 kg",
             "Lotes 1 a 6 · 20 kg ≈ 19,4 L",
             grafico_barras([x.strftime("%d/%m") for x in dias], m20, G3W - 10, GH2, "0", destaque_ult=True),
             G3W)
g_gest = caixa("Vacas gestantes (% sem DNB)", "Gestantes ÷ (adultas − DNB)",
               grafico_linhas([("gest", serie("% gestantes ÷ (adultas − DNB)"), S1)], G3W - 10, GH2, "0.0%", area=True), G3W)
g_rep = caixa("Atrasos reprodutivos",
              legenda_series([("Vazias IA > 35 d", S2), ("DEL > 150 não gest.", S1)]),
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
if at:  # duas colunas para ocupar menos altura
    meio = (len(at) + 1) // 2
    col_at = [Paragraph("<br/>".join(at[:meio]), st_at), Paragraph("<br/>".join(at[meio:]), st_at)]
else:
    col_at = [Paragraph("Nenhum indicador piorou em relação ao dia anterior.", st_at), ""]
quadro_at = Table([[Paragraph('<font name="Sym">⚠</font> Atenção hoje', st_ath), ""], col_at],
                  colWidths=[LARG / 2, LARG / 2])
quadro_at.setStyle(TableStyle([("SPAN", (0, 0), (-1, 0)), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FDF0F0")),
                               ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#F2C9C9")),
                               ("ROUNDEDCORNERS", [7, 7, 7, 7]), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                               ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))

linha1 = Table([[g_prod, g_lote]], colWidths=[G1W + 6, G2W + 6])
linha2 = Table([[g_leite, g_20, g_gest, g_rep]], colWidths=[GLW + 6] + [G3W + 6] * 3)
for t in (linha1, linha2):
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                           ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))


# ---------------------------------------------------------------- página 2: tabela
w_bl, w_un, w_mel, w_med, w_rot = 70, 30, 30, 50, 196
w_var = 46 if vcol else 0


cabec = (["", "Indicador", "Un.", "Melhor"] + [d.strftime("%d/%m") for d in dias]
         + ["Média 10 dias"] + (["Var. (dia)"] if vcol else []))
NC = len(cabec)
CDIA0, CMED = 4, 4 + ND
CVAR = CMED + 1 if vcol else None
n_linhas = 1 + sum(1 for l in linhas if l["tipo"] != "bloco")
ALT = min(12, (ALTP - 27 - 28 - 8) / n_linhas)  # tabela ocupa toda a altura livre
FS = min(8.4, ALT - 0.9)
FSN = min(9.2, ALT - 0.6)  # números da tabela, maiores que os rótulos
st_c = est("c", "Lib", FSN, TINTA, FSN + 0.2, 2)
dados = [cabec]
estilo = [
    ("BACKGROUND", (0, 0), (-1, -1), colors.white), ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ("FONT", (0, 0), (-1, -1), "Lib", FS), ("TEXTCOLOR", (0, 0), (-1, -1), TINTA),
    ("FONT", (0, 0), (-1, 0), "LibB", FS), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A5158")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ALIGN", (2, 0), (-1, -1), "CENTER"), ("ALIGN", (CDIA0, 1), (-1, -1), "RIGHT"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.HexColor("#E6E8EA")),
    ("BOX", (0, 0), (-1, -1), 0.5, LINHA),
    ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.4),
    ("LEFTPADDING", (0, 0), (-1, -1), 2.5), ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
    ("TEXTCOLOR", (2, 1), (2, -1), TINTA2), ("FONTSIZE", (2, 1), (2, -1), FS - 1),
    ("FONT", (3, 1), (3, -1), "Sym", FS), ("TEXTCOLOR", (3, 1), (3, -1), AZUL),
    ("BACKGROUND", (CDIA0 + ND - 1, 1), (CDIA0 + ND - 1, -1), HOJE),
    ("BACKGROUND", (CDIA0 + ND - 1, 0), (CDIA0 + ND - 1, 0), colors.HexColor("#2A78D6")),
    ("BACKGROUND", (CMED, 1), (CMED, -1), MEDIA),
    ("FONTSIZE", (CDIA0, 1), (CMED, -1), FSN),
    ("FONT", (CDIA0 + ND - 1, 0), (CDIA0 + ND - 1, -1), "LibB", FSN), ("FONT", (CMED, 0), (CMED, -1), "LibB", FSN),
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
        linha.append(Paragraph(var_html(l, FSN), st_c))
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
                   ("FONT", (1, i), (1, i), "LibB", FS),
                   ("BACKGROUND", (1, i), (CMED, i), clarear(c_l))]  # linha no tom claro da cor do lote
    if l["rot"].startswith("Leite comercializado"):  # destaque: verde do gráfico DairyPlan × comercializado
        estilo += [("LINEBEFORE", (1, i), (1, i), 4, S3), ("BACKGROUND", (1, i), (CMED, i), clarear(S3, 0.78)),
                   ("FONT", (1, i), (1, i), "LibB", FS), ("TEXTCOLOR", (1, i), (CMED, i), TINTA),
                   ("FONT", (CDIA0, i), (CMED, i), "LibB", FSN)]
    for k, v in enumerate(l["vals"]):
        if isinstance(v, str):
            estilo.append(("FONTSIZE", (CDIA0 + k, i), (CDIA0 + k, i), FSN - 0.9))
    n += 1
fecha_bloco(len(dados) - 1)
for ini, fim, rot in blocos:
    dados[ini][0] = Paragraph(rot, st_bl)
    estilo += [("SPAN", (0, ini), (0, fim)), ("BACKGROUND", (0, ini), (0, fim), AZUL_CLARO),
               ("LINEBELOW", (0, fim), (-1, fim), 0.9, colors.HexColor("#9AA0A6"))]

w_dia = (LARG - w_bl - w_rot - w_un - w_mel - w_med - w_var) / ND  # tabela na largura toda da página
tab = Table(dados, colWidths=[w_bl, w_rot, w_un, w_mel] + [w_dia] * ND + [w_med] + ([w_var] if vcol else []),
            rowHeights=[ALT + 1] + [ALT] * (len(dados) - 1))
tab.setStyle(TableStyle(estilo))
tab.hAlign = "LEFT"

legenda = Paragraph(
    "<b>Como ler:</b> Melhor <font name='Sym'>↑</font> bom quando sobe, <font name='Sym'>↓</font> bom quando desce, "
    "<b>0</b> bom perto de zero · Var. = último dia − anterior: <font name='Sym' color='#0B7A0B'>▲▼</font> melhorou, "
    "<font name='Sym' color='#B42D2D'>▲▼</font> piorou, <font name='Sym' color='#8A8A85'>▲▼</font> sem sentido "
    "definido · azul-claro = último dia · Produção = média (desvio padrão) · só fêmeas · lactação = lotes 1–6 e 10 "
    "(10 = tratamento; 20/30 contam como 2/3) · verde = leite comercializado (kg).", st_leg)


# ---------------------------------------------------------------- cabeçalhos e montagem
LOGO = "dados/logo_arcafla.png"  # logo já recortada (sem a margem branca); se não existir, sai sem logo


def logo(alt):
    """Logo da fazenda com altura alt; None se o arquivo não existir."""
    if not os.path.exists(LOGO):
        return None
    from PIL import Image as PILImage
    w, h = PILImage.open(LOGO).size
    return Image(LOGO, width=alt * w / h, height=alt)


def com_logo(t, alt):
    """Põe a logo numa faixa branca à esquerda do cabeçalho t (mesmos cantos arredondados)."""
    lg = logo(alt)
    if lg is None:
        return t
    wl = lg.drawWidth + 12
    t._argW[0] -= wl  # a logo ocupa parte da coluna do título
    t.setStyle(TableStyle([("ROUNDEDCORNERS", None)]))  # quem arredonda agora é a tabela de fora
    tab = Table([[lg, t]], colWidths=[wl, LARG - wl])
    tab.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), colors.white), ("BACKGROUND", (1, 0), (1, 0), AZUL),
                             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (0, 0), "CENTER"),
                             ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                             ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                             ("ROUNDEDCORNERS", [8, 8, 8, 8])]))
    return tab


def cabecalho_p1():
    t = Table([[Paragraph("Monitoramento diário", st_cab), Paragraph(f"Dados de {ultimo:%d/%m/%Y}", st_cabd)],
               [Paragraph(f"Rebanho · {ND} dia(s): {dias[0]:%d/%m} a {ultimo:%d/%m}",
                          st_cab2), Paragraph("", st_cab2)]],
              colWidths=[LARG * 0.65, LARG * 0.35])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), AZUL), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, 0), 5),
                           ("BOTTOMPADDING", (0, -1), (-1, -1), 5), ("TOPPADDING", (0, 1), (-1, 1), 0),
                           ("BOTTOMPADDING", (0, 0), (-1, 0), 0), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("ROUNDEDCORNERS", [8, 8, 8, 8])]))
    return com_logo(t, 46)


def cabecalho_p2():
    t = Table([[Paragraph("Monitoramento diário · <font size=10 color='#C9CDD1'>Tabela completa dos indicadores</font>",
                          est("t2b", "LibB", 13, colors.white, 15)),
                Paragraph(f"Dados de {ultimo:%d/%m/%Y}", est("d2b", "LibB", 10, colors.white, 12, 2))]],
              colWidths=[LARG * 0.65, LARG * 0.35])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), AZUL), ("ROUNDEDCORNERS", [8, 8, 8, 8]),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t


def rodape(c, d):
    c.saveState()
    c.setFillColor(FUNDO_PAG)  # fundo cinza bem claro: os cartões brancos se destacam
    c.rect(0, 0, PAG[0], PAG[1], stroke=0, fill=1)
    c.setFont("LibI", 6.2)
    c.setFillColor(TINTA3)
    c.drawString(MARG, 2.2 * MM, "ARCAFLA · Monitoramento diário · fonte: relatório zootécnico (BoviSync/DairyPlan), "
                                 "coletas e análises do laticínio")
    c.drawRightString(PAG[0] - MARG, 2.2 * MM, f"página {d.page} de 2")
    c.restoreState()


OUT = os.path.join(os.path.dirname(XLSX), f"Monitoramento_Diario_ARCAFLA_{ultimo:%Y-%m-%d}.pdf")
doc = SimpleDocTemplate(OUT, pagesize=PAG, leftMargin=MARG, rightMargin=MARG, topMargin=5 * MM,
                        bottomMargin=5 * MM, title=f"ARCAFLA – Monitoramento diário {ultimo:%d/%m/%Y}")
doc.build([cabecalho_p1(), Spacer(1, 4), painel, Spacer(1, 5), linha1, Spacer(1, 5), linha2, Spacer(1, 5),
           quadro_at, PageBreak(), cabecalho_p2(), Spacer(1, 2), tab, Spacer(1, 2), legenda],
          onFirstPage=rodape, onLaterPages=rodape)
from pypdf import PdfReader  # noqa: E402

npag = len(PdfReader(OUT).pages)
print(f"{OUT}: {npag} página(s)")
if npag != 2 and "--sem-checar" not in sys.argv:
    raise SystemExit("O PDF deveria ter 2 páginas")
