"""Planilha de monitoramento diário da ARCAFLA a partir do relatório zootécnico
diário ("Zootécnico Jorge atualizado DD-MM-AAAA.xlsx").

Cada relatório corresponde à data escrita no nome do arquivo. Os relatórios ficam
guardados em dados/zootecnico/Zootecnico_AAAA-MM-DD.xlsx (um por dia; um arquivo
novo da mesma data substitui o anterior). A planilha mostra sempre os 10 dias mais
recentes: cada dia é uma coluna, cada indicador é uma linha. O dia anterior ao
primeiro exibido também entra na aba Dados, para as comparações com o dia anterior.

O leite vendido vem de dados/leite_vendido.json ({"AAAA-MM-DD": kg}), que será
preenchido a partir do PDF do laticínio.

Uso:
    python3 scripts/monitor_diario.py [novo_relatorio.xlsx ...]
Depois: recalcular com recalc.py (skill xlsx) e gerar o PDF de uma página com
    python3 scripts/monitor_pdf.py
"""
import glob
import json
import os
import re
import shutil
import sys
from datetime import date

import pandas as pd
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName

PASTA = "dados/zootecnico"
VENDIDO = "dados/leite_vendido.json"
OUT = "monitoramento/Monitoramento_Diario_ARCAFLA.xlsx"
NDIAS = 10
F = "Arial"
AZUL = "2E3338"  # cor principal: cinza-escuro

thin = Side(style="thin", color="C9D1CB")
BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
HFILL = PatternFill("solid", fgColor="E6ECE8")
INFILL = PatternFill("solid", fgColor="FFF6D6")
SECFILL = PatternFill("solid", fgColor=AZUL)
SUBFILL = PatternFill("solid", fgColor="DFE2E4")
ZEBRA = PatternFill("solid", fgColor="F5F8F6")


def font(**k):
    return Font(name=F, **{"size": 10, **k})


def data_do_nome(path):
    """Data no nome do arquivo: DD-MM-AAAA (original) ou AAAA-MM-DD (guardado)."""
    nome = os.path.basename(path)
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", nome)
    if m:
        return date(int(m[1]), int(m[2]), int(m[3]))
    m = re.search(r"(\d{1,2})[-_.](\d{1,2})[-_.](\d{4})", nome)
    if m:
        return date(int(m[3]), int(m[2]), int(m[1]))
    raise SystemExit(f"Sem data no nome do arquivo: {nome}")


def guarda(path):
    d = data_do_nome(path)
    os.makedirs(PASTA, exist_ok=True)
    dest = os.path.join(PASTA, f"Zootecnico_{d.isoformat()}.xlsx")
    shutil.copyfile(path, dest)
    print(f"{os.path.basename(path)} -> {dest}")


for p in sys.argv[1:]:
    guarda(p)

todos = sorted(glob.glob(os.path.join(PASTA, "Zootecnico_*.xlsx")), key=data_do_nome)
if not todos:
    raise SystemExit(f"Nenhum relatório em {PASTA}")
arquivos = todos[-(NDIAS + 1):]          # +1: dia anterior ao primeiro exibido
DATAS = [data_do_nome(p) for p in arquivos]
DIAS = DATAS[-NDIAS:]                    # dias exibidos
ND = len(DIAS)
vendido = json.load(open(VENDIDO)) if os.path.exists(VENDIDO) else {}
ANALISES = "dados/analise_tanque.json"
COLETAS = "dados/coletas_leite.json"
analises = sorted(json.load(open(ANALISES)) if os.path.exists(ANALISES) else [],
                  key=lambda a: (a["data"], a["tanque"]))
coletas = json.load(open(COLETAS)) if os.path.exists(COLETAS) else []

frames = []
for d, p in zip(DATAS, arquivos):
    df = pd.read_excel(p)
    df.columns = df.columns.str.strip()
    df.insert(0, "Data", pd.Timestamp(d))
    frames.append(df)
# Ordenado por brinco e data: a linha de cima é o mesmo animal no relatório anterior.
dados = pd.concat(frames, ignore_index=True).sort_values(["Brinco", "Data"], kind="stable")
# Lotes equivalentes (pedido do usuário, 20/10/2026): o lote 20 conta como lote 2 e o 30 como lote 3.
LOTE_EQUIV = {20: 2, 30: 3}
dados["Lote"] = dados["Lote"].replace(LOTE_EQUIV)
# Data da última inseminação: coluna nova no relatório (a partir de 14/10/2026); antes não existia.
if "DATA da IA" not in dados.columns:
    dados["DATA da IA"] = pd.NaT
dados["DATA da IA"] = pd.to_datetime(dados["DATA da IA"], errors="coerce")
# Data do último parto: coluna nova no relatório (a partir de 15/10/2026).
if "DtÚltParto" not in dados.columns:
    dados["DtÚltParto"] = pd.NaT
dados["DtÚltParto"] = pd.to_datetime(dados["DtÚltParto"], errors="coerce")
COLS = list(dados.columns)
NR = len(dados) + 1  # última linha da aba Dados

AUX = ["Fêmea", "DNB", "Dias desde IA", "Pariu no período", "DiaNº", "Lactação", "Lote10", "Lactação ant.", "Lote10 ant.",
       "Iniciou lactação", "Entrou lote 10", "Saída adulto em", "Saída lote 10 em"]
C = {c: L(i + 1) for i, c in enumerate(COLS + AUX)}


def R(campo):
    return f"Dados!${C[campo]}$2:${C[campo]}${NR}"


wb = Workbook()
wb._named_styles["Normal"].font = Font(name=F, size=10)
ws = wb.active
ws.title = "Monitoramento"
wt = wb.create_sheet("Análises do tanque")
wp = wb.create_sheet("Parâmetros")
wd = wb.create_sheet("Dados")
wn = wb.create_sheet("Notas")


def name(n, ref):
    wb.defined_names[n] = DefinedName(n, attr_text=ref)


