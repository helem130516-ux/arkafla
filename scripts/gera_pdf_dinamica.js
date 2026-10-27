// PDF "Dinâmica da CCS no rebanho": abas Painel do mês + Evolução do painel, A4 retrato.
// Uso: PW=$(npm root -g)/playwright node scripts/gera_pdf_dinamica.js painel.html saida.pdf [ci]
const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const [html, out, ci] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1100, height: 1400 }, colorScheme: 'light' });
  await p.route(/^https?:/, r => r.abort());
  await p.goto('file://' + require('path').resolve(html));
  await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  if (ci) await p.selectOption('#selCtrl', ci);
  // renderiza as duas abas e mostra ambas, uma após a outra
  await p.click('button[data-tab=evolucao]'); await p.waitForTimeout(150);
  await p.click('button[data-tab=painel]'); await p.waitForTimeout(150);
  const ctl = await p.$eval('#selCtrl', s => s.options[s.selectedIndex].textContent);
  await p.addStyleTag({ content: `
    nav.tabs, .ctl, .foot, .noprint, section[id^=tab-]{display:none!important}
    #tab-painel, #tab-evolucao{display:grid!important}
    #tab-evolucao{break-before:page; margin-top:0}
    .panel, .kpi, .htile{break-inside:avoid}
    .wrap{padding-block:6px 0}
    .secTitle{font-family:var(--f-display);font-weight:800;font-size:1.25rem;margin:0 0 6px}
    .scroll{max-height:none!important}
  `});
  await p.evaluate((ctl) => {
    document.getElementById('tab-evolucao').hidden = false;
    const h = document.querySelector('header.top .sub');
    h.textContent = 'Dinâmica da CCS no rebanho · controle ' + ctl.replace(' (último)', '') + ' · controle leiteiro APCBRH (Relatório 2.2) · CCS em mil células/mL · limite individual 200 · estimativas do tanque calculadas pelas vacas do controle';
    const t1 = document.createElement('h2'); t1.className = 'secTitle'; t1.textContent = '1. Situação no controle';
    document.getElementById('tab-painel').prepend(t1);
    const t2 = document.createElement('h2'); t2.className = 'secTitle'; t2.textContent = '2. Evolução entre os controles';
    document.getElementById('tab-evolucao').prepend(t2);
  }, ctl);
  await p.emulateMedia({ media: 'screen' });
  await p.pdf({ path: out, format: 'A4', printBackground: true, scale: 0.55,
    margin: { top: '10mm', bottom: '12mm', left: '10mm', right: '10mm' },
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#5e6b63">Fazenda ARCAFLA · Qualidade do Leite · página <span class="pageNumber"></span> de <span class="totalPages"></span></div>' });
  await b.close();
})();
