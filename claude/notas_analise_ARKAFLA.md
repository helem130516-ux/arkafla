# Notas de análise – Qualidade do Leite ARKAFLA (2026)

## Sessão de 30/09/2026

**Dados recebidos:** os 9 Relatórios 2.2 da APCBRH, salvos em `dados/apcbrh/R22_AAAA-MM-DD.xlsx`:
02/02, 17/02, 11/03, 17/04, 19/05 e 18/06 (REB 47238); 17/07, 14/08 e 18/09 (REB 70105).
- O arquivo "r22_janeiro.xlsx" é o controle de 02/02/2026. Não existe controle com data em janeiro.
- O registro de mastite clínica não foi anexado. Os 773 tratamentos saíram do painel publicado
  (DATA.m) e estão em `dados/mastite_clinica.json`.

**Conferências:**
- Em todos os controles, Σ(prod × CCS) ÷ Σ prod bate com a "MÉDIA CCS TANQUE" e o nº de linhas bate com o "No ANIMAIS".
- A reclassificação (`scripts/processa_controles.py`) é idêntica ao painel publicado nos 13.798 registros:
  classe, controles seguidos, recorrente, queda, CCS anterior, lote, DEL, produção e parto.
- As inconsistências conhecidas se confirmam:
  - partos alterados nas mesmas 11 vacas;
  - 9 registros com CCS 9.998;
  - partos em branco entre 6 e 32 por controle.

**Decisões:**
- Queda de produção: compara com o registro anterior da mesma lactação, mesmo que a vaca tenha faltado ao controle anterior (regra do painel).
- CCS antes: último controle com data ≤ início do tratamento. Retratamento ≤ 21 dias: bate 100% com o painel.
- CCS depois: sem a coluna RETORNO original não dá para refazer. Com o retorno = data final + carência, 30 dos 773 casos divergem do painel. É preciso reanexar o registro.

**Resultados-chave (18/09/2026, n = 1.628):**
- CCS estimada do tanque sem o lote 10: 309, contra 341 em 14/08.
- "MÉDIA CCS TANQUE" APCBRH: 325, contra 367.
- Vacas com CCS ≥ 200: 29,5% (481 vacas), o pior valor do ano. O melhor foi 23,8%, em 11/03.
- Base da classificação: 1.438 vacas.
  - Sadias: 61,8% (889).
  - Novas infecções: 11,7% (168). Taxa de NI: 15,9%, ou 13,6% por 30 dias.
  - Crônicas: 18,2% (262). Permanência: 68,8%.
  - Recuperadas: 8,3% (119).
- Recorrência: 49,4% (83 das 168 NI), a maior do ano.
- CCS elevada em ≥ 3 controles seguidos: 190 vacas.
- Cura no período seco: 61,1%. Nova infecção no período seco: 15,1%.

