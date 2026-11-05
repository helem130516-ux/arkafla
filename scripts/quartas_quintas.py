"""Acompanhamento da produção nas quartas e quintas-feiras (dias em que as vacas manifestam cio).

Pedido da usuária em 05/11/2026: guardar, fora do relatório diário, a variação de produção e a média de todas as
quartas e quintas-feiras. Este script refaz tudo a partir dos relatórios em dados/zootecnico/ (já com as correções
de pesagem) e grava monitoramento/analises/Quartas_Quintas_ARCAFLA.xlsx com três abas:
  - "Quartas e quintas": um dia por linha, com produção média por vaca e total do tanque, variação em relação ao dia
    anterior e à média dos 7 dias anteriores;
  - "Resumo por dia da semana": médias de cada dia da semana (quarta, quinta e os demais) para comparar;
  - "Todos os dias": a série diária completa usada nas contas.
Tanque = vacas adultas (LACT > 0) dos lotes 1 a 6 (20 e 30 contam como 2 e 3) e, desde 03/11/2026, também do lote 7;
média por vaca só com Leite > 0, como na planilha principal.

Uso:
    python3 scripts/quartas_quintas.py
"""
import glob
import os

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

SAIDA = "monitoramento/analises/Quartas_Quintas_ARCAFLA.xlsx"
DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
LOTE7_DESDE = pd.Timestamp("2026-11-03")


def dia(arquivo):
    d = pd.Timestamp(os.path.basename(arquivo)[11:21])
    t = pd.read_excel(arquivo)
    t.columns = t.columns.str.strip()
    t = t[t.StatRepro != "Male"]
    lote = t.Lote.replace({20: 2, 30: 3})
    lotes = list(range(1, 7)) + ([7] if d >= LOTE7_DESDE else [])
    tq = t[(t.LACT > 0) & lote.isin(lotes)]
    leite = tq.Leite[tq.Leite > 0]
    return {"Data": d, "Dia da semana": DIAS[d.weekday()], "Vacas no tanque": len(tq),
            "Vacas com pesagem": len(leite), "Produção média (kg/vaca)": leite.mean(),
            "Leite total do tanque (kg)": leite.sum()}


s = pd.DataFrame([dia(a) for a in sorted(glob.glob("dados/zootecnico/Zootecnico_*.xlsx"))])
s = s.sort_values("Data").reset_index(drop=True)
m = "Produção média (kg/vaca)"
s["Variação vs dia anterior (kg/vaca)"] = s[m].diff()
s["Variação vs dia anterior (%)"] = s[m].pct_change()
# média dos 7 dias anteriores (só dias que existem nos relatórios)
s["Média dos 7 dias anteriores (kg/vaca)"] = s[m].shift(1).rolling(7, min_periods=3).mean()
s["Variação vs média dos 7 dias anteriores (kg/vaca)"] = s[m] - s["Média dos 7 dias anteriores (kg/vaca)"]
s["Variação vs média dos 7 dias anteriores (%)"] = s[m] / s["Média dos 7 dias anteriores (kg/vaca)"] - 1

qq = s[s["Dia da semana"].isin(["quarta", "quinta"])].copy()
resumo = (s.groupby("Dia da semana", sort=False)
          .agg(**{"Nº de dias": (m, "count"), "Produção média (kg/vaca)": (m, "mean"),
                  "Leite total médio (kg)": ("Leite total do tanque (kg)", "mean"),
                  "Variação média vs dia anterior (kg/vaca)": ("Variação vs dia anterior (kg/vaca)", "mean"),
                  "Variação média vs 7 dias anteriores (kg/vaca)":
                      ("Variação vs média dos 7 dias anteriores (kg/vaca)", "mean")}))
resumo = resumo.reindex([d for d in DIAS if d in resumo.index]).reset_index()
grupos = pd.DataFrame([
    {"Dia da semana": "QUARTAS E QUINTAS (média)", "Nº de dias": len(qq), m: qq[m].mean(),
     "Leite total médio (kg)": qq["Leite total do tanque (kg)"].mean(),
     "Variação média vs dia anterior (kg/vaca)": qq["Variação vs dia anterior (kg/vaca)"].mean(),
     "Variação média vs 7 dias anteriores (kg/vaca)": qq["Variação vs média dos 7 dias anteriores (kg/vaca)"].mean()},
    {"Dia da semana": "DEMAIS DIAS (média)", "Nº de dias": len(s) - len(qq),
     m: s.loc[~s.index.isin(qq.index), m].mean(),
     "Leite total médio (kg)": s.loc[~s.index.isin(qq.index), "Leite total do tanque (kg)"].mean(),
     "Variação média vs dia anterior (kg/vaca)": s.loc[~s.index.isin(qq.index), "Variação vs dia anterior (kg/vaca)"].mean(),
     "Variação média vs 7 dias anteriores (kg/vaca)":
         s.loc[~s.index.isin(qq.index), "Variação vs média dos 7 dias anteriores (kg/vaca)"].mean()}])
resumo = pd.concat([resumo, grupos], ignore_index=True)

os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with pd.ExcelWriter(SAIDA) as w:
    for nome, df in (("Quartas e quintas", qq), ("Resumo por dia da semana", resumo), ("Todos os dias", s)):
        df.to_excel(w, sheet_name=nome, index=False, startrow=2)

# formatação simples
wb = load_workbook(SAIDA)
fino = Side(style="thin", color="D0D4D8")
titulos = {"Quartas e quintas": "Produção nas quartas e quintas-feiras (dias de manifestação de cio)",
           "Resumo por dia da semana": "Produção média por dia da semana",
           "Todos os dias": "Série diária usada nas contas"}
for ws in wb.worksheets:
    ws["A1"] = f"ARCAFLA – {titulos[ws.title]} · relatórios de {s.Data.min():%d/%m/%Y} a {s.Data.max():%d/%m/%Y}"
    ws["A1"].font = Font(bold=True, size=12, color="2E3338")
    for c in ws[3]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="2E3338")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[3].height = 45
    for row in ws.iter_rows(min_row=4):
        destaque = str(row[1].value) in ("quarta", "quinta") or str(row[0].value).startswith("QUARTAS")
        for c in row:
            c.border = Border(bottom=fino)
            cab = ws.cell(3, c.column).value or ""
            if cab == "Data":
                c.number_format = "DD/MM/YYYY"
            elif "(%)" in cab:
                c.number_format = "+0.0%;-0.0%;0.0%"
            elif "Variação" in cab:
                c.number_format = "+0.0;-0.0;0.0"
            elif "kg/vaca" in cab:
                c.number_format = "0.0"
            elif "(kg)" in cab:
                c.number_format = "#,##0"
            if destaque and ws.title != "Quartas e quintas":
                c.fill = PatternFill("solid", fgColor="FFF6D6")
    for col in ws.columns:
        ws.column_dimensions[col[2].column_letter].width = 16
    ws.column_dimensions["A"].width = 26 if ws.title == "Resumo por dia da semana" else 12
    ws.freeze_panes = "A4"
wb.save(SAIDA)
print(f"{SAIDA}: {len(qq)} quartas/quintas de {len(s)} dias")
print(resumo[["Dia da semana", "Nº de dias", m, "Variação média vs dia anterior (kg/vaca)"]].round(2).to_string(index=False))
