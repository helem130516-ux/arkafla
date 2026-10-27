"""Logo oficial (assets/logo_arcafla.svg) no cabeçalho do painel e na folha de impressão. Uso: src dst"""
import base64, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
uri = 'data:image/svg+xml;base64,' + base64.b64encode(open('assets/logo_arcafla.svg', 'rb').read()).decode()

def rep(a, b, n=1):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, n)

rep('''<header class="top">
    <div>
      <h1>''', '''<header class="top">
    <div class="brand"><img class="logo" src="''' + uri + '''" alt="ARCAFLA – Castro, Paraná"><div>
      <h1>''')
rep('''<p class="sub">Controle leiteiro APCBRH (Relatório 2.2) · CCS em mil células/mL · limite individual 200</p>
    </div>''', '''<p class="sub">Controle leiteiro APCBRH (Relatório 2.2) · CCS em mil células/mL · limite individual 200</p>
    </div></div>''')
rep('/* ---- Cultura ---- */', '''.brand{display:flex;align-items:center;gap:14px}
.brand .logo{height:64px;width:auto;flex:none;background:#fff;border-radius:8px;padding:3px 6px}
@media (max-width:560px){.brand .logo{height:46px}}
.paper .plogo{height:46px;width:auto;float:right;margin:-6px 0 0 12px}
/* ---- Cultura ---- */''')
# folha de impressão: logo no topo do documento gerado
i = s.find("function renderImpressao(")
j = s.find("innerHTML", i)
# o renderImpressao monta uma string h e atribui ao printDoc; prefixamos o logo na atribuição final
k = s.find("document.getElementById('printDoc').innerHTML", i)
if k > 0:
    s = s[:k] + "h = `<img class=\"plogo\" src=\"" + uri + "\" alt=\"ARCAFLA\">` + h;\n  " + s[k:]
open(dst, 'w', encoding='utf-8').write(s)
print('ok logo')