**Entregáveis nesta sessão:**
- Painel (https://claude.ai/artifact/EVFuJezbrx7guHZUvu4MAP): já tinha os 9 controles, com dados idênticos. Não foi republicado.
- Relatório Docs: já cobre fev–set/2026, com os números conferidos.
- Planilha: `scripts/gera_planilha.py` gera o xlsx com fórmulas, mas o recálculo no LibreOffice passou de 10 min.
  - Só a aba Dados já passa de 5 min.
  - Causa provável: as fórmulas em cadeia linha a linha nas 13,8 mil linhas.
  - Próximo passo: tirar a cadeia de "Já teve elevada" e "Seguidos" ou usar valores com fórmula de conferência.
- PDF: o usuário pediu para não gerar.

**Pendências:**
- Cultura microbiológica.
- CCS real do tanque (laticínio).
- Registro de mastite original, com a coluna RETORNO.
- ~~Confirmação da APCBRH sobre REB 47238 → 70105~~ — confirmada em 01/10/2026 (ver abaixo).

## Painel – novo visual do "Painel do mês" (30/09/2026, versão 6)
- Os 4 indicadores principais ganharam cartões com tendência em todos os controles:
  - CCS estimada do tanque sem o lote 10;
  - % de vacas com CCS ≥ 200;
  - % de novas infecções;
  - % de crônicas.
- Os outros 8 indicadores ficaram em cartões compactos, com a variação indicada por seta e sinal, não só pela cor.
- Faixas de CCS e classificação sanitária: faixa de composição de 100% mais barras com marcador do controle anterior e variação.
- Blocos novos:
  - "Lotes: vacas com CCS ≥ 200", com linha da média do rebanho e o lote 10 hachurado;
  - "10 maiores contribuições para a CCS do tanque (sem o lote 10)", com simulação (estimativa). Clicar na vaca abre o histórico dela.
- Dica flutuante (tooltip) em todas as barras.
- Corrigido o "−0,0 p.p." que aparecia quando não havia variação.
- Cópia local do painel em `painel/painel_qualidade_ARKAFLA.html`. O script de alteração é `scripts/patch_painel_mes.py`.

## Culturas microbiológicas 2026 (30/09/2026, painel versão 7)
**OnFarm** (`dados/OnFarm_2026.pdf` → `dados/cultura_onfarm_2026.json`)
- Gráfico com o nº de resultados com agente por mês, de out/25 a set/26 (setembro parcial, impresso em 11/09).
- Total: 634 resultados. Staph não aureus 29,8% (189), Strep. agalactiae/dysgalactiae 29,7% (188), Outros Gram-pos 14,5%, Prototheca/Levedura 8,0% (51, com pico de 17 em ago/26), Staph. aureus 5,0%.
- Transcrevi os rótulos e conferi cada total mensal pelo comprimento da barra.
- Ambiguidade: no PDF, Outros Gram-pos e Staph não aureus têm a mesma cor, assim como Klebsiella e Strep. uberis. Separei esses agentes pela ordem em que aparecem empilhados.
- Os dados não trazem vaca nem antibiograma, e o gráfico não mostra as amostras sem crescimento.

**LabVet (Carambeí)** (`dados/cultura_labvet/LabVet_AAAA-MM-DD.xlsx` → `dados/cultura_labvet.json`, script `scripts/le_cultura_labvet.py`)
- 5 boletins: 24/07, 29/07, 03/08, 15/09 e 22/09. Total de 136 amostras por vaca e quarto, com grau (G1–G3, em 66 amostras) e lote.
- 25 amostras sem crescimento (18%) e 25 com 2 agentes.
- Agentes: Staphylococcus sp. 31, Strep. dysgalactiae 26, Strep. bovis 21, Prototheca 13, E. coli 11, Streptococcus sp. 10, Corynebacterium 10, Strep. uberis 5, Serratia 3, S. aureus 2, e 1 cada de Levedura, Klebsiella, Trueperella e Bacillus.
- Sem antibiograma.
- 8 amostras não se ligam aos controles: vacas 3544, 2825, 3192, 3479 e 4046, e as identificações "Emilia", "Nivea" e "Original". A 5759 veio como "POOL".
- Na vaca 4985, a cultura de 15/09 no PE (E. coli) difere das de 24/07 e 29/07 (Staphylococcus sp., mais Prototheca em 29/07).

**Painel**
- Nova aba "Cultura": seção LabVet por vaca (agentes, CCS antes/depois, classe, tratamento ±7 dias, filtros por agente e boletim) e seção OnFarm mensal (barras por grupo em nº ou %, culturas × tratamentos, tabela completa).
- O "Histórico da vaca" passou a listar as culturas da vaca. O "Relatório do mês" traz o resumo das culturas do intervalo.

## Registro de mastite original (MASTITE_2026.xlsx) – 30/09/2026, painel versão 8
- Aba 2026: 773 tratamentos, iguais aos do painel (vaca, início, data final, carência e quartos).
  - Com a coluna RETORNO, a "CCS depois" (1º controle após o retorno) bate 100% com o painel. A pendência "30 casos divergem" está resolvida.
  - Retorno − (data final + carência): 1 dia em 728 casos, 0–2 dias em 756, e 17 casos fora disso (datas inconsistentes). 7 casos têm retorno antes da data final ou data final antes do início.
- Outras abas lidas (`scripts/le_registro_mastite.py` → `dados/registro_fazenda.json`):
  - HIPERQUERATOSE 26: escore de 01/05/2026 por quarto (1–4) e sujidade, 1.540 vacas.
    - Em 19/05, pelo pior quarto, as vacas com CCS ≥ 200 eram 20,6% no escore 1, 20,5% no 2, 28,0% no 3 e 51,9% no 4.
    - NI (19/05 + 18/06): 10,7%, 8,7%, 13,0% e 29,1%.
    - Em 18/09: escore 4 com 54% das vacas com CCS ≥ 200 (49 de 90) e NI de 35% (15 de 43). Rebanho: 29,5% e 15,9%.
  - SECAGEM: 1.330 secagens (2024–2026), 589 em 2026. Produtos principais: Mamyzin-A e Ciprolac Vaca Seca. Não comparar produtos.
  - DOENÇAS GERAL: 187 registros de 01/07 a 25/08/2026; 70 de mastite com tratamento sistêmico, fora do registro intramamário.
  - Abas 2023, 2024 e 2025 e Plan1 (histórico) não foram usadas.
- Painel:
  - "Painel do mês" ganhou o bloco "Hiperqueratose × CCS" (% ≥ 200 e taxa de NI por escore, no controle selecionado).
  - O "Histórico da vaca" mostra o escore de hiperqueratose, as secagens e os tratamentos sistêmicos.

## Antibiograma e painel automatizado (01/10/2026, painel versão 9)
**Antibiograma LabVet** (`dados/antibiograma/LabVet_ATB_AAAA-MM-DD.xlsx` → `dados/antibiograma.json`, script `scripts/le_antibiograma.py`)
- 2 boletins: coletas de 15/09 (12 isolados) e 22/09 (7 isolados). Cada isolado testado contra 16 antibióticos.
- Os 19 isolados batem com a cultura do mesmo boletim (nº da amostra, vaca e agente).
- % sensível em todos os isolados:

| Antibiótico | % sensível |
|---|---|
| Amoxi + clavulânico | 95% |
| Marbofloxacina | 79% |
| Amoxicilina | 74% |
| Gentamicina | 58% |
| Cefalexina | 53% |
| Ceftiofur | 32% |
| Tetraciclina | 32% |
| Penicilina | 26% |
| Neomicina | 16% (13 resistentes) |
| Estreptomicina | 0% (13 resistentes) |

- Intramamários × antibiograma (princípio ativo a confirmar com o veterinário):
  - Mastjet (tetraciclina + neomicina), 246 tratamentos em 2026: tetraciclina 32% e neomicina 16% sensíveis.
  - Spectramast (ceftiofur): 32% sensível.
- Resultado in vitro, com poucos isolados: só para orientar a conversa com o veterinário.

**Aliases dos boletins** (`dados/aliases_vacas.json`, informado pela fazenda em 01/10): Emilia = 1571, Nivea = 100, Original = 101.
- Ficam 5 amostras sem ligação com os controles: 3544, 2825, 3192, 3479 e 4046.

**Como atualizar a cada novo envio** (o painel agora é montado por script):
1. Salvar o arquivo na pasta certa:
   - controle APCBRH: `dados/apcbrh/R22_AAAA-MM-DD.xlsx`;
   - registro de mastite: `dados/MASTITE_2026.xlsx`;
   - cultura LabVet: `dados/cultura_labvet/LabVet_AAAA-MM-DD.xlsx`;
   - antibiograma: `dados/antibiograma/LabVet_ATB_AAAA-MM-DD.xlsx`;
   - novo apelido de vaca: `dados/aliases_vacas.json`.
2. Rodar `python3 scripts/monta_painel.py`. Ele lê tudo, gera o DATA (`scripts/gera_data_painel.py`) e aplica os patches sobre `painel/base_original.html`.
3. Publicar `painel/painel_qualidade_ARKAFLA.html` no mesmo link.
- Conferido: o DATA gerado pelo script é idêntico ao publicado antes (9 controles, 13.798 registros, 773 tratamentos).
- O OnFarm (PDF de gráfico) continua manual: transcrever para `dados/cultura_onfarm_2026.json`.

## Mapa de pagamento do laticínio – CCS/CPP reais do tanque (01/10/2026, painel versão 10)
- Arquivo: `dados/mapa_leite/mapa_2026-09.pdf` (Pool Leite, mês 09/2026, emitido em 01/10/2026). Script `scripts/le_mapa_leite.py` → `dados/mapa_leite.json`.
  - Lê cada célula pela posição no PDF. Lê vários mapas; o mais recente substitui o mesmo tanque/mês/período.
- Conteúdo: 4 tanques, até 4 períodos por mês, de jul/26 a set/26. São 42 análises de CCS, CPP, gordura, proteína, sólidos e ureia, com o volume de cada período.
  - Faltam períodos: tanque 1 jul 1º; tanque 3 jul 1º; tanque 4 jul 4º, ago 1º e set 1º.
  - CPP só vai até o 1º período de setembro.
- CCS real (média ponderada pelo volume) × controle APCBRH do mês:

| Mês | CCS real | Estimativa sem lote 10 | APCBRH com lote 10 |
|---|---|---|---|
| jul/26 | 250 | 290 (17/07) | 329 |
| ago/26 | 260 | 341 (14/08) | 367 |
| set/26 | 332 | 309 (18/09) | 325 |

  - Em set/26, o real subiu acima da estimativa.
  - Picos de setembro: tanque 4 com 512 (2º período) e tanque 1 com 410 (1º período).
- Médias do mapa: "Média Pagto" CCS 276,21 (POOL 221,62); CPP 10,54 (POOL 9,1).
  - A CCS de 276,21 fica perto da média geométrica dos 3 meses (276,6), mas o mapa não informa o critério.
- Prêmio de CCS em 09/2026: 3,09% (R$ 0,0664/L, R$ 137.888,90). Prêmio de CPP: 5,96%. Preço final: R$ 3,0279/L.
- CPP: tanque 2, jul 1º período = 338 (o único acima de 100); tanques 3 e 4 entre 30 e 36 em julho.
- Painel: nova aba "Tanque (laticínio)". O "Painel do mês" mostra a CCS real do mês do controle ao lado da estimativa, sempre separadas.
- Próximos meses: salvar o novo mapa em `dados/mapa_leite/mapa_AAAA-MM.pdf` e rodar `scripts/monta_painel.py`.

## REB 47238 → 70105 confirmado (01/10/2026)
- A fazenda informou que a APCBRH confirmou: houve mudança no código do produtor. É o mesmo rebanho.
- A análise já tratava os controles de 02/02 a 18/06 (REB 47238) e de 17/07 em diante (REB 70105) como uma série única. Nada muda nos números.

## Monitoramento diário do rebanho (15/10/2026)
- Fonte: relatório zootécnico diário "Zootécnico Jorge atualizado DD-MM-AAAA.xlsx"; a data do arquivo é a do nome.
- Relatórios guardados em `dados/zootecnico/Zootecnico_AAAA-MM-DD.xlsx`; mesma data substitui.
- `python3 scripts/monitor_diario.py <novo.xlsx>` guarda o relatório e refaz
  `monitoramento/Monitoramento_Diario_ARKAFLA.xlsx` (10 dias mais recentes em colunas, indicadores em linhas,
  variação último − anterior). A aba Dados leva 11 dias (o 11º serve às comparações com o dia anterior).
  Depois rodar o recalc.py (11 dias ≈ 1 min, ~390 mil fórmulas, ~7,7 MB).
- Itens definidos pelo usuário (versão 2):
  - Adultos (LACT > 0): vacas adultas; em lactação (lotes 1–6 e 10); DEL médio; produção média 24 h;
    média dos lotes 1 a 6; lote 10 (tratamento); leite vendido (entrada, `dados/leite_vendido.json`,
    virá de PDF); gestantes (DDP ≥ 1); DEL > 150 não gestantes; DNB (+ Dry DNB); DEL > 70 com NumIAs = 0;
    começaram a lactação, saída de adultos e entradas/saídas/saldo do lote 10 (comparação por brinco com o
    relatório anterior).
  - Jovens (LACT = 0): totais; ≥ 3 meses (90 d); novilhas gestantes; > 15 meses (456 d) não gestantes, sem machos.
- Comparações validadas com dias simulados (entradas/saídas conhecidas) e valores conferidos com pandas.
- 14/10/2026: 1.856 adultas, 1.652 em lactação, DEL 188, 43,3 kg/vaca, 57 no lote 10, 988 gestantes,
  274 com DEL > 150 vazias, 59 DNB, 16 com DEL > 70 sem IA; jovens 2.114, novilhas atrasadas 69.
- Versão 3 (15/10/2026): voltaram os indicadores da 1ª versão como blocos "Complementar" (rebanho, produção do
  tanque, reprodução das vacas em lactação e das novilhas, animais por lote). Nova aba "Produção por lote":
  um lote por linha (1 a 6, 10 e todas em lactação), média e desvio padrão amostral por dia (SUMPRODUCT, sem
  fórmula matricial); conferidos com pandas (std, ddof = 1).
- PDF de uma página (A4 retrato) a cada atualização: `python3 scripts/monitor_pdf.py` depois do recalc →
  `monitoramento/Monitoramento_Diario_ARKAFLA_AAAA-MM-DD.pdf` (data do último dia). Testado com 10 dias: cabe em
  uma página; o script falha se passar de uma.
- Fluxo diário: monitor_diario.py <novo.xlsx> → recalc.py → monitor_pdf.py → commit.
- Versão 4 (15/10/2026): a aba/quadro "Produção por lote" saiu. O desvio padrão agora fica na mesma célula da
  média, entre parênteses ("43,6 (10,1)"), nas linhas de produção média geral e dos lotes 1 a 6 (texto via
  FIXED; a coluna Var. compara só as médias). PDF com letra 6,8 e "média (DP)" em 5,6.
- Versão 5 (15/10/2026): saíram os blocos de reprodução complementar (vacas e novilhas) e "Animais por lote";
  o restante dos complementares foi integrado em só duas seções, Adultas e Jovens.
  - Machos (StatRepro = Male) fora de todos os números (coluna auxiliar Fêmea na aba Dados).
  - DNB (DNB e Dry DNB) fora de todos os indicadores de reprodução; só a contagem de DNB os mostra.
  - % gestantes = gestantes (DDP ≥ 1, sem DNB) ÷ (adultas − DNB): 988 ÷ 1.797 = 55,0% em 14/10.
  - % DEL > 150 não gestantes = não gestantes sem DNB ÷ vacas em lactação: 224 ÷ 1.652 = 13,6%.
  - Jovens: "< 3 meses" (IdadeDias < 90) em vez de ≥ 3 meses: 245 em 14/10. Jovens fêmeas: 1.905.
  - Conferido com pandas; recálculo de 10 dias ficou mais lento (≈ 2–3 min).
- Versão 6 (15/10/2026):
  - Saíram a média de leite 7 dias, Youngstock e novilhas em reprodução.
  - Entrou o % de vacas com leitura de leite: com Leite > 0 ÷ vacas dos lotes 1 a 6 (97,0% em 14/10).
  - "Leite total do dia (tanque)" passou a se chamar "Leite Total dia DairyPlan". Logo abaixo vêm o leite
    vendido e a diferença % = (DairyPlan − vendido) ÷ vendido.
  - Nova coluna "Média N dias" com a média dos dias exibidos. Nas linhas média (DP), é a média das médias diárias.
  - PDF em A4 paisagem, só com o título no cabeçalho.
- Leite vendido: "Demonstrativo das Coletas de Leite" (Oracle Reports, LEI0275), lido por
  `python3 scripts/le_leite_vendido.py <pdf>`.
  - Soma o Volume (litros) por Data Coleta, não pela data de recepção.
  - Confere a soma com o "Total Período" do PDF.
  - Grava em `dados/leite_vendido.json` e guarda o PDF em `dados/leite_vendido/`; um PDF novo substitui as datas que traz.
  - PDF de 15/10/2026 12:13: 32 coletas, de 30/09 a 14/10, total de 1.020.426 L.
  - 14/10: 70.310 L vendidos contra 67.643 kg no DairyPlan, diferença de −3,8% (kg contra litros, sem conversão).
  - A última data de coleta de cada PDF pode estar incompleta; o próximo PDF a corrige.
- Fluxo diário: le_leite_vendido.py <pdf> → monitor_diario.py <xlsx> → recalc.py → monitor_pdf.py → commit.
- Versão 7 (15/10/2026): análises do tanque do laticínio (mensagens de WhatsApp com Ref. coleta DD/MM T-n).
  - Transcritas à mão para `dados/analise_tanque.json`; a imagem fica em `dados/analise_tanque/`.
  - Primeira imagem: 04/10 T-2 e T-3, 05/10 T-1 e T-4. Cada uma casa com exatamente uma coleta (mesmo dia e
    tanque) no Demonstrativo. `le_leite_vendido.py` passou a gravar o detalhe das coletas em
    `dados/coletas_leite.json`.
  - Nova aba "Análises do tanque": média geral por data de coleta, ponderada pelo volume do tanque (média
    simples se faltar volume). 05/10: gordura 3,33%, proteína 3,40%, ST 12,43%, CCS 277, CPP 8, ureia 13,4.
  - Cada dia do monitoramento usa a última análise com data de coleta ≤ dia e repete até chegar uma nova.
    Gordura e proteína do tanque substituíram as médias do DairyPlan.
  - Leite ECM = produção média 24 h × (0,327 + 0,1295 × G% + 0,0765 × P%) (Sjaunja et al., 1990):
    44,1 kg em 14/10.
- Versão 8 (15/10/2026), pedido do usuário: as análises de uma mesma mensagem (campo "grupo" em
  analise_tanque.json) contam como uma só coleta. 04/10 e 05/10 viraram um grupo único: 4 tanques, 134.757 L,
  gordura 3,44%, proteína 3,39%, ST 12,54%, CCS 261, CPP 11, ureia 13,4. Vale a partir de 04/10 (primeira coleta
  do grupo) até chegar um grupo novo. ECM em 14/10: 44,7 kg.
- Versão 9 (15/10/2026): o relatório ganhou a coluna "DATA da IA" (última inseminação).
  - O arquivo veio sem data no nome ("Zoot_cnico_Jorge_atualizado_1.xlsx"), mas as outras 21 colunas são
    idênticas às do relatório de 14/10. Por isso substituiu `Zootecnico_2026-10-14.xlsx`.
  - Atenção: 41 vacas têm DATA da IA = 15/10/2026 num relatório de 14/10. Para elas, dias desde a IA = −1;
    não afeta a regra de > 35 dias.
  - Novos indicadores (dias desde IA = data do relatório − DATA da IA; parâmetro P_DIAS_IA = 35; sem DNB).
    Em 14/10:
    - Adultas: Bred ou Dry Bred com IA há > 35 dias = 20; Vazia com IA há > 35 dias = 81.
    - Jovens: Bred com IA há > 35 dias = 3; Vazia com IA há > 35 dias = 2.
  - Dias de relatórios sem a coluna ficam vazios nessas linhas.

## Atualização 16/10/2026
- Zootécnico "Zoot_cnico_Jorge_atualizado_2.xlsx", sem data no nome: IdadeDias = 14/10 + 1 em todos os animais,
  portanto relatório de 15/10/2026 (`Zootecnico_2026-10-15.xlsx`). 3.962 animais; 8 saíram, nenhum entrou.
- Coletas: PDF emitido em 16/10/2026 às 14:02 (35 coletas, Total Período 1.120.394 L conferido).
  - 15/10: 64.939 L (coletas 15/10 10:34 T-2 e 18:05 T-3).
  - 16/10: 35.029 L, ainda parcial.
- 15/10:
  - 1.652 vacas em lactação; 62 no lote 10 (5 entradas, 0 saídas).
  - 44,7 kg/vaca (ECM 46,2).
  - DairyPlan 70.126 kg contra 64.939 L vendidos, diferença de +8,0%.
  - Vazias com IA há > 35 dias caíram de 81 para 50: 31 delas foram inseminadas em 15/10 e viraram Bred.
- Análises do tanque, segunda mensagem (recebida em 16/10, "Pool Leite": "Análise de Parâmetros de Qualidade"):
  - Tanques: 12/10 T-2 e T-3; 13/10 T-1 e T-4. Formam um grupo que vale a partir de 12/10; 132.982 L.
  - O formato traz lactose (nova linha e coluna) e chama a CPP de CBT. A ureia vem com "%", mas foi tratada na
    mesma escala das mensagens anteriores (mg/dL).
  - Média ponderada pelo volume: gordura 3,65%, proteína 3,39%, lactose 4,70%, ST 12,72%, CCS 251, CBT 15,
    ureia 12,7.
  - Cada item é ponderado só pelos tanques que têm valor; no grupo de 04/10 a lactose fica vazia.
  - ECM: 14/10 = 45,9 e 15/10 = 47,4 kg (gordura mais alta que no grupo de 04/10).
- Zootécnico "_3" ("ajuste de dados"): mesmo dia do "_2" (DtNasc + IdadeDias = 16/10, a data de exportação;
  os dados são de 15/10). Substituiu `Zootecnico_2026-10-15.xlsx`.
  - Diferenças em relação ao "_2": coluna nova DtÚltParto, 12 bezerros novos (nascidos de 14 a 16/10) e partos
    lançados (8 vacas com DEL reiniciado; novilhas que pariram passaram a adultas).
  - Regra observada: a data de exportação do DairyPlan é o dia seguinte ao do relatório. Por isso aparecem
    IA e parto com data D+1 no relatório do dia D.
  - "Vacas que começaram a lactação" agora é contada pela DtÚltParto: adultas com parto depois da data do
    relatório anterior e até a data do relatório. Relatórios sem a coluna continuam com a comparação por brinco.
  - 15/10: 3 partos; 1.666 vacas em lactação; 105 paridas há ≤ 21 dias.
  - Os 4 partos datados de 16/10 entram no relatório de 16/10.

## Atualização 17/10/2026 – relatório direto do BoviSync
- Com a rede liberada para bovisync.farm, `scripts/baixa_bovisync.py` baixa o relatório "Zootécnico Jorge
  atualizado" (https://bovisync.farm/report/CTBOCW) e grava `dados/zootecnico/Zootecnico_AAAA-MM-DD.xlsx` no
  mesmo formato do Excel.
  - Login por BOV_USER e BOV_PASS, variáveis de ambiente nunca gravadas em arquivo.
  - A grade do site depende de um aviso por SSE que não chega pelo proxy. O script consulta
    `/api/report/data/item` até as colunas ficarem READY e busca cada coluna em `/api/report/data/fetch`,
    de dentro da página.
  - Status vêm em inglês: Preg → Prenha, Fresh → Fresca, Open → Vazia; os demais são iguais.
  - Data do relatório = DtNasc + IdadeDias − 1. Baixado em 17/10, portanto relatório de 16/10 (3.974 animais).
- Leite vendido: `le_leite_vendido.py` agora refaz os totais com todos os PDFs guardados e ignora coletas com
  data igual ou posterior à emissão do PDF (dia incompleto). 16/10 tinha só 35.029 L e saiu até chegar o
  próximo PDF.
- 16/10:
  - 4 partos; lote 10 com 7 entradas e 15 saídas (54 vacas).
  - Produção média 44,2 kg (ECM 46,8). DairyPlan 69.517 kg.
  - Vazias com IA há > 35 dias: 78. São +33 vacas inseminadas em 10/09 que completaram 36 dias.
