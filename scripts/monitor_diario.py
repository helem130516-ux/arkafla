"""Planilha de monitoramento diário da ARKAFLA a partir do relatório zootécnico
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
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName

PASTA = "dados/zootecnico"
VENDIDO = "dados/leite_vendido.json"
OUT = "monitoramento/Monitoramento_Diario_ARKAFLA.xlsx"
NDIAS = 10
F = "Arial"
AZUL = "1F5F8B"

thin = Side(style="thin", color="C9D1CB")
BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
HFILL = PatternFill("solid", fgColor="E6ECE8")
INFILL = PatternFill("solid", fgColor="FFF6D6")
SECFILL = PatternFill("solid", fgColor=AZUL)
SUBFILL = PatternFill("solid", fgColor="D5E3EC")
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

frames = []
for d, p in zip(DATAS, arquivos):
    df = pd.read_excel(p)
    df.columns = df.columns.str.strip()
    df.insert(0, "Data", pd.Timestamp(d))
    frames.append(df)
# Ordenado por brinco e data: a linha de cima é o mesmo animal no relatório anterior.
dados = pd.concat(frames, ignore_index=True).sort_values(["Brinco", "Data"], kind="stable")
COLS = list(dados.columns)
NR = len(dados) + 1  # última linha da aba Dados

AUX = ["DiaNº", "Lactação", "Lote10", "Lactação ant.", "Lote10 ant.",
       "Iniciou lactação", "Entrou lote 10", "Saída adulto em", "Saída lote 10 em"]
C = {c: L(i + 1) for i, c in enumerate(COLS + AUX)}


def R(campo):
    return f"Dados!${C[campo]}$2:${C[campo]}${NR}"


wb = Workbook()
wb._named_styles["Normal"].font = Font(name=F, size=10)
ws = wb.active
ws.title = "Monitoramento"
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
    ("P_IDADE_3M", "Animais jovens ≥ 3 meses: idade mínima (dias)", 90),
    ("P_IDADE_15M", "Novilhas atrasadas: idade acima de (dias) – 15 meses", 456),
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
        if j == 1:
            v = v.date()
        wd.cell(i, j, v)
    x = {k: f"{C[k]}{i}" for k in C}          # esta linha
    a = {k: f"{C[k]}{i - 1}" for k in C}      # linha de cima (mesmo animal, dia anterior?)
    b = {k: f"{C[k]}{i + 1}" for k in C}      # linha de baixo (mesmo animal, dia seguinte?)
    ontem = f'AND({a["Brinco"]}={x["Brinco"]},{a["DiaNº"]}={x["DiaNº"]}-1)' if i > 2 else "FALSE"
    amanha = f'AND({b["Brinco"]}={x["Brinco"]},{b["DiaNº"]}={x["DiaNº"]}+1)'
    lt, lac = x["Lote"], x["LACT"]
    f = {
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
    parts = [f"{R('Data')},{d}"]
    for campo, v in conds:
        parts.append(f'{R(campo)},"{v}"' if isinstance(v, str) else f"{R(campo)},{v}")
    return ",".join(parts)


def cont(*conds):
    return lambda d: f"COUNTIFS({crit(conds, d)})"


def media(campo, *conds):
    return lambda d: f'IFERROR(AVERAGEIFS({R(campo)},{crit(conds, d)}),"")'


def menos(f1, f2):
    return lambda d: f"{f1(d)}-{f2(d)}"


def comparado(f1):
    """Só existe com o relatório do dia anterior na aba Dados."""
    return lambda d: f'IF(MATCH({d},DATAS,0)=1,"",{f1(d)})'


def vendido_dia(d):
    return None  # marcador: valor de entrada, vem de dados/leite_vendido.json


def soma(campo, *conds):
    return lambda d: f"SUMIFS({R(campo)},{crit(conds, d)})"


def razao(num, den):
    return lambda d: f'IFERROR({num(d)}/{den(d)},"")'


def media_dp(*conds):
    """Média e desvio padrão amostral do Leite na mesma célula: "43,6 (10,1)".
    DP sem fórmula matricial: √((Σx² − (Σx)²/n)/(n − 1)). FIXED usa o separador decimal do Excel."""
    def f(d):
        m = [f"({R('Data')}={d})"] + [f"({R(c)}{v if isinstance(v, str) else '=' + str(v)})"
                                      for c, v in conds]
        n = f"SUMPRODUCT({'*'.join(m)})"
        s1 = f"SUMPRODUCT({'*'.join(m)},{R('Leite')})"
        sq = f"SUMPRODUCT({'*'.join(m)},{R('Leite')},{R('Leite')})"
        dp = f"SQRT(MAX(0,({sq}-{s1}^2/{n})/({n}-1)))"
        return (f'IF({n}=0,"",IF({n}<2,FIXED({s1}/{n},1,TRUE),'
                f'FIXED({s1}/{n},1,TRUE)&" ("&FIXED({dp},1,TRUE)&")"))')
    f.media = media("Leite", *conds)  # para a coluna de variação
    return f


N0, N1, N2, P = "0", "0.0", "0.00", "0.0%"
TANQUE = [LAC, ("Lote", "<=6")]
COM_LEITE = [*TANQUE, ("Leite", ">0")]
DESCARTE = [LAC, ("Lote", 10), ("Leite", ">0")]
LOTES = sorted(int(x) for x in dados.loc[dados["Data"] >= pd.Timestamp(DIAS[0]), "Lote"].dropna().unique())
dnb = lambda d: f'{cont(ADULTO, ("StatRepro", "DNB"))(d)}+{cont(ADULTO, ("StatRepro", "Dry DNB"))(d)}'
ent10 = cont(("Entrou lote 10", 1))
sai10 = lambda d: f"COUNTIFS({R('Saída lote 10 em')},{d})"
GRUPOS = [
    ("Animais adultos (LACT > 0)", [
        ("Vacas adultas", "cab", cont(ADULTO), N0),
        ("Vacas em lactação (lotes 1 a 6 e 10)", "cab", cont(LAC), N0),
        ("DEL médio da lactação", "dias", media("DEL", LAC), N0),
        ("Produção média nas últimas 24 h (DP)", "kg/vaca",
         media_dp(("Lactação", 1), ("Leite", ">0")), N1),
        *[(f"   Produção média do lote {lt} (DP)", "kg/vaca",
           media_dp(("LACT", ">0"), ("Lote", lt), ("Leite", ">0")), N1) for lt in range(1, 7)],
        ("Animais em tratamento (lote 10)", "cab", cont(ADULTO, ("Lote", 10)), N0),
        ("Leite vendido", "kg", vendido_dia, "#,##0"),
        ("Vacas gestantes totais (DDP ≥ 1)", "cab", cont(ADULTO, ("DDP", ">=1")), N0),
        ("Em lactação com DEL > 150 não gestantes", "cab",
         menos(cont(LAC, ("DEL", ">\"&P_DEL_NG&\"")),
               cont(LAC, ("DEL", ">\"&P_DEL_NG&\""), ("DDP", ">=1"))), N0),
        ("Vacas a descartar (DNB)", "cab", dnb, N0),
        ("Em lactação, DEL > 70 sem IA (NumIAs = 0)", "cab",
         cont(LAC, ("DEL", ">\"&P_DEL_SEM_IA&\""), ("NumIAs", 0)), N0),
        ("Vacas que começaram a lactação", "cab", comparado(cont(("Iniciou lactação", 1))), N0),
        ("Saída de animais adultos", "cab",
         comparado(lambda d: f"COUNTIFS({R('Saída adulto em')},{d})"), N0),
        ("   Lote 10 – entradas", "cab", comparado(ent10), N0),
        ("   Lote 10 – saídas", "cab", comparado(sai10), N0),
        ("   Lote 10 – saldo (entradas − saídas)", "cab", comparado(menos(ent10, sai10)), N0),
    ]),
    ("Animais jovens (LACT = 0)", [
        ("Animais jovens totais", "cab", cont(JOVEM), N0),
        ("Animais com ≥ 3 meses", "cab", cont(JOVEM, ("IdadeDias", ">=\"&P_IDADE_3M&\"")), N0),
        ("Novilhas gestantes (DDP ≥ 1)", "cab", cont(JOVEM, ("DDP", ">=1")), N0),
        ("Novilhas > 15 meses não gestantes", "cab",
         menos(cont(JOVEM, ("StatRepro", "<>Male"), ("IdadeDias", ">\"&P_IDADE_15M&\"")),
               cont(JOVEM, ("StatRepro", "<>Male"), ("IdadeDias", ">\"&P_IDADE_15M&\""),
                    ("DDP", ">=1"))), N0),
    ]),
    ("Complementar – rebanho", [
        ("Total de animais", "cab", cont(), N0),
        ("   Em lactação no tanque (lotes 1 a 6)", "cab", cont(*TANQUE), N0),
        ("Vacas secas (adultas fora da lactação)", "cab", cont(ADULTO, ("Lactação", 0)), N0),
        ("Novilhas em reprodução (sem machos)", "cab",
         cont(JOVEM, ("StatRepro", "<>Male"), ("StatRepro", "<>Youngstock")), N0),
        ("Bezerras / recria (Youngstock)", "cab", cont(JOVEM, ("StatRepro", "Youngstock")), N0),
        ("Machos", "cab", cont(("StatRepro", "Male")), N0),
        ("Animais com até 7 dias de idade", "cab", cont(("IdadeDias", "<=7")), N0),
        ("Vacas paridas há até 21 dias (DEL ≤ 21)", "cab", cont(LAC, ("DEL", "<=21")), N0),
    ]),
    ("Complementar – produção (leite do tanque: lotes 1 a 6, vacas com leite > 0)", [
        ("Vacas com pesagem de leite", "cab", cont(*COM_LEITE), N0),
        ("Leite total do dia", "kg", soma("Leite", *COM_LEITE), "#,##0"),
        ("Leite descartado – lote 10", "kg", soma("Leite", *DESCARTE), "#,##0"),
        ("% do leite produzido que foi descartado", "%",
         razao(soma("Leite", *DESCARTE),
               lambda d: f"({soma('Leite', *COM_LEITE)(d)}+{soma('Leite', *DESCARTE)(d)})"), P),
        ("Média de leite por vaca (tanque)", "kg/vaca", media("Leite", *COM_LEITE), N1),
        ("Média de leite 7 dias (tanque)", "kg/vaca", media("Leite7", *TANQUE, ("Leite7", ">0")), N1),
        ("Média primíparas (LACT 1)", "kg/vaca", media("Leite", *COM_LEITE, ("LACT", 1)), N1),
        ("Média multíparas (LACT ≥ 2)", "kg/vaca", media("Leite", *COM_LEITE, ("LACT", ">=2")), N1),
        ("Vacas com leite < 20 kg", "cab", cont(*COM_LEITE, ("Leite", "<20")), N0),
        ("DEL médio (lotes 1 a 6)", "dias", media("DEL", *TANQUE), N0),
        ("Gordura média", "%", media("%Gord", *TANQUE, ("%Gord", ">0")), N2),
        ("Proteína média", "%", media("Prot%", *TANQUE, ("Prot%", ">0")), N2),
    ]),
    ("Complementar – reprodução das vacas em lactação (lotes 1 a 6 e 10)", [
        ("Frescas (Fresca)", "cab", cont(LAC, ("StatRepro", "Fresca")), N0),
        ("Inseminadas (Bred)", "cab", cont(LAC, ("StatRepro", "Bred")), N0),
        ("Prenhas", "cab", cont(LAC, ("StatRepro", "Prenha")), N0),
        ("Vazias", "cab", cont(LAC, ("StatRepro", "Vazia")), N0),
        ("% prenhes das vacas em lactação", "%",
         razao(cont(LAC, ("StatRepro", "Prenha")), cont(LAC)), P),
        ("DEL médio ao 1º serviço (DEL1S)", "dias", media("DEL1S", LAC, ("DEL1S", ">0")), N0),
        ("Dias em aberto médios das prenhas", "dias",
         media("DiasVazia", LAC, ("StatRepro", "Prenha")), N0),
        ("IAs por prenhez (prenhas)", "IAs", media("NumIAs", LAC, ("StatRepro", "Prenha")), N2),
    ]),
    ("Complementar – reprodução das novilhas", [
        ("Novilhas inseminadas (Bred)", "cab", cont(JOVEM, ("StatRepro", "Bred")), N0),
        ("Novilhas prenhas", "cab", cont(JOVEM, ("StatRepro", "Prenha")), N0),
        ("Novilhas vazias", "cab", cont(JOVEM, ("StatRepro", "Vazia")), N0),
    ]),
    ("Animais por lote", [
        (f"Lote {lt}", "cab", cont(("Lote", lt)), N0) for lt in LOTES
    ]),
]

DC = [L(3 + k) for k in range(ND)]   # colunas dos dias: C, D, ...
VC = L(3 + ND)                        # variação último − anterior
LAST = 3 + ND

ws["A1"] = "ARKAFLA – Monitoramento diário do rebanho"
ws["A1"].font = font(bold=True, size=14, color=AZUL)
ws["A2"] = (f"Relatório zootécnico diário · {ND} dias mais recentes "
            f"({DIAS[0]:%d/%m/%Y} a {DIAS[-1]:%d/%m/%Y}) · definições na aba Notas")
ws["A2"].font = font(italic=True, size=9, color="5E6B63")

HR = 4
for j, t in enumerate(["Indicador", "Unidade"] + [None] * ND + ["Variação\n(último − anterior)"], 1):
    c = ws.cell(HR, j, t)
    c.font = font(bold=True, size=9)
    c.fill = HFILL
    c.border = BOX
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
for k, d in enumerate(DIAS):
    ws.cell(HR, 3 + k, d).number_format = "DD/MM/YYYY"  # data vem do nome do arquivo
ws.row_dimensions[HR].height = 30

r = HR + 1
for grupo, itens in GRUPOS:
    ws.cell(r, 1, grupo).font = font(bold=True, color="FFFFFF")
    for j in range(1, LAST + 1):
        ws.cell(r, j).fill = SECFILL
    r += 1
    for n, (rotulo, un, f, fmt) in enumerate(itens):
        ws.cell(r, 1, rotulo).font = font()
        ws.cell(r, 2, un).font = font(size=9, color="5E6B63")
        ws.cell(r, 2).alignment = Alignment(horizontal="center")
        for k, col in enumerate(DC):
            if f is vendido_dia:
                c = ws.cell(r, 3 + k, vendido.get(DIAS[k].isoformat()))
                c.fill = INFILL
                c.font = font(color="0000FF")
            else:
                c = ws.cell(r, 3 + k, "=" + f(f"{col}${HR}"))
                c.font = font()
                if hasattr(f, "media"):
                    c.alignment = Alignment(horizontal="right")
            c.number_format = fmt
        if ND >= 2:
            if hasattr(f, "media"):  # célula com texto "média (DP)": variação da média
                a, b = f.media(f"{DC[-1]}${HR}"), f.media(f"{DC[-2]}${HR}")
                c = ws.cell(r, LAST, f'=IF(OR({a}="",{b}=""),"",{a}-{b})')
            else:
                a, b = f"{DC[-1]}{r}", f"{DC[-2]}{r}"
                c = ws.cell(r, LAST, f'=IF(OR({a}="",{b}=""),"",{a}-{b})')
            c.number_format = "+" + fmt + ";-" + fmt + ";0"
            c.font = font(bold=True)
        for j in range(1, LAST + 1):
            ws.cell(r, j).border = BOX
            if n % 2 and f is not vendido_dia:
                ws.cell(r, j).fill = ZEBRA
        r += 1

rng = f"{VC}{HR + 1}:{VC}{r - 1}"
ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["0"],
                                              font=Font(name=F, bold=True, color="1E7B45")))
ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"],
                                              font=Font(name=F, bold=True, color="B03A2E")))
ws.column_dimensions["A"].width = 56
ws.column_dimensions["B"].width = 9
for col in DC:
    ws.column_dimensions[col].width = 11.5
ws.column_dimensions[VC].width = 14
ws.freeze_panes = f"C{HR + 1}"
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
    ("Adultos / jovens", "Adultos: LACT > 0. Jovens: LACT = 0 (inclui machos)."),
    ("Vacas em lactação", "Adultas (LACT > 0) nos lotes 1, 2, 3, 4, 5, 6 e 10. O lote 10 são vacas "
                          "em tratamento com leite descartado."),
    ("DEL médio", "Média de DEL das vacas em lactação."),
    ("Produção 24 h", "Média da coluna Leite das vacas em lactação com Leite > 0 (lotes 1 a 6 e 10). "
                      "Por lote: adultas do lote com Leite > 0."),
    ("Leite vendido", "Valor de entrada (azul/amarelo), lido de dados/leite_vendido.json. Será "
                      "preenchido a partir do PDF do laticínio."),
    ("Gestantes", "DDP (dias de prenhez) ≥ 1. Vacas gestantes inclui secas."),
    ("DEL > 150 não gestantes", "Vacas em lactação com DEL acima do parâmetro e DDP vazio."),
    ("DNB", "Adultas com StatRepro = DNB ou Dry DNB."),
    ("DEL > 70 sem IA", "Vacas em lactação com DEL acima do parâmetro e NumIAs = 0."),
    ("Começaram a lactação", "Vacas em lactação no dia que não estavam em lactação (ou não estavam "
                             "no relatório) no dia anterior. Comparação por brinco."),
    ("Saída de adultos", "Adultos que estavam no relatório do dia anterior e não estão no do dia."),
    ("Lote 10", "Entradas: adultas no lote 10 no dia que não estavam no lote 10 no dia anterior. "
                "Saídas: estavam no lote 10 no dia anterior e no dia estão em outro lote ou saíram "
                "do relatório. Saldo = entradas − saídas."),
    ("Comparações", "\"Dia anterior\" é o relatório anterior guardado. Sem ele, a célula fica vazia. "
                    "Se faltar um dia, a comparação é com o último relatório que existe."),
    ("Média (DP)", "Linhas de produção média: a célula traz a média e, entre parênteses, o desvio "
                   "padrão amostral (n − 1) do Leite. A variação compara só as médias."),
    ("Blocos complementares", "Indicadores da primeira versão. Leite do tanque = lotes 1 a 6; o lote 10 "
                              "aparece como leite descartado. Secas = adultas fora dos lotes 1 a 6 e 10. "
                              "Novilhas = jovens sem machos e sem Youngstock."),
    ("Jovens ≥ 3 meses", "IdadeDias ≥ parâmetro (90 dias)."),
    ("Novilhas atrasadas", "LACT = 0, exceto machos, com IdadeDias acima do parâmetro "
                           "(456 dias ≈ 15 meses) e DDP vazio."),
    ("Variação", "Último dia menos o dia anterior exibido. Verde = subiu, vermelho = caiu "
                 "(a cor não indica se é bom ou ruim)."),
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
