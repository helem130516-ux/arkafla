import json, sys
src, dst, lj = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()
B = json.load(open(lj, encoding='utf-8'))
cu = [[a['amostra'], a['data'], a['vaca'], a['quartos'], a['grau'] or -1, a['lote'] or -1,
       a['agentes'], a['ident'], b['controle_lab']] for b in B for a in b['amostras']]

def rep(a, b, n=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, n)

# hbRows: opção de classe extra (rótulos longos)
rep("let h='<div class=\"hb\">';", "let h=`<div class=\"hb ${o.cls||''}\">`;")
rep("document.getElementById('cuTot').innerHTML = hbRows(ord.map(o=>({lb:`<span class=\"sw\" style=\"background:${o.g.c}\"></span>${o.a}`, v:o.n/N, color:o.g.c,\n    val:`<b>${pct(o.n/N)}</b> · ${o.n}`, tip:`${o.a}: ${o.n} culturas (${pct(o.n/N)}) · grupo ${o.g.k}`})), {});",
    "document.getElementById('cuTot').innerHTML = hbRows(ord.map(o=>({lb:`<span class=\"sw\" style=\"background:${o.g.c}\"></span>${o.a}`, v:o.n/N, color:o.g.c,\n    val:`<b>${pct(o.n/N)}</b> · ${o.n}`, tip:`${o.a}: ${o.n} culturas (${pct(o.n/N)}) · grupo ${o.g.k}`})), {cls:'wide'});")

# ---- markup: seção LabVet no topo da aba Cultura
lab = '''<section id="tab-cultura" class="grid" hidden>
    <div class="panel"><h2>Culturas por vaca – laboratório (LabVet, Carambeí)</h2>
      <p class="note" style="margin:0" id="lvIntro"></p></div>
    <div class="hero" id="lvHero"></div>
    <div class="grid g2">
      <div class="panel"><h2>Agentes isolados nas amostras</h2><p class="note" id="lvAgNote"></p><div id="lvAg"></div></div>
      <div class="panel"><h2>CCS da vaca no controle anterior à coleta</h2><p class="note">Por grupo de agente · barra = % das amostras com CCS ≥ 200 no último controle antes da coleta</p><div id="lvCcs"></div><p class="note" id="lvCcsNote" style="margin-top:10px"></p></div>
    </div>
    <div class="panel"><h2>Amostras e resultados</h2>
      <div class="row"><label class="lb" for="lvSel">Agente</label><select id="lvSel"></select><label class="lb" for="lvBol">Boletim</label><select id="lvBol"></select><span class="note" id="lvCount" style="margin:0"></span></div>
      <p class="note">Toque numa linha para abrir o histórico da vaca · CCS antes = último controle até a coleta · CCS depois = 1º controle após a coleta · mastite = tratamento iniciado de 7 dias antes a 7 dias depois da coleta</p>
      <div class="tbl scroll"><table id="lvTab"></table></div></div>
    <h2 style="font-family:var(--f-display);margin:10px 0 0">Resumo mensal do sistema OnFarm</h2>
'''
rep('<section id="tab-cultura" class="grid" hidden>\n', lab)
rep('<h2>Cultura microbiológica na fazenda (OnFarm)</h2>', '<h2>Cultura microbiológica na fazenda (OnFarm) – resumo por mês</h2>')

# ficha: tabela de culturas
rep('cultura: sem registros</p>', 'cultura: ver abaixo</p>')
rep('<div class="tbl"><table id="tblTrat"></table></div>',
    '<div class="tbl"><table id="tblTrat"></table></div>\n      <h2 id="cultTit" style="margin-top:16px">Culturas microbiológicas</h2>\n      <div class="tbl"><table id="tblCult"></table></div>')
rep("document.getElementById('tratTit').textContent = 'Tratamentos de mastite clínica: '+cs.length;",
    "document.getElementById('tratTit').textContent = 'Tratamentos de mastite clínica: '+cs.length;\n  fichaCult(v);")
rep("if(!h){ info.textContent='Vaca não encontrada nos controles.';",
    "if(!h){ fichaCult(v); info.textContent='Vaca não encontrada nos controles.'+((CUB[v]||[]).length?' Tem cultura registrada (abaixo).':'')+((CUB[document.getElementById('inVaca').value.trim()]||[]).length&&!(CUB[v]||[]).length?' Tem cultura registrada (abaixo).':'');")
