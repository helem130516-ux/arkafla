# Gráficos do Relatório Financeiro · Leite (ago/2026) em 2 páginas A4 retrato, para impressão.
# Uso: python3 scripts/gera_graficos_financeiro_a4.py && node scripts/html_para_pdf.js <html> <pdf>
import base64, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "relatorios" / "ARCAFLA_Graficos_Financeiro_2026-08_A4.html"

MESES = ["set/25", "out/25", "nov/25", "dez/25", "jan/26", "fev/26", "mar/26", "abr/26", "mai/26", "jun/26", "jul/26", "ago/26"]
REC_L = [3.01, 2.88, 2.72, 2.64, 2.40, 2.44, 2.63, 2.77, 2.92, 2.87, 2.98, 3.35]
CUS_L = [2.04, 1.87, 2.15, 2.19, 2.04, 2.14, 2.27, 2.28, 2.08, 2.24, 2.22, 2.03]
FAT = [5.69, 5.74, 5.22, 5.13, 4.68, 4.20, 4.94, 5.12, 5.83, 5.89, 6.45, 7.10]
DESP = [3.85, 3.74, 4.12, 4.26, 3.99, 3.69, 4.27, 4.21, 4.14, 4.61, 4.81, 4.30]
PROD = [1.89, 2.00, 1.92, 1.95, 1.95, 1.72, 1.88, 1.85, 1.99, 2.06, 2.16, 2.12]
# (item, % do custo em ago/26, média 2026)
COMPOS = [("Alimentação", 63.6, 62.8), ("Medicamentos", 8.1, 8.4), ("Mão de obra", 6.7, 7.5),
          ("Conservação e reparos", 6.5, 7.1), ("Taxas da cooperativa", 4.9, 4.1), ("Reprodução", 3.8, 2.7),
          ("Energia elétrica", 2.4, 1.2), ("Higienização", 1.9, 3.3), ("Combustíveis", 1.5, 1.5),
          ("Demais despesas", 0.6, 1.4)]
# (nome, R$ mil por mês set/25–ago/26, valor ago, média 12m, R$/L, % vs média)
TOP5 = [("Alimentação", [2280, 2314, 2514, 2651, 2403, 2271, 2650, 2633, 2631, 2910, 3137, 2734], "R$ 2.733.868", 2594.002, "R$ 1,29/L", "+5%"),
        ("Medicamentos", [399, 263, 382, 331, 357, 347, 370, 261, 337, 497, 324, 350], "R$ 349.668", 351.491, "R$ 0,17/L", "-1%"),
        ("Mão de obra", [287, 257, 248, 469, 318, 343, 324, 358, 279, 337, 317, 287], "R$ 287.410", 318.610, "R$ 0,14/L", "-10%"),
        ("Conservação e reparos", [275, 235, 321, 161, 288, 181, 291, 352, 345, 334, 355, 280], "R$ 280.255", 284.853, "R$ 0,13/L", "-2%"),
        ("Taxas da cooperativa", [125, 176, 162, 157, 153, 134, 154, 166, 186, 191, 209, 212], "R$ 212.354", 168.712, "R$ 0,10/L", "+26%")]

VERDE, LARANJA, OURO, CINZA = "#1f6b3a", "#d9822b", "#e0a21a", "#9aa39d"
INK, INK2, GRADE = "#1d2621", "#5e6b63", "#e3e7e3"
br = lambda v, d=2: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def barras(series, cores, W=700, H=230, dec=2, rotulo_dentro=True, destaque=None, media=None, fmt=None):
    """Barras agrupadas por mês, eixo a partir de zero, valores escritos em cada barra."""
    fmt = fmt or (lambda v: br(v, dec))
    ml, mr, mt, mb = 8, 8, 16, 21
    iw, ih = W - ml - mr, H - mt - mb
    vmax = max(max(s) for s in series) * 1.08
    n, k = len(series[0]), len(series)
    slot = iw / n
    bw = min(26, (slot * 0.78) / k)
    gap = 2
    g = f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
    base = mt + ih
    for i in range(n):
        x0 = ml + i * slot + (slot - (bw * k + gap * (k - 1))) / 2
        for j, s in enumerate(series):
            v = s[i]
            h = ih * v / vmax
            x, y = x0 + j * (bw + gap), base - h
            cor = cores[j]
            if destaque is not None and i == destaque and k == 1:
                cor = OURO
            g += f'<path d="M{x:.1f},{base} V{y+3:.1f} Q{x:.1f},{y:.1f} {x+3:.1f},{y:.1f} H{x+bw-3:.1f} Q{x+bw:.1f},{y:.1f} {x+bw:.1f},{y+3:.1f} V{base} Z" fill="{cor}"/>'
            if rotulo_dentro and k > 1:
                cx, cy = x + bw / 2, base - 5
                g += f'<text x="{cx:.1f}" y="{cy:.1f}" transform="rotate(-90 {cx:.1f} {cy:.1f})" dy="3.5" font-size="10" font-weight="700" fill="#fff">{fmt(v)}</text>'
            else:
                g += f'<text x="{x+bw/2:.1f}" y="{y-4:.1f}" text-anchor="middle" font-size="10.5" font-weight="{700 if i == destaque else 400}" fill="{INK}" stroke="#fff" stroke-width="3" paint-order="stroke">{fmt(v)}</text>'
        rot = MESES[i] if len(MESES[i]) and dec != -1 else MESES[i][:3]
        g += f'<text x="{ml+i*slot+slot/2:.1f}" y="{base+15}" text-anchor="middle" font-size="10.5" font-weight="{700 if i == n-1 else 400}" fill="{INK if i == n-1 else INK2}">{rot}</text>'
    g += f'<line x1="{ml}" x2="{W-mr}" y1="{base}" y2="{base}" stroke="{INK2}" stroke-width="1"/>'
    if media is not None:
        y = base - ih * media / vmax
        g += f'<line x1="{ml}" x2="{W-mr}" y1="{y:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.2" stroke-dasharray="5 4"/>'
    return g + "</svg>"


