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
**OnFarm** (`dados/cultura_onfarm/OnFarm_grafico_2026-09-11.pdf` → `dados/cultura_onfarm_2026.json`; arquivo movido em 26/10)
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

## Análises de tanque avulsas – out/2026 (16/10/2026, painel versão 11)
- Fonte: mensagens do Pool Leite (PC 484), registradas em `dados/tanque_avulsas.json`. Para incluir uma nova análise, basta acrescentar uma linha nesse arquivo.
- 12/10: tanque 2 com CCS 158 e CBT 15; tanque 3 com CCS 363 e CBT 16. 13/10: tanque 1 com CCS 220 e CBT 11; tanque 4 com CCS 283 e CBT 18.
- Média simples da CCS: 256 (sem volume, não ponderada). É uma prévia: o mapa de out/26 vai substituir esses valores.
- CCS ponderada de set/26 por tanque, para comparar: tanque 1 316, tanque 2 300, tanque 3 347, tanque 4 383.
- Painel: bloco "Análises avulsas recebidas" na aba Tanque. Traz CCS, CBT, gordura, proteína, lactose, sólidos e ureia, e compara com a CCS real do último mapa.

## Controle de 16/10/2026 (26/10/2026, painel versão 12)
- Arquivo: `dados/apcbrh/R22_2026-10-16.xlsx` (REB 70105, emitido em 26/10/2026). São 1.591 vacas; o nº de linhas bate com o "No ANIMAIS".
  - Σ(prod × CCS) ÷ Σ prod = 305,02, igual à "MÉDIA CCS TANQUE" da APCBRH (305,02).
  - Lotes 1–6 e 10. Nenhuma CCS 9.998. 26 partos em branco. Nenhum parto alterado.
  - 139 vacas entraram e 176 saíram em relação a 18/09.
- Resultados de 16/10 (comparados com 18/09, intervalo de 28 dias):
  - CCS estimada do tanque sem o lote 10: 290 (309). APCBRH com o lote 10: 305 (325).
  - Vacas com CCS ≥ 200: 26,0%, 414 vacas (29,5%, 481).
  - Faixas: 1.177 < 200 | 181 200–499 | 89 500–999 | 144 ≥ 1.000.
  - Base da classificação: 1.452 vacas.
    - Sadias: 63,5% (922).
    - Novas infecções: 9,0% (131). Taxa de NI: 12,4% (15,9%), ou 13,3% por 30 dias.
    - Crônicas: 17,2% (250). Permanência: 62,7% (68,8%).
    - Recuperadas: 10,3% (149).
  - Recorrência: 50,4% (66 das 131 NI), ainda alta.
  - CCS elevada em ≥ 3 controles seguidos: 172 vacas (190).
  - Período seco: cura de 67,7% e NI de 13,6%. Pós-parto elevada: 16 vacas.
  - Lote 5: 35% da CCS estimada do tanque, 48 NI e 84 crônicas. Lote 6: 48% das vacas elevadas.
  - As 20 maiores contribuições (1,3% do leite) respondem por 22% da CCS estimada. Sem elas, a estimativa iria de 290 para 229.
  - Hiperqueratose escore 4: 39% com CCS ≥ 200 (rebanho 26%) e NI de 17% (rebanho 12,4%). A diferença diminuiu; o escore é de 01/05.
- Registro de mastite só até 28/09: os 37 tratamentos do intervalo de 18/09 a 16/10 estão incompletos. O painel marca isso com "*" e um aviso no relatório do mês.
- A regra de "queda de produção" agora aceita falta no controle, na mesma lactação, como no painel. Os números de queda de 14/08 e 18/09 nas notas antigas (61 e 79) passaram a 63 e 82.