# ---------------------------------------------------------------- Parâmetros
wp["A1"] = "Parâmetros dos indicadores"
wp["A1"].font = font(bold=True, size=14, color=AZUL)
wp["A2"] = "Células amarelas podem ser alteradas; o Monitoramento recalcula."
wp["A2"].font = font(italic=True, size=9, color="5E6B63")
params = [
    ("P_DEL_NG", "Vacas não gestantes: DEL acima de (dias)", 150),
    ("P_DEL_SEM_IA", "Vacas sem inseminação: DEL acima de (dias)", 70),
    ("P_IDADE_3M", "Animais jovens < 3 meses: idade abaixo de (dias)", 90),
    ("P_IDADE_15M", "Novilhas atrasadas: idade acima de (dias) – 15 meses", 456),
    ("P_DIAS_IA", "Inseminadas / vazias: dias desde a última IA acima de", 35),
    # ECM (Sjaunja et al., 1990): 0,327 × leite + 12,95 × kg gordura + 7,65 × kg proteína
    ("P_ECM_BASE", "ECM: fator do leite (Sjaunja et al., 1990)", 0.327),
    ("P_ECM_GORD", "ECM: fator por ponto % de gordura (12,95 ÷ 100)", 0.1295),
    ("P_ECM_PROT", "ECM: fator por ponto % de proteína (7,65 ÷ 100)", 0.0765),
    ("P_DENSIDADE", "Densidade do leite (kg por litro): converte o leite comercializado de L para kg", 1.032),
]
for j, t in enumerate(["Parâmetro", "Valor", "Nome"], 1):
    c = wp.cell(4, j, t)
    c.font, c.fill, c.border = font(bold=True, size=9), HFILL, BOX
for i, (n, t, v) in enumerate(params, 5):
    wp.cell(i, 1, t).font = font()
    c = wp.cell(i, 2, v)
    c.fill, c.border, c.font = INFILL, BOX, font(bold=True, color="0000FF")
    wp.cell(i, 3, n).font = font(size=9, color="5E6B63")
    name(n, f"'Parâmetros'!$B${i}")
r0 = 5 + len(params) + 1
wp.cell(r0, 1, "Datas dos relatórios na aba Dados (nº do dia)").font = font(bold=True)
for k, d in enumerate(DATAS):
    wp.cell(r0 + 1 + k, 1, k + 1).font = font()
    c = wp.cell(r0 + 1 + k, 2, d)  # data do nome do arquivo
    c.number_format = "DD/MM/YYYY"
    c.font = font()
    wp.cell(r0 + 1 + k, 3, os.path.basename(arquivos[k])).font = font(size=9, color="5E6B63")
name("DATAS", f"'Parâmetros'!$B${r0 + 1}:$B${r0 + len(DATAS)}")
wp.column_dimensions["A"].width = 50
wp.column_dimensions["B"].width = 12
wp.column_dimensions["C"].width = 30

# ---------------------------------------------------------------- Análises do tanque
wt["A1"] = "Análises do leite do tanque (laticínio)"
wt["A1"].font = font(bold=True, size=14, color=AZUL)
wt["A2"] = ("Valores azuis transcritos das mensagens do laticínio (dados/analise_tanque.json). "
            "Volume = coleta do mesmo dia e tanque no Demonstrativo das Coletas; 0 = não encontrado. "
            "Análises do mesmo grupo (mesma mensagem) contam como uma só coleta.")
wt["A2"].font = font(italic=True, size=9, color="5E6B63")
TQ = ["Data coleta", "Tanque", "Volume (L)", "Gordura %", "Proteína %", "Lactose %", "Sólidos totais %",
      "CCS (mil cél/mL)", "CPP (mil UFC/mL)", "Ureia (mg/dL)", "Grupo", "Fonte"]
TQK = ["gordura", "proteina", "lactose", "st", "ccs", "cpp", "ureia"]
for a in analises:
    a.setdefault("grupo", a.get("fonte", a["data"]))
for j, t in enumerate(TQ, 1):
    c = wt.cell(4, j, t)
    c.font, c.fill, c.border = font(bold=True, size=9), HFILL, BOX
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
for i, a in enumerate(analises, 5):
    vol = sum(c["volume"] for c in coletas if c["data"] == a["data"] and c["tanque"] == a["tanque"])
    vals = ([date.fromisoformat(a["data"]), a["tanque"], vol] + [a.get(k) for k in TQK]
            + [a["grupo"], a.get("fonte", "")])
    for j, v in enumerate(vals, 1):
        c = wt.cell(i, j, v)
        c.border = BOX
        c.font = font(color="0000FF") if j < 12 else font(size=8, color="5E6B63")
    wt.cell(i, 1).number_format = "DD/MM/YYYY"
    wt.cell(i, 3).number_format = "#,##0"
NA = max(len(analises), 1) + 4  # última linha das análises


def TR(col):
    return f"'Análises do tanque'!${col}$5:${col}${NA}"


# média geral do tanque por grupo de análises (uma mensagem = uma coleta), ponderada pelo volume.
# Vale a partir da primeira data de coleta do grupo.
GR = {}
for a in analises:
    GR.setdefault(a["grupo"], []).append(a["data"])
