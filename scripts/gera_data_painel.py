"""Gera o objeto DATA do painel ({c, r, m}) a partir dos relatórios APCBRH e do registro de mastite.

Uso: python3 scripts/gera_data_painel.py  -> saida/data_painel.json
Regras (iguais às do painel publicado):
- r: [ci, vaca, lote, del, prod, ccs, cls, seq, rec, prev_ccs|-1, queda, ccs_tq, parto dd/mm/aaaa]
- m: [vaca, ini, produto, quartos, fim, carencia, ccs_antes|-1, ccs_depois|-1, retrat, lote_antes]
  CCS antes = último controle com data <= início; CCS depois = 1º controle com data > RETORNO;
  retratamento = mesma vaca com início anterior em até 21 dias (inclui linha repetida no mesmo dia);
  lote do caso = lote no controle usado como "antes".
"""
import glob
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from processa_controles import classifica, le_relatorio  # noqa: E402

PROD = {"mastite clinica": "(sem produto)", "synulox": "Sinulox"}


def num(x):
    return int(x) if float(x).is_integer() else round(float(x), 1)


def gera():
    ctrls = [le_relatorio(p) for p in sorted(glob.glob("dados/apcbrh/R22_*.xlsx"))]
    recs = classifica(ctrls)
    c = [dict(date=x["data"].isoformat(), reb=x["reb"], apcbrh=round(x["ccs_tq"], 1), n=x["n"], ci=x["ci"]) for x in ctrls]
    recs.sort(key=lambda x: (x["vaca"], x["ci"]))
    r = [[x["ci"], int(x["vaca"]), int(x["lote"]), x["del_"], round(x["prod"], 1), num(x["ccs"]), x["cls"], x["seq_el"],
          x["rec"], -1 if x["prev_ccs"] is None else num(x["prev_ccs"]), x["queda"], round(x["ccs_tq"], 3),
          x["parto"].strftime("%d/%m/%Y") if x["parto"] else ""] for x in recs]
    by = {}
    for x in recs:
        by.setdefault(int(x["vaca"]), []).append(x)
    trat = json.load(open("dados/registro_fazenda.json"))["tratamentos_2026"]
    ts = sorted(range(len(trat)), key=lambda i: (trat[i]["vaca"], trat[i]["ini"], i))
    m, last = [], {}
    for i in ts:
        t = trat[i]
        ini = date.fromisoformat(t["ini"])
        h = by.get(t["vaca"], [])
        bef = [x for x in h if x["data"] <= ini]
        aft = [x for x in h if t["retorno"] and x["data"] > date.fromisoformat(t["retorno"])]
        l = last.get(t["vaca"])
        p = t["produto"].strip()
        p = PROD.get(p.lower(), p[:1].upper() + p[1:].lower())
        m.append([t["vaca"], t["ini"], p, t["quartos"], t["fim"], t["carencia"],
                  num(bef[-1]["ccs"]) if bef else -1, num(aft[0]["ccs"]) if aft else -1,
                  int(l is not None and (ini - l).days <= 21), bef[-1]["lote"] if bef else ""])
        last[t["vaca"]] = ini
    return dict(c=c, r=r, m=m)


if __name__ == "__main__":
    D = gera()
    os.makedirs("saida", exist_ok=True)
    json.dump(D, open("saida/data_painel.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print("controles", len(D["c"]), "registros", len(D["r"]), "tratamentos", len(D["m"]))
