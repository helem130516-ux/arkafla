"""Folha "Eficiência de secagem" no layout do modelo da fazenda (A4 paisagem).
Uso: python3 scripts/gera_pdf_secagem_modelo.py -> relatorios/ARKAFLA_Eficiencia_Secagem_dd-mm-aaaa.html
Depois: node scripts/html_para_pdf.js <html> <pdf>
"""
import json, os, subprocess, sys
from datetime import date
D = os.path.dirname(__file__)
subprocess.run([sys.executable, os.path.join(D, "eficiencia_secagem.py")], check=True, capture_output=True)
E = json.load(open("saida/eficiencia_secagem.json"))
MIN_N = 30
OPA = 'opacity="0.55"'
COR = dict(S="#2E8B57", R="#9AA39D", N="#1B3A6B", C="#C0392B")
MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
ml_ = lambda m: MES[int(m[5:7]) - 1] + "/" + m[2:4]  # noqa: E731
br = lambda v, k=0: ("–" if v is None else f"{v:.{k}f}".replace(".", ","))  # noqa: E731
R = E["meses"]
nov = E["novilhas_mes"]
ok = [r for r in R if r["n"] >= MIN_N]
parc = [r for r in R if r["n"] < MIN_N]
avg = lambda k, rs=ok: sum(r[k] for r in rs if r[k] is not None) / len([r for r in rs if r[k] is not None])  # noqa: E731
rng = lambda k, rs=ok: (min(r[k] for r in rs if r[k] is not None), max(r[k] for r in rs if r[k] is not None))  # noqa: E731
nm = [r["mes"] for r in ok]
nv_n = sum(nov[m]["n"] for m in nm if m in nov); nv_i = sum(nov[m]["inf"] for m in nm if m in nov)
nv_p = [100 * nov[m]["inf"] / nov[m]["n"] for m in nm if m in nov and nov[m]["n"]]
T = {k: sum(r[k] for r in ok) for k in "SRNC"}
ult = date.fromisoformat(E["ultimo_controle"]).strftime("%d/%m/%Y")

def card(cor, t, v, sub, foot):
    return f'<div class="card"><div class="ct"><i style="background:{cor}"></i>{t}</div><div class="cv">{v}<small>{sub}</small></div><div class="cc">{foot}</div></div>'
cards = (card("#1d2621", "Infectadas à secagem", br(avg('pct_infect')) + "%", f"{T['R']+T['C']} vacas", "média mensal · variação %s–%s%%" % tuple(br(x) for x in rng('pct_infect'))) +
         card(COR["R"], "Taxa de cura", br(avg('cura')) + "%", f"{T['R']} vacas", "média mensal · variação %s–%s%%" % tuple(br(x) for x in rng('cura'))) +
         card(COR["N"], "Infectadas pós-parto", br(avg('infect_pos')) + "%", f"{T['N']} vacas", "das secas sadias · variação %s–%s%%" % tuple(br(x) for x in rng('infect_pos'))) +
         card(COR["C"], "Novilhas infectadas", br(100 * nv_i / nv_n) + "%", f"{nv_i} de {nv_n} novilhas", "no 1º controle · variação %s–%s%%" % (br(min(nv_p)), br(max(nv_p)))))

W, H, ml, mt, mb = 700, 500, 44, 14, 52
n = len(R); iw, ih = W - ml - 10, H - mt - mb; bw = iw / n
g = f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, Arial">'
for t in range(0, 101, 20):
    y = mt + ih - ih * t / 100
    g += f'<line x1="{ml}" x2="{W-10}" y1="{y:.1f}" y2="{y:.1f}" stroke="#e3e7e3"/><text x="{ml-6}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#5e6b63">{t}%</text>'