GR = sorted(GR.items(), key=lambda g: min(g[1]))
c0 = 15  # coluna O
wt.cell(3, c0, "Média geral do tanque por grupo de análises (ponderada pelo volume)").font = font(bold=True)
for j, t in enumerate(["Vale a partir de", "Coletas até", "Grupo", "Volume analisado (L)"] + TQ[3:10], c0):
    c = wt.cell(4, j, t)
    c.font, c.fill, c.border = font(bold=True, size=9), HFILL, BOX
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
for i, (g, datas) in enumerate(GR, 5):
    gc = f"{L(c0 + 2)}{i}"
    wt.cell(i, c0, date.fromisoformat(min(datas))).number_format = "DD/MM/YYYY"
    wt.cell(i, c0 + 1, date.fromisoformat(max(datas))).number_format = "DD/MM/YYYY"
    wt.cell(i, c0 + 2, g)
    wt.cell(i, c0 + 3, f"=SUMIFS({TR('C')},{TR('K')},{gc})").number_format = "#,##0"
    for k, col in enumerate("DEFGHIJ"):
        # só tanques com valor neste item (ex.: lactose não vinha nas primeiras mensagens)
        g = f"({TR('K')}={gc})*ISNUMBER({TR(col)})"
        f = (f'=IF(SUMPRODUCT({g})=0,"",IF(COUNTIFS({TR("K")},{gc},{TR("C")},0)>0,'
             f"AVERAGEIFS({TR(col)},{TR('K')},{gc}),"
             f"SUMPRODUCT({g}*{TR('C')}*{TR(col)})/SUMPRODUCT({g}*{TR('C')})))")
        wt.cell(i, c0 + 4 + k, f).number_format = "0.00" if k < 4 else "0"
    for j in range(c0, c0 + 11):
        wt.cell(i, j).border = BOX
        wt.cell(i, j).font = font()
NT = max(len(GR), 1) + 4
name("TQ_DATA", f"'Análises do tanque'!${L(c0)}$5:${L(c0)}${NT}")
for k, n in enumerate(["TQ_GORD", "TQ_PROT", "TQ_LACT", "TQ_ST", "TQ_CCS", "TQ_CPP", "TQ_UREIA"]):
    col = L(c0 + 4 + k)
    name(n, f"'Análises do tanque'!${col}$5:${col}${NT}")
for j in range(1, c0 + 11):
    wt.column_dimensions[L(j)].width = 11
wt.column_dimensions["K"].width = 26
wt.column_dimensions["L"].width = 34
wt.column_dimensions[L(c0 + 2)].width = 26
wt.row_dimensions[4].height = 30
wt.freeze_panes = "A5"

# ---------------------------------------------------------------- Dados
for j, c in enumerate(COLS + AUX, 1):
    cell = wd.cell(1, j, c)
    cell.font = font(bold=True, size=9)
    cell.fill = HFILL if c in COLS else SUBFILL
    cell.border = BOX
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
nd = len(DATAS)
for i, row in enumerate(dados.itertuples(index=False), 2):
    for j, v in enumerate(row, 1):
        if pd.isna(v):
            continue
        if isinstance(v, pd.Timestamp):
            v = v.date()
        wd.cell(i, j, v)
        if j == 1 or COLS[j - 1] in ("DATA da IA", "DtÚltParto"):
            wd.cell(i, j).number_format = "DD/MM/YYYY"
    x = {k: f"{C[k]}{i}" for k in C}          # esta linha
    a = {k: f"{C[k]}{i - 1}" for k in C}      # linha de cima (mesmo animal, dia anterior?)
    b = {k: f"{C[k]}{i + 1}" for k in C}      # linha de baixo (mesmo animal, dia seguinte?)
    ontem = f'AND({a["Brinco"]}={x["Brinco"]},{a["DiaNº"]}={x["DiaNº"]}-1)' if i > 2 else "FALSE"
    amanha = f'AND({b["Brinco"]}={x["Brinco"]},{b["DiaNº"]}={x["DiaNº"]}+1)'
    lt, lac = x["Lote"], x["LACT"]
    h = x["StatRepro"]
    f = {
        "Fêmea": f'=IF({h}="Male",0,1)',
        "DNB": f'=IF(OR({h}="DNB",{h}="Dry DNB"),1,0)',
        "Dias desde IA": f'=IF(ISNUMBER({x["DATA da IA"]}),{x["Data"]}-{x["DATA da IA"]},"")',
        # parto depois do relatório anterior e até o dia do relatório (sem anterior: só o próprio dia)
        "Pariu no período": (f'=IF(AND({lac}>0,ISNUMBER({x["DtÚltParto"]})),IF(AND({x["DtÚltParto"]}<={x["Data"]},'
                             f'{x["DtÚltParto"]}>IF({x["DiaNº"]}=1,{x["Data"]}-1,INDEX(DATAS,{x["DiaNº"]}-1))),1,0),"")'),
        "DiaNº": f"=MATCH({x['Data']},DATAS,0)",
        "Lactação": f"=IF(AND({lac}>0,OR(AND({lt}>=1,{lt}<=6),{lt}=10)),1,0)",
        "Lote10": f"=IF(AND({lac}>0,{lt}=10),1,0)",
        "Lactação ant.": f'=IF({ontem},{a["Lactação"]},"")',
        "Lote10 ant.": f'=IF({ontem},{a["Lote10"]},"")',
        "Iniciou lactação": f'=IF({x["DiaNº"]}=1,"",IF(AND({x["Lactação"]}=1,{x["Lactação ant."]}<>1),1,0))',
        "Entrou lote 10": f'=IF({x["DiaNº"]}=1,"",IF(AND({x["Lote10"]}=1,{x["Lote10 ant."]}<>1),1,0))',
        "Saída adulto em": f'=IF(AND({lac}>0,{x["DiaNº"]}<{nd},NOT({amanha})),'
                           f'INDEX(DATAS,{x["DiaNº"]}+1),"")',
        "Saída lote 10 em": f'=IF(AND({x["Lote10"]}=1,{x["DiaNº"]}<{nd}),'
                            f'IF({amanha},IF({b["Lote10"]}=1,"",INDEX(DATAS,{x["DiaNº"]}+1)),'
                            f'INDEX(DATAS,{x["DiaNº"]}+1)),"")',
    }
    for k, v in f.items():
        c = wd.cell(i, COLS.__len__() + AUX.index(k) + 1, v)
        if k.endswith(" em") or k == "Data":
            c.number_format = "DD/MM/YYYY"
    wd.cell(i, 1).number_format = "DD/MM/YYYY"
