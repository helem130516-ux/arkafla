"""Lê os boletins "CULTURA COM ANTIBIOGRAMA" do LabVet em dados/antibiograma/*.xlsx
e grava dados/antibiograma.json (um registro por isolado, com S/I/R por antibiótico).

O boletim tem blocos: linha "Nº AMOSTRA:" (amostras nas colunas C em diante),
"IDENTIFICAÇÃO:" (vaca + quarto), "CULTURA:" (agente) e, abaixo, uma linha por antibiótico.
Novos boletins: basta salvar o .xlsx na pasta e rodar o script.
"""
import glob
import json
import re
import warnings

import openpyxl

warnings.filterwarnings("ignore")
NUL = (None, "", "\xa0")


ALIAS = {k.lower(): v for k, v in json.load(open("dados/aliases_vacas.json")).items() if not k.startswith("_")}


def vaca_quarto(s):
    s = str(s).strip()
    m = re.match(r"^(\S+)\s*(.*)$", s)
    v, q = m.group(1), m.group(2).strip().upper()
    v = ALIAS.get(v.lower(), int(float(v)) if re.fullmatch(r"\d+(\.0)?", v) else v)
    return v, q


def le(path):
    ws = openpyxl.load_workbook(path, data_only=True).active
    ctrl = entrada = liberado = None
    for r in range(1, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            v = ws.cell(r, c).value
            if v == "Número de Controle":
                ctrl = ws.cell(r + 1, c).value
            elif v == "Data de Entrada":
                entrada = ws.cell(r + 1, c).value
            elif isinstance(v, str) and v.startswith("Conferido e liberado"):
                liberado = next((ws.cell(r, k).value for k in range(c + 1, ws.max_column + 1)
                                 if hasattr(ws.cell(r, k).value, "date")), None)
    iso = []
    for r in range(1, ws.max_row + 1):
        if str(ws.cell(r, 1).value or "").strip().upper() != "Nº AMOSTRA:":
            continue
        cols = [c for c in range(2, ws.max_column + 1) if ws.cell(r, c).value not in NUL]
        # linhas de antibióticos: depois de "CULTURA:" até a primeira linha vazia/"Obs"/novo bloco
        ab_rows, k = [], r + 3
        while k <= ws.max_row:
            a = ws.cell(k, 1).value
            if a in NUL and ab_rows:
                break
            if isinstance(a, str) and (a.strip().upper().startswith("OBS") or a.strip().upper() == "Nº AMOSTRA:"):
                break
            if isinstance(a, str) and a.strip():
                ab_rows.append(k)
            k += 1
        for c in cols:
            v, q = vaca_quarto(ws.cell(r + 1, c).value)
            iso.append(dict(amostra=ws.cell(r, c).value, vaca=v, quarto=q,
                            agente=str(ws.cell(r + 2, c).value).strip(),
                            sir={ws.cell(k, 1).value.strip(): str(ws.cell(k, c).value).strip().upper()
                                 for k in ab_rows if ws.cell(k, c).value not in NUL}))
    return dict(arquivo=path.split("/")[-1], controle_lab=ctrl, entrada=entrada.date().isoformat(),
                liberado=liberado.date().isoformat() if liberado else None, isolados=iso)


if __name__ == "__main__":
    bs = [le(p) for p in sorted(glob.glob("dados/antibiograma/*.xlsx"))]
    cult = {a["amostra"]: a for b in json.load(open("dados/cultura_labvet.json")) for a in b["amostras"]}
    for b in bs:
        for i in b["isolados"]:
            c = cult.get(i["amostra"])
            i["cultura_ok"] = bool(c and c["vaca"] == i["vaca"] and any(i["agente"].rstrip(". ").lower() in a.lower() for a in c["agentes"]))
            i["data"] = c["data"] if c else b["entrada"]
            assert set(i["sir"].values()) <= {"S", "I", "R"}, i
    json.dump(bs, open("dados/antibiograma.json", "w"), ensure_ascii=False, indent=1)
    for b in bs:
        print(b["entrada"], b["controle_lab"], len(b["isolados"]), "isolados; liberado", b["liberado"],
              "; antibióticos:", len(b["isolados"][0]["sir"]),
              "; não batem com a cultura:", [(i["amostra"], i["vaca"]) for i in b["isolados"] if not i["cultura_ok"]])
