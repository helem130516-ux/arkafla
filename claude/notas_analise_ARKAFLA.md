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
- Confirmação da APCBRH sobre REB 47238 → 70105.

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
