"""Acrescenta o antibiograma (LabVet) à aba Cultura e ao Histórico da vaca. Uso: src dst dados/antibiograma.json"""
import json, sys
src, dst, aj = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()
B = json.load(open(aj, encoding='utf-8'))
ABX = list(dict.fromkeys(k for b in B for i in b['isolados'] for k in i['sir']))
ABG = [[i['amostra'], i['data'], i['vaca'], i['quarto'], i['agente'], ''.join(i['sir'].get(k, '-') for k in ABX), b['controle_lab']]
       for b in B for i in b['isolados']]

def rep(a, b, n=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, n)

rep('<h2 style="font-family:var(--f-display);margin:10px 0 0">Resumo mensal do sistema OnFarm</h2>', '''<div class="panel"><h2>Antibiograma (LabVet)</h2><p class="note" id="abIntro"></p>
      <div class="grid g2"><div><h3 class="sub3">Resultado por antibiótico (todos os isolados)</h3><div id="abBar"></div>
        <div class="lgd"><span><i class="sw" style="background:var(--good)"></i>S sensível</span><span><i class="sw" style="background:var(--warn)"></i>I intermediário</span><span><i class="sw" style="background:var(--crit)"></i>R resistente</span></div></div>
        <div><h3 class="sub3">% sensível por grupo de agente</h3><div class="tbl"><table id="abGrp"></table></div>
        <h3 class="sub3" style="margin-top:16px">Intramamários usados na fazenda × antibiograma</h3><div class="tbl"><table id="abProd"></table></div><p class="note" style="margin-top:6px">Princípio ativo informado para referência; confirmar a composição de cada produto com o veterinário. Mastgen e Cobactam: princípio ativo não informado aqui.</p></div></div>
      <h3 class="sub3" style="margin-top:18px">Mapa por isolado</h3><p class="note">Coluna = vaca, quarto e agente · toque no número da vaca para abrir o histórico</p><div class="tbl"><table id="abMap" class="abmap"></table></div>
      <p class="foot2">O antibiograma mede a sensibilidade em laboratório (in vitro). Não garante a cura na vaca e não substitui a decisão do veterinário. Os grupos ainda têm poucos isolados.</p></div>
    <h2 style="font-family:var(--f-display);margin:10px 0 0">Resumo mensal do sistema OnFarm</h2>''')
rep('/* ---- Cultura ---- */', '''/* ---- Cultura ---- */
.sir{display:flex;gap:2px;height:18px;min-width:0}
.sir span{display:flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:700;color:#fff;min-width:0;overflow:hidden}
.sir span:first-child{border-radius:3px 0 0 3px}.sir span:last-child{border-radius:0 3px 3px 0}
.abmap td,.abmap th{padding:3px 4px;text-align:center;font-size:.78rem}
.abmap th{white-space:normal;line-height:1.15;min-width:44px;vertical-align:bottom}
.abmap th:first-child,.abmap td:first-child{text-align:left;white-space:nowrap;position:sticky;left:0;background:var(--surface);z-index:1}
.abmap th a{color:var(--accent);cursor:pointer;text-decoration:underline}
.abmap td.S{background:var(--good);color:#fff;font-weight:700}.abmap td.I{background:var(--warn);color:#1d2621;font-weight:700}.abmap td.R{background:var(--crit);color:#fff;font-weight:700}
.abmap td.x{color:var(--muted)}
''')
rep('<div class="tbl"><table id="tblCult"></table></div>',
    '<div class="tbl"><table id="tblCult"></table></div>\n      <div class="tbl" style="margin-top:8px"><table id="tblAbx"></table></div>')

