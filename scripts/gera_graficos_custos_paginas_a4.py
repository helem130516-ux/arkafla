# Um gráfico por página A4 (paisagem), Relatório Financeiro ago/2026:
# receita, custo e margem por litro (R$/L); Alimentação, Medicamentos, Mão de obra, Conservação e reparos em centavos por litro.
# Uso: python3 scripts/gera_graficos_custos_paginas_a4.py && node scripts/html_para_pdf.js <html> <pdf>
import base64, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "relatorios" / "ARCAFLA_Graficos_por_pagina_2026-08_A4.html"

MESES = ["set/25", "out/25", "nov/25", "dez/25", "jan/26", "fev/26", "mar/26", "abr/26", "mai/26", "jun/26", "jul/26", "ago/26"]
VERDE, LARANJA, AZUL, OURO = "#1f6b3a", "#d9822b", "#2a6fb0", "#e0a21a"
INK, INK2, GRADE, VERM = "#1d2621", "#5e6b63", "#e3e7e3", "#b03a2e"
br = lambda v, d=0: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
COLS = ["jul/26", "ago/26", "Média 2026", "Média 2025", "Média últ. 3m"]

REC_L = [3.01, 2.88, 2.72, 2.64, 2.40, 2.44, 2.63, 2.77, 2.92, 2.87, 2.98, 3.35]
CUS_L = [2.04, 1.87, 2.15, 2.19, 2.04, 2.14, 2.27, 2.28, 2.08, 2.24, 2.22, 2.03]
MAR_L = [round(r - c, 2) for r, c in zip(REC_L, CUS_L)]  # margem = receita − custo por litro


# Produção mensal em milhões de litros (jul e ago exatos; demais meses arredondados no relatório).
PROD = [1.89, 2.00, 1.92, 1.95, 1.95, 1.72, 1.88, 1.85, 1.99, 2.06, 2.162642, 2.116808]
cent = lambda txt: br(float(txt.replace("R$ ", "").replace(",", ".")) * 100)  # "R$ 1,29" -> "129"


def custo(nome, vals, tabela):
    """vals em R$ mil por mês -> centavos por litro (custo do mês ÷ litros do mês)."""
    c = [v / (p * 10) for v, p in zip(vals, PROD)]
    media = sum(vals) / (sum(PROD) * 10)  # média ponderada pelos litros dos 12 meses
    var = (c[-1] / media - 1) * 100
    tab = []
    for rot, cols in tabela:
        if "R$/L" in rot or rot == "R$ por litro":
            tab.append((rot.replace("(R$/L)", "(centavos/L)").replace("R$ por litro", "Centavos por litro"), [cent(x) for x in cols]))
        elif rot.startswith("%"):
            tab.append((rot, cols))
    return dict(nome=nome, series=[("ago", [round(x, 1) for x in c], VERDE)], media=media, dec=1,
                passo=20 if max(c) > 60 else 5,
                sub="Custo por litro produzido nos últimos 12 meses (set/25–ago/26), em centavos por litro",
                resumo=[("ago/26 · centavos por litro", f"{br(c[-1],1)} ¢/L", None),
                        ("Média dos 12 meses", f"{br(media,1)} ¢/L", None),
                        ("ago/26 vs média", f"{'+' if var >= 0 else '−'}{br(abs(var),0)}%", VERM if var >= 0 else VERDE),
                        ("jul/26 · centavos por litro", f"{br(c[-2],1)} ¢/L", None)],
                legenda=[(VERDE, "meses anteriores"), (OURO, "ago/26"), ("dash", f"média dos 12 meses: {br(media,1)} ¢/L")],
                tabela=tab)


