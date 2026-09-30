import json, sys
src, dst, rj = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()
J = json.load(open(rj, encoding='utf-8'))
HQ = {k: [v['AD'], v['AE'], v['PE'], v['PD'], v['sujidade']] for k, v in J['hiperqueratose']['vacas'].items()}
SEC = [[x['vaca'], x['data'], x['produto'], x['parto'] or ''] for x in J['secagem']]
DG = [[x['vaca'], x['data'], x['doenca'], x['medicamento']] for x in J['doencas']]

def rep(a, b, n=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, n)

# painel do mês: bloco hiperqueratose
rep('''<div class="panel"><h2>10 maiores contribuições para a CCS do tanque</h2>''',
    '''<div class="panel"><h2>10 maiores contribuições para a CCS do tanque</h2>''')
rep('''<div id="chTopMes"></div></div>
    </div>''', '''<div id="chTopMes"></div></div>
    </div>
    <div class="panel"><h2>Hiperqueratose da ponta do teto × CCS no controle</h2><p class="note" id="hqNote"></p>
      <div class="grid g2"><div><h3 class="sub3">Vacas com CCS ≥ 200</h3><div id="chHqEl"></div></div><div><h3 class="sub3">Taxa de novas infecções</h3><div id="chHqNi"></div></div></div>
      <p class="foot2" id="hqFoot"></p></div>''')
rep('/* ---- Cultura ---- */', '.sub3{font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600;margin:4px 0 8px}\n/* ---- Cultura ---- */')

# ficha: secagem e doenças
rep('<div class="tbl"><table id="tblCult"></table></div>',
    '<div class="tbl"><table id="tblCult"></table></div>\n      <h2 id="secTit" style="margin-top:16px">Secagens</h2><div class="tbl"><table id="tblSec"></table></div>\n      <h2 id="dgTit" style="margin-top:16px">Tratamentos sistêmicos (doenças gerais, jul–ago/2026)</h2><div class="tbl"><table id="tblDg"></table></div>')

