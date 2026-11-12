# Notas de análise – Qualidade do Leite ARKAFLA (2026)

**Preferência do usuário:** responder sempre em português.

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
- Leite vendido: a cooperativa não lança coletas no fim de semana. O PDF de coletas chega na segunda-feira;
  até lá as linhas "Leite vendido" e "Diferença DairyPlan × vendido" ficam em branco a partir de 16/10.

## Atualização 19/10/2026
- Zootécnico "Zoot_cnico_Jorge_atualizado_18-10.xlsx": registrado como 18/10, conforme o nome e o usuário.
  Atenção: DtNasc + IdadeDias = 18/10. Pela regra dos arquivos anteriores (exportação = dia seguinte) seria 17/10;
  provavelmente foi exportado no próprio dia 18. 17/10 ficou sem relatório.
- Coletas: PDF emitido em 19/10 às 09:56 (40 coletas, Total Período 1.290.251 L).
  - Dias completos: 16/10 = 68.815 L, 17/10 = 72.071 L, 18/10 = 64.000 L.
- 18/10:
  - Diferença DairyPlan 69.898 kg × vendido 64.000 L = +9,2%. Em 16/10 foi +1,0%.
  - Lote 10 com 48 vacas (0 entradas, 6 saídas). 1 parto entre 17 e 18/10.
  - Produção 44,0 kg (ECM 46,6). Vazias com IA há > 35 dias: 83.
- Rotina diária (trig_016TMVvrfCBFKNtTAUKUc2Jd): em 18/10 parou sem BOV_USER e BOV_PASS no ambiente; falta
  cadastrar os secrets. `baixa_bovisync.py` agora não sobrescreve um dia que já existe (opção `--substituir`).
- Correção (usuário, 19/10): o arquivo "atualizado_18-10" tem dados de 17/10. A regra vale sempre: data do
  relatório = DtNasc + IdadeDias − 1, ou seja, o dia anterior à exportação.
  - Ficou `Zootecnico_2026-10-17.xlsx`.
  - O "atualizado_5", recebido em 19/10 com referência 19, virou `Zootecnico_2026-10-18.xlsx`.
- 17/10: DairyPlan 69.898 kg × vendido 72.071 L = −3,0%; lote 10 com 48 vacas.
- 18/10:
  - DairyPlan 69.890 kg × vendido 64.000 L = +9,2%.
  - 1.674 vacas em lactação; lote 10 com 47 (0 entradas, 1 saída); 0 partos.
  - 43,8 kg/vaca (ECM 46,4). Vacas com < 20 kg: 70 (eram 56).
  - Gestantes: 997 (+19). DNB: 63 (+4). Vazias com IA há > 35 dias: 94.
- "atualizado_6" (19/10, "dados com os partos corretos"): é o relatório de 18/10 com os partos atrasados
  lançados (5 vacas paridas em 17/10, 1 em 18/10, 1 em 19/10) e 6 bezerros novos. O leite é igual.
  Substituiu `Zootecnico_2026-10-18.xlsx`.
- Regra nova de partos: contados pela DtÚltParto do relatório mais recente, no dia do parto (depois do relatório
  anterior e até o dia). Assim, lançamentos atrasados corrigem os dias anteriores.
  - Partos: 15/10 = 3, 16/10 = 4, 17/10 = 6 (antes 1), 18/10 = 1.
  - 18/10: 1.675 vacas em lactação, 188 secas, 991 gestantes.

## Atualização 20/10/2026
- Zootécnico "atualizado_7" (referência 20/10, portanto relatório de 19/10).
  - Lotes novos 20 e 30, com vacas vindas dos lotes 2 e 3. Pedido do usuário: o lote 20 conta como lote 2 e o
    30 como lote 3 (`LOTE_EQUIV` em `monitor_diario.py`, aplicado na carga).
  - Lote 2 = 2 + 20: 55,2 kg (DP 9,8), 212 vacas. Lote 3 = 3 + 30: 54,0 kg (DP 11,5), 220 vacas.
- Coletas: PDF emitido em 20/10 às 10:10 (42 coletas). 19/10 = 69.462 L; DairyPlan 69.506 kg, diferença +0,1%.
- 19/10:
  - 8 adultas saíram do relatório (6 DNB, mais 5814 do lote 1 e 3445 do lote 6, as duas Bred). 1.664 em lactação.
  - Lote 10 com 42 vacas (9 entradas, 14 saídas). 1 parto.
  - 43,6 kg/vaca (ECM 46,2). Vazias com IA há > 35 dias: 97.

## Atualização 21/10/2026 – nome ARCAFLA e novo visual
- O usuário pediu "ARCAFLA" em vez de "ARKAFLA" nas saídas. Arquivos renomeados para
  `monitoramento/Monitoramento_Diario_ARCAFLA*.xlsx/pdf`; a rotina também foi atualizada. O repositório e os
  nomes antigos das notas continuam como estão.
- Novo visual ("melhore a gestão visual e deixe mais didático"):
  - Planilha:
    - Blocos: Rebanho e movimentação · Produção por vaca · Leite produzido e entregue · Qualidade do leite do
      tanque · Reprodução; jovens = Recria.
    - Coluna "Melhor" (↑ bom quando sobe, ↓ bom quando desce, 0 bom perto de zero).
    - Variação verde quando melhora e vermelha quando piora (formatação condicional pela coluna Melhor).
  - PDF:
    - Painel com 6 cartões: valor, seta de melhora/piora, média e minigráfico. São vacas em lactação,
      produção 24 h + ECM, DairyPlan × vendido, % gestantes, lote 10 e vazias com IA há > 35 dias.
    - Tabela com coluna lateral de blocos, seta colorida na variação e legenda "Como ler".
- Dados:
  - Zootécnico "atualizado_8" = 20/10 (referência 21/10).
  - Coletas: PDF emitido em 21/10 às 14:31. Regra nova: a última data de coleta de cada PDF também fica de fora
    (20/10 tinha uma coleta só, 28.826 L, e daria diferença falsa de +139%).
- Análises do tanque (print de 21/10, imagem não chegou ao ambiente; valores transcritos):
  - 17/10 T-3 e T-2; 18/10 T-4 e T-1. Ureia do T-1 = 9,7, informada pelo usuário.
  - Grupo válido a partir de 17/10: gordura 3,37%, proteína 3,38%, CCS 243, CBT 19, ureia 12,4.
- 20/10:
  - 1.646 vacas em lactação (−18); lote 10 com 32 (0 entradas, 10 saídas); 2 partos.
  - 43,5 kg/vaca (ECM 44,4). Lote 6 caiu para 21,9 kg; vacas com < 20 kg: 77.
  - Gestantes: 54,6%. Vazias com IA há > 35 dias: 97.
- Envio por WhatsApp (pedido do usuário: mandar o relatório do WhatsApp dele para o Cleverson):
  `scripts/envia_whatsapp.py` usa o Z-API, com o WhatsApp do usuário conectado por QR Code.
  - Envia um resumo em texto (`/send-text`) e o PDF (`/send-document/pdf`, em base64).
  - Variáveis de ambiente: ZAPI_INSTANCE, ZAPI_TOKEN, ZAPI_CLIENT_TOKEN (opcional) e WPP_DESTINO.
  - Precisa liberar api.z-api.io na rede. A rotina roda o envio (passo 10) só quando as variáveis existem.
  - Os endpoints seguem o padrão do Z-API, mas não foram conferidos na documentação, porque o site estava
    bloqueado. Confirmar no primeiro teste.