PAGINAS = [
    dict(nome="Receita, custo e margem por litro", dec=2, passo=0.5, media=None,
         series=[("Receita por litro", REC_L, VERDE), ("Custo por litro", CUS_L, LARANJA), ("Margem por litro", MAR_L, AZUL)],
         sub="R$ por litro, últimos 12 meses (set/25–ago/26) · margem = receita − custo por litro",
         resumo=[("Receita por litro · ago/26", "R$ 3,35", VERDE), ("Custo por litro · ago/26", "R$ 2,03", LARANJA),
                 ("Margem por litro · ago/26", "R$ 1,32", AZUL), ("Preço do litro de leite · ago/26", "R$ 3,04", None)],
         legenda=[(VERDE, "Receita por litro"), (LARANJA, "Custo por litro"), (AZUL, "Margem por litro")],
         tabela=[("Preço do litro de leite", ["R$ 2,89", "R$ 3,04", "R$ 2,67", "R$ 2,79", "R$ 2,90"]),
                 ("Receita bruta por litro", ["R$ 2,98", "R$ 3,35", "R$ 2,81", "R$ 2,96", "R$ 3,07"]),
                 ("Custo operacional por litro", ["R$ 2,22", "R$ 2,03", "R$ 2,16", "R$ 2,00", "R$ 2,17"]),
                 ("Margem bruta por litro", ["R$ 0,76", "R$ 1,32", "R$ 0,65", "R$ 0,96", "R$ 0,90"])]),
    custo("Alimentação total", [2280, 2314, 2514, 2651, 2403, 2271, 2650, 2633, 2631, 2910, 3137, 2734],
          [("Valor do mês", ["R$ 3.136.888", "R$ 2.733.868", "R$ 2.671.108", "R$ 2.263.152", "—"]),
           ("   Concentrado", ["R$ 2.159.072", "R$ 1.998.144", "R$ 1.906.673", "R$ 1.702.095", "—"]),
           ("   Volumoso", ["R$ 977.817", "R$ 735.724", "R$ 764.436", "R$ 561.057", "—"]),
           ("R$ por litro", ["R$ 1,45", "R$ 1,29", "R$ 1,36", "R$ 1,23", "R$ 1,39"]),
           ("   Concentrados (R$/L)", ["R$ 1,00", "R$ 0,94", "R$ 0,97", "R$ 0,92", "R$ 0,99"]),
           ("   Volumosos (R$/L)", ["R$ 0,45", "R$ 0,35", "R$ 0,39", "R$ 0,30", "R$ 0,40"]),
           ("% do custo total", ["65,3%", "63,6%", "62,8%", "61,5%", "64,0%"]),
           ("% da receita bruta", ["48,6%", "38,5%", "48,3%", "41,5%", "45,2%"])]),
    custo("Medicamentos", [399, 263, 382, 331, 357, 347, 370, 261, 337, 497, 324, 350],
          [("Valor do mês", ["R$ 324.303", "R$ 349.668", "R$ 355.227", "R$ 328.644", "—"]),
           ("R$ por litro", ["R$ 0,15", "R$ 0,17", "R$ 0,18", "R$ 0,18", "R$ 0,18"]),
           ("% do custo total", ["6,7%", "8,1%", "8,4%", "8,9%", "8,5%"]),
           ("% da receita bruta", ["5,0%", "4,9%", "6,4%", "6,0%", "6,0%"])]),
    custo("Mão de obra", [287, 257, 248, 469, 318, 343, 324, 358, 279, 337, 317, 287],
          [("Valor do mês", ["R$ 317.479", "R$ 287.410", "R$ 320.332", "R$ 282.230", "—"]),
           ("R$ por litro", ["R$ 0,15", "R$ 0,14", "R$ 0,16", "R$ 0,15", "R$ 0,15"]),
           ("% do custo total", ["6,6%", "6,7%", "7,5%", "7,7%", "6,9%"]),
           ("% da receita bruta", ["4,9%", "4,0%", "5,8%", "5,2%", "4,8%"])]),
    custo("Conservação e reparos", [275, 235, 321, 161, 288, 181, 291, 352, 345, 334, 355, 280],
          [("Valor do mês", ["R$ 354.893", "R$ 280.255", "R$ 303.301", "R$ 227.145", "—"]),
           ("R$ por litro", ["R$ 0,16", "R$ 0,13", "R$ 0,15", "R$ 0,12", "R$ 0,15"]),
           ("% do custo total", ["7,4%", "6,5%", "7,1%", "6,2%", "7,1%"]),
           ("% da receita bruta", ["5,5%", "3,9%", "5,5%", "4,2%", "5,0%"])]),
]


