"""Leite vendido por dia a partir do "Demonstrativo das Coletas de Leite" (PDF do laticínio).

Soma o Volume de todas as coletas com a mesma Data Coleta (a data de recepção não é usada)
e grava em dados/leite_vendido.json ({"AAAA-MM-DD": volume}). As datas de um PDF novo
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
PASTA = "dados/leite_vendido"
# boleto, data/hora da coleta, ... volume no fim da linha (milhar com ponto)
LINHA = re.compile(r"\b\d{8,}\s+(\d{2}/\d{2}/\d{4})\s+\d{2}:\d{2}\s.*?\s([\d.]+)\s*$")
EMITIDO = re.compile(r"Emitido em\s+(\d{2}/\d{2}/\d{4})\s+as\s+(\d{2}):(\d{2})")


def le(pdf):
    txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True,
                         check=True).stdout
    dias = OrderedDict()
    n = 0
    for ln in txt.splitlines():
        m = LINHA.search(ln)
        if not m:
            continue
        d = datetime.strptime(m[1], "%d/%m/%Y").date().isoformat()
        dias[d] = dias.get(d, 0) + int(m[2].replace(".", ""))
        n += 1
    # conferência com o "Total Período" do relatório
    tot = re.search(r"Total Período:\s+\S+\s+([\d.]+)", txt)
    if tot and int(tot[1].replace(".", "")) != sum(dias.values()):
        raise SystemExit(f"{pdf}: soma das coletas ({sum(dias.values())}) ≠ Total Período ({tot[1]})")
    em = EMITIDO.search(txt)
    return dias, n, em


vendido = json.load(open(JSON)) if os.path.exists(JSON) else {}
os.makedirs(PASTA, exist_ok=True)
for pdf in sys.argv[1:]:
    dias, n, em = le(pdf)
    vendido.update(dias)
    nome = (f"Coletas_{datetime.strptime(em[1], '%d/%m/%Y'):%Y-%m-%d}_{em[2]}{em[3]}.pdf"
            if em else os.path.basename(pdf))
    shutil.copyfile(pdf, os.path.join(PASTA, nome))
    print(f"{os.path.basename(pdf)}: {n} coletas, {len(dias)} datas de coleta -> {PASTA}/{nome}")
    for d, v in dias.items():
        print(f"  {d}: {v:,}".replace(",", "."))
json.dump(dict(sorted(vendido.items())), open(JSON, "w"), indent=1)
print(f"{JSON}: {len(vendido)} dias")