def composicao(W=700):
    lh, ml, vw = 20, 170, 52
    iw = W - ml - vw - 10
    H = lh * len(COMPOS) + 6
    vmax = 70
    g = f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
    for i, (nome, v, m) in enumerate(COMPOS):
        y = 4 + i * lh
        g += f'<text x="0" y="{y+13}" font-size="11.5" fill="{INK}">{nome}</text>'
        g += f'<rect x="{ml}" y="{y+3}" width="{iw}" height="13" rx="3" fill="#f0f2f0"/>'
        g += f'<rect x="{ml}" y="{y+3}" width="{max(iw*v/vmax,2):.1f}" height="13" rx="3" fill="{LARANJA if i == 0 else VERDE}"/>'
        xm = ml + iw * m / vmax
        g += f'<line x1="{xm:.1f}" x2="{xm:.1f}" y1="{y}" y2="{y+19}" stroke="{INK}" stroke-width="2"/>'
        g += f'<text x="{W}" y="{y+13}" text-anchor="end" font-size="12" font-weight="700" fill="{INK}">{br(v,1)}%</text>'
    return g + "</svg>"


def kpi(cor, titulo, var, valor, sub):
    return f'<div class="kpi" style="border-left-color:{cor}"><div class="kt"><span>{titulo}</span><b>{var}</b></div><div class="kv" style="color:{cor}">{valor}</div><div class="ks">{sub}</div></div>'


def leg(*itens):
    return '<div class="leg">' + "".join(f'<span><i style="background:{c}"></i>{t}</span>' for c, t in itens) + "</div>"


logo = ROOT / "assets" / "logo_arcafla_small.png"
logo_tag = f'<img src="data:image/png;base64,{base64.b64encode(logo.read_bytes()).decode()}" alt="ARCAFLA">' if logo.exists() else ""

cabec = lambda pag: f'''<header>{logo_tag}<div><div class="eyebrow">RELATÓRIO FINANCEIRO · LEITE</div>
<h1>Agosto de 2026 · Gráficos</h1><div class="sub">Dados do Agriwin, atualizados em 11/11/2026 · últimos 12 meses (set/25–ago/26)</div></div>
<div class="pg">pág. {pag}/2</div></header>'''

kpis = "".join([
    kpi(OURO, "FATURAMENTO", "+10,1% vs jul/26", "R$ 7,10 mi", "2,12 milhões de litros a R$ 3,04"),
    kpi("#b03a2e", "DESPESAS", "−10,5% vs jul/26", "R$ 4,30 mi", "alimentação é 63,6% do total"),
    kpi(VERDE, "SALDO DO MÊS", "+70,1% vs jul/26", "R$ 2,80 mi", "sobra 39,4% do faturamento"),
    kpi("#1d4f7a", "RECEITA POR LITRO", "+R$ 0,37 vs jul/26", "R$ 3,35", "leite a R$ 3,04 + outras receitas"),
    kpi("#b03a2e", "CUSTO POR LITRO", "−R$ 0,19 vs jul/26", "R$ 2,03", "custo operacional de cada litro"),
    kpi(VERDE, "MARGEM POR LITRO", "+R$ 0,56 vs jul/26", "R$ 1,32", "o que sobra de cada litro"),
])

pequenos = ""
for i, (nome, vals, atual, med, rl, var) in enumerate(TOP5):
    cor_var = "#b03a2e" if var.startswith("+") else VERDE
    pequenos += f'''<div class="mini"><div class="mh"><span><b>{i+1}º {nome}</b> <span class="sm">· média 12m R$ {br(med*1000,0)} · {rl}</span></span><span><b>{atual}</b> <span class="sm" style="color:{cor_var};font-weight:700">{var} vs média</span></span></div>
{barras([vals], [VERDE], H=108, dec=0, rotulo_dentro=False, destaque=11, media=med, fmt=lambda v: br(v,0))}</div>'''