js = r'''
// ---------- antibiograma (LabVet) ----------
const ABX = ''' + json.dumps(ABX, ensure_ascii=False) + r''';
const ABG = ''' + json.dumps(ABG, ensure_ascii=False) + r'''.map(a=>({am:a[0],data:a[1],vaca:a[2],q:a[3],ag:a[4],sir:a[5].split(''),bol:a[6]}));
const ABGRP = [['Strep.',a=>/^Streptococcus/.test(a)],['Staph. sp.',a=>/^Staphylococcus sp/.test(a)],['Staph. aureus',a=>/aureus/.test(a)],['Gram-neg.',a=>/coli|Serratia|Klebsiella|Pseudomonas|Enterobacter/.test(a)],['Outros G+',a=>/Corynebacterium|Trueperella|Bacillus|Enterococcus|Lactococcus/.test(a)]];
const ABPROD = [['Mastjet','Tetraciclina + neomicina',['Tetraciclina','Neomicina']],['Spectramast','Ceftiofur',['Ceftiofur']],['Ubrolexin','Cefalexina + canamicina',['Cefalexina']],['Ciprolac','Ciprofloxacina',['Ciprofloxacina']],['Sinulox','Amoxicilina + ác. clavulânico',['Amoxi.+Ác. Clavulânico']]];
const abName = a => a.trim().replace(/\s+/g,' ');
const shortAg = a => a.replace('Streptococcus dysgalactiae','S. dysgal.').replace('Streptococcus ','S. ').replace('Staphylococcus aureus','S. aureus').replace('Staphylococcus','Staph.').replace('Escherichia','E.').replace('Corynebacterium','Coryneb.').replace('Trueperella','Truep.').replace(/\s*sp\.?\s*$/,' sp.');
function renderAbx(){
  const n = ABG.length; if(!n){ document.getElementById('abIntro').textContent='Nenhum antibiograma recebido.'; return; }
  const bols=[...new Set(ABG.map(x=>x.bol))], ds=[...new Set(ABG.map(x=>x.data))].sort();
  document.getElementById('abIntro').textContent = `${n} isolados com antibiograma em ${bols.length} boletim(ns) (coletas de ${ds.map(fmtD).join(', ')}/2026) · ${ABX.length} antibióticos.`;
  const st = ABX.map((a,j)=>{ const c={S:0,I:0,R:0}; ABG.forEach(x=>{ if(c[x.sir[j]]!=null) c[x.sir[j]]++; }); return {a,j,...c,t:c.S+c.I+c.R}; }).sort((x,y)=>y.S/y.t-x.S/x.t||x.R-y.R);
  document.getElementById('abBar').innerHTML = '<div class="hb wide">'+st.map(o=>`<div class="rw" data-tip="${esc(abName(o.a)+': S '+o.S+' · I '+o.I+' · R '+o.R+' de '+o.t+' isolados')}"><div class="lb">${esc(abName(o.a))}</div><div class="sir">${[['S','var(--good)'],['I','var(--warn)'],['R','var(--crit)']].filter(([k])=>o[k]).map(([k,c])=>`<span style="flex:${o[k]} 1 0;background:${c};${k==='I'?'color:#1d2621':''}">${o[k]/o.t>=.12?o[k]:''}</span>`).join('')}</div><div class="vl"><b>${pct(o.S/o.t,0)}</b> S<small>R ${o.R}</small></div></div>`).join('')+'</div>';
  const gs = ABGRP.map(([g,f])=>[g, ABG.filter(x=>f(x.ag))]).filter(([,x])=>x.length);
  document.getElementById('abGrp').innerHTML = '<thead><tr><th>Antibiótico</th>'+gs.map(([g,x])=>`<th>${g}<br><small>n=${x.length}</small></th>`).join('')+'</tr></thead><tbody>'+
    st.map(o=>`<tr><td class="l">${esc(abName(o.a))}</td>`+gs.map(([,x])=>{ const s=x.filter(y=>y.sir[o.j]==='S').length; const p=s/x.length; return `<td class="${p<.5?'hot':''}">${pct(p,0)}</td>`; }).join('')+'</tr>').join('')+'</tbody>';
  const use = {}; MC.forEach(c=>use[c.prod]=(use[c.prod]||0)+1);
  document.getElementById('abProd').innerHTML = '<thead><tr><th>Produto</th><th class="l">Princípio ativo</th><th>Trat. 2026</th><th class="l">Sensíveis</th></tr></thead><tbody>'+
    ABPROD.map(([p,pa,ks])=>`<tr><td class="l">${p}</td><td class="l">${pa}</td><td>${use[p]||0}</td><td class="ag">${ks.map(k=>{ const j=ABX.indexOf(k); if(j<0) return ''; const s=ABG.filter(x=>x.sir[j]==='S').length; return `${abName(k)}: <b class="${s/n<.5?'hot':''}">${pct(s/n,0)}</b> <small>(${s}/${n})</small>`; }).join('<br>')}</td></tr>`).join('')+'</tbody>';
  const cols = ABG.slice().sort((a,b)=>a.ag.localeCompare(b.ag)||String(a.vaca).localeCompare(String(b.vaca),undefined,{numeric:true}));
  document.getElementById('abMap').innerHTML = '<thead><tr><th>Antibiótico</th>'+cols.map(x=>`<th><a data-v="${esc(x.vaca)}">${esc(x.vaca)}</a><br>${esc(x.q||'–')}<br><small>${esc(shortAg(x.ag))}</small></th>`).join('')+'</tr></thead><tbody>'+
    st.map(o=>`<tr><td>${esc(abName(o.a))}</td>`+cols.map(x=>{ const v=x.sir[o.j]; return `<td class="${'SIR'.includes(v)?v:'x'}">${v==='-'?'·':v}</td>`; }).join('')+'</tr>').join('')+'</tbody>';
}
function fichaAbx(v){
  const raw = document.getElementById('inVaca').value.trim();
  const xs = ABG.filter(x=>String(x.vaca)===String(v)||String(x.vaca)===raw);
  document.getElementById('tblAbx').innerHTML = xs.length ? '<thead><tr><th>Antibiograma</th><th class="l">Agente</th><th class="l">Sensível</th><th class="l">Intermediário</th><th class="l">Resistente</th></tr></thead><tbody>'+
    xs.map(x=>{ const L=k=>ABX.filter((a,j)=>x.sir[j]===k).map(abName).join(', ')||'–'; return `<tr><td>${fmtD(x.data)} ${esc(x.q)}</td><td class="l">${esc(x.ag)}</td><td class="ag">${L('S')}</td><td class="ag">${L('I')}</td><td class="ag" style="color:var(--crit)">${L('R')}</td></tr>`; }).join('')+'</tbody>' : '';
}
document.getElementById('abMap').addEventListener('click',e=>{ const a=e.target.closest('a[data-v]'); if(!a) return; document.getElementById('inVaca').value=a.dataset.v; showTab('ficha'); });
'''
j = s.index('function renderAll(){')
s = s[:j] + js + s[j:]
rep("else if(t==='cultura'){ renderLabvet(); renderCultura(); }", "else if(t==='cultura'){ renderLabvet(); renderAbx(); renderCultura(); }")
rep("  fichaCult(v); fichaExtra(v);\n}", "  fichaCult(v); fichaExtra(v); fichaAbx(v);\n}")
rep("if(!h){ fichaCult(v); setTimeout(()=>fichaExtra(v));", "if(!h){ fichaCult(v); fichaAbx(v); setTimeout(()=>fichaExtra(v));")
rep("Não há antibiograma. ", "${ABG.length?'Antibiograma de '+ABG.length+' isolados na seção abaixo. ':'Sem antibiograma. '}")
rep("Sem antibiograma.`;", "${ABG.filter(x=>x.data>lo && x.data<=hi).length} isolados com antibiograma.`;")
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(ABG), 'isolados', len(ABX), 'antibióticos')
