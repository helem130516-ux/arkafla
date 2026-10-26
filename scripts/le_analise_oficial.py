"""Lê o "Resultado Análise Leite" (Sistema Controle de Leite / Pool) em dados/analise_oficial/*.pdf
e grava dados/analise_oficial.json: uma linha por tanque e coleta, com todas as análises.

Cada linha do PDF tem: resultado, tipo de análise, data e nº do tanque (lidos pela posição na página).
As análises PARLPR (CCS, CPP, gordura...) vêm com a data da análise; os ácidos graxos vêm com a
data da coleta. A k-ésima análise de um tanque corresponde à k-ésima coleta desse tanque.
"""
import glob
import json
import re
from collections import defaultdict

import pymupdf

KEY = {"C.P.P. - PARLPR": "CPP", "CCS - PARLPR": "CCS", "GORDURA - PARLPR": "GOR", "PROTEINA  - PARLPR": "PROT",
       "PROTEINA - PARLPR": "PROT", "LACTOSE": "LACT", "SOLIDOS TOTAIS - PARLPR": "SOL", "UREIA - PARLPR": "UREIA"}


def le(path):
    doc = pymupdf.open(path)
    linhas = []
    mes = emit = None
    for page in doc:
        t = page.get_text()
        mes = mes or re.search(r"Mês:\s*\n\s*(\d{2}/\d{4})", t).group(1)
        emit = emit or re.search(r"(\d{2}/\d{2}/\d{4})\s+as", t).group(1)
        W = page.get_text("words")
        # agrupa por linha (y), só a área da tabela
        rows = defaultdict(list)
        for w in W:
            rows[round(w[1] / 2)].append(w)
        for _, ws in sorted(rows.items()):
            ws.sort(key=lambda w: w[0])
            # colunas: tipo (x < 300) | data (300–355) | tanque (355–400) | resultado (> 400)
            tipo = " ".join(w[4] for w in ws if 60 < w[0] < 300)
            dat = [w[4] for w in ws if 300 <= w[0] < 355 and re.fullmatch(r"\d{2}/\d{2}/\d{4}", w[4])]
            tq = [w[4] for w in ws if 355 <= w[0] < 400 and w[4].isdigit()]
            vl = [w[4] for w in ws if w[0] >= 400 and re.fullmatch(r"\d+(\.\d+)?", w[4])]
            if not (tipo and dat and tq and vl):
                continue
            linhas.append(dict(valor=float(vl[0]), tipo=tipo.strip(), data=dat[0], tanque=int(tq[0])))
    return mes, emit, linhas


def junta(linhas):
    tipos = sorted({l["tipo"] for l in linhas})
    # coletas por tanque: datas dos ácidos graxos (não PARLPR)
    acid = [l for l in linhas if "PARLPR" not in l["tipo"] and l["tipo"] != "LACTOSE"]
    col = defaultdict(list)
    ref = acid[0]["tipo"] if acid else None
    for l in linhas:
        if l["tipo"] == ref:
            col[l["tanque"]].append(l["data"])
    out = {}
    for tp in tipos:
        por_t = defaultdict(list)
        for l in linhas:
            if l["tipo"] == tp:
                por_t[l["tanque"]].append(l)
        for tq, ls in por_t.items():
            ls.sort(key=lambda l: l["data"][6:] + l["data"][3:5] + l["data"][:2])
            for k, l in enumerate(ls):
                cd = sorted(col[tq], key=lambda d: d[6:] + d[3:5] + d[:2])
                dc = cd[k] if k < len(cd) else None
                r = out.setdefault((tq, k), dict(tanque=tq, coleta=k + 1, data_coleta=dc))
                nome = KEY.get(tp, tp.title())
                r[nome] = l["valor"]
                if tp in KEY:
                    r.setdefault("data_analise", {})[nome] = l["data"]
    return [out[k] for k in sorted(out, key=lambda k: (k[1], k[0]))], tipos


if __name__ == "__main__":
    todos = []
    for p in sorted(glob.glob("dados/analise_oficial/*.pdf")):
        mes, emit, linhas = le(p)
        regs, tipos = junta(linhas)
        todos.append(dict(arquivo=p.split("/")[-1], mes=mes, emissao=emit, n_linhas=len(linhas), tipos=tipos, registros=regs))
        print(p, mes, emit, len(linhas), "linhas;", len(tipos), "tipos;", len(regs), "coletas×tanque")
        for r in regs:
            print("  ", r["tanque"], r["coleta"], r["data_coleta"], {k: r.get(k) for k in ["CCS", "CPP", "GOR", "PROT", "LACT", "SOL", "UREIA"]})
    json.dump(todos, open("dados/analise_oficial.json", "w"), ensure_ascii=False, indent=1)