def grafico(p, W=1000, H=None):
    H = H or 360 + (8 - len(p["tabela"])) * 24
    series, dec, passo = p["series"], p["dec"], p["passo"]
    ml, mr, mt, mb = 52, 10, 26, 30
    iw, ih = W - ml - mr, H - mt - mb
    topo = max(max(s[1]) for s in series) * 1.1
    vmax = (int(topo / passo) + 1) * passo
    base = mt + ih
    g = f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
    t = 0.0
    while t <= vmax + 1e-9:
        y = base - ih * t / vmax
        g += f'<line x1="{ml}" x2="{W-mr}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRADE}"/>'
        g += f'<text x="{ml-8}" y="{y+4:.1f}" text-anchor="end" font-size="12" fill="{INK2}">{br(t, 0 if float(passo).is_integer() else 1)}</text>'
        t += passo
    k, n = len(series), len(MESES)
    slot = iw / n
    gap = 2
    bw = slot * 0.62 if k == 1 else (slot * 0.86 - gap * (k - 1)) / k
    for i in range(n):
        x0 = ml + i * slot + (slot - (bw * k + gap * (k - 1))) / 2
        ult = i == n - 1
        for j, (_, vals, cor) in enumerate(series):
            v = vals[i]
            x, y = x0 + j * (bw + gap), base - ih * v / vmax
            r = min(4, bw / 4)
            fill = OURO if (k == 1 and ult) else cor
            g += f'<path d="M{x:.1f},{base} V{y+r:.1f} Q{x:.1f},{y:.1f} {x+r:.1f},{y:.1f} H{x+bw-r:.1f} Q{x+bw:.1f},{y:.1f} {x+bw:.1f},{y+r:.1f} V{base} Z" fill="{fill}"/>'
            if k == 1:
                g += f'<text x="{x+bw/2:.1f}" y="{y-7:.1f}" text-anchor="middle" font-size="14" font-weight="{700 if ult else 400}" fill="{INK}" stroke="#fff" stroke-width="4" paint-order="stroke">{br(v, dec)}</text>'
            else:  # valor na vertical, logo acima da barra
                cx, cy = x + bw / 2, y - 4
                g += f'<text x="{cx:.1f}" y="{cy:.1f}" transform="rotate(-90 {cx:.1f} {cy:.1f})" dy="4" font-size="11.5" font-weight="{700 if ult else 400}" fill="{INK}">{br(v, dec)}</text>'
        g += f'<text x="{ml+i*slot+slot/2:.1f}" y="{base+19}" text-anchor="middle" font-size="13" font-weight="{700 if ult else 400}" fill="{INK if ult else INK2}">{MESES[i]}</text>'
    if p["media"] is not None:
        y = base - ih * p["media"] / vmax
        g += f'<line x1="{ml}" x2="{W-mr}" y1="{y:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="7 5"/>'
    g += f'<line x1="{ml}" x2="{W-mr}" y1="{base}" y2="{base}" stroke="{INK2}"/>'
    return g + "</svg>"


logo = ROOT / "assets" / "logo_arcafla_small.png"
logo_tag = f'<img src="data:image/png;base64,{base64.b64encode(logo.read_bytes()).decode()}" alt="ARCAFLA">' if logo.exists() else ""

