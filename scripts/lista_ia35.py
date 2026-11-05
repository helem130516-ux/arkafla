"""Lista de vacas e novilhas com a última inseminação há mais de 35 dias (pedido da usuária).

Mesmo critério da planilha: última inseminação = a mais recente entre DATA da IA e DtIMPL (implante de embrião);
StatRepro Bred (adultas também Dry Bred) ou Vazia; sem DNB; dias = data do relatório − última inseminação > 35.
Grava monitoramento/listas/IA_mais_35_dias_AAAA-MM-DD.xlsx (abas Vacas e Novilhas; vazias em vermelho claro).

Uso:
    python3 scripts/lista_ia35.py [AAAA-MM-DD]     (sem data: o relatório mais recente)
"""
import glob
import os
import sys

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

arquivos = sorted(glob.glob("dados/zootecnico/Zootecnico_*.xlsx"))
arq = next((a for a in arquivos if sys.argv[1:] and sys.argv[1] in a), arquivos[-1])
dia = pd.Timestamp(os.path.basename(arq)[11:21])
t = pd.read_excel(arq)
t.columns = t.columns.str.strip()
t = t[t.StatRepro != "Male"].copy()
if "DtIMPL" not in t.columns:
    t["DtIMPL"] = pd.NaT
ia = pd.to_datetime(t["DATA da IA"], errors="coerce")
impl = pd.to_datetime(t["DtIMPL"], errors="coerce")
t["Última inseminação"] = pd.concat([ia, impl], axis=1).max(axis=1)
t["Origem"] = ["Implante" if pd.notna(b) and (pd.isna(a) or b > a) else "IA" for a, b in zip(ia, impl)]
t["Dias desde a inseminação"] = (dia - t["Última inseminação"]).dt.days
dnb = t.StatRepro.astype(str).str.contains("DNB")
status_ok = t.StatRepro.isin(["Vazia", "Bred"]) | ((t.LACT > 0) & (t.StatRepro == "Dry Bred"))
sel = t[~dnb & status_ok & (t["Dias desde a inseminação"] > 35)].copy()
sel["Situação"] = sel.StatRepro.map({"Bred": "Inseminada (Bred)", "Dry Bred": "Inseminada (Dry Bred)", "Vazia": "Vazia"})
sel["Lote"] = sel.Lote.replace({20: 2, 30: 3})
for c in ("DEL", "DiasVazia"):
    sel[c] = sel[c].round(0)
for c in ("DATA da IA", "DtIMPL", "Última inseminação"):
    sel[c] = pd.to_datetime(sel[c], errors="coerce").dt.strftime("%d/%m/%Y")
cols = ["Brinco", "Lote", "LACT", "DEL", "Situação", "DATA da IA", "DtIMPL", "Última inseminação", "Origem",
        "Dias desde a inseminação", "NumIAs", "DiasVazia"]
os.makedirs("monitoramento/listas", exist_ok=True)
saida = f"monitoramento/listas/IA_mais_35_dias_{dia:%Y-%m-%d}.xlsx"
contagem = {}
with pd.ExcelWriter(saida) as w:
    for nome, filtro in (("Vacas", sel.LACT > 0), ("Novilhas", sel.LACT == 0)):
        x = sel[filtro].sort_values(["Situação", "Lote", "Dias desde a inseminação"], ascending=[False, True, False])
        x = x[cols] if nome == "Vacas" else x[[c for c in cols if c not in ("DEL", "DiasVazia")]]
        contagem[nome] = x["Situação"].value_counts().to_dict()
        x.to_excel(w, sheet_name=nome, index=False, startrow=2)
wb = load_workbook(saida)
fino = Side(style="thin", color="D0D4D8")
for ws in wb.worksheets:
    n = ws.max_row - 3
    ws["A1"] = (f"ARCAFLA – {ws.title} com a última inseminação (IA ou implante) há mais de 35 dias · relatório de "
                f"{dia:%d/%m/%Y} · sem DNB · {n} animais")
    ws["A1"].font = Font(bold=True, size=12, color="2E3338")
    for c in ws[3]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="2E3338")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[3].height = 32
    col_sit = [c.value for c in ws[3]].index("Situação")
    for row in ws.iter_rows(min_row=4):
        vazia = row[col_sit].value == "Vazia"
        for c in row:
            c.border = Border(bottom=fino)
            c.alignment = Alignment(horizontal="center")
            if vazia:
                c.fill = PatternFill("solid", fgColor="FBE6E6")
    for col in ws.columns:
        ws.column_dimensions[col[2].column_letter].width = 13
    ws.column_dimensions[[c.column_letter for c in ws[3] if c.value == "Situação"][0]].width = 20
    ws.freeze_panes = "A4"
    ws.auto_filter.ref = f"A3:{ws.cell(3, ws.max_column).column_letter}{ws.max_row}"
wb.save(saida)
print(saida, contagem)
v = sel[(sel.LACT > 0) & (sel.StatRepro == "Vazia")]
print("vacas vazias por lote:", v.Lote.value_counts().sort_index().to_dict())
print("vazias por dias:", pd.cut(v["Dias desde a inseminação"], [35, 42, 60, 90, 10000]).value_counts().sort_index().to_dict())
print("vacas em que a data usada é o implante:", int((sel[sel.LACT > 0].Origem == "Implante").sum()))
