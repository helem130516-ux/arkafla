"""Lê os relatórios "Resultado Análise Leite" (LEI0940, Pool/Castrolanda) e grava dados/analise_oficial.json.

Cada PDF (dados/analise_oficial/analise_oficial_AAAA-MM.pdf) traz linhas "Tipo  Dt Analise  Nº Tanque  Resultado".
- Componentes de pagamento (CCS, CPP, gordura, proteína, lactose, sólidos, ureia): data = dia da análise no laboratório.
- Ácidos graxos (DE NOVO, MISTO, PRÉ FORMADO...): data = dia da coleta no tanque (1 a 3 dias antes da análise).
Cada amostra oficial é montada por tanque: a data de coleta é a data dos ácidos graxos do mesmo tanque
mais próxima antes da análise (até 6 dias). Sem ácidos graxos do tanque, usa a coleta de outro tanque
na mesma janela e marca coleta_estimada.
"""
import datetime as dt
import glob
import json
import re

import pdfplumber

COMP = {"CCS - PARLPR": "CCS", "C.P.P. - PARLPR": "CPP", "GORDURA - PARLPR": "G", "PROTEINA - PARLPR": "P",
        "LACTOSE": "L", "SOLIDOS TOTAIS - PARLPR": "S", "UREIA - PARLPR": "U"}
AG = {"DE NOVO": "ag_denovo", "MISTO": "ag_misto", "PRÉ FORMADO": "ag_preformado", "SATURADOS": "ag_saturados",
      "INSATURADOS": "ag_insaturados", "MONOINSATURADOS": "ag_mono", "POLINSATURADOS": "ag_poli",
      "ÁCIDO ESTEÁRICO": "ag_estearico", "ÁCIDO OLEICO": "ag_oleico", "ÁCIDO PALMITICO": "ag_palmitico"}
data = lambda s: dt.datetime.strptime(s, "%d/%m/%Y").date()  # noqa: E731


def le(pdf):
  with pdfplumber.open(pdf) as d:
    txt = "\n".join(p.extract_text() for p in d.pages)
  mes = re.search(r"Mês: (\d\d/\d{4})", txt).group(1)
  linhas = []
  for l in txt.splitlines():
    m = re.match(r"(.+?) (\d\d/\d\d/\d{4}) (\d) ([\d.,]+)$", l)
    if m:
      linhas.append((m.group(1).strip(), data(m.group(2)), int(m.group(3)), float(m.group(4).replace(",", "."))))
  return mes, linhas


def main():
  amostras = {}
  for pdf in sorted(glob.glob("dados/analise_oficial/*.pdf")):
    mes, linhas = le(pdf)
    coletas = {}  # (tanque, data coleta) -> ácidos graxos
    for tipo, d, tq, v in linhas:
      if tipo in AG:
        coletas.setdefault((tq, d), {})[AG[tipo]] = v
    for tipo, d, tq, v in linhas:
      if tipo not in COMP:
        continue
      cands = [c for (t, c) in coletas if t == tq and d - dt.timedelta(6) <= c <= d]
      estimada = not cands
      if estimada:  # sem ácidos graxos deste tanque: usa a coleta de outro tanque analisado na mesma janela
        cands = [c for (t, c) in coletas if d - dt.timedelta(6) <= c <= d]
      coleta = max(cands)
      a = amostras.setdefault((tq, coleta.isoformat()), dict(tanque=tq, mes=mes, coleta=coleta.isoformat(), analise={}, arquivo=pdf.split("/")[-1]))
      if estimada:
        a["coleta_estimada"] = True
      a[COMP[tipo]] = v
      a["analise"][COMP[tipo]] = d.isoformat()
    for (tq, c), ag in coletas.items():
      a = amostras.setdefault((tq, c.isoformat()), dict(tanque=tq, mes=mes, coleta=c.isoformat(), analise={}, arquivo=pdf.split("/")[-1]))
      a.update(ag)
  out = sorted(amostras.values(), key=lambda a: (a["coleta"], a["tanque"]))
  json.dump(dict(_nota=__doc__.strip().splitlines()[0], amostras=out), open("dados/analise_oficial.json", "w"), ensure_ascii=False, indent=1)
  print(f"{len(out)} amostras oficiais; com CCS: {sum('CCS' in a for a in out)}; coleta estimada: {sum(a.get('coleta_estimada', False) for a in out)}")


if __name__ == "__main__":
  main()