wd.freeze_panes = "B2"
wd.auto_filter.ref = f"A1:{C[AUX[-1]]}{NR}"
wd.column_dimensions["A"].width = 11
for k in AUX:
    wd.column_dimensions[C[k]].width = 12

# ---------------------------------------------------------------- Indicadores
ADULTO = ("LACT", ">0")
JOVEM = ("LACT", 0)
LAC = ("Lactação", 1)


def crit(conds, d):
    parts = [f"{R('Data')},{d}", f"{R('Fêmea')},1"]  # machos fora de todos os números
    for campo, v in conds:
        parts.append(f'{R(campo)},"{v}"' if isinstance(v, str) else f"{R(campo)},{v}")
    return ",".join(parts)


def cont(*conds):
    return lambda d: f"COUNTIFS({crit(conds, d)})"


def media(campo, *conds):
    return lambda d: f'IFERROR(AVERAGEIFS({R(campo)},{crit(conds, d)}),"")'


def menos(f1, f2):
    return lambda d: f"({f1(d)}-{f2(d)})"


def partos(d):
    """Partos pela DtÚltParto do relatório MAIS RECENTE (pega lançamentos atrasados), contados no dia
    do parto: depois do relatório anterior e até o dia. Sem a coluna no dia: comparação com o dia anterior."""
    ult = "MAX(DATAS)"
    ant = f"IF(MATCH({d},DATAS,0)=1,{d}-1,INDEX(DATAS,MATCH({d},DATAS,0)-1))"
    novo = (f'COUNTIFS({R("Data")},{ult},{R("Fêmea")},1,{R("LACT")},">0",'
            f'{R("DtÚltParto")},">"&{ant},{R("DtÚltParto")},"<="&{d})')
    antigo = comparado(cont(("Iniciou lactação", 1)))(d)
    return f'IF(COUNTIFS({R("Data")},{d},{R("DtÚltParto")},">0")>0,{novo},{antigo})'


def com_ia(f1):
    """Só existe nos dias em que o relatório traz a coluna DATA da IA."""
    return lambda d: f'IF(COUNTIFS({R("Data")},{d},{R("Dias desde IA")},">-100000")=0,"",{f1(d)})'


def comparado(f1):
    """Só existe com o relatório do dia anterior na aba Dados."""
    return lambda d: f'IF(MATCH({d},DATAS,0)=1,"",{f1(d)})'


def vendido_dia(d):
    return None  # marcador: valor de entrada, vem de dados/leite_vendido.json


def tanque(nome):
    """Última análise do tanque com data de coleta ≤ dia (repete até chegar outra)."""
    return lambda d: f'IFERROR(INDEX({nome},MATCH({d},TQ_DATA,1)),"")'


def data_tanque(d):
    return f'IFERROR(INDEX(TQ_DATA,MATCH({d},TQ_DATA,1)),"")'


data_tanque.sem_media = True


def dif_vendido(d):
    return None  # marcador: (DairyPlan − vendido) ÷ vendido, das duas linhas de cima


def soma(campo, *conds):
    return lambda d: f"SUMIFS({R(campo)},{crit(conds, d)})"


def razao(num, den):
    return lambda d: f'IFERROR({num(d)}/{den(d)},"")'


def media_dp(*conds):
    """Média e desvio padrão amostral do Leite na mesma célula: "43,6 (10,1)".
    DP sem fórmula matricial: √((Σx² − (Σx)²/n)/(n − 1)). FIXED usa o separador decimal do Excel."""
    def f(d):
        m = [f"({R('Data')}={d})", f"({R('Fêmea')}=1)"] + [f"({R(c)}{v if isinstance(v, str) else '=' + str(v)})"
                                      for c, v in conds]
        n = f"SUMPRODUCT({'*'.join(m)})"
        s1 = f"SUMPRODUCT({'*'.join(m)},{R('Leite')})"
        sq = f"SUMPRODUCT({'*'.join(m)},{R('Leite')},{R('Leite')})"
        dp = f"SQRT(MAX(0,({sq}-{s1}^2/{n})/({n}-1)))"
        return (f'IF({n}=0,"",IF({n}<2,FIXED({s1}/{n},1,TRUE),'
                f'FIXED({s1}/{n},1,TRUE)&" ("&FIXED({dp},1,TRUE)&")"))')
    f.media = media("Leite", *conds)  # para a coluna de variação
    f.raw = lambda d: f"AVERAGEIFS({R('Leite')},{crit(conds, d)})"  # para a média dos dias
    return f


N0, N1, N2, P = "0", "0.0", "0.00", "0.0%"
TANQUE = [LAC, ("Lote", "<=6")]
COM_LEITE = [*TANQUE, ("Leite", ">0")]
DESCARTE = [LAC, ("Lote", 10), ("Leite", ">0")]
# Reprodução: DNB fica fora de todos os indicadores (exceto a contagem de DNB).
REPRO = ("DNB", 0)
ent10 = cont(("Entrou lote 10", 1))
sai10 = lambda d: f"COUNTIFS({R('Saída lote 10 em')},{d})"
ng150 = menos(cont(LAC, REPRO, ("DEL", ">\"&P_DEL_NG&\"")),
              cont(LAC, REPRO, ("DEL", ">\"&P_DEL_NG&\""), ("DDP", ">=1")))
PROD24 = media_dp(("Lactação", 1), ("Leite", ">0"))
ecm = lambda d: (f'IFERROR({PROD24.raw(d)}*(P_ECM_BASE+P_ECM_GORD*INDEX(TQ_GORD,MATCH({d},TQ_DATA,1))'
                 f'+P_ECM_PROT*INDEX(TQ_PROT,MATCH({d},TQ_DATA,1))),"")')
def IA35(status, grupo):
    return cont(grupo, REPRO, ("StatRepro", status), ("Dias desde IA", ">\"&P_DIAS_IA&\""))


