import re, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()

# ---- 1. markup da aba Painel do mês
old_sec = s[s.index('<section id="tab-painel"'):s.index('<section id="tab-evolucao"')]
new_sec = '''<section id="tab-painel" class="grid">
    <div class="hero" id="hero"></div>
    <div class="kpis kpis-sm" id="kpis"></div>
    <div class="grid g2">
      <div class="panel"><h2>Faixas de CCS no controle</h2><p class="note" id="faixaNote"></p><div id="chFaixa"></div></div>
      <div class="panel"><h2>Classificação sanitária no controle</h2><p class="note">% das vacas com CCS neste controle e no anterior</p><div id="chClasseMes"></div></div>
      <div class="panel"><h2>Lotes: vacas com CCS ≥ 200</h2><p class="note" id="lotesMesNote"></p><div id="chLotesMes"></div></div>
      <div class="panel"><h2>10 maiores contribuições para a CCS do tanque</h2><p class="note">Sem o lote 10 · % da soma produção × CCS · toque numa vaca para abrir o histórico</p><div id="chTopMes"></div></div>
    </div>
  </section>

  '''
s = s.replace(old_sec, new_sec)

# ---- 2. estilos
css = '''
/* ---- Painel do mês: blocos visuais ---- */
:root{--fx1:#c9d1cb;--fx2:#eeb08a;--fx3:#d9713c;--fx4:#a8322b;--track:#edf0ec;--mark:#1d2621;--fxt2:#1d2621}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--fx1:#4a5750;--fx2:#8c5a3c;--fx3:#d07445;--fx4:#f07a6f;--track:#243029;--mark:#e6ebe7;--fxt2:#fff}}
:root[data-theme="dark"]{--fx1:#4a5750;--fx2:#8c5a3c;--fx3:#d07445;--fx4:#f07a6f;--track:#243029;--mark:#e6ebe7;--fxt2:#fff}
.hero{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
@media (max-width:980px){.hero{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:480px){.hero{grid-template-columns:minmax(0,1fr)}}
.htile{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px 10px;display:flex;flex-direction:column;gap:4px;min-width:0}
.htile .k{font-size:.74rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600}
.htile .row1{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.htile .v{font-family:var(--f-display);font-weight:800;font-size:2.15rem;line-height:1.05;font-variant-numeric:tabular-nums}
.htile .u{font-size:.85rem;color:var(--muted)}
.htile .s{font-size:.84rem;color:var(--muted);font-variant-numeric:tabular-nums}
.spark svg{display:block;width:100%;height:auto;overflow:visible}
.chip{display:inline-flex;align-items:center;gap:4px;font-size:.8rem;font-weight:600;padding:1px 8px;border-radius:999px;border:1px solid currentColor;white-space:nowrap;font-variant-numeric:tabular-nums}
.chip.up-bad,.chip.down-bad{color:var(--crit)} .chip.up-good,.chip.down-good{color:var(--good)} .chip.flat{color:var(--muted)}
.kpis-sm{grid-template-columns:repeat(4,minmax(0,1fr))}
@media (max-width:760px){.kpis-sm{grid-template-columns:repeat(2,minmax(0,1fr))}}
.kpis-sm .kpi .v{font-size:1.3rem}
.kpis-sm .kpi .k{min-height:0}
.strip{display:flex;gap:2px;height:30px;margin:4px 0 14px}
.strip span{display:flex;align-items:center;justify-content:center;font-size:.78rem;font-weight:700;min-width:0;overflow:hidden;white-space:nowrap;font-variant-numeric:tabular-nums}
.strip span:first-child{border-radius:4px 0 0 4px}.strip span:last-child{border-radius:0 4px 4px 0}
.hb{display:grid;grid-template-columns:minmax(84px,120px) minmax(0,1fr) minmax(118px,auto);gap:4px 12px;align-items:center}
.hb .lb{font-size:.88rem;color:var(--fg);display:flex;align-items:center;gap:6px;min-width:0;white-space:nowrap}
.hb .lb small{color:var(--muted);font-size:.76rem}
.hb .tr{position:relative;height:20px;background:var(--track);border-radius:0 4px 4px 0}
.hb .br{position:absolute;left:0;top:0;bottom:0;border-radius:0 4px 4px 0;min-width:2px}
.hb .pv{position:absolute;top:-4px;bottom:-4px;width:2px;margin-left:-1px;background:var(--mark);opacity:.6;border-radius:1px}
.hb .rf{position:absolute;top:-6px;bottom:-6px;border-left:2px dashed var(--muted)}
.hb .vl{font-size:.86rem;font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
.hb .vl b{font-weight:700}.hb .vl small{color:var(--muted);font-size:.76rem;margin-left:4px}
.hb .rw{display:contents}
.hb .rw:hover>*{background-color:transparent}
.hb .rw[data-v]{cursor:pointer}
.hb .rw[data-v]:hover .lb{text-decoration:underline}
.sw{width:10px;height:10px;border-radius:2px;display:inline-block;flex:none;border:1px solid transparent}
.lgd{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.78rem;color:var(--muted);margin-top:12px}
.lgd i{display:inline-block;vertical-align:middle;margin-right:5px}
.lgd .pvk{width:2px;height:12px;background:var(--mark);opacity:.6}
.lgd .rfk{width:0;height:12px;border-left:2px dashed var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.chips span{display:inline-flex;align-items:center;gap:6px;font-size:.8rem;color:var(--fg);border:1px solid var(--line);border-radius:999px;padding:2px 10px}
.hatch{background-image:repeating-linear-gradient(135deg,transparent 0 4px,rgba(255,255,255,.55) 4px 6px)}
.tag{font-size:.68rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);border:1px solid var(--line);border-radius:4px;padding:0 4px}
.foot2{font-size:.82rem;color:var(--muted);margin-top:12px}
.foot2 b{color:var(--fg)}
.tip{position:fixed;z-index:50;pointer-events:none;background:var(--fg);color:var(--bg);font-size:.8rem;line-height:1.35;padding:6px 9px;border-radius:6px;max-width:260px;box-shadow:0 4px 14px rgba(0,0,0,.18)}
@media (max-width:560px){.hb{grid-template-columns:auto minmax(40px,1fr) auto;gap:4px 8px}.hb .vl small,.hb .lb small{display:none}.hb .lb,.hb .vl{font-size:.8rem}}
@media print{.tip{display:none!important}}
'''
s = s.replace('@media (prefers-reduced-motion:reduce)', css + '@media (prefers-reduced-motion:reduce)', 1)

