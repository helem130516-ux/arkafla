import json, sys
src, dst, cj = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()
C = json.load(open(cj, encoding='utf-8'))
cult = {"agentes": C["agentes"], "meses": C["meses"], "n": [C["n"][m] for m in C["meses"]], "impresso": "11/09/2026"}

def rep(a, b, n=1):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, n)

rep('<button role="tab" data-tab="ficha" aria-selected="false">Histórico da vaca</button>',
    '<button role="tab" data-tab="ficha" aria-selected="false">Histórico da vaca</button>\n    <button role="tab" data-tab="cultura" aria-selected="false">Cultura</button>')

sec = '''<section id="tab-cultura" class="grid" hidden>
    <div class="panel"><h2>Cultura microbiológica na fazenda (OnFarm)</h2>
      <p class="note" style="margin:0">Resultados com agente isolado, agregados por mês (out/2025 a set/2026; setembro parcial, relatório impresso em 11/09/2026). O relatório não traz vaca, quarto, data da coleta nem antibiograma, por isso não dá para ligar os resultados às vacas, à CCS ou ao registro de mastite. As amostras sem crescimento não aparecem.</p></div>
    <div class="hero" id="cuHero"></div>
    <div class="panel"><h2>Agentes isolados por mês</h2>
      <div class="row"><div class="seg" id="segCult" role="group" aria-label="Escala"><button data-m="n" aria-pressed="true">Nº de culturas</button><button data-m="p" aria-pressed="false">% do mês</button></div></div>
      <div class="lgd" id="cuLeg" style="margin:0 0 12px"></div>
      <div id="cuMes"></div>
      <p class="note" style="margin-top:10px">Grupos: Gram-negativos = E. coli, Klebsiella/Enterobacter, Serratia, Pseudomonas e outros Gram-negativos · Outros Gram-positivos = outros Gram-positivos, Enterococcus e Lactococcus.</p></div>
    <div class="grid g2">
      <div class="panel"><h2>Agentes no período</h2><p class="note" id="cuTotNote"></p><div id="cuTot"></div></div>
      <div class="panel"><h2>Culturas × tratamentos de mastite clínica</h2><p class="note">Por mês. Tratamentos = registro da fazenda (início no mês). As duas fontes não se ligam por vaca.</p><div class="tbl"><table id="cuTrat"></table></div><p class="note" id="cuTratNote" style="margin-top:8px"></p></div>
    </div>
    <div class="panel"><h2>Tabela de agentes por mês</h2><p class="note">Nº de culturas com o agente · última coluna = % do total do período</p><div class="tbl"><table id="cuTab"></table></div>
      <p class="note" style="margin-top:8px">Transcrito do gráfico OnFarm e conferido pelo comprimento das barras. No PDF, "Outros Gram-pos" e "Staph não aureus" têm a mesma cor, assim como "Klebsiella/Enterobacter" e "Strep. uberis". Por isso, esses agentes foram separados pela ordem em que aparecem empilhados na barra.</p></div>
  </section>

  '''
rep('<section id="tab-impressao"', sec + '<section id="tab-impressao"')

css = '''
/* ---- Cultura ---- */
:root{--g1:#2a78d6;--g2:#eb6834;--g3:#1baf7a;--g4:#eda100;--g5:#e87ba4;--g6:#008300;--g7:#4a3aa7}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--g1:#3987e5;--g2:#d95926;--g3:#199e70;--g4:#c98500;--g5:#d55181;--g6:#008300;--g7:#9085e9}}
:root[data-theme="dark"]{--g1:#3987e5;--g2:#d95926;--g3:#199e70;--g4:#c98500;--g5:#d55181;--g6:#008300;--g7:#9085e9}
.sb{display:grid;grid-template-columns:64px minmax(0,1fr) 44px;gap:6px 10px;align-items:center}
.sb .m{font-size:.86rem;color:var(--fg);font-variant-numeric:tabular-nums}
.sb .t{font-size:.86rem;font-weight:700;text-align:right;font-variant-numeric:tabular-nums}
.sb .bx{display:flex;gap:2px;height:24px;min-width:0}
.sb .bx span{display:flex;align-items:center;justify-content:center;color:#fff;font-size:.74rem;font-weight:700;min-width:0;overflow:hidden;white-space:nowrap;font-variant-numeric:tabular-nums}
.sb .bx span:first-child{border-radius:4px 0 0 4px}.sb .bx span:last-child{border-radius:0 4px 4px 0}
.sb .m small{color:var(--muted);font-size:.72rem;display:block;line-height:1}
td.z{color:var(--grey)}
'''
rep('@media (prefers-reduced-motion:reduce)', css + '@media (prefers-reduced-motion:reduce)')