# Cada item: (rótulo, unidade, fórmula, formato, melhor). melhor: "↑" bom quando sobe, "↓" bom quando
# desce, "0" bom quando se aproxima de zero, "" sem sentido definido. ("§", título) abre um bloco.
SUB = "§"
GRUPOS = [
    ("Animais adultos (fêmeas, LACT > 0)", [
        (SUB, "Rebanho e movimentação"),
        ("Vacas adultas", "cab", cont(ADULTO), N0, ""),
        ("Vacas em lactação (lotes 1 a 6 e 10)", "cab", cont(LAC), N0, ""),
        ("   Em lactação no tanque (lotes 1 a 6)", "cab", cont(*TANQUE), N0, "↑"),
        ("   Animais em tratamento (lote 10)", "cab", cont(ADULTO, ("Lote", 10)), N0, "↓"),
        ("Vacas secas (adultas fora da lactação)", "cab", cont(ADULTO, ("Lactação", 0)), N0, ""),
        ("Vacas paridas há até 21 dias (DEL ≤ 21)", "cab", cont(LAC, ("DEL", "<=21")), N0, ""),
        ("Vacas que começaram a lactação (partos)", "cab", partos, N0, ""),
        ("Saída de animais adultos", "cab",
         comparado(lambda d: f"COUNTIFS({R('Saída adulto em')},{d})"), N0, ""),
        ("   Lote 10 – entradas", "cab", comparado(ent10), N0, "↓"),
        ("   Lote 10 – saídas", "cab", comparado(sai10), N0, ""),
        ("   Lote 10 – saldo (entradas − saídas)", "cab", comparado(menos(ent10, sai10)), N0, "↓"),
        ("DEL médio da lactação", "dias", media("DEL", LAC), N0, ""),
        ("DEL médio (lotes 1 a 6)", "dias", media("DEL", *TANQUE), N0, ""),
        (SUB, "Produção por vaca"),
        ("Produção média nas últimas 24 h (DP)", "kg/vaca", PROD24, N1, "↑"),
        ("Média de leite ECM (gordura e proteína do tanque)", "kg/vaca", ecm, N1, "↑"),
        *[(f"   Produção média do lote {lt} (DP)", "kg/vaca",
           media_dp(("LACT", ">0"), ("Lote", lt), ("Leite", ">0")), N1, "↑") for lt in range(1, 7)],
        ("Média de leite por vaca (tanque)", "kg/vaca", media("Leite", *COM_LEITE), N1, "↑"),
        ("Média primíparas (LACT 1, tanque)", "kg/vaca", media("Leite", *COM_LEITE, ("LACT", 1)), N1, "↑"),
        ("Média multíparas (LACT ≥ 2, tanque)", "kg/vaca",
         media("Leite", *COM_LEITE, ("LACT", ">=2")), N1, "↑"),
        ("Vacas com leite < 20 kg (tanque)", "cab", cont(*COM_LEITE, ("Leite", "<20")), N0, "↓"),
        ("Vacas com pesagem de leite (tanque)", "cab", cont(*COM_LEITE), N0, ""),
        ("% vacas com leitura de leite (tanque)", "%", razao(cont(*COM_LEITE), cont(*TANQUE)), P, "↑"),
        (SUB, "Leite produzido e entregue"),
        ("Leite Total dia DairyPlan", "kg", soma("Leite", *COM_LEITE), "#,##0", "↑"),
        ("Leite comercializado no dia (coletas do laticínio)", "kg", vendido_dia, "#,##0", "↑"),
        ("Diferença DairyPlan × comercializado", "%", dif_vendido, "+0.0%;-0.0%;0.0%", "0"),
        ("Leite descartado – lote 10", "kg", soma("Leite", *DESCARTE), "#,##0", "↓"),
        ("% do leite produzido que foi descartado", "%",
         razao(soma("Leite", *DESCARTE),
               lambda d: f"({soma('Leite', *COM_LEITE)(d)}+{soma('Leite', *DESCARTE)(d)})"), P, "↓"),
        (SUB, "Qualidade do leite do tanque (laticínio)"),
        ("Análise do tanque vigente desde", "data", data_tanque, "DD/MM/YYYY", ""),
        ("Gordura – análise do tanque", "%", tanque("TQ_GORD"), N2, "↑"),
        ("Proteína – análise do tanque", "%", tanque("TQ_PROT"), N2, "↑"),
        ("Lactose – análise do tanque", "%", tanque("TQ_LACT"), N2, "↑"),
        ("Sólidos totais – análise do tanque", "%", tanque("TQ_ST"), N2, "↑"),
        ("CCS – análise do tanque", "mil/mL", tanque("TQ_CCS"), N0, "↓"),
        ("CPP (CBT) – análise do tanque", "mil UFC", tanque("TQ_CPP"), N0, "↓"),
        ("Ureia – análise do tanque", "mg/dL", tanque("TQ_UREIA"), N1, ""),
        (SUB, "Reprodução"),
        ("Vacas gestantes (DDP ≥ 1, sem DNB)", "cab", cont(ADULTO, REPRO, ("DDP", ">=1")), N0, "↑"),
        ("% gestantes ÷ (adultas − DNB)", "%",
         razao(cont(ADULTO, REPRO, ("DDP", ">=1")), cont(ADULTO, REPRO)), P, "↑"),
        ("DEL > 150 não gestantes (sem DNB)", "cab", ng150, N0, "↓"),
        ("% DEL > 150 não gestantes ÷ em lactação", "%", razao(ng150, cont(LAC)), P, "↓"),
        ("Vacas a descartar (DNB)", "cab", cont(ADULTO, ("DNB", 1)), N0, "↓"),
        ("DEL > 70 sem IA (NumIAs = 0, sem DNB)", "cab",
         cont(LAC, REPRO, ("DEL", ">\"&P_DEL_SEM_IA&\""), ("NumIAs", 0)), N0, "↓"),
        ("Inseminadas (Bred) com IA há > 35 dias", "cab",
         com_ia(lambda d: f'({IA35("Bred", ADULTO)(d)}+{IA35("Dry Bred", ADULTO)(d)})'), N0, "↓"),
        ("Vazias com IA há > 35 dias", "cab", com_ia(IA35("Vazia", ADULTO)), N0, "↓"),
    ]),
    ("Animais jovens (fêmeas, LACT = 0)", [
        ("Animais jovens totais", "cab", cont(JOVEM), N0, ""),
        ("Animais com < 3 meses", "cab", cont(JOVEM, ("IdadeDias", "<\"&P_IDADE_3M&\"")), N0, ""),
        ("Nascidas há até 7 dias", "cab", cont(JOVEM, ("IdadeDias", "<=7")), N0, ""),
        ("Novilhas gestantes (DDP ≥ 1, sem DNB)", "cab", cont(JOVEM, REPRO, ("DDP", ">=1")), N0, "↑"),
        ("Novilhas > 15 meses não gestantes", "cab",
         menos(cont(JOVEM, REPRO, ("IdadeDias", ">\"&P_IDADE_15M&\"")),
               cont(JOVEM, REPRO, ("IdadeDias", ">\"&P_IDADE_15M&\""), ("DDP", ">=1"))), N0, "↓"),
        ("Novilhas inseminadas (Bred) com IA há > 35 dias", "cab", com_ia(IA35("Bred", JOVEM)), N0, "↓"),
        ("Novilhas vazias com IA há > 35 dias", "cab", com_ia(IA35("Vazia", JOVEM)), N0, "↓"),
    ]),
]

