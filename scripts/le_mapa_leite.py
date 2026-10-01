"""Lê o mapa de fornecimento do Pool Leite (PDF) e grava dados/mapa_leite.json.

Tabela "DEMONSTRATIVO MÉDIAS DAS ANÁLISES": por tanque, por período (mês/período) o volume (L)
e as análises CCS (mil céls/mL), CPP (mil UFC/mL), gordura, proteína, sólidos e ureia.
As células são lidas pela posição no PDF. 'destaque' = valor em azul/sombreado no mapa
(o critério do laticínio para o destaque não vem explicado no documento).
"""
import glob
import json
import re

import pymupdf

LIN = ["CCS", "CPP", "GOR.", "PROT.", "SOL.", "UREIA"]
num = lambda t: float(t.replace(".", "").replace(",", ".")) if re.fullmatch(r"[\d.]+(,\d+)?", t) else None  # noqa: E731

def le(PDF):
  doc = pymupdf.open(PDF)
  txt = doc[0].get_text()
  cab = dict(
      mes=re.search(r"(\d{2}/\d{4})\s*\nEmissão", txt).group(1),
      emissao=re.search(r"(\d{2}/\d{2}/\d{4})\s+as", txt).group(1),
      producao_mes_l=num(re.search(r"([\d.]+)\s*\nProdução Mês", txt).group(1)),
      preco_final_litro=num(re.search(r"Preço Final por Litro:\s*\n[\s\S]*?\n\s*([\d]+,\d{4})\s*\nValor Total", txt).group(1)),
  )
  # médias do mapa (Média Pagto / Média POOL)
  m = re.search(r"Pagto\s*\nMédia\s*\nPOOL\s*\n([\s\S]+?)\nCCS\s*\nCPP", txt)
  vals = [float(x) for x in m.group(1).split()] if m else []
  cab["media_pagto"] = dict(zip(["CCS", "CPP", "GOR.", "PROT.", "SOL.", "UREIA"], vals[:6]))
  cab["media_pool"] = dict(zip(["CCS", "CPP", "GOR.", "PROT.", "SOL.", "UREIA"], vals[6:12]))

  tanques = []
  for page in doc:
      words = page.get_text("words")  # x0,y0,x1,y1,txt,block,line,wno
      spans = [s for b in page.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]
      tq_rows = sorted([w for w in words if w[4] == "Tanque:"], key=lambda w: w[1])
      for k, tw in enumerate(tq_rows):
          y0 = tw[1]
          y1 = tq_rows[k + 1][1] if k + 1 < len(tq_rows) else page.rect.height
          W = [w for w in words if y0 - 2 <= w[1] < y1 - 2]
          tq = int(next(w[4] for w in W if abs(w[1] - tw[1]) < 3 and w[0] > tw[2]))
          # linha de volumes: tokens seguidos de "L"
          ls = [w for w in W if w[4] == "L"]
          yv = ls[0][1]
          vols = sorted([w for w in W if abs(w[1] - yv) < 3 and num(w[4]) is not None], key=lambda w: w[0])
          lsr = sorted([w for w in ls if abs(w[1] - yv) < 3], key=lambda w: w[0])
          # cada coluna termina no "L" que segue o volume; os valores são alinhados à direita nessa borda
          cols = [(v[0], next(l_[2] for l_ in lsr if l_[0] >= v[2] - 1)) for v in vols]
          # meses e períodos
          meses = sorted([w for w in W if re.fullmatch(r"\d{2}/\d{4}", w[4])], key=lambda w: w[0])
          pers = sorted([w for w in W if re.fullmatch(r"\d+o\.", w[4])], key=lambda w: w[0])
          rows = {}
          for lab in LIN:
              lw = next(w for w in W if w[4] == lab and w[0] < 40)
              rows[lab] = lw[1]
          for j, (cx0, cx1) in enumerate(cols):
              mes = [m_[4] for m_ in meses if m_[0] <= cx1][-1]
              per = min(pers, key=lambda p: abs(p[0] - cx0))[4]
              rec = dict(tanque=tq, mes=mes, periodo=int(per[0]), volume_l=num(vols[j][4]))
              for lab, yy in rows.items():
                  cell = [w for w in W if abs(w[1] - yy) < 3 and abs(w[2] - cx1) < 7 and num(w[4]) is not None and w[0] > 40]
                  v = num(cell[0][4]) if cell else None
                  rec[lab] = v
                  # destaque: span azul na mesma posição
                  hl = [s for s in spans if s["text"].strip() == (cell[0][4] if cell else None) and abs(s["bbox"][1] - cell[0][1]) < 3 and abs(s["bbox"][0] - cell[0][0]) < 3 and s["color"] != 0] if cell else []
                  rec[lab + "_destaque"] = bool(hl)
              tanques.append(rec)

  # premiações
  pm = re.search(r"PREMIAÇÕES\s*\n([\s\S]+?)\nIndicadores\s*\n([\s\S]+?)\n% Prêmio\s*\n([\s\S]+?)\nPrêmio p/ Litro \(R\$\)\s*\nPREMIAÇÕES\s*\n([\s\S]+?)\nTotal do Prêmio", txt)
  if not pm:
      pm = re.search(r"\n((?:[A-ZÇÃÕÉ][^\n]*\n)+?)Indicadores\s*\n([\s\S]+?)\n% Prêmio\s*\n([\s\S]+?)\nPrêmio p/ Litro \(R\$\)\s*\nPREMIAÇÕES\s*\n([\s\S]+?)\nTotal do Prêmio", txt)
  if pm:
      nomes = [x.strip() for x in pm.group(1).strip().split("\n")][-len(pm.group(2).split()):]
      cab["premiacoes"] = [dict(indicador=n, pct=num(a), rs_litro=num(b), total=num(c)) for n, a, b, c in
                           zip(nomes, pm.group(2).split(), pm.group(3).split(), pm.group(4).split())]
  tp = re.search(r"([\d.]+,\d{2})\s*\nTotal Premiações", txt)
  cab["total_premiacoes"] = num(tp.group(1)) if tp else None
  cab["arquivo"] = PDF.split("/")[-1]
  return cab, tanques


if __name__ == "__main__":
    mapas, regs = [], {}
    for p in sorted(glob.glob("dados/mapa_leite/*.pdf")):
        cab, tq = le(p)
        mapas.append(cab)
        for r in tq:  # o mapa mais recente substitui o mesmo tanque/mês/período
            regs[(r["tanque"], r["mes"][3:] + r["mes"][:2], r["periodo"])] = dict(r, fonte=cab["arquivo"])
    R = [regs[k] for k in sorted(regs)]
    json.dump(dict(mapas=mapas, registros=R), open("dados/mapa_leite.json", "w"), ensure_ascii=False, indent=1)
    for c in mapas:
        print(c["mes"], c["arquivo"], "média pagto", c["media_pagto"], "pool", c["media_pool"])
        for x in c.get("premiacoes", []):
            print("   ", x)
    print(len(R), "análises de tanque/período")