- PDF redesenhado (21/10, pedido do usuário: letra maior, mais visual, menos informação, nova aparência, cor
  principal cinza-escuro #2E3338). Agora tem 2 páginas, A4 paisagem:
  - Página 1: cabeçalho escuro; 6 cartões; quadros de produção por vaca + ECM nos dias exibidos, produção por lote
    (barras com ± DP), leite DairyPlan × vendido, vacas com leite < 20 kg (pedido do usuário; 20 kg ≈ 19,4 L),
    % gestantes e atrasos reprodutivos (vazias com IA > 35 d e DEL > 150 não gestantes); quadro
    "Atenção hoje" com os 6 indicadores que mais pioraram. Não há gráfico do lote 10 (o usuário pediu para tirar).
  - Página 2: tabela completa com letra ~7,5 pt e legenda.
  - Cores dos dados: azul #2A78D6, laranja #EB6834, verde-água #1BAF7A, validadas pelo validate_palette.js; todos
    os gráficos têm rótulos com valores. A planilha também usa o cinza-escuro.
- Cores de identidade dos lotes (definidas pela fazenda em 21/10): lote 1 amarelo #EDA100, lote 2 azul #2A78D6,
  lote 3 vermelho #E34948, lote 4 verde #008300, lote 5 roxo #6250D6, lote 6 laranja #EB6834. Validadas com o
  validate_palette.js: aviso de daltonismo entre verde e vermelho (ΔE 7,2) e amarelo com contraste baixo, por isso
  o nome do lote vai sempre escrito junto.
  - PDF: barras do gráfico "Produção por lote" e marca colorida nas linhas de lote da tabela.
  - Planilha: borda grossa colorida à esquerda das linhas "Produção média do lote N".
- Visual moderno no PDF (21/10, pedido do usuário):
  - Cantos arredondados em cabeçalho, cartões, quadros de gráfico, "Atenção hoje" e tabela.
  - Fundo da página #F3F4F5 com cartões brancos separados.
  - Linhas suaves com interpolação monotônica (Fritsch–Carlson), que não ultrapassa os valores reais.
    A Catmull-Rom foi descartada porque criava vales falsos.
  - Área clara sob a série principal (produção e % gestantes); ponto destacado só no último dia.
  - Grade tracejada; barras com cantos arredondados.

### 21/10/2026 – logo no PDF
- Logo da fazenda (enviada pelo usuário) recortada sem a margem branca e salva em `dados/logo_arcafla.png` (900×535).
- Aparece só no cabeçalho da página 1, numa faixa branca à esquerda (altura 46 pt). Se o arquivo não existir, o PDF sai sem logo.

### 21/10/2026 – cartões e título do PDF
- Os 6 cartões da página 1 foram redesenhados: faixa lateral na cor do juízo (verde melhorou, vermelho piorou, cinza
  neutro), valor grande (encolhe se não couber), selo arredondado com a variação "vs ontem", "média 10 dias",
  linha extra com o número em negrito e a sparkline embaixo. Altura 82 pt; gráficos de cima reduzidos para 158 pt.
- Título do cabeçalho: "Monitoramento diário" (sem "ARCAFLA"; a logo identifica a fazenda). Página 2:
  "Monitoramento diário · Tabela completa dos indicadores".

## PADRÃO DO PDF (aprovado pelo usuário em 21/10/2026; atualizado no mesmo dia)
Este é o modelo oficial do PDF diário. Não mudar o layout sem pedido do usuário. Versão de referência: commit
`a2c809e` (branch claude/tender-clarke-13z0dx).
- A4 paisagem, 2 páginas. Cor principal cinza-escuro (#2E3338), fundo da página #F3F4F5, cantos arredondados.
- Página 1:
  - Cabeçalho com a logo (`dados/logo_arcafla.png`) e o título "Monitoramento diário".
  - 6 cartões: faixa do juízo, valor grande, selo "vs ontem", média 10 dias, linha extra e sparkline.
    - Os 6 seguem a mesma grade: título, valor, média e linha extra nas mesmas alturas.
    - Título e valor têm um só tamanho para os 6: o maior que cabe no cartão mais apertado.
    - O selo tem largura fixa, encostado à direita; "vs ontem" fica centrado embaixo dele, na linha da média.
    - A sparkline termina alinhada à borda direita do selo.
  - Gráficos: produção por vaca (azul = produção, verde = ECM, com valores) e produção por lote (cores dos lotes, ± DP).
  - Gráficos: DairyPlan × comercializado (azul/verde, mil kg/L, com a linha "dif." %), vacas < 20 kg, % gestantes e atrasos
    reprodutivos.
  - Quadro "⚠ Atenção hoje".
- Página 2: tabela completa ocupando a página toda; linhas dos lotes no tom claro da cor do lote; último dia em azul.
- Cores dos lotes: L1 amarelo, L2 azul, L3 vermelho, L4 verde, L5 roxo, L6 laranja.
- Subtítulos dos gráficos sem "bom quando sobe/cai".
- Leite comercializado em kg (litros × 1,032; parâmetro P_DENSIDADE). Termo "leite comercializado" (nunca "vendido"). Na página 2, a linha "Leite comercializado no dia" fica em destaque:
  marca verde, fundo verde-claro e números em negrito.
- A variação é arredondada às casas exibidas, então "= 0" fica sem cor.

### 21/10/2026 – revisão de erros
- Recálculo sem erros (362 mil fórmulas). Os indicadores de 20/10 foram refeitos à parte com pandas a partir do
  arquivo bruto e bateram todos: lactação, tanque, lote 10, produção e DP por lote, < 20 kg, gestantes, DNB,
  DEL > 150, DEL > 70 sem IA e jovens.
- Corrigido: a variação agora é arredondada às casas exibidas (ROUND na fórmula). Antes, uma variação que aparecia
  como "= 0" (ex.: lote 5 −0,04 kg; % leitura −0,05 p.p.) ainda era pintada de verde ou vermelho e podia entrar no
  "Atenção hoje".
- Vazias com IA > 35 d em 15/10 = 50 (81 → 50 → 78) está certo pelo arquivo bruto. É um lote de IATF cruzando os
  35 dias.
- Cadastro (DairyPlan/BoviSync): 4 vacas "Bred" sem DATA da IA (brincos 5557, 3291, 5541 e 5791) ficam fora de
  "Inseminadas com IA > 35 d". A 5791 tem a 1ª IA com 16 DEL: conferir.
- A diferença DairyPlan × vendido compara kg com L sem conversão (decisão anterior). Com densidade de 1,032, os kg
  viram ~3% menos litros.

### 21/10/2026 – "leite comercializado"
- Onde aparecia "vendido" agora aparece "comercializado": planilha, PDF (cartão, gráfico, legenda, tabela) e resumo
  do WhatsApp. Os nomes de arquivos (`dados/leite_vendido.json`, `scripts/le_leite_vendido.py`) não mudaram.
- Na página 2, a linha "Leite comercializado no dia" ficou em destaque: marca verde à esquerda (o mesmo verde do
  gráfico), fundo verde-claro na linha toda e números em negrito. Na legenda, "verde = leite comercializado (L)".

### 21/10/2026 – alinhamento dos cartões
- Antes, o título "DairyPlan × comercializado" passava da borda, o selo e o "vs ontem" mudavam de lugar em cada
  cartão, e valor e título tinham tamanhos diferentes. Agora tudo segue uma grade fixa (ver PADRÃO DO PDF).

### 21/10/2026 – teste da rotina e datas nos gráficos estreitos
- Conferido para a rotina das 11h:
  - BOV_USER e BOV_PASS cadastradas; o login funcionou na execução de 21/10.
  - Bibliotecas, fontes, LibreOffice e pdftoppm estão instalados, e a logo está versionada.
  - Uma cópia nova do branch gerou a planilha sem erros e o PDF com 2 páginas.
- A simulação com 8 dias mostrou datas encavaladas nos gráficos estreitos e a linha "dif." apertada. Correções:
  - eixo_x calcula o passo pela largura do rótulo (a última data sempre aparece).
  - Na faixa "dif.", se os textos não cabem lado a lado, eles alternam em duas linhas.
  - Testado com 8 dias: 2 páginas. O teste com 10 dias não foi feito (interrompido pelo usuário).

### 22/10/2026 – coletas (PDF emitido em 22/10 às 10:16)
- Completa 20/10: 62.438 L (duas coletas, às 19:54 e às 20:03). DairyPlan 68.881 kg, diferença +10,3%.
- Atenção: a coleta de 19/10 às 23:19 (34.821 L) é praticamente leite de 20/10. Pela regra combinada (soma por
  data de coleta), ela conta em 19/10. Por isso a diferença diária oscila (+9,2% em 18/10, +10,3% em 20/10).
  Pela média dos dias, a diferença fica em torno de +3%.
- 21/10 (35.380 + 36.584 L até agora) fica para o próximo PDF.

### 22/10/2026 – relatório de 21/10
- Rotina das 10h49: baixou, gerou e enviou ao celular, mas o push falhou (403, o repositório não está nas fontes
  da rotina). O 21/10 foi baixado de novo nesta sessão e salvo aqui.
- 21/10:
  - Lactação: 1.650 (+4); lote 10: 41 (+16 entradas / −7 saídas).
  - Produção: 43,8 kg (ECM 44,7). Vacas < 20 kg: 57 (−20). Partos: 7. DNB: 65 (+6).
  - DairyPlan: 69.121 kg; comercializado de 21/10 ainda pendente.
- "Vazias com IA > 35 d" caiu de 97 para 38: 55 vacas foram reinseminadas (IATF) com data de IA de 22/10 (o
  BoviSync baixado às 11h já inclui o lançamento da manhã). Outras 4 foram para DNB.

### 22/10/2026 – correção da rotina (push 403)
- Causa: a rotina abria uma sessão nova por dia, sem o repositório autorizado. O push dava 403, e o add_repo com
  push esperava a usuária aprovar no app.
- Correção: nova Routine `trig_01Ebntwen6FKHeU9uyxqdMZi`, às 10h48, rodando dentro da conversa principal (que tem
  permissão de gravação). A antiga, `trig_016TMVvrfCBFKNtTAUKUc2Jd`, foi desativada, não apagada.

### 22/10/2026 – comercializado em kg
- A usuária decidiu: o leite comercializado é convertido para kg (litros × 1,032, parâmetro P_DENSIDADE na aba
  Parâmetros). A diferença DairyPlan × comercializado passa a ser kg × kg.
- Efeito: a diferença média caiu de +3,1% para −0,1%. Por dia, 20/10 foi de +10,3% para +6,9% e 19/10 de +0,1%
  para −3,0%.

### 23/10/2026 – rotina automática (relatório de 22/10)
- Primeira execução da rotina dentro da conversa principal: baixou, gerou, enviou e salvou.
- 22/10:
  - Lactação: 1.651 (+1); lote 10: 44 (+4 entradas / −1 saída).
  - Produção: 44,8 kg (+1,0); ECM 45,8. Vacas < 20 kg: 50 (−7).
  - DairyPlan: 70.379 kg. Vazias com IA > 35 d: 31 (−7). DNB: 65.
- Partos em 22/10 = 0. O arquivo bruto não tem nenhum parto (DtÚltParto) nem nascimento com data de 22/10; deve ser
  lançamento ainda não feito. Como os partos são contados pelo relatório mais recente, o dia se corrige sozinho
  quando forem lançados.
- Leite comercializado de 21 e 22/10: pendente (falta o PDF da cooperativa).

### 23/10/2026 – coletas (PDF emitido em 23/10 às 11:45) e BoviSync baixado de novo
- Leite comercializado de 21/10: 71.964 L = 74.267 kg. DairyPlan 69.121 kg, diferença −6,9%. 22/10 fica para o
  próximo PDF.
- A pedido da usuária, o BoviSync foi baixado de novo à tarde (`--substituir`, relatório de 22/10) para pegar os
  partos lançados depois.
  - Partos de 22/10: 0 → 4. Partos de 21/10: 7 → 8.
  - Nascidas até 7 dias: 21. Lactação: 1.655. Lote 10: 39 (4 entradas, 6 saídas). Produção: 44,8 kg; ECM 45,8.
  - DairyPlan: 70.513 kg.

### 23/10/2026 – atualização da tarde
- A usuária aprovou uma segunda execução diária por volta das 16h: Routine `trig_01NS4miGnNSiY4d6HbGKRdUq`, às
  15h53, na conversa principal.
- Ela baixa o BoviSync de novo com `--substituir`, para pegar partos lançados depois das 11h, gera tudo de novo e só
  envia e salva se algum número mudou.
- Teste de gravação da rotina (sessão nova com add_repo push): OK.

### 24/10/2026 – rotina automática (relatório de 23/10)
- Primeira vez com os 10 dias completos (14/10 a 23/10). Planilha sem erros; PDF com 2 páginas.
- 23/10:
  - Lactação: 1.660 (+5); lote 10: 44 (+5 entradas, 0 saídas).
  - Produção: 44,6 kg (−0,2); ECM 45,6. Vacas < 20 kg: 44 (−8). Partos: 2.
  - DairyPlan: 70.955 kg.
- Vazias com IA > 35 d: 31 → 60 (+29). Todas as 29 que entraram estão como Vazia, com a última IA há exatamente
  36 dias. É um lote de IATF de 17/09 cruzando os 35 dias, não erro.
- Leite comercializado de 22 e 23/10: pendente (falta o PDF da cooperativa).
- Atualização da tarde (24/10, 15h53), relatório de 23/10:
  - Lote 10: 44 → 48 (entradas 5 → 9). No tanque: 1.616 → 1.612.
  - Vacas < 20 kg: 44 → 43. DairyPlan: 70.955 → 70.949 kg. Leite descartado: 564 → 570 kg.
  - Inseminadas > 35 d: 25 → 24. Partos sem mudança (2).

### 25/10/2026 – rotina automática (relatório de 24/10, sábado)
- Janela agora de 15/10 a 24/10 (10 dias; o 14/10 saiu). Planilha sem erros; PDF com 2 páginas.
- 24/10:
  - Lactação: 1.660 (=); lote 10: 48 (0 entradas / 0 saídas).
  - Produção: 44,7 kg; ECM 45,6. Vacas < 20 kg: 42. Partos: 3. DNB: 63 (−2).
  - DairyPlan: 70.604 kg.
- **Achado – a atualização da tarde desloca eventos de um dia para o anterior:**
  - O BoviSync é uma foto do momento do download. O download das 15h53 do dia D (gravado como relatório de D−1) já
    traz os lançamentos da manhã e da tarde de D.
  - Exemplo: as 3 vacas paridas em 24/10 (DtÚltParto 24/10; brincos 6223, 5195, 5277) já estavam Frescas, nos lotes
    1, 3 e 10, no "relatório de 23/10" baixado às 15h53 de 24/10. As 4 entradas a mais no lote 10 desse download
    eram, provavelmente, movimentos de 24/10. Por isso 24/10 aparece com 0 entradas e 0 saídas e com a lactação igual.
  - Os partos não são afetados, porque já são contados pela DtÚltParto do relatório mais recente: o atraso de
    lançamento se corrige sozinho no dia seguinte, mesmo sem a atualização da tarde.
  - Recomendação feita à usuária: desligar a atualização da tarde ou limitá-la. Aguardando a decisão.

### 26/10/2026 – coletas (PDF emitido em 26/10 às 10:21)
- Completa de 22 a 24/10:
  - 22/10: 68.408 L = 70.597 kg; DairyPlan 70.513, diferença −0,1%.
  - 23/10: 70.089 L = 72.332 kg; DairyPlan 70.949, diferença −1,9%.
  - 24/10: 71.876 L = 74.176 kg; DairyPlan 70.604, diferença −4,8%.
- Média dos 10 dias: −0,8%.
- 25/10 fica para o próximo PDF.

### 26/10/2026 – rotina automática (relatório de 25/10, domingo)
- **Produção de 25/10 incompleta no BoviSync/DairyPlan:**
  - Leite 24 h médio de 20,6 kg (normal ~45); total DairyPlan de 32.674 kg (normal ~70.000).
  - Em todas as vacas, o leite do dia veio com mediana de 42% do Leite7 (no dia 24/10 era 103%). Faltam ordenhas de
    25/10 na importação, não é queda real.
  - Baixado de novo às 10h56: igual. Enviado à usuária com aviso.
  - A Leite7 também caiu (43,8 → 40,4) porque inclui esse dia parcial.
  - Corrigir com novo download quando as ordenhas entrarem.
- Demais números de 25/10 (corretos):
  - Lactação: 1.672 (+12). No tanque: 1.626. Lote 10: 46 (0 entradas, 2 saídas). Secas: 196 (−9).
  - Partos: 10. Nascidas até 7 dias: 28. DNB: 67 (+4). Vazias com IA > 35 d: 68 (+8). Gestantes: 982 (54,5%).
- Leite comercializado de 25/10: pendente (próximo PDF).

### 27/10/2026 – correção das pesagens de 25/10, relatório de 26/10 e coletas
- **Correção pedida pela usuária:**
  - "desconsiderar as pesagens de ontem, pq houve erro de leitura; usar as de hoje para ontem".
  - A coluna Leite de `Zootecnico_2026-10-25.xlsx` foi trocada, vaca por vaca (pelo brinco), pela Leite de
    `Zootecnico_2026-10-26.xlsx`. O original ficou em
    `dados/zootecnico_original/Zootecnico_2026-10-25_pesagem_com_erro.xlsx`, e o registro em
    `dados/correcoes_leite.json`.
  - Efeito em 25/10: produção 20,4 → 45,7 kg; DairyPlan 32.674 → 73.529 kg.
  - **Não rodar `baixa_bovisync.py --substituir` para 25/10**, senão o erro volta.
- **Relatório de 26/10** (baixado às 9h21, antes da rotina; a rotina das 10h48 vai encontrar o arquivo e parar):
  - Lactação: 1.666 (−6). No tanque: 1.603 (−23).
  - Lote 10: 63 (+32 entradas, −15 saídas). As 32 entradas vieram de todos os lotes (10 do lote 5), com DEL de 7
    a 409, a maioria prenhes; parece um tratamento em lote. Leite descartado: 1.533 kg (2,1%).
  - Produção: 45,7 kg; ECM 46,7. Vacas < 20 kg: 44. Partos: 2. Saída de adultas: 6.
  - DairyPlan: 72.719 kg.
- **Coletas (PDF emitido em 27/10 às 9:20):** 25/10 = 70.175 L = 72.421 kg × DairyPlan 73.529 kg (corrigido),
  diferença +1,5%. 26/10 fica para o próximo PDF.

### 28/10/2026 – rotina automática (relatório de 27/10)
- Pesagens normais (Leite/Leite7 com mediana de 1,10). Planilha sem erros; PDF com 2 páginas.
- 27/10:
  - Lactação: 1.644 (−22); secas: 218 (+22). Secagem de 22 vacas prenhes para o lote 7, já vista na comparação
    da tarde de 27/10.
  - Lote 10: 64 (+1 entrada / 0 saídas); leite descartado 1.503 kg (2,1%).
  - Produção: 44,7 kg (−1,0); ECM 45,6. Vacas < 20 kg: 47. DairyPlan: 70.217 kg.
  - Partos: 0, ainda sem lançamento com data de 27/10. Corrige sozinho no próximo relatório se for lançado depois.
- Leite comercializado de 26 e 27/10: pendente (próximo PDF).
- Coletas (PDF emitido em 28/10 às 11:02): 26/10 = 70.702 L = 72.964 kg × DairyPlan 72.719 kg, diferença −0,3%.
  Média dos 10 dias: −0,3%. 27/10 fica para o próximo PDF.
- Partos de 27/10, a pedido da usuária ("rodar novamente já com os partos lançados"):
  - O BoviSync foi baixado às 11h36 de 28/10 numa cópia separada. No relatório oficial de 27/10 foram levados **só**
    DtÚltParto e LACT dos animais com parto até 27/10: brincos 5945 (novilha, LACT 0 → 1), 3693 e 4723.
  - Lotes e demais colunas ficaram iguais, para não trazer os movimentos de 28/10 para 27/10.
  - Partos de 27/10: 0 → 3. Adultas: 1.862 → 1.863. Jovens: 1.912 → 1.911.
  - O original ficou em `dados/zootecnico_original/Zootecnico_2026-10-27_antes_partos.xlsx` e o registro em
    `dados/correcoes_leite.json`.
  - Já há 4 partos lançados com data de 28/10 (novilhas 6063, 6185, 6209, 6234); entram no relatório de 28/10.

### 29/10/2026 – rotina automática (relatório de 28/10)
- Pesagens normais (mediana Leite/Leite7 de 1,10). Planilha sem erros; PDF com 2 páginas.
- 28/10:
  - Lactação: 1.648 (+3). Lote 10: 66 (12 entradas / 10 saídas); leite descartado 1.684 kg (2,3%).
  - Produção: 44,6 kg; ECM 45,6. Vacas < 20 kg: 48. DairyPlan: 70.000 kg.
  - Partos: 4 (novilhas 6063, 6185, 6209, 6234).
  - Vazias com IA > 35 d: 66 (−6). DEL > 70 sem IA: 7 (−3).
- Novilhas gestantes: 527 → 547 (+20). 24 novilhas passaram de Bred para gestantes, com DDP de 27 a 33 dias, o que
  indica diagnóstico de gestação em 28/10.
- Leite comercializado de 27 e 28/10: pendente (próximo PDF).
- Coletas (PDF emitido em 29/10 às 15:13): 27/10 = 66.117 L = 68.233 kg × DairyPlan 70.217 kg, diferença +2,9%.
  Média dos 10 dias: −0,6%. 28/10 fica para o próximo PDF.

### 30/10/2026 – rotina automática (relatório de 29/10)
- Pesagens normais (mediana Leite/Leite7 de 1,10). Planilha sem erros; PDF com 2 páginas.
- 29/10:
  - Lactação: 1.652 (+4). Lote 10: 65 (0 entradas / 1 saída); leite descartado 1.679 kg (2,3%).
  - Produção: 44,7 kg; ECM 45,7. Vacas < 20 kg: 46. DairyPlan: 70.317 kg. Partos: 2.
- Os partos de 28/10 foram de 4 para 6 sozinhos (os 2 lançados à tarde), sem precisar trocar o relatório. Isso
  confirma que a contagem pela DtÚltParto do relatório mais recente corrige os atrasos.
- Leite comercializado de 28/10: 70.987 kg (−1,4%). 29/10 pendente.

### 31/10/2026 – rotina automática (relatório de 30/10)
- Pesagens normais (mediana Leite/Leite7 de 1,09). Planilha sem erros; PDF com 2 páginas.
- 30/10:
  - Lactação: 1.657 (+5). No tanque: 1.607 (+20).
  - Lote 10: 50 (9 entradas / 24 saídas). As 24 saídas voltaram todas para o lote 6, provavelmente o fim do
    tratamento em lote de 26/10. Leite descartado: 1.373 kg (1,9%).
  - Produção: 44,9 kg; ECM 45,9. Vacas < 20 kg: 56 (+10). DairyPlan: 70.380 kg. Partos: 2.
- Vazias com IA > 35 d: 67 → 93 (+26).
  - 25 são vazias com a última IA há exatamente 36 dias (lote de IATF de 24/09 cruzando os 35 dias).
  - 1 passou de Prenha para Vazia com IA há 71 dias: possível perda gestacional, vale conferir.
- Leite comercializado de 29 e 30/10: pendente.

### 01/11/2026 – rotina automática (relatório de 31/10, sábado)
- Planilha sem erros; PDF com 2 páginas. Mediana Leite/Leite7 de 1,11 no geral.
- **Lote 1 provavelmente com erro de registro de leite:**
  - As mesmas 221 vacas foram de 45,1 para 56,5 kg em um dia.
  - Leite/Leite7 mediana de 1,43 (nos outros lotes, 1,08–1,12). Razão 31/10 ÷ 30/10 por vaca: mediana 1,32.
  - Deve ser uma ordenha a mais ou duplicada no lote 1. Isso puxa a produção geral (46,1 kg) e o DairyPlan
    (73.310 kg, +2.931).
  - Enviado com aviso; dados não alterados. Esperando a usuária dizer se corrige, como foi feito em 25/10.
- **Saída de 19 adultas:**
  - 10 do lote 1, 3 do 6, 3 do 7, 2 do 10, 1 do 14.
  - Status: 4 Frescas, 5 DNB, 3 Bred, 3 secas, 2 prenhes, 2 vazias.
  - DNB caiu de 65 para 58. Adultas: 1.851.
- **Outros números de 31/10:**
  - Lactação: 1.642 (−15). Lote 10: 44 (3 entradas / 9 saídas). Partos: 2. Vacas < 20 kg: 49.
- Leite comercializado de 29 a 31/10: pendente.

### 02/11/2026 – mudança de indicadores (pedido da usuária)
- Removida a linha "DEL médio (lotes 1 a 6)". Fica só "DEL médio da lactação".
- Nova linha no bloco Recria: **"% de fêmeas nas nascidas (últimos 7 dias)"**.
  - Cálculo: fêmeas com idade ≤ 7 dias ÷ todos os nascidos com idade ≤ 7 dias, machos incluídos (LACT 0). Melhor ↑.
  - É o único indicador em que os machos entram (no denominador).
  - Valores: de 72% (22/10) a 85% (28/10); 31/10 = 69,2% (18 fêmeas e 8 machos).
- **Correção da usuária, no mesmo dia:** a conta é **fêmeas nascidas ÷ partos**. Os machos não entram, porque nem
  todos são cadastrados.
  - Linha renomeada para "% de fêmeas nascidas ÷ partos (últimos 7 dias)".
  - Denominador: vacas e novilhas com DtÚltParto nos últimos 7 dias, no relatório do próprio dia.
  - Valores: de 65,6% (22/10) a 78,1% (26/10); 31/10 = 66,7% (18 fêmeas em 27 partos).

### 02/11/2026 – data do implante de embrião (DtIMPL)
- Pedido da usuária: incluir a data do implante de embrião e usá-la como data da última inseminação nas vacas que a
  tiverem.
- A usuária criou no BoviSync uma versão do relatório com a coluna (item `IMPLDate`, cabeçalho DtIMPL):
  `https://bovisync.farm/report/insights/?report_uuid=6ca8ee06680b46ad90a1f3873a1cafa5`. O download passa a usar
  esse relatório; o antigo era `report/CTBOCW`.
  - Nesse relatório o item interno ApiId nunca fica pronto; o script agora o ignora.
- Planilha: "Dias desde IA" = data − MAX(DATA da IA, DtIMPL), ou seja, vale a mais recente. Isso altera Inseminadas
  e Vazias com IA > 35 dias (vacas e novilhas). Os relatórios antigos não têm DtIMPL.
- Teste com o relatório de 01/11:
  - 346 animais com DtIMPL (308 adultas e 38 novilhas).
  - Em 91 o implante é mais recente que a IA; 32 não têm IA.

### 02/11/2026 – relatório de 01/11 (domingo)
- A rotina das 10h48 não disparou (a conversa estava ocupada com o ajuste da DtIMPL); rodado à mão às 11h02.
  Primeiro relatório baixado do BoviSync novo, com DtIMPL. Planilha sem erros; PDF com 2 páginas.
- **Leite dos lotes 1 a 4 com provável erro de registro:**
  - Leite/Leite7 com mediana de 1,32 a 1,36 (lotes 5 e 6: 1,07–1,09).
  - Produção 55,2 kg (normal ~45); DairyPlan 87.636 kg.
  - Mesmo padrão do lote 1 em 31/10, agora em 4 lotes. Provável ordenha duplicada ou erro de importação no DairyPlan.
  - Enviado com aviso; dados não alterados. Aguardando a usuária decidir a correção (31/10 e 01/11).
- **Diagnóstico de gestação em 01/11:**
  - 48 vacas passaram de Bred para Prenha (DDP mediano de 32).
  - As 24 inseminadas com IA > 35 d foram todas examinadas: 12 prenhes e 12 vazias. Inseminadas com IA > 35 d: 24 → 0.
  - Gestantes: 968 → 1.002 (55,8%).
- Vazias com IA > 35 d: 106 (+11), já contando a DtIMPL.
- Lactação: 1.652. Lote 10: 44. Partos: 7. DNB: 60. Novilhas > 15 meses não gestantes: 80.
- Usuária, 02/11: **"corrigir"** o leite de 31/10 (lote 1) e 01/11 (lotes 1 a 4) com as pesagens do primeiro dia
  normal seguinte.
  - Ainda não há esse dia; o relatório de 02/11 sai em 03/11.
  - A pendência ficou em `dados/correcoes_pendentes.json`, e a rotina diária confere e aplica.
- Usuária, 02/11: **"ajuste pelo último dia com pesagem normal"**. Aplicado na hora, e a pendência foi apagada:
  - 31/10, lote 1: Leite de 30/10. Média 56,5 → 45,1 kg.
  - 01/11, lote 1: Leite de 30/10. Média 55,3 → 45,0 kg.
  - 01/11, lotes 2 a 4: Leite de 31/10, normal nesses lotes. Média 66,3 → 51,8 kg.
  - Vacas sem pesagem no dia de origem (15–20 no lote 1, quase todas recém-paridas) ficaram sem pesagem.
  - Originais em `dados/zootecnico_original/*_pesagem_com_erro.xlsx`; registro em `dados/correcoes_leite.json`.
  - Resultado: produção 31/10 = 44,6 kg (DairyPlan 70.574); 01/11 = 46,2 kg (DairyPlan 72.660).
  - **Não rodar `--substituir` em 31/10 nem em 01/11.**

### 03/11/2026 – rotina automática (relatório de 02/11)
- Pesagens normais em todos os lotes (Leite/Leite7: lotes 1–4 de 0,99 a 1,03; lote 5 1,14; lote 6 1,04). Sem
  correções pendentes. Planilha sem erros; PDF com 2 páginas.
- 02/11:
  - Lactação: 1.653; no tanque: 1.620 (+12). Lote 10: 33 (0 entradas, 11 saídas); descarte de 615 kg (0,8%).
  - Produção: 45,3 kg; ECM 46,3. Vacas < 20 kg: 44. DairyPlan: 72.267 kg.
  - Partos: 0, ainda sem lançamento com data de 02/11; corrige sozinho no próximo relatório.
  - Gestantes: 1.002 (55,8%). Vazias com IA > 35 d: 106.
- Coletas de outubro (PDF do mês, emitido em 03/11): 29/10 = 68.652 L = 70.849 kg × DairyPlan 70.317 kg, −0,8%.
- Coletas de novembro (PDF emitido em 03/11 às 13:37; período por recepção de 01/11 a 03/11).
  - **Correção no `le_leite_vendido.py`:** antes, cada PDF novo substituía os dias do anterior, e o dia dividido
    entre dois PDFs na virada do mês ficava errado ou sumia (30/10).
  - Agora as coletas de todos os PDFs são juntadas pelo boleto, e só vale o corte do PDF mais recente.
  - Conferido: todos os dias antigos ficaram iguais.
  - Novos dias:
    - 30/10: 62.185 L = 64.175 kg × DairyPlan 70.380, diferença +9,7% (só 2 coletas, às 13:12 e 17:48;
      efeito do horário).
    - 31/10: 72.311 L = 74.625 kg × 70.574 (corrigido), −5,4%.
    - 01/11: 70.874 L = 73.142 kg × 72.660 (corrigido), −0,7%.
  - Média de 10 dias: +0,1%. 02/11 fica para o próximo PDF.

### 04/11/2026 – rotina automática (relatório de 03/11)
- **Lotes renumerados pela fazenda em 03/11:**
  - Lote 7 (antes das secas) agora tem 127 vacas em lactação, todas com leite: 47 Frescas, 40 Prenhes,
    25 Bred, 14 Vazias.
  - Lote 15 (antes dos machos) agora tem 105 secas e 10 machos.
  - 147 vacas saíram dos lotes de lactação: 126 foram para o 7 e 21 para o 15.
  - Pela regra atual (lactação = lotes 1–6 e 10; 20 e 30 contam como 2 e 3), a lactação cai de 1.653 para 1.504,
    as secas sobem para 350 e as paridas até 21 dias caem de 89 para 46.
  - **Aguardando a usuária confirmar os lotes de lactação** (incluir o 7?).
- **Pesagens de 03/11 baixas nos lotes 1–4:** Leite/Leite7 de 0,68 a 0,73 (lotes 5–6 normais), provável ordenha
  faltando. DairyPlan: 45.794 kg. Aguardando confirmação para corrigir pelo último dia normal (02/11).
- Enviado com aviso. Partos: 1. Gestantes: 1.000. Vazias com IA > 35 d: 113.
- Coletas (PDF emitido em 04/11 às 18:32): 02/11 = 71.398 L = 73.683 kg × DairyPlan 72.267 kg, diferença −1,9%.
- **Decisões da usuária em 04/11:**
  - **Lote 7 virou lote de lactação** a partir de 03/11; antes era o das secas. **Lote 15 virou o lote das secas.**
  - "Usar pesagens do dia 2": as medidas falharam por erro de comunicação.
- **Planilha:**
  - Lactação = lotes 1–6 e 10, e o lote 7 com Data ≥ 03/11/2026 (fórmula com DATE(2026,11,3)).
  - Tanque = lactação menos o lote 10 (lotes 1 a 7).
  - Nova linha "Produção média do lote 7 (DP)", cor rosa #D6409F.
  - Linhas renomeadas: "Vacas em lactação (lotes 1 a 7 e 10)" e "Em lactação no tanque (lotes 1 a 7)".
  - O lote 15 entra sozinho como seca (adulta fora da lactação).
- **PDF:** gráfico por lote com 7 barras; página 2 com a linha do lote 7. Continua com 2 páginas.
- **Pesagens de 03/11, lotes 1–4 e 7:** trocadas, pelo brinco, pelas de 02/11. Média 33,4 → 50,5 kg; 21 vacas sem
  par. Os lotes 5–6 ficaram como estavam (normais). Original em
  `dados/zootecnico_original/Zootecnico_2026-11-03_pesagem_com_erro.xlsx`.
  - **Não rodar `--substituir` em 03/11.**
- **03/11 corrigido:**
  - Lactação: 1.631 (22 secadas para o lote 15). No tanque: 1.597. Secas: 223.
  - Produção: 43,9 kg; ECM 44,9. Lote 7: 54,0 kg. DairyPlan: 68.206 kg.
  - Lote 5 caiu para 34,6 kg e lote 6 para 24,4 kg por mudança de composição: as maiores produtoras do 5 foram para
    o 7, e o 6 recebeu 29 vacas. Vacas < 20 kg: 68, a maioria no lote 6 (45).

### 05/11/2026 – rotina automática (relatório de 04/11)
- Pesagens normais em todos os lotes, de 1 a 7 (Leite/Leite7 de 0,99 a 1,08). Sem correções pendentes. Planilha
  sem erros; PDF com 2 páginas.
- 04/11:
  - Lactação: 1.631; no tanque: 1.581.
  - Lote 10: 50 (+16 entradas); descarte de 948 kg (1,4%).
  - Produção: 42,7 kg; ECM 43,6. Lote 7: 46,0 kg.
  - Vacas < 20 kg: 59. DairyPlan: 66.868 kg. Partos: 1.
- Lote 7 caiu de 54,0 para 46,0 kg: em 03/11 o valor era o leite de 02/11, quando essas vacas ainda estavam nos
  lotes de origem (correção). 46 kg é a primeira medida real do lote 7.
- Novilhas gestantes: +9 (544), diagnóstico de prenhez. Novilhas > 15 meses não gestantes: 72 (−10).
- Coletas (PDF emitido em 05/11 às 18:39): 03/11 = 70.589 L = 72.848 kg × DairyPlan 68.206 kg (corrigido com as
  pesagens de 02/11), diferença −6,4%. Média de 10 dias: −0,5%. 04/11 fica para o próximo PDF.

### 05/11/2026 – acompanhamento das quartas e quintas (dias de cio)
- Pedido da usuária: guardar, **fora do relatório**, a variação de produção e a média de todas as quartas e
  quintas-feiras, dias em que as vacas manifestam cio.
- `scripts/quartas_quintas.py` gera `monitoramento/analises/Quartas_Quintas_ARCAFLA.xlsx`.
  - Abas: Quartas e quintas, Resumo por dia da semana, Todos os dias.
  - Produção média (kg/vaca, tanque, Leite > 0) e total do tanque, por dia.
  - Variação vs dia anterior e vs média dos 7 dias anteriores.
  - Usa os relatórios já corrigidos; o lote 7 entra no tanque desde 03/11.
- A rotina diária roda o script e salva o arquivo, sem enviar.
- Primeiro resultado (14/10 a 04/11, 7 quartas e quintas):
  - Quartas: 43,9 kg; quintas: 45,0 kg; demais dias: 45,0 kg. Quarta é o dia de menor média.
  - 04/11 (quarta): −1,15 kg vs terça e −2,15 kg vs média dos 7 dias.

### 06/11/2026 – rotina automática (relatório de 05/11, quinta)
- Pesagens normais em todos os lotes (Leite/Leite7 de 1,00 a 1,08). Planilha sem erros; PDF com 2 páginas.
- 05/11:
  - Lactação: 1.631 (=). Lote 10: 50 (sem entradas nem saídas). Nenhuma movimentação de lote no dia.
  - Produção: 43,0 kg; ECM 44,0. Lote 7: 49,9 kg. Vacas < 20 kg: 69. DairyPlan: 67.776 kg.
  - Partos: 0, ainda sem lançamento; corrige sozinho.
- Vazias com IA > 35 d: 114 → 41, por causa das 73 IAs e implantes de 05/11 (vistos na véspera às 18h51).
  DEL > 70 sem IA: 22 → 11.
- Quintas: 05/11 = 43,6 kg/vaca, +0,56 kg vs quarta e −3,0% vs média dos 7 dias anteriores. Arquivo das
  quartas e quintas atualizado.
- 06/11 às 12h22, a pedido da usuária ("atualizar dados, pegar dados atualizados do BoviSync"):
  - **Coletas (PDF emitido em 06/11 às 12:21):** 04/11 = 64.343 L = 66.402 kg × DairyPlan 66.868 kg, diferença
    +0,7%. Média de 10 dias: −0,4%.
  - **BoviSync baixado de novo:** 4 partos em 05/11 (brincos 6015, 6109, 6167 — novilhas — e 4190) levados ao
    relatório de 05/11, só DtÚltParto e LACT. Partos de 05/11: 0 → 4. Adultas: 1.858.
  - Original em `dados/zootecnico_original/Zootecnico_2026-11-05_antes_partos.xlsx`.
  - Também havia 15 mudanças de lote (9 saídas do lote 10 para os lotes 2, 3 e 6; 5 recém-paridas do lote 14 para
    o 1) e 2 partos de 06/11. Não foram levadas para 05/11 (não dá para saber se foram de 05 ou 06/11); entram no
    relatório de 06/11.

### 07/11/2026 – rotina automática (relatório de 06/11, sexta)
- Pesagens normais em todos os lotes (Leite/Leite7 de 0,98 a 1,09). Planilha sem erros; PDF com 2 páginas.
- 06/11:
  - Lactação: 1.640 (+9). Lote 10: 56 (15 entradas, 9 saídas); descarte de 1.007 kg (1,5%).
  - Produção: 42,6 kg; ECM 43,6. Lote 7: 48,0 kg. Vacas < 20 kg: 77. DairyPlan: 67.005 kg.
  - Partos: 4. Nascidas até 7 dias: 17.
- Vazias com IA > 35 d: 41 → 60 (+19). As 20 que entraram estão como Vazia, com a última IA há exatamente 36 dias:
  lote de IATF de 01/10 cruzando os 35 dias.
- Gestantes: 992 (−9); 3 prenhes pariram.

### 08/11/2026 – rotina automática (relatório de 07/11, sábado)
- Pesagens normais (Leite/Leite7 de 0,95 a 1,09). Planilha sem erros; PDF com 2 páginas.
- 07/11:
  - Lactação: 1.640 (=). Lote 10: 52 (0 entradas, 4 saídas); descarte de 1.025 kg (1,5%).
  - Produção: 42,7 kg; ECM 43,6. Lote 7: 49,7 kg. Lotes 5 e 6 caíram 1,4 e 1,6 kg.
  - Vacas < 20 kg: 90 (+13). DairyPlan: 66.798 kg. Partos: 3.
  - Gestantes: 992. Vazias com IA > 35 d: 60. Novilhas > 15 meses não gestantes: 79 (+6).
- Leite comercializado de 05/11 em diante: pendente.

### 09/11/2026 – rotina automática (relatório de 08/11, domingo)
- Pesagens normais (Leite/Leite7 de 0,90 a 1,07; o lote 6 no limite de baixo, 0,90). Planilha sem erros; PDF
  com 2 páginas.
- 08/11:
  - Lactação: 1.650 (+10). Lote 10: 55 (5 entradas / 2 saídas).
  - Produção: 41,8 kg (−0,9); ECM 42,7. DairyPlan: 65.528 kg. Partos: 3.
- **Diagnóstico de gestação:** 35 vacas de Bred para prenhes (DDP de 28 a 34). Gestantes: 1.017 (56,4%).
  DEL > 150 não gestantes: 234 (−9).
- **Vacas < 20 kg subindo:** 77 → 90 → 103 em três dias.
  - Concentradas no lote 6: 55 → 66 → 80.
  - DEL mediano ~300: vacas de final de lactação, perto da secagem; o lote 6 caiu de 24,0 para 20,7 kg.
- Leite comercializado de 05/11 em diante: pendente.
- 09/11 às 14h22, a pedido ("atualizar dados" e "atualizar dados do BoviSync também"):
  - **Coletas (PDF emitido em 09/11 às 13:08):** completou de 05 a 07/11.
    - 05/11: 69.268 L = 71.485 kg × DairyPlan 67.776 kg, −5,2%.
    - 06/11: 70.870 L = 73.138 kg × 67.005 kg, −8,4%.
    - 07/11: 38.427 L = 39.657 kg × 66.798 kg, +68,4%. **Só 1 coleta nesse dia** (16:47); as coletas
      vizinhas foram em 06/11 às 23:02 e em 08/11 às 05:03. É efeito do horário, não falta de leite.
    - A média de 10 dias passou a +5,7% por causa desse dia.
  - **BoviSync de 14h22:** nenhum parto novo até 08/11. 7 saídas do rebanho, 9 vacas do lote 10 para o 6 e mudanças
    de status (2 prenhes → vazias, 3 para DNB) — provavelmente de 09/11, entram no relatório de amanhã. Nada alterado
    em 08/11.
- 09/11, **análises do tanque** (PDF mensal Castrolanda "Resultado Análise Leite" de 10/2026, emitido em 09/11; guardado
  em `dados/analise_tanque/Castrolanda_Resultado_Analise_2026-10.pdf`):
  - O PDF dá a **data da análise** (~2 dias depois da coleta). Cada resultado foi ligado à coleta do mesmo tanque
    (data do "DE NOVO", que é a data de coleta).
  - As análises já transcritas dos prints (04–05/10, 12–13/10, 17–18/10) **conferem 100%**.
  - Faltava a lactose de 04–05/10: incluída.
  - **Grupo novo:** coletas de 24 e 25/10, tanques 2, 3 e 4. O tanque 1 dessa semana só tinha ácidos graxos.
    Média ponderada: gordura 3,57; proteína 3,36; lactose 4,73; ST 12,64; CCS 263; CPP 11,7; ureia 11,8. Vale de
    24/10 em diante e altera o ECM desses dias.
  - Pedidos da usuária: **ácidos graxos não precisam** (não guardados). A linha passou a se chamar "Data da análise
    do tanque (última coleta)" e mostra **só a última data de coleta do grupo** (ex.: 25/10). A validade continua a
    partir da primeira data.

## 10/11/2026 – rotina diária (relatório de 09/11)
- Pesagens normais (Leite/Leite7 por lote 1–7: 1,09 · 1,07 · 1,08 · 1,08 · 1,02 · 0,97 · 1,10); sem correções.
- Lactação 1653 (+3); tanque 1606; produção 43,6 kg (+1,8); ECM 45,6; DairyPlan 67.802 kg.
- 8 partos em 09/11 (3 em 08/11); lote 14 → 1 (5) e 14 → 7 (4).
- 7 saídas de adultas: 4 DNB (lotes 6 e 10), 1 seca (lote 14), 2 do lote 10 (fresca DEL 40 e vazia DEL 131).
- Lote 10: 4 entradas, 12 saídas (9 voltaram ao lote 6, 2 saíram do rebanho, 1 DNB saiu) → 47 animais.
- Vacas < 20 kg: 85 (−18). Comercializado de 08/11 = 72.501 kg (−9,6% vs DairyPlan; 07/11 teve só uma coleta).

## 11/11/2026 – coletas (PDF de 11/11 10h17)
- 09/11: 2 coletas (05h02 tanque 2 e 16h23 tanque 3) = 73.711 L = 76.070 kg; DairyPlan 67.802 kg → −10,9%.
  A coleta das 05h02 leva leite do dia 08; somando 07 a 09/11 a diferença se equilibra (07/11 teve só 1 coleta).

## 11/11/2026 – rotina diária (relatório de 10/11)
- Pesagens normais (1,04 · 1,02 · 1,02 · 1,03 · 1,06 · 1,08 · 1,05); sem correções.
- Lactação 1629 (−24): 22 secagens para o lote 15 (lotes 2–6 e 1 do lote 10); 27 vacas do 15 → 14 (pré-parto).
- Reorganização grande de lotes (1→4, 4→5/7, 5→6/7, 6→4/5, 7→5); produção 43,7 kg (+0,1), ECM 45,7.
- 3 partos; 2 saídas de adultas (Bred, lotes 6 e 10); lote 10: 0 entradas, 2 saídas → 45.
- Vazias com IA > 35 d: 73 (+5) — 6 vazias inseminadas em 05/10 completaram 36 dias.
- Vacas < 20 kg: 58 (−27). Comercializado de 09/11 = 76.070 kg (DairyPlan −10,9%).

## 11/11/2026 – DairyPlan × comercializado pela média do período
- Pedido: "no quadro leite comercializado x leite DairyPlan usar a média do período".
- A média agora é (Σ DairyPlan − Σ comercializado) ÷ Σ comercializado nos dias com coleta (antes: média simples
  das diferenças diárias, que o 07/11 com uma coleta só puxava para +2,9%). Período 01–09/11: −0,6%.
- O cartão do PDF mostra essa média como valor principal (sem "vs ontem"), com o período e a média diária em kg.
  O gráfico continua com a linha "dif." de cada dia e o "dif. méd." no subtítulo, agora com a mesma média.
- Gráfico "Leite DairyPlan × comercializado" também passou para a média acumulada (escolha da usuária entre
  acumulada, móvel de 3 dias e linha da média): pontos e linha "dif." acumulados desde o 1º dia; 10/11: −0,6%.

## 12/11/2026 – coletas (PDF de 12/11 09h35)
- 10/11: 35.422 L (05h49) + 34.816 L (21h39) + 7 L (20h00, boleto 101126484, tanque 1 – provável amostra/resíduo)
  = 70.245 L = 72.493 kg; DairyPlan 67.813 kg → −6,5% no dia. Média do período (01–10/11): −1,3%.

## 12/11/2026 – análises do tanque de novembro (PDF Castrolanda emitido 12/11 10h44)
- O PDF chegou junto com as coletas, mas é "Resultado Análise Leite" (LEI0940). Tirado de leite_vendido/ e salvo em
  dados/analise_tanque/Castrolanda_Resultado_Analise_2026-11_emitido_2026-11-12.pdf (ácidos graxos ignorados).
- Grupo novo: coletas de 05/11 (tanques 1 e 4) e 06/11 (tanques 2 e 3). Médias: gordura 3,45 · proteína 3,34 ·
  lactose 4,74 · ST 12,46 · CCS 219 · CPP 6,75 · ureia 13,45. ECM de 10/11: 44,96 (antes 45,7 com a análise de 25/10).

## 12/11/2026 – rotina diária (relatório de 11/11, quarta)
- Pesagens normais (1,03 · 1,02 · 1,01 · 1,04 · 1,09 · 1,14 · 1,02); sem correções.
- Lactação 1630 (+1); tanque 1586; produção 43,8 kg (+0,1); ECM 45,0 (análise de 06/11); DairyPlan 68.931 kg.
- 6 partos; 9 saídas de adultas (4 frescas DEL 13–58 dos lotes 7 e 10, 2 secas, 1 DNB, 1 prenha, 1 inseminada).
- Lote 10: 14 entradas (lotes 2–7 e 20), 15 saídas (7 → lote 6, 2 → 7, 1 → 4, 1 → 15, 4 saíram do rebanho) → 44.
- Gestantes 1000 (−11): 6 partos, 3 prenhas → vazias, 1 saída; novilhas gestantes 540 (+10).
- Quarta-feira: 44,05 kg/vaca no tanque, +0,04 vs terça e +0,8 kg (+1,9%) vs média dos 7 dias anteriores.
- Vacas < 20 kg: 63 (+5).
- Pedido 12/11: resumo das análises do tanque (gordura, proteína, CPP, ureia, CCS) em tabela, com a média embaixo, em
  PDF → scripts/resumo_analises_pdf.py → monitoramento/analises/Resumo_Analises_Tanque_AAAA-MM-DD.pdf
  (arredondamento meio para cima, como no Excel). Rodar de novo quando chegar análise nova, se a usuária pedir.