C0 = 4                                 # primeira coluna de dia (A rótulo, B unidade, C melhor)
DC = [L(C0 + k) for k in range(ND)]    # colunas dos dias
MC = L(C0 + ND)                        # média dos dias exibidos
VC = L(C0 + 1 + ND)                    # variação último − anterior
LAST = C0 + 1 + ND
VERDE, VERMELHO, CINZA = "0B7A0B", "B42D2D", "6B6B66"
def clarear_hex(h, f=0.80):
    """Tom claro de uma cor hexadecimal (mistura com branco)."""
    return "".join(f"{round(int(h[k:k + 2], 16) + (255 - int(h[k:k + 2], 16)) * f):02X}" for k in (0, 2, 4))


# cor de identidade de cada lote (definida pela fazenda)
COR_LOTE = {"1": "EDA100", "2": "2A78D6", "3": "E34948", "4": "008300", "5": "6250D6", "6": "EB6834"}
SUBFILL2 = PatternFill("solid", fgColor="ECEEEF")

ws["A1"] = "ARCAFLA – Monitoramento diário do rebanho"
ws["A1"].font = font(bold=True, size=14, color=AZUL)
ws["A2"] = (f"Relatório zootécnico diário · {ND} dias mais recentes "
            f"({DIAS[0]:%d/%m/%Y} a {DIAS[-1]:%d/%m/%Y}) · "
            "Melhor: ↑ bom quando sobe, ↓ bom quando desce, 0 bom perto de zero · "
            "variação verde = melhorou, vermelha = piorou · definições na aba Notas")
ws["A2"].font = font(italic=True, size=9, color="5E6B63")

HR = 4
for j, t in enumerate(["Indicador", "Unidade", "Melhor"] + [None] * ND
                      + ["Média\n10 dias", "Variação\n(último − anterior)"], 1):
    c = ws.cell(HR, j, t)
    c.font = font(bold=True, size=9)
    c.fill = HFILL
    c.border = BOX
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
for k, d in enumerate(DIAS):
    ws.cell(HR, C0 + k, d).number_format = "DD/MM/YYYY"  # data do relatório
ws.row_dimensions[HR].height = 30