# ---- 3. JS: nova renderPainel
i0 = s.index('function renderPainel(){')
i1 = s.index('\n}\n', i0) + 3
js = r'''const sgn=(d,dec)=>{ const r=+d.toFixed(dec); return r===0?'= 0':(r>0?'+':'−')+fmt(Math.abs(r),dec); };
function deltaChip(val, pv, isPct, dec, upGood){
  if(val==null || pv==null) return '';
  let diff = isPct ? (val-pv)*100 : val-pv; const r = +diff.toFixed(isPct?1:dec);
  if(r===0) return `<span class="chip flat" title="sem variação">= 0${isPct?' p.p.':''}</span>`;
  const up = r>0, cls = up ? (upGood?'up-good':'up-bad') : (upGood?'down-bad':'down-good');
  return `<span class="chip ${cls}">${up?'▲':'▼'} ${up?'+':'−'}${fmt(Math.abs(r), isPct?1:dec)}${isPct?' p.p.':''}</span>`;
}
function sparkM(vals, ci, isPct){
  const W=220, H=46, p=6, pts=vals.map((v,i)=>v==null?null:[i,v]).filter(Boolean);
  if(pts.length<2) return '';
  const vs=pts.map(q=>q[1]), mn=Math.min(...vs), mx=Math.max(...vs), rg=(mx-mn)||1;
  const X=i=>p+(W-2*p)*i/(vals.length-1), Y=v=>H-p-(H-2*p-8)*(v-mn)/rg;
  const d=pts.map((q,j)=>(j?'L':'M')+X(q[0]).toFixed(1)+' '+Y(q[1]).toFixed(1)).join(' ');
  const c=vals[ci-1], f=v=>isPct?pct(v):fmt(v);
  let g=`<svg viewBox="0 0 ${W} ${H}" aria-hidden="true"><path d="${d}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" opacity=".85"/>`;
  pts.forEach(q=>{ g+=`<circle cx="${X(q[0])}" cy="${Y(q[1])}" r="${q[0]===ci-1?4.5:2.2}" fill="${q[0]===ci-1?'var(--accent)':'var(--surface)'}" stroke="var(--accent)" stroke-width="${q[0]===ci-1?2:1.4}" ${q[0]===ci-1?'':''}/>`; });
  if(c!=null) g+=`<text x="${X(ci-1)}" y="${Y(c)-8}" text-anchor="${ci-1>vals.length-2?'end':ci-1<1?'start':'middle'}" font-size="10.5" font-weight="700" fill="var(--fg)" paint-order="stroke" stroke="var(--surface)" stroke-width="3">${f(c)}</text>`;
  g+=`<text x="${p}" y="${H}" font-size="9.5" fill="var(--muted)">${lab(ctrls[pts[0][0]])}</text><text x="${W-p}" y="${H}" text-anchor="end" font-size="9.5" fill="var(--muted)">${lab(ctrls[pts[pts.length-1][0]])}</text>`;
  return g+'</svg>';
}
function hbRows(rows, o){ // rows: {lb, v, pv, color, val, sub, tip, cls, data}
  const mx = o.max || Math.max(...rows.map(r=>Math.max(r.v, r.pv||0)))*1.08 || 1;
  let h='<div class="hb">';
  rows.forEach(r=>{ const w=100*r.v/mx;
    h+=`<div class="rw"${r.data?` data-v="${r.data}"`:''} data-tip="${esc(r.tip||'')}"><div class="lb">${r.lb}</div><div class="tr"><div class="br ${r.cls||''}" style="width:${w.toFixed(2)}%;background-color:${r.color}"></div>${r.pv!=null?`<div class="pv" style="left:${(100*r.pv/mx).toFixed(2)}%"></div>`:''}${o.ref!=null?`<div class="rf" style="left:${(100*o.ref/mx).toFixed(2)}%"></div>`:''}</div><div class="vl">${r.val}${r.sub?`<small>${r.sub}</small>`:''}</div></div>`; });
  return h+'</div>';
}
function strip(parts){ // parts: {w, color, txt, tip, textColor}
  const t=parts.reduce((s,q)=>s+q.w,0)||1;
  return '<div class="strip">'+parts.filter(q=>q.w>0).map(q=>`<span style="flex:${q.w/t} 1 0;background:${q.color};color:${q.textColor||'#fff'}" data-tip="${esc(q.tip)}">${q.w/t>=.07?q.txt:''}</span>`).join('')+'</div>';
}
function renderPainel(){
  const a = A[cur-1], p = A[cur-2], pl = p ? lab(ctrls[cur-2]) : null;
  const ser = f => A.map(x=>x?f(x):null);
  // ---- blocos principais com tendência
  const hero = [
    ['CCS estimada do tanque sem lote 10', fmt(a.semDesvio), 'mil/mL', deltaChip(a.semDesvio,p&&p.semDesvio,false,0,false), '"Média CCS tanque" APCBRH (com lote 10): '+fmt(a.apcbrh), sparkM(ser(x=>x.semDesvio),cur,false)],
    ['Vacas com CCS ≥ 200', pct(a.ge200), '', deltaChip(a.ge200,p&&p.ge200,true,1,false), fmt(a.f[1]+a.f[2]+a.f[3])+' de '+fmt(a.n)+' vacas', sparkM(ser(x=>x.ge200),cur,true)],
    ['Novas infecções', a.first?'–':pct(a.cnt.N/a.n4), '', a.first?'':deltaChip(a.cnt.N/a.n4,p&&!p.first?p.cnt.N/p.n4:null,true,1,false), a.first?'sem controle anterior':a.cnt.N+' vacas · taxa '+pct(a.taxaNI), sparkM(ser(x=>x.first?null:x.cnt.N/x.n4),cur,true)],
    ['Crônicas', a.first?'–':pct(a.cnt.C/a.n4), '', a.first?'':deltaChip(a.cnt.C/a.n4,p&&!p.first?p.cnt.C/p.n4:null,true,1,false), a.first?'sem controle anterior':a.cnt.C+' vacas · permanência '+pct(a.perman), sparkM(ser(x=>x.first?null:x.cnt.C/x.n4),cur,true)],
  ];
  document.getElementById('hero').innerHTML = hero.map(([t,v,u,d,sub,sp])=>`<div class="htile"><span class="k">${t}</span><div class="row1"><span class="v">${v}</span>${u?`<span class="u">${u}</span>`:''}${d}</div><span class="s">${sub}${pl&&d?' · vs. '+pl:''}</span><div class="spark">${sp}</div></div>`).join('');
  // ---- indicadores secundários
  const k = [
    ['CCS média do rebanho', fmt(a.arit), a.arit, p&&p.arit, 'geométrica '+fmt(a.geo)+' · mil/mL', false, 0],
    ['% vacas sadias', a.first?'–':pct(a.cnt.S/a.n4), a.first?null:a.cnt.S/a.n4, p&&!p.first?p.cnt.S/p.n4:null, a.first?'sem controle anterior':a.cnt.S+' de '+fmt(a.n4)+' vacas', true, 1],
    ['% recuperadas', a.first?'–':pct(a.cnt.R/a.n4), a.first?null:a.cnt.R/a.n4, p&&!p.first?p.cnt.R/p.n4:null, a.first?'':a.cnt.R+' vacas', true, 1],
    ['% CCS ≥ 500', pct(a.ge500), a.ge500, p&&p.ge500, a.f[2]+a.f[3]+' vacas', false, 1],
    ['% CCS ≥ 1.000', pct(a.ge1000), a.ge1000, p&&p.ge1000, a.f[3]+' vacas', false, 1],
    ['Produção média', fmt(a.prod,1), a.prod, p&&p.prod, 'kg/vaca/dia', true, 1],
    ['Elevada ≥ 2 controles seguidos', fmt(a.seq2), a.seq2, p&&p.seq2, fmt(a.seq3)+' com ≥ 3 seguidos', false, 0],
    ['Tratamentos de mastite', a.first?'–':fmt(a.clin), a.first?null:a.clin, p&&!p.first?p.clin:null, a.first?'desde 01/01: '+casesPeriod(1).length:fmt(a.clin/a.n*100*30/a.intervalo,1)+' por 100 vacas/30 d', false, 0],
  ];
  document.getElementById('kpis').innerHTML = k.map(([t,v,val,pv,sub,upGood,dec])=>
    `<div class="kpi"><span class="k">${t}</span><span class="v">${v}</span><span class="d">${deltaChip(val,pv,t.startsWith('%'),dec,upGood)||'&nbsp;'}</span><span class="d flat">${sub}</span></div>`).join('');
  const prevLg = pl ? `<span><i class="pvk"></i>controle anterior (${pl})</span>` : '';

  // ---- faixas de CCS
  const FX=['< 200','200–499','500–999','≥ 1.000'], FC=['var(--fx1)','var(--fx2)','var(--fx3)','var(--fx4)'], FT=['var(--fg)','var(--fxt2)','#fff','#fff'];
  document.getElementById('faixaNote').textContent = fmt(a.n)+' vacas no controle · mil células/mL';
  document.getElementById('chFaixa').innerHTML =
    strip(a.f.map((v,i)=>({w:v,color:FC[i],txt:pct(v/a.n,0),textColor:FT[i],tip:FX[i]+': '+fmt(v)+' vacas ('+pct(v/a.n)+')'}))) +
    hbRows(a.f.map((v,i)=>({lb:`<span class="sw" style="background:${FC[i]}"></span>${FX[i]}`, v, pv:p?p.f[i]:null, color:FC[i],
      val:`<b>${fmt(v)}</b> · ${pct(v/a.n)}`, sub:p?sgn(v-p.f[i],0):'',
      tip:`${FX[i]}: ${fmt(v)} vacas (${pct(v/a.n)})`+(p?` · ${pl}: ${fmt(p.f[i])} (${pct(p.f[i]/p.n)})`:'')})), {}) +
    `<div class="lgd"><span>barra = nº de vacas neste controle${pl?' · ± = variação em vacas vs. '+pl:''}</span>${prevLg}</div>`;

  // ---- classificação sanitária
  const box = document.getElementById('chClasseMes');
  if(a.first){ box.innerHTML='<p class="note">Primeiro controle: sem controle anterior para comparar.</p>'; }
  else {
    const K=['S','R','N','C'], share=q=>q.cnt; 
    box.innerHTML = strip(K.map(c=>({w:a.cnt[c],color:clsColor(c),textColor:clsText(c),txt:pct(a.cnt[c]/a.n4,0),tip:CL[c]+': '+a.cnt[c]+' vacas ('+pct(a.cnt[c]/a.n4)+')'}))) +
      hbRows(K.map(c=>{ const v=a.cnt[c]/a.n4, pv=p&&!p.first?p.cnt[c]/p.n4:null;
        return {lb:`<span class="sw" style="background:${clsColor(c)}"></span>${CL[c]}`, v, pv, color:clsColor(c),
          val:`<b>${pct(v)}</b> · ${fmt(a.cnt[c])}`, sub: pv!=null?sgn((v-pv)*100,1)+' p.p.':'',
          tip:`${CL[c]}: ${pct(v)} (${a.cnt[c]} vacas)`+(pv!=null?` · ${pl}: ${pct(pv)} (${p.cnt[c]} vacas)`:'')}; }), {}) +
      `<div class="lgd"><span>base: <b style="color:var(--fg)">${fmt(a.n4)}</b> vacas</span>${prevLg}</div>` +
      `<div class="chips"><span style="border:0;padding-left:0;color:var(--muted)">Fora da base:</span><span><i class="sw" style="background:var(--cs-PB)"></i>${a.cnt.PB} pós-parto baixa</span><span><i class="sw" style="background:var(--cs-PE)"></i>${a.cnt.PE} pós-parto elevada</span><span><i class="sw" style="background:var(--cs-H);border-color:#9aa39d"></i>${a.cnt.H} sem histórico</span></div>`;
  }

  // ---- lotes
  const rows = byCi[cur] || [], L = {};
  const totC = rows.filter(r=>r.lote!==DESVIO).reduce((s,r)=>s+r.prod*r.ccs,0);
  rows.forEach(r=>{ const o=(L[r.lote] ||= {n:0,el:0,ni:0,c:0,pc:0}); o.n++; if(r.ccs>=LIM) o.el++; if(r.cls==='N') o.ni++; if(r.cls==='C') o.c++; o.pc+=r.prod*r.ccs; });
  const lotes = Object.entries(L).map(([l,o])=>({l:+l,...o,pe:o.el/o.n})).sort((x,y)=>y.pe-x.pe||x.l-y.l);
  document.getElementById('lotesMesNote').textContent = 'Barra = % das vacas do lote com CCS ≥ 200 · valor = vacas elevadas de vacas no lote · linha tracejada = rebanho ('+pct(a.ge200)+')';
  document.getElementById('chLotesMes').innerHTML = hbRows(lotes.map(o=>({
      lb:`Lote ${o.l}`, v:o.pe, color:o.l===DESVIO?'var(--grey)':'var(--accent)', cls:o.l===DESVIO?'hatch':'',
      val:`<b>${pct(o.pe,0)}</b> · ${o.el} de ${o.n}`, sub: o.l===DESVIO?'desviado':pct(o.pc/totC,0)+' do tanque',
      tip:`Lote ${o.l}: ${o.el} de ${o.n} vacas com CCS ≥ 200 (${pct(o.pe)}) · ${o.ni} novas infecções · ${o.c} crônicas`+(o.l===DESVIO?' · leite desviado':` · ${pct(o.pc/totC)} da CCS estimada do tanque`)})), {max:1, ref:a.ge200}) +
    `<div class="lgd"><span><i class="sw" style="background:var(--accent)"></i>lote que vai para o tanque</span><span><i class="sw hatch" style="background-color:var(--grey)"></i>lote 10 (tratamento)</span><span><i class="rfk"></i>média do rebanho</span></div>`;

  // ---- top 10 contribuições
  const top = rows.filter(r=>r.lote!==DESVIO).map(r=>({...r,pc:r.prod*r.ccs})).sort((x,y)=>y.pc-x.pc).slice(0,10);
  const sp = rows.filter(r=>r.lote!==DESVIO).reduce((s,r)=>s+r.prod,0);
  const tPc = top.reduce((s,r)=>s+r.pc,0), tP = top.reduce((s,r)=>s+r.prod,0);
  document.getElementById('chTopMes').innerHTML = hbRows(top.map(r=>({
      lb:`${r.vaca}<small>lote ${r.lote}</small>`, v:r.pc/totC, color:clsColor(r.cls), data:r.vaca,
      val:`<b>${pct(r.pc/totC)}</b> · ${fmt(r.ccs)}`, sub:fmt(r.prod,1)+' kg',
      tip:`Vaca ${r.vaca} · lote ${r.lote} · ${CL[r.cls]} · CCS ${fmt(r.ccs)} · ${fmt(r.prod,1)} kg · ${pct(r.pc/totC)} da CCS estimada do tanque`+(r.seq>=2?` · ${r.seq} controles seguidos elevada`:'')})), {}) +
    `<div class="lgd">${['C','N','H','PE','R','S','PB'].filter(c=>top.some(r=>r.cls===c)).map(c=>`<span><i class="sw" style="background:${clsColor(c)};${c==='H'?'border-color:#9aa39d':''}"></i>${CL[c]}</span>`).join('')}<span>valor = % do tanque · CCS</span></div>` +
    `<p class="foot2">Estas 10 vacas somam <b>${pct(tPc/totC)}</b> da CCS estimada do tanque com <b>${pct(tP/sp)}</b> do leite. Sem elas, a estimativa cairia de <b>${fmt(a.semDesvio)}</b> para <b>${fmt((totC-tPc)/(sp-tP))}</b> mil/mL. Decisões com o veterinário.</p>`;
}
'''
s = s[:i0] + js + s[i1:]

# ---- 4. tooltip compartilhado + clique no top 10
tipjs = '''
// ---- tooltip compartilhado (hover no computador, toque no celular)
(()=>{ const tip=document.createElement('div'); tip.className='tip'; tip.hidden=true; document.body.appendChild(tip);
  const show=(el,x,y)=>{ const t=el.getAttribute('data-tip'); if(!t){tip.hidden=true;return;} tip.textContent=t; tip.hidden=false;
    const r=tip.getBoundingClientRect(); tip.style.left=Math.min(window.innerWidth-r.width-8,Math.max(8,x+12))+'px'; tip.style.top=Math.max(8,y-r.height-12)+'px'; };
  document.addEventListener('pointermove',e=>{ const el=e.target.closest&&e.target.closest('[data-tip]'); if(el) show(el,e.clientX,e.clientY); else tip.hidden=true; });
  document.addEventListener('scroll',()=>tip.hidden=true,{passive:true});
  document.getElementById('tab-painel').addEventListener('click',e=>{ const r=e.target.closest('[data-v]'); if(!r) return; document.getElementById('inVaca').value=r.dataset.v; showTab('ficha'); });
})();
'''
j = s.rindex('</script>')
s = s[:j] + tipjs + s[j:]
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