## Registro de mastite atualizado até 24/10/2026 (26/10/2026, painel versão 13)
- Arquivo: `dados/mastite_tratamentos_2026.xlsx` (aba "Planilha1", mesmo layout da aba 2026).
  - `scripts/le_registro_mastite.py` lê os tratamentos desse arquivo, se ele existir. Hiperqueratose, secagem e doenças continuam vindo do `dados/MASTITE_2026.xlsx`.
- Total: 844 tratamentos. Os 773 anteriores não mudaram em nenhum campo; há 71 novos, de 29/09 a 24/10.
  - Produtos dos novos: 33 sem produto ("Mastite clinica"), 13 Ubrolexin, 13 Mastjet e 12 Mastgen.
  - 2 tratamentos novos estão sem quarto.
  - A coluna O agora só tem "MORTA" (vaca 6000, 13/07); o grau de hiperqueratose saiu desta planilha.
- Intervalo de 18/09 a 16/10: 86 tratamentos (antes eram 37, com o registro incompleto); 5,8 por 100 vacas a cada 30 dias.
  - 16 retratamentos.
  - 80% (67 de 84) em vacas que já estavam com CCS ≥ 200.
  - Mais casos nos lotes 5 (23), 2 (20), 3 (16) e 6 (11).
- Depois de 16/10 já há 22 tratamentos, que vão contar no próximo controle.
- Vacas com 3 ou mais tratamentos em 2026: 83.
- O aviso de "registro incompleto" saiu do painel, porque o registro agora cobre o controle de 16/10.

## Análise oficial do tanque – out/2026 (26/10/2026, painel versão 14)
- Arquivo: `dados/analise_oficial/analise_2026-10_emitido-2026-10-26.pdf`, o relatório "Resultado Análise Leite" do Sistema Controle de Leite, emitido em 26/10/2026.
  - Lido por `scripts/le_analise_oficial.py` → `dados/analise_oficial.json`. Cada linha é lida pela posição de suas colunas (tipo, data, tanque, resultado).
- Conteúdo: 204 linhas, ou seja, 17 análises × 4 tanques × 3 coletas.
  - Coletas: 04–05/10, 12–13/10 e 17–18/10. As análises de CCS, CPP etc. trazem a data da análise; os ácidos graxos trazem a data da coleta.
  - Pareamento: a k-ésima análise de cada tanque corresponde à k-ésima coleta. A 2ª coleta bate exatamente com as 4 mensagens de 12–13/10 (7 campos cada).
- CCS por tanque nas coletas 1 / 2 / 3: T1 253/220/268; T2 266/158/203; T3 224/363/219; T4 309/283/290.
  - Média simples de out/26: 255, contra 332 de set/26 (ponderada). Sem volume: é prévia até chegar o mapa de outubro.
- CPP entre 7 e 22.
- Controle de 16/10: estimativa sem lote 10 de 290 e APCBRH de 305. A CCS real ficou 35 abaixo da estimativa.
- Painel, aba Tanque:
  - outubro entra como coletas 1–3 (sem volume, marcado com "*");
  - as mensagens avulsas ficaram como "confirmadas";
  - nova tabela de ácidos graxos por tanque e coleta (o relatório não traz as unidades).
- Quando chegar o mapa de pagamento de outubro, ele passa a valer para o mês, com volume. As análises oficiais continuam na tabela de ácidos graxos.

## OnFarm por vaca (26/10/2026, painel versão 15)
- Arquivo: `dados/cultura_onfarm/onfarm_2026-10-19.xlsx` (exportação por vaca), lido por `scripts/le_onfarm_vacas.py`. Gera dois arquivos:
  - `dados/cultura_onfarm_vacas.json`: as 839 culturas;
  - `dados/cultura_onfarm_mensal.json`: o resumo mensal, que usa o gráfico até jan/26 e a planilha de fev/26 em diante.
- Período: 26/01 a 19/10/2026. São 752 culturas de mastite clínica e 87 de secagem.
  - Resultados: 419 positivos, 341 negativos, 70 contaminados (todos com 3 ou mais agentes) e 9 "fazer leitura".
  - Grau nos casos clínicos: 474 leves, 71 moderados e 229 graves.
  - A planilha não traz antibiograma nem tratamento (colunas vazias). Status "Em aberto" em todas as linhas.
