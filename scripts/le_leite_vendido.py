"""Leite vendido por dia a partir do "Demonstrativo das Coletas de Leite" (PDF do laticínio).

Soma o Volume de todas as coletas com a mesma Data Coleta (a data de recepção não é usada)
e grava em dados/leite_vendido.json ({"AAAA-MM-DD": volume}). O detalhe de cada coleta
(data, hora, tanque, volume) vai para dados/coletas_leite.json, usado para ponderar as
análises do tanque pelo volume. As datas de um PDF novo
substituem as que já existiam; as demais ficam. O PDF é guardado em dados/leite_vendido/.

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
    return dias, n, em, col


vendido = json.load(open(JSON)) if os.path.exists(JSON) else {}
coletas = {c["boleto"]: c for c in json.load(open(COLETAS))} if os.path.exists(COLETAS) else {}
os.makedirs(PASTA, exist_ok=True)
for pdf in sys.argv[1:]:
    dias, n, em, col = le(pdf)
    vendido.update(dias)
    coletas.update({c["boleto"]: c for c in col})
    nome = (f"Coletas_{datetime.strptime(em[1], '%d/%m/%Y'):%Y-%m-%d}_{em[2]}{em[3]}.pdf"
            if em else os.path.basename(pdf))
    dest = os.path.join(PASTA, nome)
    if os.path.abspath(pdf) != os.path.abspath(dest):
        shutil.copyfile(pdf, dest)
    print(f"{os.path.basename(pdf)}: {n} coletas, {len(dias)} datas de coleta -> {PASTA}/{nome}")
    for d, v in dias.items():
        print(f"  {d}: {v:,}".replace(",", "."))
json.dump(dict(sorted(vendido.items())), open(JSON, "w"), indent=1)
json.dump(sorted(coletas.values(), key=lambda c: (c["data"], c["hora"])), open(COLETAS, "w"), indent=1)
print(f"{JSON}: {len(vendido)} dias")
