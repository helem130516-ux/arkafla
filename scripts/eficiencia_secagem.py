"""Eficiência de secagem: situação das vacas da secagem ao 1º controle pós-parto.

Regras (como no modelo da fazenda, com o limite do projeto: elevada = CCS ≥ 200):
- À secagem: média da CCS dos controles nos 60 dias antes da data de secagem (inclusive).
- Pós-parto: 1º controle depois do parto que veio após a secagem.
- Só secagens com período seco de 20 a 120 dias (parto − secagem).
- Sadia: baixa → baixa; Curada: elevada → baixa; Nova infecção: baixa → elevada; Crônica: elevada → elevada.
- Taxa de cura = curadas ÷ infectadas à secagem; infectadas pós-parto = novas infecções ÷ secas sadias.
- Novilhas (1ª lactação): idade ao parto ≤ 30 meses (campo IDADE do Relatório 2.2, anos/meses ao parto),
  % com CCS ≥ 200 no 1º controle após o parto, agrupadas pelo mês do parto.
Saída: saida/eficiencia_secagem.json
"""
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from processa_controles import le_relatorio  # noqa: E402

LIM = 200
ctrls = [le_relatorio(p) for p in sorted(glob.glob("dados/apcbrh/R22_*.xlsx"))]
ctrls.sort(key=lambda c: c["data"])
por_vaca = defaultdict(list)
for c in ctrls:
    for r in c["rows"]:
        por_vaca[int(r["vaca"])].append(dict(r, data=c["data"]))
d_ini, d_fim = ctrls[0]["data"], ctrls[-1]["data"]
sec = json.load(open("dados/registro_fazenda.json"))["secagem"]

vacas, excl = [], defaultdict(int)
for s in sec:
    ds, dp = date.fromisoformat(s["data"]), date.fromisoformat(s["parto"]) if s["parto"] else None
    if not dp or dp <= ds:
        excl["sem parto depois da secagem"] += 1; continue
    seco = (dp - ds).days
    if not 20 <= seco <= 120:
        excl["período seco fora de 20–120 dias"] += 1; continue
    if ds - timedelta(days=60) < d_ini - timedelta(days=0) and ds < d_ini:
        excl["secagem antes dos controles disponíveis"] += 1; continue
    h = por_vaca.get(s["vaca"], [])
    antes = [r["ccs"] for r in h if ds - timedelta(days=60) <= r["data"] <= ds]
    depois = [r for r in h if r["data"] > dp]
    if not antes:
        excl["sem controle nos 60 dias antes da secagem"] += 1; continue
    if not depois:
        excl["sem controle depois do parto (ainda)"] += 1; continue
    a, p = sum(antes) / len(antes), depois[0]["ccs"]
    cls = {(0, 0): "S", (1, 0): "R", (0, 1): "N", (1, 1): "C"}[(int(a >= LIM), int(p >= LIM))]
    vacas.append(dict(vaca=s["vaca"], secagem=s["data"], parto=s["parto"], seco=seco, ccs_antes=round(a), n_antes=len(antes),
                      ccs_pos=p, data_pos=depois[0]["data"].isoformat(), del_pos=depois[0]["del_"], cls=cls, produto=s["produto"]))

meses = sorted({v["secagem"][:7] for v in vacas})
res = []
for m in meses:
    x = [v for v in vacas if v["secagem"][:7] == m]
    k = {c: sum(1 for v in x if v["cls"] == c) for c in "SRNC"}
    inf, sad = k["R"] + k["C"], k["S"] + k["N"]
    res.append(dict(mes=m, n=len(x), **k, infect=inf, pct_infect=100 * inf / len(x),
                    cura=100 * k["R"] / inf if inf else None, infect_pos=100 * k["N"] / sad if sad else None))

# novilhas: 1º controle depois do parto, idade ao parto ≤ 30 meses
nov = []
for v, h in por_vaca.items():
    seen = set()
    for i, r in enumerate(h):
        if not r["parto"] or not r["idade"] or "/" not in r["idade"] or r["parto"] in seen:
            continue
        an, me = map(int, r["idade"].split("/"))
        if an * 12 + me > 30 or r["parto"] < d_ini - timedelta(days=60):
            continue
        prev = [q for q in h[:i] if q["parto"] == r["parto"]]
        if prev:
            continue  # não é o 1º controle desta lactação
        seen.add(r["parto"])
        if r["parto"] < d_ini:  # parto antes do 1º controle disponível: só vale se este é o 1º controle após o parto
            pass
        nov.append(dict(vaca=v, parto=r["parto"].isoformat(), data=r["data"].isoformat(), del_=r["del_"], ccs=r["ccs"], idade=r["idade"]))
nov = [n for n in nov if n["parto"] >= d_ini.isoformat()[:8] + "01"]
mn = sorted({n["parto"][:7] for n in nov})
novm = {m: dict(n=len([n for n in nov if n["parto"][:7] == m]), inf=len([n for n in nov if n["parto"][:7] == m and n["ccs"] >= LIM])) for m in mn}

json.dump(dict(regras=__doc__, ultimo_controle=d_fim.isoformat(), vacas=vacas, meses=res, excluidas=dict(excl),
               novilhas=nov, novilhas_mes=novm), open("saida/eficiencia_secagem.json", "w"), ensure_ascii=False, indent=1)
for r in res:
    print(r["mes"], r["n"], {k: r[k] for k in "SRNC"}, f"infect {r['pct_infect']:.0f}% cura {r['cura'] or 0:.0f}% infect_pos {r['infect_pos'] or 0:.0f}%")
print("excluídas:", dict(excl))
T = {c: sum(r[c] for r in res) for c in "SRNC"}; N = sum(r["n"] for r in res)
print("total", N, T, "infect", T["R"] + T["C"], "cura", T["R"], "NI", T["N"])
print("novilhas por mês do parto:", {m: (v["n"], v["inf"], round(100 * v["inf"] / v["n"])) for m, v in novm.items()})