- Validação: em resultados "Positivo", o nº de agentes por mês bate exatamente com o gráfico em PDF de fev a ago/26. Em ago/26 bate agente por agente, o que confirma a transcrição do PDF, inclusive a separação dos cinzas.
  - Jan/26: a planilha começa em 26/01 (19 contra 69 no gráfico). Set/26: o gráfico estava parcial (30 contra 55).
- Casos clínicos:
  - 40% negativos (300) e 9% contaminados (68).
  - Entre os positivos (378): Strep. agalactiae/dysgalactiae 42% (157; 43% graves), Staph não aureus 36%, Outros Gram-pos 21%, Prototheca/Levedura 9%, Gram-negativos 9%, Strep. uberis 7% (42% graves) e Staph. aureus 6%.
  - CCS ≥ 200 no controle anterior à cultura: Strep. ag/dysg 69%, Prototheca 84%, Staph. aureus 76% e negativas 66%.
- Cultura × registro de mastite: 220 de 844 tratamentos (26%) têm cultura OnFarm da mesma vaca até 3 dias do início. Em 73 deles (33%) a cultura foi negativa.
  - A cobertura de cultura caiu de 44–64% (fev–abr) para 8–22% (jun–out).
- Painel:
  - aba Cultura com a nova seção "OnFarm – por vaca": cartões, agentes por grau, CCS antes, cultura × tratamento e lista filtrável;
  - resumo mensal atualizado até out/26 (parcial);
  - Histórico da vaca com a lista de culturas OnFarm.

## PDF "Dinâmica da CCS no rebanho" (26/10/2026)
- Pedido explícito do usuário. Gerado por `scripts/gera_pdf_dinamica.js` a partir do painel montado, com as abas "Painel do mês" e "Evolução", controle de 16/10/2026.
- Saída: `relatorios/ARKAFLA_Dinamica_CCS_16-10-2026.pdf`, A4 retrato, 3 páginas.
- Para outro controle: `PW=$(npm root -g)/playwright node scripts/gera_pdf_dinamica.js painel/painel_qualidade_ARKAFLA.html relatorios/ARKAFLA_Dinamica_CCS_dd-mm-aaaa.pdf <nº do controle>`.

## Folha "Dinâmica da CCS no rebanho" no layout do modelo da fazenda (26/10/2026)
- O usuário trouxe o modelo impresso (APCBRH Relatório 2, controles de nov/25 a set/26, emitido em 24/09/2026) e pediu o mesmo layout com os dados atualizados.
- Gerada por `scripts/gera_pdf_dinamica_modelo.py` (HTML) e `scripts/html_para_pdf.js` (PDF). Saída: `relatorios/ARKAFLA_Dinamica_CCS_modelo_16-10-2026.pdf`, 1 página A4 paisagem.
- Layout do modelo: 4 cartões com o 1º controle para comparar, colunas 100% empilhadas por controle com n, tabela por controle e quadro de critérios.
- Cores e critérios do projeto, não do modelo:
  - cores: Sadia verde, Recuperada cinza, Nova infecção azul escuro, Crônica vermelho;
  - limite: < 200 = baixa, ≥ 200 = elevada;
  - comparação com o controle seguinte da mesma lactação; pós-parto e sem histórico ficam fora da base.
- Diferenças em relação ao modelo:
  - o modelo começa em nov/25; os nossos dados começam no controle de 02/02/26 (a 1ª classificação é 17/02);
  - em set/26, o modelo tem base de 1.456 vacas (S 61,6 / N 11,7 / C 18,1 / R 8,5); o nosso tem 1.438 (61,8 / 11,7 / 18,2 / 8,3). Diferença provável: o tratamento das recém-paridas e das faltas ao controle.