rep('cultura microbiológica ainda não fornecida.</p>', 'cultura: boletins LabVet por vaca (jul–set/2026) e resumo mensal OnFarm, sem antibiograma.</p>')
rep("Cultura microbiológica: sem registros até o momento.",
    "Cultura microbiológica: ${cultResumo()}")

css = '''
.hb.wide{grid-template-columns:minmax(120px,max-content) minmax(60px,1fr) auto}
@media (max-width:560px){.hb.wide{grid-template-columns:minmax(0,max-content) minmax(40px,1fr) auto}.hb.wide .lb{white-space:normal}}
td.ag{text-align:left;white-space:normal;min-width:170px}
'''
rep('/* ---- Cultura ---- */', '/* ---- Cultura ---- */' + css)

js = r'''
// ---------- culturas LabVet (por vaca) ----------
const CU = ''' + json.dumps(cu, ensure_ascii=False) + r'''.map(a=>({am:a[0],data:a[1],vaca:a[2],q:a[3],grau:a[4],lote:a[5],ag:a[6],ident:a[7],bol:a[8]}));
const LVGRP = {'Streptococcus dysgalactiae':0,'Staphylococcus aureus':1,'Staphylococcus sp.':2,'Streptococcus uberis':3,
  'Escherichia coli':4,'Klebsiella sp.':4,'Serratia sp.':4,'Streptococcus bovis':5,'Streptococcus sp.':5,'Corynebacterium sp.':5,
  'Trueperella sp.':5,'Bacillus sp.':5,'Prototheca sp.':6,'Leveduras sp.':6};
const grpOf = a => CGRP[LVGRP[a]!=null?LVGRP[a]:5];
const CUB = {}; CU.forEach(c=>(CUB[c.vaca] ||= []).push(c));
const addD = (d,n) => { const x=new Date(d+'T12:00:00'); x.setDate(x.getDate()+n); return x.toISOString().slice(0,10); };
function cuCtx(c){
  const h = byCow[c.vaca]||[];
  const bef = h.filter(r=>ctrls[r.ci-1].date<=c.data).pop(), aft = h.find(r=>ctrls[r.ci-1].date>c.data);
  const tr = (casesBy[c.vaca]||[]).filter(t=>t.ini>=addD(c.data,-7) && t.ini<=addD(c.data,7));
  return {bef, aft, tr};
}
const agTxt = c => c.ag.length ? c.ag.map(a=>a.replace(/\s*sp\.$/,' sp.')).join(' + ') : 'Sem crescimento';
function cultResumo(){
  const hi = ctrls[cur-1].date, lo = cur>1 ? ctrls[cur-2].date : '0000';
  const x = CU.filter(c=>c.data>lo && c.data<=hi);
  if(!x.length) return 'nenhuma amostra LabVet coletada neste intervalo entre controles.';
  const cnt = {}; x.forEach(c=>c.ag.forEach(a=>cnt[a]=(cnt[a]||0)+1));
  const top = Object.entries(cnt).sort((a,b)=>b[1]-a[1]).slice(0,3).map(([a,n])=>a+' ('+n+')').join(', ');
  return `${x.length} amostras LabVet neste intervalo, ${x.filter(c=>!c.ag.length).length} sem crescimento; mais frequentes: ${top}. Sem antibiograma.`;
}
function fichaCult(v){
  const cs = CUB[v]||CUB[document.getElementById('inVaca').value.trim()]||[];
  document.getElementById('cultTit').textContent = 'Culturas microbiológicas: '+cs.length;
  document.getElementById('tblCult').innerHTML = cs.length ? '<thead><tr><th>Coleta</th><th>Quartos</th><th>Grau</th><th class="l">Agente(s)</th><th>CCS antes</th><th>CCS depois</th><th class="l">Mastite ±7 d</th></tr></thead><tbody>'+
    cs.map(c=>{ const k=cuCtx(c); return `<tr><td>${fmtD(c.data)}</td><td class="l">${c.q||c.ident||'–'}</td><td>${c.grau>0?c.grau:'–'}</td><td class="ag">${agTxt(c)}</td><td class="${k.bef&&k.bef.ccs>=LIM?'hot':''}">${k.bef?fmt(k.bef.ccs)+' <small>('+lab(ctrls[k.bef.ci-1])+')</small>':'–'}</td><td class="${k.aft&&k.aft.ccs>=LIM?'hot':''}">${k.aft?fmt(k.aft.ccs)+' <small>('+lab(ctrls[k.aft.ci-1])+')</small>':'–'}</td><td class="l">${k.tr.length?k.tr.map(t=>fmtD(t.ini)+' '+t.prod).join('; '):'–'}</td></tr>`; }).join('')+'</tbody>'
    : '<tbody><tr><td class="l">Nenhuma cultura registrada para esta vaca (boletins LabVet de jul–set/2026).</td></tr></tbody>';
}
let lvAg = '', lvBol = '';
function renderLabvet(){
  const N = CU.length, pos = CU.filter(c=>c.ag.length), neg = N-pos.length, mix = CU.filter(c=>c.ag.length>1).length;
  const bols = [...new Set(CU.map(c=>c.bol))], datas = [...new Set(CU.map(c=>c.data))].sort();
  const naoCtrl = CU.filter(c=>!byCow[c.vaca]);
  document.getElementById('lvIntro').textContent = `${N} amostras de leite em ${bols.length} boletins (${datas.map(fmtD).join(', ')}/2026). Identificação: quarto, grau da mastite (G1 a G3, quando informado) e lote. Não há antibiograma. ${naoCtrl.length} amostras não se ligam aos controles: ${naoCtrl.map(c=>c.vaca).join(', ')}.`;
  const iso = {}; CU.forEach(c=>c.ag.forEach(a=>iso[a]=(iso[a]||0)+1));
  const ord = Object.entries(iso).sort((a,b)=>b[1]-a[1]);
  const tile = (t,v,sub) => `<div class="htile"><span class="k">${t}</span><div class="row1"><span class="v">${v}</span></div><span class="s">${sub}</span></div>`;
  const ctg = CU.filter(c=>c.ag.some(a=>a==='Staphylococcus aureus'||a==='Streptococcus dysgalactiae')).length;
  const pro = CU.filter(c=>c.ag.some(a=>a==='Prototheca sp.'||a==='Leveduras sp.')).length;
  document.getElementById('lvHero').innerHTML =
    tile('Amostras analisadas', fmt(N), `${fmt(pos.length)} com crescimento · ${fmt(neg)} sem crescimento (${pct(neg/N,0)}) · ${mix} com 2 agentes`) +
    tile('Strep. dysgalactiae ou Staph. aureus', pct(ctg/N,0), `${ctg} amostras · agentes que passam de vaca para vaca na ordenha`) +
    tile('Staphylococcus sp. (não aureus)', pct(CU.filter(c=>c.ag.includes('Staphylococcus sp.')).length/N,0), `${CU.filter(c=>c.ag.includes('Staphylococcus sp.')).length} amostras · mais frequente`) +
    tile('Prototheca / leveduras', pct(pro/N,0), `${pro} amostras · não respondem a antibiótico`);
  document.getElementById('lvAgNote').textContent = `Nº de amostras com o agente (uma amostra pode ter 2) · % sobre as ${N} amostras · cor = grupo (legenda do OnFarm)`;
  document.getElementById('lvAg').innerHTML = hbRows(ord.map(([a,n])=>({lb:`<span class="sw" style="background:${grpOf(a).c}"></span>${a}`, v:n/N, color:grpOf(a).c,
      val:`<b>${pct(n/N,0)}</b> · ${n}`, tip:`${a}: ${n} de ${N} amostras (${pct(n/N)}) · grupo ${grpOf(a).k}`})).concat([{lb:'<span class="sw" style="background:var(--grey)"></span>Sem crescimento', v:neg/N, color:'var(--grey)', val:`<b>${pct(neg/N,0)}</b> · ${neg}`, tip:`Sem crescimento: ${neg} amostras`}]), {cls:'wide'});
  // CCS antes por grupo
  const gs = CGRP.map((g,i)=>{ const x = CU.filter(c=>c.ag.some(a=>grpOf(a)===g)).map(cuCtx).filter(k=>k.bef); return {g, n:x.length, el:x.filter(k=>k.bef.ccs>=LIM).length}; })
    .concat([{g:{k:'Sem crescimento',c:'var(--grey)'}, ...(()=>{ const x=CU.filter(c=>!c.ag.length).map(cuCtx).filter(k=>k.bef); return {n:x.length, el:x.filter(k=>k.bef.ccs>=LIM).length}; })()}]).filter(o=>o.n);
  document.getElementById('lvCcs').innerHTML = hbRows(gs.map(o=>({lb:`<span class="sw" style="background:${o.g.c}"></span>${o.g.k}`, v:o.el/o.n, color:o.g.c,
      val:`<b>${pct(o.el/o.n,0)}</b> · ${o.el} de ${o.n}`, tip:`${o.g.k}: ${o.el} de ${o.n} amostras de vacas já com CCS ≥ 200 no controle anterior`})), {max:1, cls:'wide'});
  const semCtx = CU.filter(c=>!cuCtx(c).bef).length;
  document.getElementById('lvCcsNote').textContent = `${semCtx} amostras ficam fora: a vaca não tem controle antes da coleta ou não aparece nos controles. CCS alta antes da coleta sugere infecção antiga, com mais chance de ser crônica.`;
  // filtros
  const sA = document.getElementById('lvSel'), sB = document.getElementById('lvBol');
  if(!sA.options.length){
    sA.innerHTML = '<option value="">Todos</option>'+ord.map(([a,n])=>`<option value="${esc(a)}">${esc(a)} (${n})</option>`).join('')+`<option value="-">Sem crescimento (${neg})</option>`;
    sB.innerHTML = '<option value="">Todos</option>'+bols.map(b=>{ const d=CU.find(c=>c.bol===b).data; return `<option value="${b}">${fmtD(d)} · nº ${b}</option>`; }).join('');
    sA.addEventListener('change',()=>{lvAg=sA.value; renderLabvet();}); sB.addEventListener('change',()=>{lvBol=sB.value; renderLabvet();});
  }
  const L = CU.filter(c=>(!lvAg || (lvAg==='-'?!c.ag.length:c.ag.includes(lvAg))) && (!lvBol || c.bol===lvBol)).slice().sort((a,b)=>b.data.localeCompare(a.data)||String(a.vaca).localeCompare(String(b.vaca),undefined,{numeric:true}));
  document.getElementById('lvCount').textContent = L.length+' amostras';
  document.getElementById('lvTab').innerHTML = '<thead><tr><th>Coleta</th><th>Vaca</th><th>Quartos</th><th>Grau</th><th>Lote</th><th class="l">Agente(s)</th><th>CCS antes</th><th>CCS depois</th><th class="l">Classe no controle antes</th><th class="l">Mastite ±7 d</th></tr></thead><tbody>'+
    L.map(c=>{ const k=cuCtx(c); return `<tr class="click" data-v="${esc(c.vaca)}"><td>${fmtD(c.data)}</td><td>${esc(c.vaca)}</td><td class="l">${c.q||(c.ident==='-'?'–':esc(c.ident))}</td><td>${c.grau>0?c.grau:'–'}</td><td>${c.lote>0?c.lote:(k.bef?k.bef.lote:'–')}</td><td class="ag">${c.ag.length?c.ag.map(a=>`<span class="sw" style="background:${grpOf(a).c};margin-right:4px"></span>${a}`).join('<br>'):'<span style="color:var(--muted)">Sem crescimento</span>'}</td><td class="${k.bef&&k.bef.ccs>=LIM?'hot':''}">${k.bef?fmt(k.bef.ccs):'–'}</td><td class="${k.aft&&k.aft.ccs>=LIM?'hot':''}">${k.aft?fmt(k.aft.ccs):'–'}</td><td class="l">${k.bef?pill(k.bef.cls):'–'}</td><td class="l">${k.tr.length?k.tr.map(t=>fmtD(t.ini)+' '+esc(t.prod)).join('<br>'):'–'}</td></tr>`; }).join('')+'</tbody>';
}
document.getElementById('lvTab').addEventListener('click',e=>{ const tr=e.target.closest('tr[data-v]'); if(!tr) return; document.getElementById('inVaca').value=tr.dataset.v; showTab('ficha'); });
'''
j = s.index('function renderAll(){')
s = s[:j] + js + s[j:]
rep("else if(t==='cultura') renderCultura();", "else if(t==='cultura'){ renderLabvet(); renderCultura(); }")
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(cu))