r = HR + 1
for grupo, itens in GRUPOS:
    ws.cell(r, 1, grupo).font = font(bold=True, color="FFFFFF")
    for j in range(1, LAST + 1):
        ws.cell(r, j).fill = SECFILL
    r += 1
    n = 0
    for item in itens:
        if item[0] == SUB:  # faixa de bloco
            ws.cell(r, 1, item[1]).font = font(bold=True, color=AZUL)
            for j in range(1, LAST + 1):
                ws.cell(r, j).fill = SUBFILL2
            r += 1
            n = 0
            continue
        rotulo, un, f, fmt, melhor = item
        ws.cell(r, 1, rotulo).font = font()
        m_lote = re.search(r"Produção média do lote (\d)", rotulo)
        if m_lote and m_lote[1] in COR_LOTE:  # cor de identidade do lote (barra à esquerda + negrito)
            ws.cell(r, 1).font = font(bold=True)
            ws.cell(r, 1).border = Border(left=Side(style="thick", color=COR_LOTE[m_lote[1]]),
                                          top=thin, bottom=thin, right=thin)
        ws.cell(r, 2, un).font = font(size=9, color="5E6B63")
        ws.cell(r, 2).alignment = Alignment(horizontal="center")
        ws.cell(r, 3, melhor or None).font = font(bold=True, color=AZUL)
        ws.cell(r, 3).alignment = Alignment(horizontal="center")
        for k, col in enumerate(DC):
            if f is vendido_dia:
                litros = vendido.get(DIAS[k].isoformat())  # litros do laticínio, convertidos para kg
                c = ws.cell(r, C0 + k, f"={litros}*P_DENSIDADE" if litros is not None else None)
                c.fill = INFILL
                c.font = font(color="0000FF")
            elif f is dif_vendido:  # linhas de cima: DairyPlan (r − 2) e vendido (r − 1)
                dp, vd = f"{col}{r - 2}", f"{col}{r - 1}"
                c = ws.cell(r, C0 + k, f'=IF(OR({dp}="",{vd}="",{vd}=0),"",({dp}-{vd})/{vd})')
                c.font = font()
            else:
                c = ws.cell(r, C0 + k, "=" + f(f"{col}${HR}"))
                c.font = font()
                if hasattr(f, "media"):
                    c.alignment = Alignment(horizontal="right")
            c.number_format = fmt
        sem_media = getattr(f, "sem_media", False)  # ex.: linha de data
        if sem_media:
            c = ws.cell(r, LAST - 1)
        elif hasattr(f, "media"):  # média das médias diárias (sem o DP), só dias com valor
            raw = [f.raw(f"{col}${HR}") for col in DC]
            num = "+".join(f"IFERROR({x},0)" for x in raw)
            den = "+".join(f"IF(ISERROR({x}),0,1)" for x in raw)
            c = ws.cell(r, LAST - 1, f'=IF(({den})=0,"",({num})/({den}))')
        else:
            c = ws.cell(r, LAST - 1, f'=IFERROR(AVERAGE({DC[0]}{r}:{DC[-1]}{r}),"")')
        c.number_format = fmt
        c.font = font(bold=True)
        if ND >= 2 and not sem_media:
            if hasattr(f, "media"):  # célula com texto "média (DP)": variação da média
                a, b = f.media(f"{DC[-1]}${HR}"), f.media(f"{DC[-2]}${HR}")
            else:
                a, b = f"{DC[-1]}{r}", f"{DC[-2]}{r}"
            # variação arredondada às casas exibidas: o que aparece como "0" não ganha cor de melhorou/piorou
            base = fmt.split(";")[0]
            casas = (len(base.split(".")[1].rstrip("%")) if "." in base else 0) + (2 if "%" in base else 0)
            if melhor == "0":  # bom quando se aproxima de zero: variação do valor absoluto
                c = ws.cell(r, LAST, f'=IF(OR({a}="",{b}=""),"",ROUND(ABS({a})-ABS({b}),{casas}))')
            else:
                c = ws.cell(r, LAST, f'=IF(OR({a}="",{b}=""),"",ROUND({a}-{b},{casas}))')
            c.number_format = fmt if fmt.startswith("+") else "+" + fmt + ";-" + fmt + ";0"
            c.font = font(bold=True)
        for j in range(1, LAST + 1):
            if not (j == 1 and m_lote and m_lote[1] in COR_LOTE):
                ws.cell(r, j).border = BOX
            if m_lote and m_lote[1] in COR_LOTE and j < LAST:  # linha do lote no tom claro da sua cor
                ws.cell(r, j).fill = PatternFill("solid", fgColor=clarear_hex(COR_LOTE[m_lote[1]]))
            elif n % 2 and f is not vendido_dia:
                ws.cell(r, j).fill = ZEBRA
        if not (m_lote and m_lote[1] in COR_LOTE):
            ws.cell(r, LAST - 1).fill = PatternFill("solid", fgColor="EEF3F7")
        r += 1
        n += 1

# variação colorida pelo sentido desejado (coluna C): verde melhorou, vermelho piorou
rng = f"{VC}{HR + 1}:{VC}{r - 1}"
v1 = f"{VC}{HR + 1}"
bom = f'AND(ISNUMBER({v1}),OR(AND($C{HR + 1}="↑",{v1}>0),AND($C{HR + 1}="↓",{v1}<0),AND($C{HR + 1}="0",{v1}<0)))'
ruim = f'AND(ISNUMBER({v1}),OR(AND($C{HR + 1}="↑",{v1}<0),AND($C{HR + 1}="↓",{v1}>0),AND($C{HR + 1}="0",{v1}>0)))'
ws.conditional_formatting.add(rng, FormulaRule(formula=[bom], font=Font(name=F, bold=True, color=VERDE),
                                               fill=PatternFill("solid", fgColor="E3F4E3")))
ws.conditional_formatting.add(rng, FormulaRule(formula=[ruim], font=Font(name=F, bold=True, color=VERMELHO),
                                               fill=PatternFill("solid", fgColor="FBE6E6")))
ws.column_dimensions["A"].width = 52
ws.column_dimensions["B"].width = 9
ws.column_dimensions["C"].width = 8
for col in DC:
    ws.column_dimensions[col].width = 11.5
ws.column_dimensions[MC].width = 11
ws.column_dimensions[VC].width = 14
ws.freeze_panes = f"D{HR + 1}"
ws.sheet_view.showGridLines = False
ws.page_setup.orientation = "landscape"
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.print_title_rows = f"{HR}:{HR}"

