"""Planilha de monitoramento diário da ARKAFLA a partir do relatório zootécnico
diário ("Zootécnico Jorge atualizado DD-MM-AAAA.xlsx").

Cada relatório corresponde à data escrita no nome do arquivo. Os relatórios ficam
guardados em dados/zootecnico/Zootecnico_AAAA-MM-DD.xlsx (um por dia; um arquivo
novo da mesma data substitui o anterior). A planilha mostra sempre os 10 dias mais
recentes: cada dia é uma coluna, cada indicador é uma linha.

Uso:
    python3 scripts/monitor_diario.py [novo_relatorio.xlsx ...]
Depois: recalcular com recalc.py (skill xlsx).
"""
import glob
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

PASTA = "dados/zootecnico"
OUT = "monitoramento/Monitoramento_Diario_ARKAFLA.xlsx"
NDIAS = 10
F = "Arial"
AZUL = "1F5F8B"

thin = Side(style="thin", color="C9D1CB")
BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
HFILL = PatternFill("solid", fgColor="E6ECE8")
SECFILL = PatternFill("solid", fgColor=AZUL)
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

arquivos = sorted(glob.glob(os.path.join(PASTA, "Zootecnico_*.xlsx")), key=data_do_nome)
if not arquivos:
    raise SystemExit(f"Nenhum relatório em {PASTA}")
arquivos = arquivos[-NDIAS:]
DIAS = [data_do_nome(p) for p in arquivos]

frames = []
for d, p in zip(DIAS, arquivos):
    df = pd.read_excel(p)
    df.columns = df.columns.str.strip()
    df.insert(0, "Data", pd.Timestamp(d))
    frames.append(df)
dados = pd.concat(frames, ignore_index=True)
COLS = list(dados.columns)
LOTES = sorted(int(x) for x in dados["Lote"].dropna().unique())
NR = len(dados) + 1  # última linha da aba Dados

# Coluna (letra) de cada campo na aba Dados; Categoria vem depois dos campos do relatório.
C = {c: L(i + 1) for i, c in enumerate(COLS)}
C["Categoria"] = L(len(COLS) + 1)
C["Destino"] = L(len(COLS) + 2)
LOTES_LAC = "1 a 6 e 10"


def R(campo):
    return f"Dados!${C[campo]}$2:${C[campo]}${NR}"


wb = Workbook()
wb._named_styles["Normal"].font = Font(name=F, size=10)
ws = wb.active
ws.title = "Monitoramento"
wd = wb.create_sheet("Dados")
wn = wb.create_sheet("Notas")

# ---------------------------------------------------------------- Dados
cat_col = len(COLS) + 1
for j, c in enumerate(COLS + ["Categoria", "Destino"], 1):
    cell = wd.cell(1, j, c)
    cell.font = font(bold=True, size=9)
    cell.fill = HFILL
    cell.border = BOX
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
for i, row in enumerate(dados.itertuples(index=False), 2):
    for j, v in enumerate(row, 1):
        if pd.isna(v):
            continue
        if j == 1:
            v = v.date()
        wd.cell(i, j, v)
    h, lac, lt = f"{C['StatRepro']}{i}", f"{C['LACT']}{i}", f"{C['Lote']}{i}"
    # vacas em lactação = lotes 1 a 6 (leite vai para o tanque) e 10 (tratamento, leite descartado)
    wd.cell(i, cat_col, f'=IF(OR(AND({lt}>=1,{lt}<=6),{lt}=10),"Vaca em lactação",'
                        f'IF({h}="Male","Macho",IF({lac}>=1,"Vaca seca",'
                        f'IF({h}="Youngstock","Bezerra/recria","Novilha"))))')
    wd.cell(i, cat_col + 1, f'=IF(AND({lt}>=1,{lt}<=6),"Tanque",IF({lt}=10,"Descarte",""))')
for i in range(2, NR + 1):
    wd.cell(i, 1).number_format = "DD/MM/YYYY"
wd.freeze_panes = "B2"
wd.auto_filter.ref = f"A1:{L(cat_col + 1)}{NR}"
wd.column_dimensions["A"].width = 11
wd.column_dimensions[L(cat_col)].width = 17
wd.column_dimensions[L(cat_col + 1)].width = 10

# ---------------------------------------------------------------- Indicadores
LAC = ("Categoria", "Vaca em lactação")
TANQUE = ("Destino", "Tanque")
COM_LEITE = [TANQUE, ("Leite", ">0")]
DESCARTE = [("Destino", "Descarte"), ("Leite", ">0")]


def crit(conds, d):
    parts = [f"{R('Data')},{d}"]
    for campo, v in conds:
        parts.append(f'{R(campo)},"{v}"' if isinstance(v, str) else f"{R(campo)},{v}")
    return ",".join(parts)


def cont(*conds):
    return lambda d: f"COUNTIFS({crit(conds, d)})"