js = r'''
// ---------- cultura (OnFarm) ----------
const CULT = ''' + json.dumps(cult, ensure_ascii=False) + r''';
const CGRP = [
  {k:'Strep. agalactiae / dysgalactiae', c:'var(--g1)', a:['Strep. agalactiae / dysgalactiae']},
  {k:'Staph. aureus', c:'var(--g2)', a:['Staph. aureus']},
  {k:'Staph não aureus', c:'var(--g3)', a:['Staph não aureus']},
  {k:'Strep. uberis', c:'var(--g4)', a:['Strep. uberis']},
  {k:'Gram-negativos', c:'var(--g5)', a:['E. coli','Klebsiella / Enterobacter','Serratia spp','Pseudomonas spp','Outros Gram-neg']},
  {k:'Outros Gram-positivos', c:'var(--g6)', a:['Outros Gram-pos','Enterococcus spp','Lactococcus spp']},
  {k:'Prototheca / Levedura', c:'var(--g7)', a:['Prototheca / Levedura']},
];
const MESN = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
const mLab = m => MESN[+m.slice(5,7)-1]+'/'+m.slice(2,4);
let cultMode = 'n';
function cGroups(row){ return CGRP.map(g=>g.a.reduce((s,a)=>s+row[CULT.agentes.indexOf(a)],0)); }
function renderCultura(){
  const M = CULT.meses, rows = CULT.n, tot = rows.map(r=>r.reduce((a,b)=>a+b,0)), N = tot.reduce((a,b)=>a+b,0);
  const T = CULT.agentes.map((_,j)=>rows.reduce((s,r)=>s+r[j],0));
  const G = CGRP.map((_,i)=>rows.reduce((s,r)=>s+cGroups(r)[i],0));
  const last = M.length-1, cmp = M.slice(-4,-1), cmpN = cmp.map(m=>tot[M.indexOf(m)]);
  // blocos
  const tile = (t,v,sub) => `<div class="htile"><span class="k">${t}</span><div class="row1"><span class="v">${v}</span></div><span class="s">${sub}</span></div>`;
  const gi = k => CGRP.findIndex(g=>g.k===k);
  const pr = CULT.agentes.indexOf('Prototheca / Levedura');
  const prMax = rows.reduce((b,r,i)=>r[pr]>rows[b][pr]?i:b,0);
  document.getElementById('cuHero').innerHTML =
    tile('Culturas com agente', fmt(N), mLab(M[0])+' a '+mLab(M[last])+' ('+mLab(M[last])+' parcial) · '+fmt(N/M.length,0)+' por mês') +
    tile('Strep. agalactiae / dysgalactiae', pct(G[gi('Strep. agalactiae / dysgalactiae')]/N), fmt(G[0])+' culturas · contagioso (agalactiae) / ambiental-contagioso (dysgalactiae)') +
    tile('Staph. aureus', pct(G[gi('Staph. aureus')]/N), fmt(G[1])+' culturas · contagioso') +
    tile('Prototheca / Levedura', pct(G[gi('Prototheca / Levedura')]/N), fmt(G[6])+' culturas · pico em '+mLab(M[prMax])+' ('+rows[prMax][pr]+') · não responde a antibiótico');
  // legenda
  document.getElementById('cuLeg').innerHTML = CGRP.map(g=>`<span><i class="sw" style="background:${g.c}"></i>${g.k}</span>`).join('');
  // barras empilhadas por mês (mais recente em cima)
  const mx = Math.max(...tot);
  let h = '<div class="sb">';
  for(let i=last;i>=0;i--){ const g = cGroups(rows[i]), t = tot[i];
    const wbar = cultMode==='n' ? 100*t/mx : 100;
    h += `<div class="m">${mLab(M[i])}${i===last?'<small>parcial</small>':''}</div><div><div class="bx" style="width:${wbar.toFixed(2)}%">` +
      g.map((v,j)=> v ? `<span style="flex:${v} 1 0;background:${CGRP[j].c}" data-tip="${esc(mLab(M[i])+' · '+CGRP[j].k+': '+v+' culturas ('+pct(v/t)+' do mês)')}">${(v/t)*wbar>=5.5?(cultMode==='n'?v:pct(v/t,0)):''}</span>` : '').join('') +
      `</div></div><div class="t">${t}</div>`; }
  document.getElementById('cuMes').innerHTML = h + '</div>';
  // agentes no período
  document.getElementById('cuTotNote').textContent = fmt(N)+' culturas com agente · barra = % do total · cor = grupo do agente';
  const ord = CULT.agentes.map((a,j)=>({a,n:T[j],g:CGRP.find(g=>g.a.includes(a))})).sort((x,y)=>y.n-x.n);
  document.getElementById('cuTot').innerHTML = hbRows(ord.map(o=>({lb:`<span class="sw" style="background:${o.g.c}"></span>${o.a}`, v:o.n/N, color:o.g.c,
    val:`<b>${pct(o.n/N)}</b> · ${o.n}`, tip:`${o.a}: ${o.n} culturas (${pct(o.n/N)}) · grupo ${o.g.k}`})), {});
  // culturas x tratamentos
  const tr = {}; MC.forEach(c=>{ const k=c.ini.slice(0,7); tr[k]=(tr[k]||0)+1; });
  let tb = '<thead><tr><th>Mês</th><th>Tratamentos</th><th>Culturas</th><th>Culturas por 100 trat.</th><th>% Strep. ag./dysg.</th><th>% Staph. aureus</th></tr></thead><tbody>';
  M.forEach((m,i)=>{ const t=tr[m]; const g=cGroups(rows[i]);
    tb += `<tr><td class="l">${mLab(m)}${i===last?' (parcial)':''}</td><td>${t!=null?fmt(t):'–'}</td><td>${tot[i]}</td><td>${t?fmt(100*tot[i]/t,0):'–'}</td><td>${pct(g[0]/tot[i],0)}</td><td>${pct(g[1]/tot[i],0)}</td></tr>`; });
  document.getElementById('cuTrat').innerHTML = tb + '</tbody>';
  document.getElementById('cuTratNote').textContent = 'Em alguns meses há mais culturas que tratamentos (ago/26: 90 culturas para 79 tratamentos). O OnFarm pode incluir amostras de vacas com CCS alta sem sinais clínicos ou mais de um quarto por caso. É preciso confirmar com a fazenda o que entra na cultura.';
  // tabela completa
  let tt = '<thead><tr><th>Agente</th>'+M.map(m=>`<th>${mLab(m)}</th>`).join('')+'<th>Total</th><th>%</th></tr></thead><tbody>';
  ord.forEach(o=>{ const j=CULT.agentes.indexOf(o.a); tt += `<tr><td class="l"><span class="sw" style="background:${o.g.c};margin-right:6px"></span>${o.a}</td>`+rows.map(r=>`<td class="${r[j]?'':'z'}">${r[j]||'·'}</td>`).join('')+`<td><b>${T[j]}</b></td><td>${pct(T[j]/N)}</td></tr>`; });
  tt += `<tr><td class="l"><b>Total</b></td>`+tot.map(t=>`<td><b>${t}</b></td>`).join('')+`<td><b>${N}</b></td><td>100%</td></tr>`;
  document.getElementById('cuTab').innerHTML = tt + '</tbody>';
}
segInit('segCult', m=>{ cultMode=m; renderCultura(); });
'''
j = s.index('function renderAll(){')
s = s[:j] + js + s[j:]
rep("else if(t==='impressao') renderImpressao(); else renderRelatorio(); }",
    "else if(t==='impressao') renderImpressao(); else if(t==='cultura') renderCultura(); else renderRelatorio(); }")
open(dst, 'w', encoding='utf-8').write(s)
print('ok')
