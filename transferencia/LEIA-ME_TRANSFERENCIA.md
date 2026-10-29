# ARCAFLA – Qualidade do Leite: pacote de transferência

Pacote gerado em 29/10/2026 com tudo o que foi feito nesta sessão: dados recebidos, scripts, painel, folhas em PDF, logo, notas de análise e a instrução (skill) atualizada. Serve para continuar o trabalho em outra conta Claude sem precisar reenviar os arquivos um a um.

## Como usar na outra conta
1. **Claude Code (recomendado):** descompacte o zip numa pasta (ou num repositório Git novo) e abra a sessão nessa pasta. Peça: "leia LEIA-ME_TRANSFERENCIA.md e claude/notas_analise_ARCAFLA.md e continue a análise".
2. **Instrução do projeto (skill):** crie uma skill com o conteúdo de `skill/qualidade-leite-arcafla/SKILL.md`. Ela já está com o nome ARCAFLA, os novos tipos de dados e a seção 10 ("como retomar").
3. **Projeto do claude.ai (sem Claude Code):** suba este zip ou os arquivos de `dados/` e as notas. O projeto guarda só parte de cada xlsx, por isso o Claude Code é melhor para reprocessar tudo.
4. **Painel e relatório:** o painel publicado (https://claude.ai/artifact/EVFuJezbrx7guHZUvu4MAP) e o relatório no Claude Docs pertencem à conta antiga. Na conta nova, publique o `painel/painel_qualidade_ARCAFLA.html` como um novo Artifact. Se quiser manter o acesso ao antigo, compartilhe-o pelo menu "Share" da conta antiga.
5. Também há uma cópia de tudo no GitHub: repositório `helem130516-ux/arkafla`, branch `claude/bold-bell-yvjyxv`.

## Conteúdo
| Pasta | O que tem |
|---|---|
| `dados/apcbrh/` | 10 Relatórios 2.2 da APCBRH (02/02 a 16/10/2026) |
| `dados/MASTITE_2026.xlsx`, `dados/mastite_tratamentos_2026.xlsx` | registro de mastite (até 24/10), hiperqueratose, secagem, doenças gerais |
| `dados/secagem/` | exportação do rebanho com a última secagem e o último parto (27/10) |
| `dados/cultura_labvet/`, `dados/antibiograma/` | culturas e antibiogramas LabVet por vaca |
| `dados/cultura_onfarm/` | OnFarm por vaca (jan–out/26) e o gráfico em PDF |
| `dados/mapa_leite/`, `dados/analise_oficial/`, `dados/tanque_avulsas.json` | CCS/CPP reais do tanque (laticínio) |
| `dados/*.json` | dados já lidos e conferidos (gerados pelos scripts) |
| `scripts/` | leitura dos arquivos, classificação, painel, folhas e PDFs |
| `painel/` | painel interativo pronto (`painel_qualidade_ARCAFLA.html`) e a base usada pelos scripts |
| `relatorios/` | folhas "Dinâmica da CCS" e "Eficiência de secagem" (PDF e HTML) |
| `assets/` | logo oficial ARCAFLA (PDF, SVG e PNG) |
| `claude/notas_analise_ARCAFLA.md` | histórico de todas as decisões, conferências e resultados |
| `skill/` | instrução atualizada para a conta nova |

## Para refazer o painel e as folhas
```
pip install openpyxl pymupdf
npm i -g playwright   # Chromium para os PDFs
python3 scripts/monta_painel.py
python3 scripts/gera_pdf_dinamica_modelo.py   # depois: node scripts/html_para_pdf.js <html> <pdf>
python3 scripts/gera_pdf_secagem_modelo.py
```

## Situação no último controle (16/10/2026)
- 1.591 vacas. CCS estimada do tanque sem o lote 10: 290 mil/mL; APCBRH: 305. CCS real do tanque em out/26: 255 (média simples das análises oficiais).
- Vacas com CCS ≥ 200: 26,0%. Na base de 1.452 vacas: sadias 63,5%, novas infecções 9,0%, crônicas 17,2%, recuperadas 10,3%.
- Eficiência de secagem (fev–ago/26): 38% secam infectadas, cura de 71%, 20% de novas infecções no período seco, novilhas infectadas 21%.

## Pendências
- Mapa de pagamento de out/26 (com volume).
- Planilha Excel: o gerador existe (`scripts/gera_planilha.py`), mas o recálculo no LibreOffice passou de 10 min. Próximo passo: tirar as fórmulas em cadeia da aba Dados.
- Decidir se os tratamentos sistêmicos de mastite (aba DOENÇAS GERAL) entram nos indicadores.
