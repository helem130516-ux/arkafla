"""Baixa o relatório "Zootécnico Jorge atualizado" direto do BoviSync e grava no mesmo formato
do Excel exportado (dados/zootecnico/Zootecnico_AAAA-MM-DD.xlsx).

O login vem das variáveis de ambiente BOV_USER e BOV_PASS (nunca gravadas em arquivo).
A grade do site espera um aviso por SSE que não chega por este proxy; por isso o script
consulta a API do relatório (/api/report/data/item) até as colunas ficarem READY e busca
cada coluna em /api/report/data/fetch, de dentro da própria página (mesma sessão).

Data do relatório: o BoviSync calcula idade e DEL na data de hoje (exportação); como nos
arquivos Excel, o relatório corresponde ao dia anterior (DtNasc + IdadeDias − 1).

Uso:
    BOV_USER=... BOV_PASS=... python3 scripts/baixa_bovisync.py [url_do_relatorio] [--substituir]
Se o arquivo do dia já existir, não grava nada (a menos que se passe --substituir).
Requer: pip install playwright (usa o Chromium em /opt/pw-browsers/chromium).
"""
import json
import os
import re
import sys
import time
from urllib.parse import unquote

import pandas as pd
from playwright.sync_api import sync_playwright

URL = next((a for a in sys.argv[1:] if a.startswith("http")), None) or "https://bovisync.farm/report/CTBOCW"
PASTA = "dados/zootecnico"
CHROMIUM = "/opt/pw-browsers/chromium"
# item da API -> coluna do Excel exportado
COLUNAS = {
    "Pen": "Lote", "EART": "Brinco", "DIM": "DEL", "LACT": "LACT", "BDATE": "DtNasc", "Milk": "Leite",
    "Milk7": "Leite7", "Repro": "StatRepro", "DOPN": "DiasVazia", "DIM1B": "DEL1S", "DCC": "DDP",
    "Milk_GenPTA": "PTAGen_Leite", "Fat_GenPTA": "Gord_PTAGen", "Pro_GenPTA": "Pro_GenPTA",
    "Fat%": "%Gord", "Prot%": "Prot%", "=acc_milk(1,100)": "ProdLeite 100DEL",
    "=acc_milk(1,200)": "ProdLeite 200DEL", "SummitMilk": "PicoLeite", "AGDAY": "IdadeDias",
    "TBRD": "NumIAs", "BREDDate": "DATA da IA", "FDAT": "DtÚltParto",
}
# status em inglês (API) -> como sai no Excel em português
STATUS = {"Preg": "Prenha", "Fresh": "Fresca", "Open": "Vazia"}
JS = "u => fetch(u, {credentials: 'include'}).then(r => r.text())"


def baixa():
    req = {}
    with sync_playwright() as p:
        # Chromium pré-instalado no ambiente de nuvem; em outro computador usa o do Playwright
        # (instalar uma vez com: python3 -m playwright install chromium)
        exe = {"executable_path": CHROMIUM} if os.path.exists(CHROMIUM) else {}
        b = p.chromium.launch(args=["--no-sandbox"], **exe)
        ctx = b.new_context(viewport={"width": 1600, "height": 1000}, locale="pt-BR")
        pg = ctx.new_page()
        pg.on("request", lambda r: req.setdefault("item", r.url) if "/api/report/data/item" in r.url else None)
        pg.goto(URL, wait_until="networkidle", timeout=90000)
        if pg.locator("input[type=password]").count():
            pg.locator("input[name=username]").fill(os.environ["BOV_USER"])
            pg.locator("input[type=password]").fill(os.environ["BOV_PASS"])
            pg.locator("input[type=password]").press("Enter")
            pg.wait_for_load_state("networkidle", timeout=90000)
        for _ in range(60):
            if "item" in req:
                break
            pg.wait_for_timeout(1000)
        else:
            raise SystemExit("O relatório não pediu dados (login falhou?)")
        item_url = req["item"]
        inst = re.search(r"instance=([0-9a-f]+)", item_url)[1]
        itens = re.findall(r"item=([^&]+)", item_url)
        t0 = time.time()
        while True:
            st = {i["item"]: i["status"] for i in json.loads(pg.evaluate(JS, item_url))["items"]}
            pend = [_dec(i) for i in itens if st.get(_dec(i)) != "READY"]
            if not pend:
                break
            if time.time() - t0 > 600:
                raise SystemExit(f"Colunas não ficaram prontas: {pend}")
            time.sleep(5)
        dados = {}
        for it in itens:
            txt = pg.evaluate(JS, f"https://bovisync.farm/api/report/data/fetch?instance={inst}&item={it}")
            dados[_dec(it)] = pd.DataFrame(json.loads(txt)).set_index("id")
        b.close()
    return dados


def _dec(i):
    return unquote(i)


def converte(dados):
    t = pd.concat([dados[k] for k in dados if k in COLUNAS], axis=1)
    t = t.rename(columns=COLUNAS)[list(COLUNAS.values())]
    t["StatRepro"] = t["StatRepro"].replace(STATUS)
    t = t.sort_values(["Lote", "Brinco"], kind="stable").reset_index(drop=True)
    ref = (pd.to_datetime(t["DtNasc"]) + pd.to_timedelta(t["IdadeDias"], unit="D")).mode()[0]
    dia = (ref - pd.Timedelta(days=1)).date()
    return t, dia


if __name__ == "__main__":
    t, dia = converte(baixa())
    os.makedirs(PASTA, exist_ok=True)
    dest = os.path.join(PASTA, f"Zootecnico_{dia.isoformat()}.xlsx")
    if os.path.exists(dest) and "--substituir" not in sys.argv:
        # não sobrescreve um relatório que já existe (ex.: arquivo enviado pelo usuário com a data no nome)
        raise SystemExit(f"{dest} já existe; nada foi gravado (use --substituir para trocar)")
    t.to_excel(dest, index=False)
    print(f"{dest}: {len(t)} animais, relatório de {dia:%d/%m/%Y}")
