"""Aba "Tanque (laticínio)": CCS/CPP reais do mapa de pagamento × estimativas do controle. Uso: src dst dados/mapa_leite.json"""
import json, sys
src, dst, mj = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()
J = json.load(open(mj, encoding='utf-8'))
TQ = [[r['tanque'], r['mes'], r['periodo'], r['volume_l'], r['CCS'], r['CPP'], r['GOR.'], r['PROT.'], r['SOL.'], r['UREIA']] for r in J['registros']]
MAPAS = J['mapas']

def rep(a, b, n=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, n)

rep('<button role="tab" data-tab="evolucao" aria-selected="false">Evolução</button>',
    '<button role="tab" data-tab="tanque" aria-selected="false">Tanque (laticínio)</button>\n    <button role="tab" data-tab="evolucao" aria-selected="false">Evolução</button>')
sec = '''<section id="tab-tanque" class="grid" hidden>
    <div class="panel"><h2>CCS e CPP reais do tanque (laticínio)</h2><p class="note" id="tqIntro" style="margin:0"></p></div>
    <div class="hero" id="tqHero"></div>
    <div class="grid g2">
      <div class="panel"><h2>CCS real do tanque por mês × estimativa do controle</h2><p class="note">Barra = CCS real (média das análises do mês ponderada pelo volume) · traço = estimativa do controle APCBRH do mês, sem o lote 10</p><div id="tqMes"></div><div class="lgd"><span><i class="sw" style="background:var(--accent)"></i>CCS real (laticínio)</span><span><i class="pvk"></i>estimativa do controle (sem lote 10)</span></div><div class="tbl" style="margin-top:12px"><table id="tqCmp"></table></div><p class="note" id="tqCmpNote" style="margin-top:8px"></p></div>
      <div class="panel"><h2>Premiações do mês</h2><p class="note" id="tqPremNote"></p><div class="tbl"><table id="tqPrem"></table></div></div>
    </div>
    <div class="panel"><h2>CCS por período de coleta</h2><p class="note">Mil células/mL · linha grossa = média ponderada dos tanques no período · linhas finas = cada tanque</p><div class="chart" style="max-width:820px"><div id="tqLine"></div></div></div>
    <div class="panel"><h2>Análises por tanque e período</h2><p class="note">CCS em mil céls/mL e CPP em mil UFC/mL · CCS ≥ 400 em vermelho, 300 a 399 em laranja · CPP ≥ 100 em vermelho · vazio = sem análise no mapa</p>
      <div class="tbl"><table id="tqCcs" class="abmap"></table></div><div class="tbl" style="margin-top:12px"><table id="tqCpp" class="abmap"></table></div></div>
    <div class="panel"><h2>Composição do leite por mês</h2><p class="note">Médias ponderadas pelo volume · última coluna = "Média Pagto" e "Média POOL" do mapa mais recente</p><div class="tbl"><table id="tqComp"></table></div></div>
  </section>

  '''
rep('<section id="tab-evolucao"', sec + '<section id="tab-evolucao"')
rep('/* ---- Cultura ---- */', '''.abmap td.hi{color:var(--crit);font-weight:700}.abmap td.md{color:var(--serious);font-weight:700}
/* ---- Cultura ---- */''')