html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Gráficos Financeiros ago/26</title>
<style>
@page{{size:A4 portrait;margin:11mm 12mm}}
*{{box-sizing:border-box}} body{{margin:0;font-family:"DejaVu Sans",Arial,sans-serif;color:{INK};background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.page{{height:274mm;display:flex;flex-direction:column;page-break-after:always;overflow:hidden}} .page:last-child{{page-break-after:auto}}
header{{display:flex;align-items:center;gap:14px;border-bottom:3px solid {OURO};padding-bottom:7px;margin-bottom:8px}}
header img{{height:46px}} header>div:nth-child(2){{flex:1}} .eyebrow{{font-size:9.5px;letter-spacing:.08em;color:{INK2};font-weight:700}}
h1{{font-size:21px;margin:1px 0}} .sub{{font-size:10.5px;color:{INK2}}} .pg{{font-size:10px;color:{INK2}}}
.kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-bottom:8px}}
.kpi{{border:1px solid #d5dbd5;border-left:4px solid;border-radius:6px;padding:6px 9px}}
.kt{{display:flex;justify-content:space-between;font-size:9px;font-weight:700;color:{INK2}}} .kt b{{color:{INK}}}
.kv{{font-size:19px;font-weight:700;margin:2px 0 1px}} .ks{{font-size:9.5px;color:{INK2}}}
.card{{border:1px solid #d5dbd5;border-radius:6px;padding:7px 10px 4px;margin-bottom:7px}}
h2{{font-size:13px;margin:0 0 2px}} h2 small{{font-weight:400;color:{INK2}}}
.leg{{display:flex;gap:14px;font-size:10.5px;color:{INK2};margin-bottom:2px}} .leg span{{display:flex;align-items:center;gap:5px}}
.leg i{{width:11px;height:11px;border-radius:2px;display:inline-block}} .leg i.dash{{height:0;border-top:2px dashed {INK};border-radius:0;width:18px}}
svg{{width:100%;height:auto;display:block;font-family:"DejaVu Sans",Arial,sans-serif}}
.mini{{border:1px solid #d5dbd5;border-radius:6px;padding:5px 10px 1px;margin-bottom:5px}}
.mh{{display:flex;justify-content:space-between;font-size:12px}} .mh .sm{{font-size:9.5px;color:{INK2}}}
footer{{margin-top:auto;border-top:1px solid {CINZA};padding-top:4px;font-size:9px;color:{INK2};display:flex;justify-content:space-between}}
</style></head><body>
<section class="page">{cabec(1)}
<div class="kpis">{kpis}</div>
<div class="card"><h2>Receita e custo por litro <small>· R$/L</small></h2>{leg((VERDE,"Receita por litro"),(LARANJA,"Custo por litro"))}
{barras([REC_L, CUS_L], [VERDE, LARANJA], H=228)}</div>
<div class="card"><h2>Faturamento e despesa <small>· R$ milhões</small></h2>{leg((VERDE,"Faturamento"),(LARANJA,"Despesa"))}
{barras([FAT, DESP], [VERDE, LARANJA], H=228)}</div>
<div class="card"><h2>Produção de leite <small>· milhões de litros (mês atual em dourado)</small></h2>
{barras([PROD], [VERDE], H=190, rotulo_dentro=False, destaque=11)}</div>
<footer><span>Fazenda ARCAFLA · Relatório Financeiro · Leite</span><span>Fonte: Relatório Financeiro ago/2026 · gerado em 12/11/2026</span></footer>
</section>
<section class="page">{cabec(2)}
<div class="card"><h2>Composição da despesa do mês <small>· % do custo total, ago/26</small></h2>
<div class="leg"><span><i style="background:{LARANJA}"></i>Alimentação</span><span><i style="background:{VERDE}"></i>Demais itens</span><span><i class="dash" style="border-top-style:solid"></i>traço = média de 2026</span></div>
{composicao()}</div>
<h2 style="margin:4px 0 1px">Os 5 maiores custos do mês <small>· histórico de 12 meses, R$ mil</small></h2>
<div class="leg" style="margin-bottom:5px"><span><i style="background:{VERDE}"></i>meses anteriores</span><span><i style="background:{OURO}"></i>ago/26</span><span><i class="dash"></i>média dos 12 meses</span></div>
{pequenos}
<footer><span>Fazenda ARCAFLA · Relatório Financeiro · Leite</span><span>Fonte: Relatório Financeiro ago/2026 · gerado em 12/11/2026</span></footer>
</section>
</body></html>'''
OUT.write_text(html, encoding="utf-8")
print(OUT)
