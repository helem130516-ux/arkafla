"""Monta o painel completo a partir dos dados do repositório.

Uso: python3 scripts/monta_painel.py  -> painel/painel_qualidade_ARKAFLA.html
Passos: lê os dados (APCBRH, mastite, culturas, antibiograma), gera o DATA e aplica,
em ordem, os patches sobre painel/base_original.html. Depois é só publicar no mesmo link.
"""
import json
import os
import subprocess
import sys
import tempfile

S = os.path.dirname(__file__)
py = lambda *a: subprocess.run([sys.executable, *a], check=True)  # noqa: E731

py(f"{S}/le_cultura_labvet.py")
py(f"{S}/le_registro_mastite.py")
py(f"{S}/le_antibiograma.py")
py(f"{S}/gera_data_painel.py")
base = open("painel/base_original.html", encoding="utf-8").read()
i = base.index("const DATA = ") + len("const DATA = ")
_, end = json.JSONDecoder().raw_decode(base[i:])
data = open("saida/data_painel.json", encoding="utf-8").read()
tmp = tempfile.mkdtemp()
f0 = os.path.join(tmp, "p0.html")
open(f0, "w", encoding="utf-8").write(base[:i] + data + base[i + end:])
passos = [("patch_painel_mes.py", None), ("patch_painel_cultura_onfarm.py", "dados/cultura_onfarm_2026.json"),
          ("patch_painel_cultura_labvet.py", "dados/cultura_labvet.json"),
          ("patch_painel_registro_fazenda.py", "dados/registro_fazenda.json"),
          ("patch_painel_antibiograma.py", "dados/antibiograma.json")]
cur = f0
for k, (p, arg) in enumerate(passos, 1):
    nxt = os.path.join(tmp, f"p{k}.html")
    py(f"{S}/{p}", cur, nxt, *([arg] if arg else []))
    cur = nxt
os.makedirs("painel", exist_ok=True)
open("painel/painel_qualidade_ARKAFLA.html", "w", encoding="utf-8").write(open(cur, encoding="utf-8").read())
print("painel/painel_qualidade_ARKAFLA.html pronto")
