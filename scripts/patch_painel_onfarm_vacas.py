"""OnFarm por vaca: seção na aba Cultura e lista no Histórico da vaca. Uso: src dst dados/cultura_onfarm_vacas.json"""
import json, sys
src, dst, oj = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()
J = json.load(open(oj, encoding='utf-8'))
TIPO = {'Mastite Clínica': 'C', 'Secagem': 'S'}
RES = {'Positivo': 'P', 'Negativo': 'N', 'Contaminado': 'X', 'Fazer Leitura': 'L'}
GR = {'Leve': 'L', 'Moderado': 'M', 'Grave': 'G', 'Não aplicável': '-'}
OFV = [[r['vaca'], r['data'], TIPO.get(r['tipo'], r['tipo']), r['quarto'], GR.get(r['grau'], r['grau']), RES.get(r['resultado'], r['resultado']), r['agentes']] for r in J['registros']]

def rep(a, b, n=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, n)

sec = '''<h2 style="font-family:var(--f-display);margin:10px 0 0">Cultura na fazenda (OnFarm) – por vaca</h2>
    <div class="panel"><p class="note" style="margin:0" id="ofIntro"></p></div>
    <div class="hero" id="ofHero"></div>
    <div class="grid g2">
      <div class="panel"><h2>Agentes nos casos clínicos positivos</h2><p class="note" id="ofAgNote"></p><div id="ofAg"></div><div class="tbl" style="margin-top:12px"><table id="ofGrau"></table></div></div>
      <div class="panel"><h2>CCS da vaca no controle anterior à cultura</h2><p class="note">Casos clínicos · barra = % das culturas em vacas que já estavam com CCS ≥ 200 no último controle antes da coleta</p><div id="ofCcs"></div>
        <h3 class="sub3" style="margin-top:16px">Cultura × tratamento intramamário (registro da fazenda)</h3><div class="tbl"><table id="ofTrat"></table></div><p class="note" id="ofTratNote" style="margin-top:8px"></p></div>
    </div>
    <div class="panel"><h2>Culturas por vaca</h2>
      <div class="row"><label class="lb" for="ofMes">Mês</label><select id="ofMes"></select><label class="lb" for="ofGrp">Agente</label><select id="ofGrp"></select><label class="lb" for="ofRes">Resultado</label><select id="ofRes"></select><span class="note" id="ofCount" style="margin:0"></span></div>
      <p class="note">Toque numa linha para abrir o histórico da vaca · mostra até 300 linhas, as mais recentes primeiro</p>
      <div class="tbl scroll"><table id="ofTab"></table></div></div>
    <h2 style="font-family:var(--f-display);margin:10px 0 0">OnFarm – resumo por mês</h2>'''
rep('<h2 style="font-family:var(--f-display);margin:10px 0 0">Resumo mensal do sistema OnFarm</h2>', sec)
rep('<div class="tbl" style="margin-top:8px"><table id="tblAbx"></table></div>',
    '<div class="tbl" style="margin-top:8px"><table id="tblAbx"></table></div>\n      <h2 id="ofFTit" style="margin-top:16px">Culturas OnFarm</h2><div class="tbl"><table id="tblOnf"></table></div>')