for i, r in enumerate(R):
    x = ml + bw * i + bw * .18; w = bw * .64; acc = 0
    for k in "SRNC":
        v = 100 * r[k] / r["n"]; y1 = mt + ih - ih * (acc + v) / 100; h = ih * v / 100
        g += f'<rect x="{x:.1f}" y="{y1:.1f}" width="{w:.1f}" height="{max(h-1.5,0):.1f}" fill="{COR[k]}" {OPA if r in parc else ""}/>'
        if h >= 13:
            g += f'<text x="{x+w/2:.1f}" y="{y1+h/2+4:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="{"#1d2621" if k=="R" else "#fff"}">{round(v)}</text>'
        acc += v
    g += f'<text x="{x+w/2:.1f}" y="{mt+ih+17:.1f}" text-anchor="middle" font-size="12" fill="#1d2621">{ml_(r["mes"])}{"*" if r in parc else ""}</text>'
    g += f'<text x="{x+w/2:.1f}" y="{mt+ih+32:.1f}" text-anchor="middle" font-size="10.5" fill="#5e6b63">n={r["n"]}</text>'
g += "</svg>"

def nvp(m):
    return br(100 * nov[m]["inf"] / nov[m]["n"]) + "%" if m in nov and nov[m]["n"] else "–"
rows = "".join(f'<tr><td>{ml_(r["mes"])}{"*" if r in parc else ""}</td><td>{r["n"]}</td><td>{br(r["pct_infect"])}%</td><td>{br(r["cura"])}%</td><td>{br(r["infect_pos"])}%</td><td>{nvp(r["mes"])}</td></tr>' for r in R)
rows += f'<tr class="b"><td>Média{"¹" if parc else ""}</td><td>{br(sum(r["n"] for r in ok)/len(ok),1)}</td><td>{br(avg("pct_infect"))}%</td><td>{br(avg("cura"))}%</td><td>{br(avg("infect_pos"))}%</td><td>{br(sum(nv_p)/len(nv_p))}%</td></tr>'
extra = {m: v for m, v in nov.items() if m > R[-1]["mes"]}
ex_txt = (" Novilhas que pariram depois: " + ", ".join(f"{ml_(m)} {br(100*v['inf']/v['n'])}% (n={v['n']})" for m, v in extra.items()) + ".") if extra else ""
leg = "".join(f'<span><i style="background:{COR[k]}"></i>{ {"S":"Sadia","R":"Curada","N":"Nova infecção","C":"Crônica"}[k] }</span>' for k in "SRNC")
X = E["excluidas"]
html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Eficiência de secagem</title><style>
@page{{size:A4 landscape;margin:9mm 11mm}} *{{box-sizing:border-box}}
body{{margin:0;font-family:"DejaVu Sans",Arial,sans-serif;color:#1d2621;background:#fff}}
.sheet{{width:275mm;height:190mm;display:flex;flex-direction:column}}
header{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2px solid #1d2621;padding-bottom:6px}}
h1{{font-family:"DejaVu Serif",Georgia,serif;font-size:25px;margin:0}} .sub{{font-size:12.5px;color:#3e4a43;margin-top:3px}}
.rt{{text-align:right;font-size:12px;color:#3e4a43;line-height:1.5}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:10px 0 8px}} .card{{border:1px solid #d5dbd5;border-radius:8px;padding:8px 12px}}
.ct{{font-size:12.5px;display:flex;align-items:center;gap:6px}} .ct i,.leg i{{width:11px;height:11px;border-radius:2px;display:inline-block}}
.cv{{font-family:"DejaVu Serif",Georgia,serif;font-size:27px;font-weight:700;margin:2px 0}} .cv small{{font-family:"DejaVu Sans";font-size:12px;font-weight:400;color:#3e4a43;margin-left:8px}}
.cc{{font-size:11.5px;color:#5e6b63}} .main{{display:grid;grid-template-columns:1.45fr 1fr;gap:16px;flex:1}}
h2{{font-size:14px;margin:2px 0 4px}} .leg{{display:flex;gap:14px;font-size:12px;margin-bottom:2px}} .leg span{{display:flex;align-items:center;gap:5px}}
svg{{width:100%;height:auto}} table{{border-collapse:collapse;width:100%;font-size:12px;font-variant-numeric:tabular-nums}}
th{{font-size:11px;text-align:right;border-bottom:1.5px solid #1d2621;padding:4px 5px;vertical-align:bottom}} td{{text-align:right;padding:4px 5px;border-bottom:1px solid #e3e7e3}}
th:first-child,td:first-child{{text-align:left}} tr.b td{{font-weight:700}} .crit{{margin-top:14px}} .crit td,.crit th{{text-align:left}}
.crit i{{width:10px;height:10px;border-radius:2px;display:inline-block;margin-right:6px}}
footer{{border-top:1px solid #9aa39d;margin-top:6px;padding-top:5px;font-size:10.2px;color:#3e4a43;line-height:1.4}}
</style></head><body><div class="sheet">
<header><div><h1>Eficiência de secagem</h1><div class="sub">Armando P. Carvalho Filho e/ou Flávio A. Carvalho · Castro/PR · Rebanho 70105</div></div>
<div class="rt">Vacas agrupadas pelo mês da secagem · {ml_(R[0]["mes"])} a {ml_(R[-1]["mes"])}<br>Último controle: <b>{ult}</b></div></header>
<div class="cards">{cards}</div>
<div class="main"><div><h2>Situação das vacas secas: da secagem ao 1º controle pós-parto (%)</h2><div class="leg">{leg}</div>{g}</div>
<div><table><thead><tr><th>Secagem</th><th>Vacas</th><th>Infect. %</th><th>Cura %</th><th>Infect. pós-parto %</th><th>Novilhas %</th></tr></thead><tbody>{rows}</tbody></table>
<table class="crit"><thead><tr><th>Situação</th><th>À secagem</th><th>1º controle pós-parto</th></tr></thead><tbody>
<tr><td><i style="background:{COR['S']}"></i>Sadia</td><td>&lt; 200 mil</td><td>&lt; 200 mil</td></tr>
<tr><td><i style="background:{COR['R']}"></i>Curada</td><td>≥ 200 mil</td><td>&lt; 200 mil</td></tr>
<tr><td><i style="background:{COR['N']}"></i>Nova infecção</td><td>&lt; 200 mil</td><td>≥ 200 mil</td></tr>
<tr><td><i style="background:{COR['C']}"></i>Crônica</td><td>≥ 200 mil</td><td>≥ 200 mil</td></tr></tbody></table></div></div>
<footer>CCS em céls/mL; limite de 200 mil. À secagem: média da CCS nos controles dos 60 dias antes da data de secagem. Pós-parto: 1º controle após o parto. Só secagens com período seco de 20 a 120 dias ({sum(r["n"] for r in R)} vacas).
Taxa de cura = curadas ÷ infectadas à secagem; infectadas pós-parto = novas infecções ÷ secas sadias. Novilhas = 1ª lactação (idade ao parto até 30 meses), % com CCS ≥ 200 no 1º controle, agrupadas pelo mês do parto.{ex_txt}
*{", ".join(ml_(r["mes"]) for r in parc)} parcial (planilha de secagem até 15/07; só vacas que já pariram e tiveram controle até {ult}); ¹ médias e variações sem os meses parciais.
Fora da análise: {X.get("secagem antes dos controles disponíveis",0)} secagens antes de fev/26 (sem controle nos 60 dias antes), {X.get("período seco fora de 20–120 dias",0)} com período seco fora de 20–120 dias, {X.get("sem controle nos 60 dias antes da secagem",0)} sem controle antes e {X.get("sem controle depois do parto (ainda)",0)} ainda sem controle pós-parto.
Fontes: aba SECAGEM do registro da fazenda (MASTITE_2026.xlsx) e APCBRH – Relatório 2.2 (controles de 02/02 a {ult}).</footer>
</div></body></html>'''
os.makedirs("relatorios", exist_ok=True)
out = f"relatorios/ARKAFLA_Eficiencia_Secagem_{ult.replace('/','-')}.html"
open(out, "w", encoding="utf-8").write(html)
print(out)