js = r'''
// ---------- registro da fazenda: hiperqueratose, secagem, doenças ----------
const HQ = ''' + json.dumps(HQ) + r''';
const HQ_DATA = ''' + json.dumps(J['hiperqueratose']['data']) + r''';
const SEC = ''' + json.dumps(SEC, ensure_ascii=False) + r''';
const DG = ''' + json.dumps(DG, ensure_ascii=False) + r''';
const hqMax = v => { const h=HQ[v]; if(!h) return null; const q=h.slice(0,4).filter(x=>typeof x==='number'); return q.length?Math.max(...q):null; };
const SECB = {}; SEC.forEach(x=>(SECB[x[0]] ||= []).push(x));
const DGB = {}; DG.forEach(x=>(DGB[x[0]] ||= []).push(x));
function renderHq(){
  const a = A[cur-1], x = (byCi[cur]||[]);
  const sc = [1,2,3,4].map(k=>{ const r=x.filter(q=>hqMax(q.vaca)===k); const b=r.filter(q=>q.cls==='S'||q.cls==='N');
    return {k, n:r.length, el:r.filter(q=>q.ccs>=LIM).length, b:b.length, ni:b.filter(q=>q.cls==='N').length}; });
  const tot = sc.reduce((s,o)=>s+o.n,0);
  const shade = ['var(--fx1)','var(--fx2)','var(--fx3)','var(--fx4)'];
  document.getElementById('hqNote').textContent = `Escore de hiperqueratose avaliado em ${fmtD(HQ_DATA)}/2026 (1 a 4, pior quarto da vaca) · ${fmt(tot)} vacas deste controle têm escore · CCS e classificação do controle de ${lab(ctrls[cur-1])}`;
  document.getElementById('chHqEl').innerHTML = hbRows(sc.map(o=>({lb:`<span class="sw" style="background:${shade[o.k-1]}"></span>Escore ${o.k}<small>${o.n} vacas</small>`, v:o.n?o.el/o.n:0, color:shade[o.k-1],
    val:`<b>${o.n?pct(o.el/o.n,0):'–'}</b> · ${o.el}`, tip:`Escore ${o.k}: ${o.el} de ${o.n} vacas com CCS ≥ 200`})), {max:1, ref:a.ge200, cls:'wide'}) +
    `<div class="lgd"><span><i class="rfk"></i>rebanho (${pct(a.ge200)})</span></div>`;
  document.getElementById('chHqNi').innerHTML = a.first ? '<p class="note">Primeiro controle: sem classificação.</p>' :
    hbRows(sc.map(o=>({lb:`<span class="sw" style="background:${shade[o.k-1]}"></span>Escore ${o.k}<small>${o.b} vacas</small>`, v:o.b?o.ni/o.b:0, color:shade[o.k-1],
      val:`<b>${o.b?pct(o.ni/o.b,0):'–'}</b> · ${o.ni}`, tip:`Escore ${o.k}: ${o.ni} novas infecções entre ${o.b} vacas com CCS baixa no controle anterior`})), {max:Math.max(.4,...sc.map(o=>o.b?o.ni/o.b:0)), ref:a.taxaNI, cls:'wide'}) +
      `<div class="lgd"><span><i class="rfk"></i>rebanho (${pct(a.taxaNI)})</span><span>base = vacas sadias + novas infecções</span></div>`;
  document.getElementById('hqFoot').innerHTML = `Associação, não prova de causa: vacas de maior produção ou mais velhas também tendem a ter escore maior. O escore é de uma única avaliação (${fmtD(HQ_DATA)}); fica mais antigo a cada controle.`;
}
function fichaExtra(v){
  const h = HQ[v];
  const info = document.getElementById('vacaInfo');
  if(h) info.textContent += ` · Hiperqueratose ${fmtD(HQ_DATA)}: AD ${h[0]??'–'} · AE ${h[1]??'–'} · PE ${h[2]??'–'} · PD ${h[3]??'–'} (sujidade ${h[4]??'–'})`;
  const sc = (SECB[v]||[]).slice().sort((a,b)=>a[1].localeCompare(b[1]));
  document.getElementById('secTit').textContent = 'Secagens: '+sc.length;
  document.getElementById('tblSec').innerHTML = sc.length ? '<thead><tr><th>Data da secagem</th><th class="l">Produto</th><th>Parto seguinte</th></tr></thead><tbody>'+sc.map(x=>`<tr><td>${x[1].split('-').reverse().join('/')}</td><td class="l">${esc(x[2])}</td><td>${x[3]?x[3].split('-').reverse().join('/'):'–'}</td></tr>`).join('')+'</tbody>' : '<tbody><tr><td class="l">Sem secagem registrada.</td></tr></tbody>';
  const dg = DGB[v]||[];
  document.getElementById('dgTit').textContent = 'Tratamentos sistêmicos (doenças gerais, jul–ago/2026): '+dg.length;
  document.getElementById('tblDg').innerHTML = dg.length ? '<thead><tr><th>Data</th><th class="l">Doença</th><th class="l">Medicamento</th></tr></thead><tbody>'+dg.map(x=>`<tr><td>${fmtD(x[1])}</td><td class="l">${esc(x[2])}</td><td class="l">${esc(x[3])}</td></tr>`).join('')+'</tbody>' : '<tbody><tr><td class="l">Nenhum registro.</td></tr></tbody>';
}
'''
j = s.index('function renderAll(){')
s = s[:j] + js + s[j:]
rep("  fichaCult(v);\n}", "  fichaCult(v); fichaExtra(v);\n}")
rep("if(!h){ fichaCult(v);", "if(!h){ fichaCult(v); setTimeout(()=>fichaExtra(v));")
rep("if(t==='painel') renderPainel();", "if(t==='painel'){ renderPainel(); renderHq(); }")
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(HQ), len(SEC), len(DG))