js = r'''
// ---------- tanque (mapa de pagamento do laticínio) ----------
const TQ = ''' + json.dumps(TQ, ensure_ascii=False) + r'''.map(a=>({tq:a[0],mes:a[1],per:a[2],vol:a[3],CCS:a[4],CPP:a[5],GOR:a[6],PROT:a[7],SOL:a[8],UREIA:a[9]}));
const MAPAS = ''' + json.dumps(MAPAS, ensure_ascii=False) + r''';
const mKey = m => m.slice(3)+'-'+m.slice(0,2);
const TQM = [...new Set(TQ.map(r=>r.mes))].sort((a,b)=>mKey(a).localeCompare(mKey(b)));
const wavg = (xs,k) => { const y=xs.filter(r=>r[k]!=null); const v=y.reduce((s,r)=>s+r.vol,0); return v? y.reduce((s,r)=>s+r.vol*r[k],0)/v : null; };
const realMes = m => wavg(TQ.filter(r=>r.mes===m),'CCS');
const ctrlDoMes = m => ctrls.filter(c=>c.date.slice(0,7)===mKey(m));
const mesLab = m => MESN[+m.slice(0,2)-1]+'/'+m.slice(5);
function renderTanque(){
  const ult = MAPAS[MAPAS.length-1];
  document.getElementById('tqIntro').textContent = `Mapa de fornecimento do Pool Leite (mês ${ult.mes}, emitido em ${ult.emissao}) · ${TQ.length} análises de ${new Set(TQ.map(r=>r.tq)).size} tanques, ${TQM.map(mesLab).join(', ')}, até 4 períodos por mês. Estes são os valores reais medidos pelo laticínio. As estimativas do controle APCBRH vêm das vacas no dia do controle e ficam separadas.`;
  const r = TQM.map(m=>({m, ccs:realMes(m), cpp:wavg(TQ.filter(x=>x.mes===m),'CPP'), n:TQ.filter(x=>x.mes===m).length}));
  const L = r[r.length-1], P = r[r.length-2];
  const tile = (t,v,u,d,sub) => `<div class="htile"><span class="k">${t}</span><div class="row1"><span class="v">${v}</span>${u?`<span class="u">${u}</span>`:''}${d||''}</div><span class="s">${sub}</span></div>`;
  const prem = (ult.premiacoes||[]).find(x=>/^CCS/.test(x.indicador));
  document.getElementById('tqHero').innerHTML =
    tile('CCS real do tanque · '+mesLab(L.m), fmt(L.ccs), 'mil/mL', P?deltaChip(L.ccs,P.ccs,false,0,false):'', `média ponderada de ${L.n} análises`+(P?` · ${mesLab(P.m)}: ${fmt(P.ccs)}`:'')) +
    tile('"Média Pagto" CCS (mapa)', fmt(ult.media_pagto.CCS), 'mil/mL', '', `média do POOL: ${fmt(ult.media_pool.CCS)} · fazenda ${fmt(ult.media_pagto.CCS-ult.media_pool.CCS)} acima`) +
    tile('"Média Pagto" CPP (mapa)', fmt(ult.media_pagto.CPP,1), 'mil UFC/mL', '', `média do POOL: ${fmt(ult.media_pool.CPP,1)}`) +
    tile('Prêmio de CCS', prem?fmt(prem.pct,2)+'%':'–', '', '', prem?`R$ ${fmt(prem.rs_litro,4)}/L · R$ ${fmt(prem.total,2)} no mês · preço final R$ ${fmt(ult.preco_final_litro,4)}/L`:'');
  document.getElementById('tqMes').innerHTML = hbRows(r.map(o=>{ const c=ctrlDoMes(o.m).pop(); const e=c?A[c.ci-1].semDesvio:null;
    return {lb:mesLab(o.m), v:o.ccs, pv:e, color:'var(--accent)', val:`<b>${fmt(o.ccs)}</b>`, sub:e!=null?'estim. '+fmt(e):'',
      tip:`${mesLab(o.m)}: CCS real ${fmt(o.ccs)} (${o.n} análises)`+(c?` · controle ${lab(c)}: estimativa sem lote 10 ${fmt(e)}, "Média CCS tanque" APCBRH ${fmt(c.apcbrh)}`:'')}; }), {max:Math.max(...r.map(o=>o.ccs), ...r.map(o=>{const c=ctrlDoMes(o.m).pop(); return c?A[c.ci-1].semDesvio:0;}))*1.1});
  document.getElementById('tqCmp').innerHTML = '<thead><tr><th>Mês</th><th>CCS real</th><th>Controle</th><th>Estim. s/ lote 10</th><th>APCBRH</th><th>Real − estim.</th></tr></thead><tbody>'+
    r.map(o=>{ const c=ctrlDoMes(o.m).pop(); const e=c?A[c.ci-1].semDesvio:null; return `<tr><td class="l">${mesLab(o.m)}</td><td><b>${fmt(o.ccs)}</b></td><td>${c?lab(c):'–'}</td><td>${e!=null?fmt(e):'–'}</td><td>${c?fmt(c.apcbrh):'–'}</td><td class="${e!=null&&o.ccs-e>0?'hot':''}">${e!=null?(o.ccs-e>0?'+':'−')+fmt(Math.abs(o.ccs-e)):'–'}</td></tr>`; }).join('')+'</tbody>';
  document.getElementById('tqCmpNote').textContent = 'A estimativa é de um só dia (dia do controle) e só das vacas controladas; o laticínio mede o leite de todo o período. Diferenças grandes podem vir de leite do lote 10 ou de vacas em carência indo para o tanque, de vacas fora do controle ou da variação entre os dias.';
  const pr = ult.premiacoes||[];
  document.getElementById('tqPremNote').textContent = `Mapa de ${ult.mes} · total de premiações R$ ${fmt(ult.total_premiacoes,2)}`;
  document.getElementById('tqPrem').innerHTML = '<thead><tr><th>Indicador</th><th>% prêmio</th><th>R$/litro</th><th>Total (R$)</th></tr></thead><tbody>'+
    pr.map(x=>`<tr${/CCS|C\.P\.P/.test(x.indicador)?' style="font-weight:700"':''}><td class="l">${esc(x.indicador.replace(/\s+/g,' '))}</td><td>${fmt(x.pct,2)}%</td><td>${fmt(x.rs_litro,4)}</td><td>${fmt(x.total,2)}</td></tr>`).join('')+'</tbody>';
  // linha por período
  const per = []; TQM.forEach(m=>[1,2,3,4].forEach(p=>{ if(TQ.some(x=>x.mes===m&&x.per===p)) per.push([m,p]); }));
  const cats = per.map(([m,p])=>MESN[+m.slice(0,2)-1]+' '+p+'º');
  const tqs = [...new Set(TQ.map(x=>x.tq))].sort();
  const tcol = ['var(--g1)','var(--g2)','var(--g3)','var(--g4)','var(--g5)','var(--g6)'];
  chart('tqLine',{cats, label:'CCS por período', y:{title:'mil céls/mL', max:Math.max(600, Math.ceil(Math.max(...TQ.map(x=>x.CCS||0))/100)*100+100)}, h:280, series:[
    ...tqs.map((t,i)=>({name:'Tanque '+t, type:'line', data:per.map(([m,p])=>{ const x=TQ.find(y=>y.tq===t&&y.mes===m&&y.per===p); return x?x.CCS:null; }), color:tcol[i%6], width:1.3, labels:false, span:true})),
    {name:'Média ponderada', type:'line', data:per.map(([m,p])=>wavg(TQ.filter(y=>y.mes===m&&y.per===p),'CCS')), color:'var(--fg)', width:3, lbl:v=>fmt(v)}]});
  const grid = (k, hi, md, d) => '<thead><tr><th>Tanque</th>'+per.map(([m,p])=>`<th>${MESN[+m.slice(0,2)-1]}<br>${p}º</th>`).join('')+'</tr></thead><tbody>'+
    tqs.map(t=>`<tr><td>Tanque ${t}</td>`+per.map(([m,p])=>{ const x=TQ.find(y=>y.tq===t&&y.mes===m&&y.per===p); const v=x?x[k]:null; return `<td class="${v==null?'x':v>=hi?'hi':(md&&v>=md?'md':'')}" ${x?`data-tip="${esc('Tanque '+t+' · '+mesLab(m)+' '+p+'º período · '+fmt(x.vol)+' L · '+k+' '+(v==null?'sem análise':fmt(v,d)))}"`:''}>${v==null?'·':fmt(v,d)}</td>`; }).join('')+'</tr>').join('')+
    `<tr><td><b>Ponderada</b></td>`+per.map(([m,p])=>{ const v=wavg(TQ.filter(y=>y.mes===m&&y.per===p),k); return `<td><b>${v==null?'·':fmt(v,d)}</b></td>`; }).join('')+'</tr></tbody>';
  document.getElementById('tqCcs').innerHTML = grid('CCS',400,300,0).replace('<th>Tanque</th>','<th>CCS</th>');
  document.getElementById('tqCpp').innerHTML = grid('CPP',100,null,0).replace('<th>Tanque</th>','<th>CPP</th>');
  const K=[['CCS','CCS',0],['CPP','CPP',1],['GOR','GOR.',2],['PROT','PROT.',2],['SOL','SOL.',2],['UREIA','UREIA',2]];
  document.getElementById('tqComp').innerHTML = '<thead><tr><th>Análise</th>'+TQM.map(m=>`<th>${mesLab(m)}</th>`).join('')+'<th>Média Pagto</th><th>Média POOL</th></tr></thead><tbody>'+
    K.map(([k,mk,d])=>`<tr><td class="l">${mk.replace('.','')}</td>`+TQM.map(m=>{ const v=wavg(TQ.filter(y=>y.mes===m),k); return `<td>${v==null?'–':fmt(v,d)}</td>`; }).join('')+`<td><b>${fmt(ult.media_pagto[mk],d)}</b></td><td>${fmt(ult.media_pool[mk],d)}</td></tr>`).join('')+'</tbody>';
}
'''
j = s.index('function renderAll(){')
s = s[:j] + js + s[j:]
rep("else if(t==='cultura'){", "else if(t==='tanque') renderTanque(); else if(t==='cultura'){")
# Painel do mês: CCS real no 1º bloco
rep("'\"Média CCS tanque\" APCBRH (com lote 10): '+fmt(a.apcbrh)",
    "'\"Média CCS tanque\" APCBRH (com lote 10): '+fmt(a.apcbrh)+(()=>{ const m=ctrls[cur-1].date.slice(5,7)+'/'+ctrls[cur-1].date.slice(0,4); const v=TQM.includes(m)?realMes(m):null; return v!=null?' · <b>CCS real do tanque em '+mesLab(m)+' (laticínio): '+fmt(v)+'</b>':''; })()")
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(TQ), 'análises')
