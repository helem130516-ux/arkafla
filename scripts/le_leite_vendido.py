"""Leite vendido por dia a partir do "Demonstrativo das Coletas de Leite" (PDF do laticínio).

Soma o Volume de todas as coletas com a mesma Data Coleta (a data de recepção não é usada)
e grava em dados/leite_vendido.json ({"AAAA-MM-DD": volume}). O detalhe de cada coleta
(data, hora, tanque, volume) vai para dados/coletas_leite.json, usado para ponderar as
análises do tanque pelo volume. O PDF é guardado em dados/leite_vendido/.

A cada execução os totais são refeitos com todos os PDFs guardados: as coletas de todos eles são
juntadas pelo número do boleto (sem repetir), e o total do dia é a soma das coletas com aquela data.
Do PDF mais recente, são ignoradas as coletas com data igual ou posterior à de emissão e as da última
data de coleta: esses dias podem estar incompletos (ex.: PDF emitido em 21/10 às 14:31 só tinha uma
coleta com data de 20/10). O próximo PDF completa esses dias. Isso também resolve a virada do mês
(relatório mensal por data de recepção: parte das coletas de 30/10 só aparece no PDF de novembro).

Uso:
    python3 scripts/le_leite_vendido.py relatorio.pdf [...]
"""
import json
import os
import re
import shutil
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime

JSON = "dados/leite_vendido.json"
COLETAS = "dados/coletas_leite.json"
PASTA = "dados/leite_vendido"
# boleto, data e hora da coleta, temperatura, tanque, placa, sobras, volume (milhar com ponto)
LINHA = re.compile(r"\b(\d{8,})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s+[\d,]+\s+(\d+)\s+\S+"
                   r"\s+\d+\s+([\d.]+)\s*$")
EMITIDO = re.compile(r"Emitido em\s+(\d{2}/\d{2}/\d{4})\s+as\s+(\d{2}):(\d{2})")


def le(pdf):
    txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True,
                         check=True).stdout
    dias = OrderedDict()
    col = []
    for ln in txt.splitlines():
        m = LINHA.search(ln)
        if not m:
            continue
        d = datetime.strptime(m[2], "%d/%m/%Y").date().isoformat()
        v = int(m[5].replace(".", ""))
        dias[d] = dias.get(d, 0) + v
        col.append({"boleto": m[1], "data": d, "hora": m[3], "tanque": int(m[4]), "volume": v})
    n = len(col)
    # conferência com o "Total Período" do relatório
    tot = re.search(r"Total Período:\s+\S+\s+([\d.]+)", txt)
    if tot and int(tot[1].replace(".", "")) != sum(dias.values()):
        raise SystemExit(f"{pdf}: soma das coletas ({sum(dias.values())}) ≠ Total Período ({tot[1]})")
    em = EMITIDO.search(txt)
    # dia da emissão (e depois) e a última data de coleta do relatório podem estar incompletos
    corte = datetime.strptime(em[1], "%d/%m/%Y").date().isoformat() if em else "9999"
    corte = min(corte, max(dias)) if dias else corte
    return n, em, col, corte


os.makedirs(PASTA, exist_ok=True)
for pdf in sys.argv[1:]:  # guarda os PDFs novos com o nome da emissão
    em = EMITIDO.search(subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True,
                                       text=True, check=True).stdout)
    nome = (f"Coletas_{datetime.strptime(em[1], '%d/%m/%Y'):%Y-%m-%d}_{em[2]}{em[3]}.pdf"
            if em else os.path.basename(pdf))
    dest = os.path.join(PASTA, nome)
    if os.path.abspath(pdf) != os.path.abspath(dest):
        shutil.copyfile(pdf, dest)
# Junta as coletas de todos os PDFs pelo número do boleto (sem repetir). Assim um dia que ficou dividido entre dois
# PDFs (ex.: virada do mês, quando o relatório é por data de recepção) soma as coletas dos dois. Só o corte do PDF
# mais recente vale: os dias anteriores a ele já estão completos.
coletas, corte = {}, "9999"
for pdf in sorted(os.path.join(PASTA, f) for f in os.listdir(PASTA) if f.endswith(".pdf")):
    n, em, col, corte = le(pdf)
    coletas.update({c["boleto"]: c for c in col})
    print(f"{os.path.basename(pdf)}: {n} coletas ({min(c['data'] for c in col)} a {max(c['data'] for c in col)})"
          if col else f"{os.path.basename(pdf)}: sem coletas")
coletas = {b: c for b, c in coletas.items() if c["data"] < corte}
vendido = {}
for c in coletas.values():
    vendido[c["data"]] = vendido.get(c["data"], 0) + c["volume"]
json.dump(dict(sorted(vendido.items())), open(JSON, "w"), indent=1)
json.dump(sorted(coletas.values(), key=lambda c: (c["data"], c["hora"])), open(COLETAS, "w"), indent=1)
print(f"{JSON}: {len(vendido)} dias completos ({min(vendido)} a {max(vendido)}; corte do PDF mais recente: {corte})")
