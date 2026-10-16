"""Compara as análises oficiais do tanque (laticínio) com as amostras diárias do amostrador.

Entradas:
  dados/amostrador/Resultados_amostrador_PC_484.xlsx  (amostras diárias, uma por coleta)
  dados/mapa_leite.json                               (oficiais por tanque/mês/período)
  dados/tanque_avulsas.json                           (oficiais avulsas recebidas por mensagem)
Saída: dados/oficial_x_diaria.json

Como as oficiais são casadas com as diárias:
- O mapa não traz a data da amostra oficial, só o período (1º a 4º do mês).
- Nas diárias há, uma vez por semana, 1 a 2 dias seguidos sem nenhuma amostra. Nesses dias a
  amostra do tanque vai para a análise oficial (04-06/10 contém a oficial de 05/10). O k-ésimo
  "buraco" do mês é tratado como a data do k-ésimo período (OFICIAL_DIAS abaixo).
  Conferência: casando com o período certo, a correlação da CCS é 0,45; deslocando um período
  para trás ou para frente, cai para 0,13 / 0,23.
- Para cada oficial: média das diárias do mesmo tanque na coleta imediatamente antes e depois
  (até 4 dias), e média das diárias do mesmo tanque em ±7 dias.
- Amostras diárias suspeitas (gordura < 2,6% ou > 5,5%, ou sem resultado) ficam de fora:
  gordura muito baixa junto com CCS muito baixa indica amostra sem agitação do tanque.
"""
import datetime as dt
import json
import math
import statistics as st

import openpyxl

XLSX = "dados/amostrador/Resultados_amostrador_PC_484.xlsx"
D = dt.date
# (mês, período) -> dias sem amostra diária (data provável da amostra oficial)
OFICIAL_DIAS = {
    ("07", 1): (D(2026, 7, 5), D(2026, 7, 6)), ("07", 2): (D(2026, 7, 11), D(2026, 7, 12)),
    ("07", 3): (D(2026, 7, 18), D(2026, 7, 18)), ("07", 4): (D(2026, 7, 22), D(2026, 7, 22)),
    # ago: sem diárias de 01 a 11/08, então os períodos 1 e 2 não têm par
    ("08", 3): (D(2026, 8, 15), D(2026, 8, 16)), ("08", 4): (D(2026, 8, 22), D(2026, 8, 23)),
    ("09", 1): (D(2026, 9, 1), D(2026, 9, 2)), ("09", 2): (D(2026, 9, 9), D(2026, 9, 10)),
    ("09", 3): (D(2026, 9, 16), D(2026, 9, 17)), ("09", 4): (D(2026, 9, 22), D(2026, 9, 23)),
    ("10", 2): (D(2026, 10, 12), D(2026, 10, 13)),
}
K = ["G", "P", "S", "CCS", "CPP", "U"]


def num(x):
  if x in (None, "", "-"):
    return None
  return float(str(x).replace(",", "."))


def le_diarias():
  ws = openpyxl.load_workbook(XLSX, read_only=True, data_only=True).active
  out = []
  for v in ws.iter_rows(min_row=2, values_only=True):
    if v[0] is None:
      continue
    out.append(dict(amostra=v[0], tq=int(v[2].split("_")[1]), dt=v[4], rota=v[5], motorista=v[6],
                    G=num(v[8]), P=num(v[9]), L=num(v[10]), S=num(v[11]), CCS=num(v[12]),
                    CPP=num(v[13]), U=num(v[14]), ESD=num(v[15])))
  out.sort(key=lambda r: r["dt"])
  return out


def suspeita(r):
  return r["G"] is None or r["G"] < 2.6 or r["G"] > 5.5


def le_oficiais():
  of = []
  for r in json.load(open("dados/mapa_leite.json"))["registros"]:
    of.append(dict(tq=r["tanque"], mes=r["mes"][:2], per=r["periodo"], vol=r["volume_l"], G=r["GOR."],
                   P=r["PROT."], S=r["SOL."], CCS=r["CCS"], CPP=r["CPP"], U=r["UREIA"], fonte="mapa"))
  for a in json.load(open("dados/tanque_avulsas.json"))["analises"]:
    of.append(dict(tq=a["tanque"], mes=a["data"][5:7], per=2 if a["data"][5:7] == "10" else None, vol=None,
                   G=a["GOR"], P=a["PROT"], S=a["SOL"], CCS=a["CCS"], CPP=a["CPP"], U=a["UREIA"], fonte="avulsa"))
  return of