def soma(campo, *conds):
    return lambda d: f"SUMIFS({R(campo)},{crit(conds, d)})"


def media(campo, *conds):
    return lambda d: f'IFERROR(AVERAGEIFS({R(campo)},{crit(conds, d)}),"")'


def razao(num, den):
    return lambda d: f'IFERROR({num(d)}/{den(d)},"")'


N0, N1, N2 = "0", "0.0", "0.00"
P = "0.0%"
GRUPOS = [
    ("Rebanho", [
        ("Total de animais", "cab", cont(), N0),
        ("Vacas em lactação (lotes 1 a 6 e 10)", "cab", cont(LAC), N0),
        ("   em produção – leite no tanque (lotes 1 a 6)", "cab", cont(TANQUE), N0),
        ("   em tratamento – leite descartado (lote 10)", "cab", cont(("Destino", "Descarte")), N0),
        ("Vacas secas (LACT ≥ 1 fora dos lotes de lactação)", "cab", cont(("Categoria", "Vaca seca")), N0),
        ("Novilhas (em reprodução)", "cab", cont(("Categoria", "Novilha")), N0),
        ("Bezerras / recria", "cab", cont(("Categoria", "Bezerra/recria")), N0),
        ("Machos", "cab", cont(("Categoria", "Macho")), N0),
        ("Animais com até 7 dias de idade", "cab", cont(("IdadeDias", "<=7")), N0),
        ("Vacas paridas há até 21 dias (DEL ≤ 21)", "cab", cont(LAC, ("DEL", "<=21")), N0),
    ]),
    ("Produção – leite do tanque (lotes 1 a 6, vacas com leite > 0)", [
        ("Vacas com pesagem de leite", "cab", cont(*COM_LEITE), N0),
        ("Leite total do dia", "kg", soma("Leite", *COM_LEITE), "#,##0"),
        ("Leite descartado – lote 10", "kg", soma("Leite", *DESCARTE), "#,##0"),
        ("% do leite produzido que foi descartado", "%",
         razao(soma("Leite", *DESCARTE),
               lambda d: f"({soma('Leite', *COM_LEITE)(d)}+{soma('Leite', *DESCARTE)(d)})"), P),
        ("Média de leite por vaca", "kg/vaca", media("Leite", *COM_LEITE), N1),
        ("Média de leite 7 dias", "kg/vaca", media("Leite7", TANQUE, ("Leite7", ">0")), N1),
        ("Média primíparas (LACT 1)", "kg/vaca", media("Leite", *COM_LEITE, ("LACT", 1)), N1),
        ("Média multíparas (LACT ≥ 2)", "kg/vaca", media("Leite", *COM_LEITE, ("LACT", ">=2")), N1),
        ("Vacas com leite < 20 kg", "cab", cont(*COM_LEITE, ("Leite", "<20")), N0),
        ("DEL médio (lotes 1 a 6)", "dias", media("DEL", TANQUE), N0),
        ("Gordura média", "%", media("%Gord", TANQUE, ("%Gord", ">0")), N2),
        ("Proteína média", "%", media("Prot%", TANQUE, ("Prot%", ">0")), N2),
    ]),
    ("Reprodução – vacas em lactação (lotes 1 a 6 e 10)", [
        ("Frescas (Fresca)", "cab", cont(LAC, ("StatRepro", "Fresca")), N0),
        ("Inseminadas (Bred)", "cab", cont(LAC, ("StatRepro", "Bred")), N0),
        ("Prenhas", "cab", cont(LAC, ("StatRepro", "Prenha")), N0),
        ("Vazias", "cab", cont(LAC, ("StatRepro", "Vazia")), N0),
        ("Não inseminar (DNB)", "cab", cont(LAC, ("StatRepro", "DNB")), N0),
        ("% prenhes das vacas em lactação", "%",
         razao(cont(LAC, ("StatRepro", "Prenha")), cont(LAC)), P),
        ("DEL médio ao 1º serviço (DEL1S)", "dias", media("DEL1S", LAC, ("DEL1S", ">0")), N0),
        ("Dias em aberto médios das prenhas", "dias",
         media("DiasVazia", LAC, ("StatRepro", "Prenha")), N0),
        ("IAs por prenhez (prenhas)", "IAs", media("NumIAs", LAC, ("StatRepro", "Prenha")), N2),
    ]),
    ("Reprodução – novilhas", [
        ("Novilhas inseminadas (Bred)", "cab", cont(("Categoria", "Novilha"), ("StatRepro", "Bred")), N0),
        ("Novilhas prenhas", "cab", cont(("Categoria", "Novilha"), ("StatRepro", "Prenha")), N0),
        ("Novilhas vazias", "cab", cont(("Categoria", "Novilha"), ("StatRepro", "Vazia")), N0),
    ]),
    ("Animais por lote", [
        (f"Lote {lt}", "cab", cont(("Lote", lt)), N0) for lt in LOTES
    ]),
    ("Média de leite por lote de lactação (vacas com leite > 0)", [
        (f"Lote {lt}" + (" (descarte)" if lt == 10 else ""), "kg/vaca",
         media("Leite", LAC, ("Leite", ">0"), ("Lote", lt)), N1)
        for lt in LOTES if 1 <= lt <= 6 or lt == 10
    ]),
]

