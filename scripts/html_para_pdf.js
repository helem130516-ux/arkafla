// Converte uma página HTML em PDF (usa o @page da própria página). Uso: node html_para_pdf.js in.html out.pdf [out.png]
const { chromium } = require(process.env.PW || 'playwright');
(async () => { const [i, o, png] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1123, height: 794 } });
  await p.route(/^https?:/, r => r.abort()); await p.goto('file://' + require('path').resolve(i));
  await p.pdf({ path: o, preferCSSPageSize: true, printBackground: true });
  if (png) await p.screenshot({ path: png, fullPage: true });
  await b.close(); })();