def media(vs):
  vs = [v for v in vs if v is not None]
  return round(st.mean(vs), 3) if vs else None


def main():
  diarias = le_diarias()
  validas = [r for r in diarias if not suspeita(r)]
  pares = []
  for o in le_oficiais():
    g = OFICIAL_DIAS.get((o["mes"], o["per"]))
    if not g:
      continue
    mesmo = [r for r in validas if r["tq"] == o["tq"]]
    ant = [r for r in mesmo if g[0] - dt.timedelta(4) <= r["dt"].date() < g[0]]
    dep = [r for r in mesmo if g[1] < r["dt"].date() <= g[1] + dt.timedelta(4)]
    viz = [x for x in (ant[-1:] + dep[:1])]
    sem = [r for r in mesmo if g[0] - dt.timedelta(7) <= r["dt"].date() <= g[1] + dt.timedelta(7)]
    pares.append(dict(
        tanque=o["tq"], mes=o["mes"], periodo=o["per"], dias=[g[0].isoformat(), g[1].isoformat()],
        oficial={k: o[k] for k in K},
        vizinhas={k: media([r[k] for r in viz]) for k in K}, vizinhas_datas=[r["dt"].strftime("%d/%m") for r in viz],
        semana={k: media([r[k] for r in sem]) for k in K}, semana_n=len(sem)))

  resumo = {}
  for base in ("vizinhas", "semana"):
    resumo[base] = {}
    for k in K:
      xs = [(p["oficial"][k], p[base][k]) for p in pares if p["oficial"][k] is not None and p[base][k] is not None]
      if k == "CPP":  # picos isolados (ex.: 338 no tanque 2, jul) dominariam a média
        xs = [x for x in xs if x[0] < 100 and x[1] < 100]
      d = [a - b for a, b in xs]
      sd = st.stdev(d)
      resumo[base][k] = dict(n=len(xs), oficial=round(st.mean(a for a, _ in xs), 3), diaria=round(st.mean(b for _, b in xs), 3),
                             dif=round(st.mean(d), 3), dp=round(sd, 3), t=round(st.mean(d) / (sd / math.sqrt(len(d))), 2),
                             dif_abs=round(st.mean(abs(x) for x in d), 3), oficial_maior=sum(x > 0 for x in d),
                             r=round(st.correlation([a for a, _ in xs], [b for _, b in xs]), 2))

  mensal = []
  for m in range(1, 11):
    ds = [r for r in validas if r["dt"].year == 2026 and r["dt"].month == m]
    mensal.append(dict(mes=m, n=len(ds), **{k: media([r[k] for r in ds]) for k in ["G", "P", "L", "S", "CCS", "U", "ESD"]},
                       CPP_mediana=st.median(r["CPP"] for r in ds), CPP_acima_100=sum(r["CPP"] > 100 for r in ds),
                       CCS_acima_400=sum(r["CCS"] >= 400 for r in ds)))

  out = dict(
      _nota="Gerado por scripts/compara_oficial_diaria.py. Médias simples; CPP sem picos > 100 no resumo.",
      diarias_total=len(diarias), diarias_suspeitas=[dict(data=r["dt"].strftime("%d/%m/%Y"), tanque=r["tq"], G=r["G"], CCS=r["CCS"])
                                                     for r in diarias if suspeita(r)],
      cpp_picos=[dict(data=r["dt"].strftime("%d/%m/%Y"), tanque=r["tq"], CPP=r["CPP"]) for r in validas if r["CPP"] > 100],
      pares=pares, resumo=resumo, mensal_diarias=mensal)
  json.dump(out, open("dados/oficial_x_diaria.json", "w"), ensure_ascii=False, indent=1)
  for base, rk in resumo.items():
    print(base)
    for k, v in rk.items():
      print(f"  {k:4} n={v['n']:2} oficial={v['oficial']:8.2f} diaria={v['diaria']:8.2f} dif={v['dif']:+7.2f} t={v['t']:+.2f} r={v['r']}")


if __name__ == "__main__":
  main()