ND = len(DIAS)
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
    c = ws.cell(HR, 3 + k, d)  # data vem do nome do arquivo do relatório
    c.number_format = "DD/MM/YYYY"
ws.row_dimensions[HR].height = 30

r = HR + 1
var_rows = []
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
            c = ws.cell(r, 3 + k, "=" + f(f"{col}${HR}"))
            c.number_format = fmt
            c.font = font()
        if ND >= 2:
            a, b = f"{DC[-1]}{r}", f"{DC[-2]}{r}"
            c = ws.cell(r, LAST, f'=IF(OR({a}="",{b}=""),"",{a}-{b})')
            c.number_format = "+" + fmt + ";-" + fmt + ";0"
            c.font = font(bold=True)
            var_rows.append(r)
        for j in range(1, LAST + 1):
            ws.cell(r, j).border = BOX
            if n % 2:
                ws.cell(r, j).fill = ZEBRA
        r += 1
    r += 0

if var_rows:
    rng = f"{VC}{HR + 1}:{VC}{r - 1}"
    ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["0"],
                                                  font=Font(name=F, bold=True, color="1E7B45")))
    ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"],
                                                  font=Font(name=F, bold=True, color="B03A2E")))
ws.column_dimensions["A"].width = 44
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
                      "novo, o mais antigo sai da tabela (o arquivo continua guardado)."),
    ("Atualização", "python3 scripts/monitor_diario.py <novo_relatorio.xlsx> — guarda o relatório "
                    "como Zootecnico_AAAA-MM-DD.xlsx e refaz esta planilha. Um relatório novo da "
                    "mesma data substitui o anterior."),
    ("Aba Dados", "Linhas dos relatórios dos dias exibidos, empilhadas, com a coluna Data. "
                  "Todos os indicadores são fórmulas (CONT.SES/SOMASES/MÉDIASES) sobre esta aba."),
    ("Vacas em lactação", "Regra da fazenda: lotes 1, 2, 3, 4, 5, 6 e 10. O lote 10 são vacas em "
                          "tratamento com leite descartado (coluna Destino = Descarte); os lotes 1 a 6 "
                          "vão para o tanque (Destino = Tanque)."),
    ("Categoria", "Fórmula na aba Dados: lotes 1 a 6 e 10 → Vaca em lactação; nos demais lotes: "
                  "Male → Macho; LACT ≥ 1 → Vaca seca; LACT = 0 e Youngstock → Bezerra/recria; "
                  "LACT = 0 nos demais (Bred, Prenha, Vazia, Sterile…) → Novilha."),
    ("Produção", "Leite do tanque: lotes 1 a 6, só vacas com Leite > 0. O leite do lote 10 aparece "
                 "à parte como descartado. Pesagens antigas de vacas em outros lotes (ex.: secas do "
                 "lote 7) ficam de fora."),
    ("Gordura / proteína", "Média simples de %Gord e Prot% das vacas em lactação com valor > 0."),
    ("% prenhes", "Vacas em lactação com StatRepro = Prenha ÷ vacas em lactação."),
    ("Dias em aberto", "Média de DiasVazia das vacas em lactação prenhas (dias do parto à concepção)."),
    ("IAs por prenhez", "Média de NumIAs das vacas em lactação prenhas."),
    ("Variação", "Último dia menos o dia anterior exibido. Verde = subiu, vermelho = caiu "
                 "(a cor não indica se é bom ou ruim)."),
    ("Lotes", "A lista de lotes é a união dos lotes presentes nos dias exibidos."),
]
wn["A1"] = "Notas e definições"
wn["A1"].font = font(bold=True, size=14, color=AZUL)
for i, (k, v) in enumerate(notas, 3):
    wn.cell(i, 1, k).font = font(bold=True)
    c = wn.cell(i, 2, v)
    c.font = font()
    c.alignment = Alignment(wrap_text=True, vertical="top")
    wn.cell(i, 1).alignment = Alignment(vertical="top")
wn.column_dimensions["A"].width = 20
wn.column_dimensions["B"].width = 100
i += 2
wn.cell(i, 1, "Arquivos usados").font = font(bold=True)
for k, (d, p) in enumerate(zip(DIAS, arquivos)):
    wn.cell(i + 1 + k, 1, d).number_format = "DD/MM/YYYY"
    wn.cell(i + 1 + k, 2, os.path.basename(p)).font = font()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
wb.save(OUT)
print(f"{OUT}: {ND} dia(s), {len(dados)} linhas em Dados, {len(LOTES)} lotes")