secoes = ""
for n, p in enumerate(PAGINAS, 1):
    linhas = "".join(f'<tr class="{"sub" if r.startswith("   ") else ""}"><td>{r.strip()}</td>' + "".join(f"<td>{c}</td>" for c in cs) + "</tr>" for r, cs in p["tabela"])
    resumo = "".join(f'<div style="border-left-color:{c or INK2}"><span>{t}</span><b style="color:{c if c in (VERM, VERDE) and "vs" in t else INK}">{v}</b></div>' for t, v, c in p["resumo"])
    legenda = "".join(f'<span><i class="dash"></i>{t}</span>' if c == "dash" else f'<span><i style="background:{c}"></i>{t}</span>' for c, t in p["legenda"])
    secoes += f'''<section class="page">
<header>{logo_tag}<div><div class="eyebrow">RELATÓRIO FINANCEIRO · LEITE · AGOSTO DE 2026</div><h1>{p["nome"]}</h1>
<div class="sub">{p["sub"]} · dados do Agriwin, atualizados em 11/11/2026</div></div>
<div class="pg">pág. {n}/{len(PAGINAS)}</div></header>
<div class="resumo">{resumo}</div>
<div class="leg">{legenda}</div>
{grafico(p)}
<table><tr><th></th>{"".join(f"<th>{c}</th>" for c in COLS)}</tr>{linhas}</table>
<footer><span>Fazenda ARCAFLA · Relatório Financeiro · Leite</span><span>Fonte: Relatório Financeiro ago/2026 · gerado em 12/11/2026</span></footer>
</section>'''

html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Gráficos por página ago/26</title>
<style>
@page{{size:A4 landscape;margin:10mm 12mm}}
*{{box-sizing:border-box}} body{{margin:0;font-family:"DejaVu Sans",Arial,sans-serif;color:{INK};background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.page{{height:189mm;display:flex;flex-direction:column;page-break-after:always;overflow:hidden}} .page:last-child{{page-break-after:auto}}
header{{display:flex;align-items:center;gap:14px;border-bottom:3px solid {OURO};padding-bottom:6px;margin-bottom:8px}}
header img{{height:46px}} header>div:nth-child(2){{flex:1}} .eyebrow{{font-size:9.5px;letter-spacing:.08em;color:{INK2};font-weight:700}}
h1{{font-size:24px;margin:1px 0}} .sub{{font-size:10.5px;color:{INK2}}} .pg{{font-size:10px;color:{INK2}}}
.resumo{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:6px}}
.resumo div{{border:1px solid #d5dbd5;border-left:4px solid;border-radius:6px;padding:5px 10px}}
.resumo span{{display:block;font-size:10px;color:{INK2}}} .resumo b{{font-size:18px}}
.leg{{display:flex;gap:16px;font-size:11px;color:{INK2}}} .leg span{{display:flex;align-items:center;gap:5px}}
.leg i{{width:11px;height:11px;border-radius:2px;display:inline-block}} .leg i.dash{{height:0;border-top:2px dashed {INK};border-radius:0;width:18px}}
svg{{width:100%;height:auto;display:block;font-family:"DejaVu Sans",Arial,sans-serif}}
table{{border-collapse:collapse;width:100%;font-size:11px;font-variant-numeric:tabular-nums;margin-top:4px}}
th{{font-size:10.5px;text-align:right;border-bottom:1.5px solid {INK};padding:3px 6px}} td{{text-align:right;padding:2.5px 6px;border-bottom:1px solid {GRADE}}}
th:first-child,td:first-child{{text-align:left}} td:nth-child(3){{font-weight:700}} tr.sub td:first-child{{padding-left:18px;color:{INK2}}}
footer{{margin-top:auto;border-top:1px solid #9aa39d;padding-top:4px;font-size:9px;color:{INK2};display:flex;justify-content:space-between}}
</style></head><body>{secoes}</body></html>'''
OUT.write_text(html, encoding="utf-8")
print(OUT)
