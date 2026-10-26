"""Folha "Qualidade do leite: dinâmica da CCS no rebanho" no layout do modelo da fazenda
(cartões + colunas 100% empilhadas + tabela + critérios), A4 paisagem.

Uso: python3 scripts/gera_pdf_dinamica_modelo.py  -> relatorios/ARKAFLA_Dinamica_CCS_modelo_dd-mm-aaaa.html
Depois: node scripts/html_para_pdf.js <html> <pdf>
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "processa_controles.py")], check=True, capture_output=True)
C = [c for c in json.load(open("saida/controles.json")) if c["base"]]
last, first = C[-1], C[0]
COR = dict(S="#2E8B57", R="#9AA39D", N="#1B3A6B", C="#C0392B")
NOME = dict(S="Sadias", N="Novas infecções", C="Crônicas", R="Recuperadas")
dm = lambda d: d[8:10] + "/" + d[5:7]  # noqa: E731
br = lambda v, k=1: f"{v:.{k}f}".replace(".", ",")  # noqa: E731
mil = lambda n: f"{n:,}".replace(",", ".")  # noqa: E731
MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
ultimo = f"{last['data'][8:10]}/{last['data'][5:7]}/{last['data'][:4]}"

cards = ""
for k in "SNCR":
    cards += f'''<div class="card"><div class="ct"><i style="background:{COR[k]}"></i>{NOME[k]}</div>
      <div class="cv">{br(last['p'+k])}%<small>{mil(last[k])} vacas</small></div>
      <div class="cc">{dm(first['data'])}: {br(first['p'+k])}%</div></div>'''

# gráfico SVG: colunas 100% empilhadas (de baixo para cima: Sadia, Recuperada, Nova infecção, Crônica)
W, H, ml, mt, mb = 700, 500, 44, 14, 52
n = len(C)
iw, ih = W - ml - 10, H - mt - mb
bw = iw / n
g = f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="Source Sans 3, DejaVu Sans, Arial" >'
for t in range(0, 101, 20):
    y = mt + ih - ih * t / 100
    g += f'<line x1="{ml}" x2="{W-10}" y1="{y:.1f}" y2="{y:.1f}" stroke="#e3e7e3"/><text x="{ml-6}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#5e6b63">{t}%</text>'
for i, c in enumerate(C):
    x = ml + bw * i + bw * 0.16
    w = bw * 0.68
    acc = 0
    for k in "SRNC":
        v = c[k] / c["base"] * 100
        y1 = mt + ih - ih * (acc + v) / 100
        h = ih * v / 100
        g += f'<rect x="{x:.1f}" y="{y1:.1f}" width="{w:.1f}" height="{max(h-1.5,0):.1f}" fill="{COR[k]}"/>'
        if h >= 13:
            tc = "#1d2621" if k == "R" else "#fff"
            g += f'<text x="{x+w/2:.1f}" y="{y1+h/2+4:.1f}" text-anchor="middle" font-size="11.5" font-weight="700" fill="{tc}">{round(v)}</text>'
        acc += v
    g += f'<text x="{x+w/2:.1f}" y="{mt+ih+17:.1f}" text-anchor="middle" font-size="11.5" fill="#1d2621">{dm(c["data"])}</text>'
    g += f'<text x="{x+w/2:.1f}" y="{mt+ih+32:.1f}" text-anchor="middle" font-size="10.5" fill="#5e6b63">n={mil(c["base"])}</text>'
g += "</svg>"

rows = "".join(
    f'<tr class="{"b" if c is last else ""}"><td>{dm(c["data"])}/{c["data"][2:4]}</td><td>{mil(c["base"])}</td><td>{br(c["pS"])}</td><td>{br(c["pN"])}</td><td>{br(c["pC"])}</td><td>{br(c["pR"])}</td></tr>'
    for c in C)
leg = "".join(f'<span><i style="background:{COR[k]}"></i>{ {"S":"Sadia","R":"Recuperada","N":"Nova infecção","C":"Crônica"}[k] }</span>' for k in "SRNC")
html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Dinâmica da CCS no rebanho</title>
<style>
@page{{size:A4 landscape;margin:9mm 11mm}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:"Source Sans 3","DejaVu Sans",Arial,sans-serif;color:#1d2621;background:#fff}}
.sheet{{width:275mm;height:190mm;display:flex;flex-direction:column}}
header{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2px solid #1d2621;padding-bottom:6px}}
h1{{font-family:"DejaVu Serif",Georgia,serif;font-size:25px;margin:0;letter-spacing:-.01em}}
.sub{{font-size:12.5px;color:#3e4a43;margin-top:3px}}
.rt{{text-align:right;font-size:12px;color:#3e4a43;line-height:1.5}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:10px 0 8px}}
.card{{border:1px solid #d5dbd5;border-radius:8px;padding:8px 12px}}
.ct{{font-size:12.5px;display:flex;align-items:center;gap:6px}}
.ct i,.leg i{{width:11px;height:11px;border-radius:2px;display:inline-block}}
.cv{{font-family:"DejaVu Serif",Georgia,serif;font-size:27px;font-weight:700;margin:2px 0}}
.cv small{{font-family:"DejaVu Sans",Arial;font-size:12px;font-weight:400;color:#3e4a43;margin-left:8px}}
.cc{{font-size:11.5px;color:#5e6b63}}
.main{{display:grid;grid-template-columns:1.55fr 1fr;gap:16px;flex:1}}
h2{{font-size:14px;margin:2px 0 4px}}
.leg{{display:flex;gap:14px;font-size:12px;margin-bottom:2px}}
.leg span{{display:flex;align-items:center;gap:5px}}
svg{{width:100%;height:auto}}
table{{border-collapse:collapse;width:100%;font-size:12px;font-variant-numeric:tabular-nums}}
th{{font-size:11.5px;text-align:right;border-bottom:1.5px solid #1d2621;padding:4px 5px}}
td{{text-align:right;padding:3.2px 5px;border-bottom:1px solid #e3e7e3}}
th:first-child,td:first-child{{text-align:left}}
tr.b td{{font-weight:700}}
.crit{{margin-top:12px}} .crit td,.crit th{{text-align:left}}
footer{{border-top:1px solid #9aa39d;margin-top:6px;padding-top:5px;font-size:10.5px;color:#3e4a43;line-height:1.4}}
</style></head><body><div class="sheet">
<header><div><h1>Qualidade do leite: dinâmica da CCS no rebanho</h1>
<div class="sub">Armando P. Carvalho Filho e/ou Flávio A. Carvalho · Castro/PR · Rebanho 70105 (REB 47238 até jun/2026)</div></div>
<div class="rt">Controles de {MES[int(first["data"][5:7])-1]}/{first["data"][:4]} a {MES[int(last["data"][5:7])-1]}/{last["data"][:4]}<br>Último controle: <b>{ultimo}</b></div></header>
<div class="cards">{cards}</div>
<div class="main"><div><h2>Distribuição das vacas por situação (% das vacas na base)</h2><div class="leg">{leg}</div>{g}</div>
<div><table><thead><tr><th>Controle</th><th>Vacas</th><th>Sadia %</th><th>Nova %</th><th>Crôn. %</th><th>Recup. %</th></tr></thead><tbody>{rows}</tbody></table>
<table class="crit"><thead><tr><th>Situação</th><th>Controle anterior</th><th>Controle atual</th></tr></thead><tbody>
<tr><td>Sadia</td><td>&lt; 200 mil</td><td>&lt; 200 mil</td></tr><tr><td>Nova infecção</td><td>&lt; 200 mil</td><td>≥ 200 mil</td></tr>
<tr><td>Crônica</td><td>≥ 200 mil</td><td>≥ 200 mil</td></tr><tr><td>Recuperada</td><td>≥ 200 mil</td><td>&lt; 200 mil</td></tr></tbody></table></div></div>
<footer>CCS em céls/mL; limite de 200 mil. Classificação comparando cada controle com o anterior da mesma vaca, na mesma lactação; entram só as vacas com CCS nos dois controles seguidos.
Ficam fora da base as recém-paridas e as vacas sem registro anterior (em {ultimo}: {last["PB"]} pós-parto com CCS baixa, {last["PE"]} pós-parto com CCS elevada e {last["H"]} sem histórico).
O primeiro intervalo (02/02 → 17/02) tem 15 dias; os demais, 22 a 37 dias. Fonte: APCBRH – Relatório 2.2, {len(C)+1} controles de 02/02 a {ultimo}.</footer>
</div></body></html>'''
os.makedirs("relatorios", exist_ok=True)
out = f"relatorios/ARKAFLA_Dinamica_CCS_modelo_{ultimo.replace('/','-')}.html"
open(out, "w", encoding="utf-8").write(html)
print(out)