js = r'''
// ---------- OnFarm por vaca ----------
const OFV = ''' + json.dumps(OFV, ensure_ascii=False) + r'''.map(a=>({vaca:a[0],data:a[1],tipo:a[2],q:a[3],grau:a[4],res:a[5],ag:a[6]}));
const OF_ARQ = ''' + json.dumps(J['arquivo']) + r''';
const OFB = {}; OFV.forEach(o=>(OFB[o.vaca] ||= []).push(o));
const RESN = {P:'Positivo',N:'Negativo',X:'Contaminado',L:'Fazer leitura'}, GRN = {L:'Leve',M:'Moderado',G:'Grave','-':'–'};
const grpAg = a => CGRP.find(g=>g.a.includes(a)) || CGRP[5];
function ofCtx(v,d){ const h=byCow[v]||[]; return {bef:h.filter(r=>ctrls[r.ci-1].date<=d).pop(), aft:h.find(r=>ctrls[r.ci-1].date>d)}; }
let ofMes='', ofGrp='', ofRes='';
function renderOnfarm(){
  const N=OFV.length, cl=OFV.filter(o=>o.tipo==='C'), sc=OFV.filter(o=>o.tipo==='S');
  const d0=OFV[0].data, d1=OFV[N-1].data, cnt=(x,f)=>x.filter(f).length;
  document.getElementById('ofIntro').textContent = `Exportação por vaca do OnFarm (${OF_ARQ}): ${fmt(N)} culturas de ${fmtD(d0)}/${d0.slice(0,4)} a ${fmtD(d1)}/${d1.slice(0,4)} · ${fmt(cl.length)} de mastite clínica e ${sc.length} na secagem · ${cnt(OFV,o=>o.ag.length>0&&o.res==='P')} positivas. Sem antibiograma. Conferido: em resultados positivos, os agentes por mês batem exatamente com o gráfico do OnFarm de fev a ago/26.`;
  const tile = (t,v,sub) => `<div class="htile"><span class="k">${t}</span><div class="row1"><span class="v">${v}</span></div><span class="s">${sub}</span></div>`;
  document.getElementById('ofHero').innerHTML =
    tile('Culturas de mastite clínica', fmt(cl.length), `${pct(cnt(cl,o=>o.res==='P')/cl.length,0)} positivas · ${fmt(cnt(cl,o=>o.grau==='G'))} graves (${pct(cnt(cl,o=>o.grau==='G')/cl.length,0)})`) +
    tile('Sem crescimento (negativas)', pct(cnt(cl,o=>o.res==='N')/cl.length,0), `${fmt(cnt(cl,o=>o.res==='N'))} casos clínicos · candidatos a não usar antibiótico, se o protocolo do veterinário permitir`) +
    tile('Contaminadas', pct(cnt(cl,o=>o.res==='X')/cl.length,0), `${fmt(cnt(cl,o=>o.res==='X'))} amostras com 3 ou mais agentes · rever a higiene da coleta`) +
    tile('Culturas na secagem', fmt(sc.length), `${pct(cnt(sc,o=>o.res==='P')/sc.length,0)} positivas · ${cnt(sc,o=>o.res==='N')} negativas`);
  const pos = cl.filter(o=>o.res==='P'), np = pos.length;
  document.getElementById('ofAgNote').textContent = `${np} culturas clínicas positivas · % das culturas com o grupo de agente (uma cultura pode ter 2)`;
  const gs = CGRP.map(g=>({g, x:pos.filter(o=>o.ag.some(a=>grpAg(a)===g))})).filter(o=>o.x.length).sort((a,b)=>b.x.length-a.x.length);
  document.getElementById('ofAg').innerHTML = hbRows(gs.map(o=>({lb:`<span class="sw" style="background:${o.g.c}"></span>${o.g.k}`, v:o.x.length/np, color:o.g.c, val:`<b>${pct(o.x.length/np,0)}</b> · ${o.x.length}`, tip:`${o.g.k}: ${o.x.length} de ${np} culturas clínicas positivas`})), {cls:'wide'});
  document.getElementById('ofGrau').innerHTML = '<thead><tr><th>Grupo</th><th>Leve</th><th>Moderado</th><th>Grave</th><th>% grave</th></tr></thead><tbody>'+
    gs.map(o=>{ const c=k=>o.x.filter(y=>y.grau===k).length; return `<tr><td class="l">${o.g.k}</td><td>${c('L')}</td><td>${c('M')}</td><td>${c('G')}</td><td class="${c('G')/o.x.length>=.35?'hot':''}">${pct(c('G')/o.x.length,0)}</td></tr>`; }).join('')+
    `<tr><td class="l">Negativas</td><td>${cnt(cl,o=>o.res==='N'&&o.grau==='L')}</td><td>${cnt(cl,o=>o.res==='N'&&o.grau==='M')}</td><td>${cnt(cl,o=>o.res==='N'&&o.grau==='G')}</td><td>${pct(cnt(cl,o=>o.res==='N'&&o.grau==='G')/Math.max(1,cnt(cl,o=>o.res==='N')),0)}</td></tr></tbody>`;
  const cc = gs.map(o=>{ const k=o.x.map(y=>ofCtx(y.vaca,y.data)).filter(z=>z.bef); return {g:o.g, n:k.length, el:k.filter(z=>z.bef.ccs>=LIM).length}; })
    .concat([(()=>{ const k=cl.filter(o=>o.res==='N').map(y=>ofCtx(y.vaca,y.data)).filter(z=>z.bef); return {g:{k:'Negativas',c:'var(--grey)'}, n:k.length, el:k.filter(z=>z.bef.ccs>=LIM).length}; })()]).filter(o=>o.n);
  document.getElementById('ofCcs').innerHTML = hbRows(cc.map(o=>({lb:`<span class="sw" style="background:${o.g.c}"></span>${o.g.k}`, v:o.el/o.n, color:o.g.c, val:`<b>${pct(o.el/o.n,0)}</b> · ${o.el} de ${o.n}`, tip:`${o.g.k}: ${o.el} de ${o.n} culturas em vacas já com CCS ≥ 200`})), {max:1, cls:'wide'});
  // cultura x tratamento: tratamento do registro com cultura clínica da mesma vaca de 3 dias antes a 3 dias depois do início
  const ms = [...new Set(MC.map(c=>c.ini.slice(0,7)))].filter(m=>m>=d0.slice(0,7)).sort();
  const match = c => (OFB[c.vaca]||[]).filter(o=>o.tipo==='C' && o.data>=addD(c.ini,-3) && o.data<=addD(c.ini,3));
  const rowsT = ms.map(m=>{ const t=MC.filter(c=>c.ini.slice(0,7)===m); const w=t.filter(c=>match(c).length); const ng=w.filter(c=>match(c).every(o=>o.res==='N')); return {m,t:t.length,w:w.length,ng:ng.length}; });
  document.getElementById('ofTrat').innerHTML = '<thead><tr><th>Mês</th><th>Tratamentos</th><th>Com cultura OnFarm</th><th>%</th><th>Cultura negativa</th></tr></thead><tbody>'+
    rowsT.map(o=>`<tr><td class="l">${MESN[+o.m.slice(5)-1]}/${o.m.slice(2,4)}</td><td>${o.t}</td><td>${o.w}</td><td>${o.t?pct(o.w/o.t,0):'–'}</td><td>${o.ng}${o.w?' <small>('+pct(o.ng/o.w,0)+')</small>':''}</td></tr>`).join('')+'</tbody>';
  const T=rowsT.reduce((s,o)=>s+o.t,0), Wc=rowsT.reduce((s,o)=>s+o.w,0), Ng=rowsT.reduce((s,o)=>s+o.ng,0);
  document.getElementById('ofTratNote').textContent = `Desde ${MESN[+d0.slice(5,7)-1]}/${d0.slice(2,4)}: ${Wc} de ${T} tratamentos (${pct(Wc/T,0)}) têm cultura OnFarm da mesma vaca até 3 dias do início; em ${Ng} deles (${pct(Ng/Math.max(1,Wc),0)}) a cultura foi negativa. Ligação por vaca e data; o quarto pode não ser o mesmo.`;
  // filtros e lista
  const sM=document.getElementById('ofMes'), sG=document.getElementById('ofGrp'), sR=document.getElementById('ofRes');
  if(!sM.options.length){
    sM.innerHTML='<option value="">Todos</option>'+[...new Set(OFV.map(o=>o.data.slice(0,7)))].sort().reverse().map(m=>`<option value="${m}">${MESN[+m.slice(5)-1]}/${m.slice(2,4)}</option>`).join('');
    sG.innerHTML='<option value="">Todos</option>'+CGRP.map((g,i)=>`<option value="${i}">${g.k}</option>`).join('');
    sR.innerHTML='<option value="">Todos</option>'+Object.entries(RESN).map(([k,v])=>`<option value="${k}">${v}</option>`).join('');
    sM.addEventListener('change',()=>{ofMes=sM.value;renderOnfarm();}); sG.addEventListener('change',()=>{ofGrp=sG.value;renderOnfarm();}); sR.addEventListener('change',()=>{ofRes=sR.value;renderOnfarm();});
  }
  const L = OFV.filter(o=>(!ofMes||o.data.slice(0,7)===ofMes)&&(!ofRes||o.res===ofRes)&&(ofGrp===''||o.ag.some(a=>grpAg(a)===CGRP[+ofGrp]))).slice().reverse();
  document.getElementById('ofCount').textContent = L.length+' culturas';
  document.getElementById('ofTab').innerHTML = '<thead><tr><th>Data</th><th>Vaca</th><th>Tipo</th><th>Quarto</th><th>Grau</th><th>Resultado</th><th class="l">Agente(s)</th><th>CCS antes</th><th>CCS depois</th><th class="l">Classe antes</th></tr></thead><tbody>'+
    L.slice(0,300).map(o=>{ const k=ofCtx(o.vaca,o.data); return `<tr class="click" data-v="${esc(o.vaca)}"><td>${fmtD(o.data)}</td><td>${esc(o.vaca)}</td><td>${o.tipo==='C'?'Clínica':'Secagem'}</td><td class="l">${o.q.split(' ').length===4?'composta':esc(o.q)}</td><td>${GRN[o.grau]||'–'}</td><td>${RESN[o.res]||o.res}</td><td class="ag">${o.ag.length?o.ag.map(a=>`<span class="sw" style="background:${grpAg(a).c};margin-right:4px"></span>${a}`).join('<br>'):'–'}</td><td class="${k.bef&&k.bef.ccs>=LIM?'hot':''}">${k.bef?fmt(k.bef.ccs):'–'}</td><td class="${k.aft&&k.aft.ccs>=LIM?'hot':''}">${k.aft?fmt(k.aft.ccs):'–'}</td><td class="l">${k.bef?pill(k.bef.cls):'–'}</td></tr>`; }).join('')+'</tbody>';
}
document.getElementById('ofTab').addEventListener('click',e=>{ const tr=e.target.closest('tr[data-v]'); if(!tr) return; document.getElementById('inVaca').value=tr.dataset.v; showTab('ficha'); });
function fichaOnf(v){
  const raw=document.getElementById('inVaca').value.trim(); const xs=OFB[v]||OFB[raw]||[];
  document.getElementById('ofFTit').textContent='Culturas OnFarm: '+xs.length;
  document.getElementById('tblOnf').innerHTML = xs.length ? '<thead><tr><th>Data</th><th>Tipo</th><th>Quarto</th><th>Grau</th><th>Resultado</th><th class="l">Agente(s)</th></tr></thead><tbody>'+
    xs.map(o=>`<tr><td>${fmtD(o.data)}</td><td>${o.tipo==='C'?'Clínica':'Secagem'}</td><td class="l">${o.q.split(' ').length===4?'composta':esc(o.q)}</td><td>${GRN[o.grau]||'–'}</td><td>${RESN[o.res]||o.res}</td><td class="ag">${o.ag.join(' + ')||'–'}</td></tr>`).join('')+'</tbody>' : '<tbody><tr><td class="l">Nenhuma cultura OnFarm registrada para esta vaca.</td></tr></tbody>';
}
'''
j = s.index('function renderAll(){')
s = s[:j] + js + s[j:]
rep("else if(t==='cultura'){ renderLabvet(); renderAbx(); renderCultura(); }", "else if(t==='cultura'){ renderLabvet(); renderAbx(); renderOnfarm(); renderCultura(); }")
rep("  fichaCult(v); fichaExtra(v); fichaAbx(v);\n}", "  fichaCult(v); fichaExtra(v); fichaAbx(v); fichaOnf(v);\n}")
rep("if(!h){ fichaCult(v); fichaAbx(v);", "if(!h){ fichaCult(v); fichaAbx(v); fichaOnf(v);")
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(OFV), 'culturas OnFarm por vaca')