# ---------------------------------------------------------------- Notas
notas = [
    ("Fonte", "Relatório zootécnico diário (\"Zootécnico Jorge atualizado DD-MM-AAAA.xlsx\"), "
              "um arquivo por dia. A data de cada coluna é a data escrita no nome do arquivo."),
    ("Dias exibidos", f"Os {NDIAS} relatórios mais recentes guardados em {PASTA}. Ao entrar um dia "
                      "novo, o mais antigo sai da tabela (o arquivo continua guardado). A aba Dados "
                      "traz também o dia anterior ao primeiro exibido, para as comparações."),
    ("Atualização", "python3 scripts/monitor_diario.py <novo_relatorio.xlsx> — guarda o relatório "
                    "como Zootecnico_AAAA-MM-DD.xlsx e refaz esta planilha. Um relatório novo da "
                    "mesma data substitui o anterior."),
    ("Machos", "Fora de todos os números (StatRepro = Male). Tudo é calculado só sobre fêmeas."),
    ("Adultos / jovens", "Adultas: LACT > 0. Jovens: LACT = 0."),
    ("Lotes 20 e 30", "Desde 19/10/2026, o lote 20 é contado como lote 2 e o lote 30 como lote 3 (troca feita na "
                      "carga dos dados; a aba Dados já mostra 2 e 3)."),
    ("Vacas em lactação", "Adultas (LACT > 0) nos lotes 1, 2, 3, 4, 5, 6 e 10. O lote 10 são vacas "
                          "em tratamento com leite descartado."),
    ("DEL médio", "Média de DEL das vacas em lactação."),
    ("Produção 24 h", "Média da coluna Leite das vacas em lactação com Leite > 0 (lotes 1 a 6 e 10). "
                      "Por lote: adultas do lote com Leite > 0."),
    ("Análises do tanque", "Aba própria. Valores transcritos das mensagens do laticínio (Ref. coleta = data "
                           "da coleta e tanque). As análises de uma mesma mensagem formam um grupo, tratado "
                           "como uma só coleta: média geral ponderada pelo volume de cada tanque "
                           "(Demonstrativo das Coletas; sem volume, média simples), válida a partir da "
                           "primeira data de coleta do grupo e repetida até chegar um grupo novo. Gordura e proteína do tanque substituem as médias do DairyPlan."),
    ("Leite ECM", "Produção média nas últimas 24 h × (0,327 + 0,1295 × gordura % + 0,0765 × proteína %), "
                  "com gordura e proteína da análise do tanque (Sjaunja et al., 1990; fatores na aba "
                  "Parâmetros)."),
    ("Leite comercializado", "Em kg: litros lidos de dados/leite_vendido.json × densidade (aba Parâmetros, "
                      "1,032 kg/L). Vem do \"Demonstrativo das Coletas de Leite\" (scripts/le_leite_vendido.py): "
                      "soma do Volume de todas as coletas com a mesma Data Coleta."),
    ("Diferença DairyPlan × comercializado", "(Leite Total dia DairyPlan − leite comercializado) ÷ leite comercializado. "
                                      "Negativo = DairyPlan abaixo do comercializado. Os dois em kg (o "
                                      "comercializado é convertido de litros pela densidade)."),
    ("DNB", "StatRepro = DNB ou Dry DNB. Ficam fora de todos os indicadores de reprodução "
            "(só aparecem na própria contagem de DNB)."),
    ("Gestantes", "DDP (dias de prenhez) ≥ 1, sem DNB; inclui secas. % = gestantes ÷ (adultas − DNB)."),
    ("DEL > 150 não gestantes", "Vacas em lactação, sem DNB, com DEL acima do parâmetro e DDP vazio. "
                                "% = esse número ÷ todas as vacas em lactação."),
    ("IA há > 35 dias", "Dias desde IA = data do relatório − DATA da IA (última inseminação, coluna "
                        "do relatório desde 14/10/2026). Inseminadas: StatRepro Bred (adultas também Dry "
                        "Bred); vazias: StatRepro Vazia; sem DNB. Dias sem a coluna ficam vazios."),
    ("DEL > 70 sem IA", "Vacas em lactação, sem DNB, com DEL acima do parâmetro e NumIAs = 0."),
    ("Começaram a lactação", "Partos: adultas do relatório mais recente com DtÚltParto depois da data do "
                             "relatório anterior e até a data do dia (sem relatório anterior na aba Dados: "
                             "parto no próprio dia). Usar o relatório mais recente faz partos lançados com "
                             "atraso entrarem no dia certo. Relatórios sem a coluna DtÚltParto (antes de 15/10/2026): vacas em "
                             "lactação no dia que não estavam em lactação no dia anterior, por brinco."),
    ("Saída de adultos", "Adultos que estavam no relatório do dia anterior e não estão no do dia."),
    ("Lote 10", "Entradas: adultas no lote 10 no dia que não estavam no lote 10 no dia anterior. "
                "Saídas: estavam no lote 10 no dia anterior e no dia estão em outro lote ou saíram "
                "do relatório. Saldo = entradas − saídas."),
    ("Comparações", "\"Dia anterior\" é o relatório anterior guardado. Sem ele, a célula fica vazia. "
                    "Se faltar um dia, a comparação é com o último relatório que existe."),
    ("Média (DP)", "Linhas de produção média: a célula traz a média e, entre parênteses, o desvio "
                   "padrão amostral (n − 1) do Leite. A variação compara só as médias."),
    ("Tanque", "Leite do tanque = lotes 1 a 6; o lote 10 aparece como leite descartado. "
               "Secas = adultas fora dos lotes 1 a 6 e 10."),
    ("Jovens < 3 meses", "IdadeDias abaixo do parâmetro (90 dias)."),
    ("Novilhas", "Em reprodução = jovens que não são Youngstock. Atrasadas: sem DNB, IdadeDias acima "
                 "do parâmetro (456 dias ≈ 15 meses) e DDP vazio."),
    ("Média 10 dias", "Média de cada indicador nos dias exibidos (até 10), ignorando dias sem valor. "
                      "Nas linhas média (DP): média das médias diárias."),
    ("% leitura de leite", "Vacas do tanque (lotes 1 a 6) com Leite > 0 ÷ vacas em lactação nos lotes 1 a 6."),
    ("Leite Total dia DairyPlan", "Soma da coluna Leite das vacas dos lotes 1 a 6 no relatório do DairyPlan."),
    ("Como ler", "Coluna Melhor: ↑ = bom quando sobe; ↓ = bom quando desce; 0 = bom quando se aproxima de "
                 "zero (diferença DairyPlan × comercializado); vazio = sem sentido definido (ex.: partos)."),
    ("Variação", "Último dia menos o dia anterior exibido. Fica verde quando melhorou e vermelha quando "
                 "piorou, de acordo com a coluna Melhor; sem cor quando não há sentido definido. Na diferença "
                 "DairyPlan × comercializado a variação é da distância até zero."),
]
wn["A1"] = "Notas e definições"
wn["A1"].font = font(bold=True, size=14, color=AZUL)
for i, (k, v) in enumerate(notas, 3):
    wn.cell(i, 1, k).font = font(bold=True)
    wn.cell(i, 1).alignment = Alignment(vertical="top")
    c = wn.cell(i, 2, v)
    c.font = font()
    c.alignment = Alignment(wrap_text=True, vertical="top")
wn.column_dimensions["A"].width = 24
wn.column_dimensions["B"].width = 100

os.makedirs(os.path.dirname(OUT), exist_ok=True)
wb.save(OUT)
print(f"{OUT}: {ND} dia(s) exibidos, {len(DATAS)} em Dados, {len(dados)} linhas")
