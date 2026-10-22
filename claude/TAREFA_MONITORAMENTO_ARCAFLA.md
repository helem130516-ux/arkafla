# Tarefa: Monitoramento diário do rebanho – Fazenda ARCAFLA (Castro – PR)

Documento de passagem de contexto para outro Claude. Ele descreve a tarefa, as regras de cálculo, o modelo do PDF
aprovado, a automação diária e as preferências da usuária. Atualizado em 22/10/2026.

---

## 1. Como trabalhar com a usuária

- **Responder sempre em português do Brasil**, inclusive nas mensagens de andamento.
- O nome da fazenda é **ARCAFLA**, com C. A grafia antiga "ARKAFLA" aparece só em nomes de arquivos antigos.
- **Não criar coisas novas sem pedido**: nada de colunas, indicadores ou gráficos extras. Ajustar só o que for pedido.
- O **modelo do PDF está aprovado como padrão** (seção 6). Não mudar o layout sem pedido explícito.
- Ao terminar cada mudança, mandar a **imagem da página 1** (PNG), o PDF e, quando mudar, a planilha.
  O app do celular nem sempre mostra o PDF, por isso a imagem vai junto.
- Imagens coladas no texto não chegam como arquivo. Pedir que a usuária **anexe pelo clipe**.
- **Segurança**:
  - Nunca gravar login, senha, tokens ou telefones em arquivo.
  - Nunca pedir senha no chat.
  - O login do BoviSync fica nas variáveis de ambiente `BOV_USER` e `BOV_PASS`, já cadastradas pela usuária.
  - A usuária **não vai trocar a senha**; não insistir nisso.
- O caminho pago do WhatsApp (Z-API) foi **recusado** pela usuária. O script existe, mas fica inativo.

---

## 2. Onde está tudo

- **Repositório GitHub**: `helem130516-ux/arkafla`
- **Branch de trabalho**: `claude/tender-clarke-13z0dx`. Todo o trabalho e os pushes vão para ele.
- **Notas detalhadas, com o histórico de cada decisão**: `claude/notas_analise_ARKAFLA.md`, nas seções de
  monitoramento diário e "PADRÃO DO PDF".

| Arquivo | Função |
|---|---|
| `scripts/baixa_bovisync.py` | Baixa o relatório "Zootécnico Jorge atualizado" do BoviSync (Playwright + Chromium) e grava `dados/zootecnico/Zootecnico_AAAA-MM-DD.xlsx`. Não sobrescreve um dia que já existe; só troca com `--substituir`. |
| `scripts/le_leite_vendido.py` | Lê o PDF "Demonstrativo das Coletas de Leite" da cooperativa e grava `dados/leite_vendido.json` (litros por dia) e `dados/coletas_leite.json`. Os PDFs ficam em `dados/leite_vendido/`. |
| `dados/analise_tanque.json` | Análises do tanque do laticínio (gordura, proteína, lactose, ST, CCS, CPP/CBT, ureia), em grupos por mensagem recebida. As imagens ficam em `dados/analise_tanque/`. |
| `scripts/monitor_diario.py` | Monta a planilha `monitoramento/Monitoramento_Diario_ARCAFLA.xlsx` só com fórmulas, nas abas Monitoramento, Análises do tanque, Parâmetros, Dados e Notas. |
| `scripts/monitor_pdf.py` | Gera `monitoramento/Monitoramento_Diario_ARCAFLA_AAAA-MM-DD.pdf`, A4 paisagem com 2 páginas. Confere que saíram exatamente 2 páginas. |
| `dados/logo_arcafla.png` | Logo da fazenda, já recortada, que aparece só na página 1. |
| `monitoramento/imagens/` | PNG das páginas, enviados à usuária. |
| `scripts/envia_whatsapp.py` | Envio pelo WhatsApp via Z-API. Inativo, porque a usuária recusou. |

### Sequência para atualizar o relatório

Usar sempre `/usr/bin/python3`, o Python 3.13 que tem pandas, openpyxl, reportlab, pypdf e PIL.

```bash
/usr/bin/python3 scripts/baixa_bovisync.py              # ou salvar o Excel enviado pela usuária
/usr/bin/python3 scripts/le_leite_vendido.py [novo.pdf] # quando chegar PDF de coletas
/usr/bin/python3 scripts/monitor_diario.py
/usr/bin/python3 <skill xlsx>/scripts/recalc.py monitoramento/Monitoramento_Diario_ARCAFLA.xlsx 600  # precisa: success, 0 erros
/usr/bin/python3 scripts/monitor_pdf.py                  # precisa: 2 páginas
pdftoppm -r 130 -png monitoramento/Monitoramento_Diario_ARCAFLA_AAAA-MM-DD.pdf monitoramento/imagens/ARCAFLA_AAAA-MM-DD_pagina
```

Depois:
1. Registrar o dia nas notas.
2. Fazer commit em português e `git push -u origin claude/tender-clarke-13z0dx`.
3. Mandar à usuária a imagem da página 1, o PDF e a planilha.

---

## 3. O que a usuária manda e o que fazer com cada coisa

1. **Excel "Zootécnico Jorge atualizado"**, se ela mandar à mão.
   - A data do relatório é **ref − 1**: o BoviSync calcula idade e DEL no dia da exportação, então o relatório é do
     dia anterior. A ref sai de DtNasc + IdadeDias.
   - Salvar como `dados/zootecnico/Zootecnico_AAAA-MM-DD.xlsx`.
2. **PDF de coletas da cooperativa**: rodar `le_leite_vendido.py arquivo.pdf`.
   - A cooperativa **não lança no fim de semana**; na segunda vem tudo.
3. **Prints das análises do tanque**: acrescentar um **grupo novo** em `dados/analise_tanque.json`, transcrevendo
   os valores e guardando a imagem.

---

## 4. Regras dos indicadores (planilha e PDF)

- **10 dias mais recentes como colunas** e indicadores como linhas, mais a coluna "Média 10 dias" e a coluna
  "Variação (último − anterior)".
  - A variação é **arredondada às casas exibidas**: o que aparece como "= 0" fica sem cor.
  - A coluna "Melhor" indica o sentido bom: ↑ bom quando sobe, ↓ bom quando desce, 0 bom perto de zero, vazio sem
    sentido definido. Ela decide a cor verde ou vermelha da variação.
- **Machos fora de tudo** (StatRepro = Male).
- **Lote 20 conta como lote 2, e lote 30 como lote 3.**
- **Em lactação** = lotes 1–6 e 10. O lote 10 é tratamento, com leite descartado.
  **Tanque** = lotes 1–6.

### Adultas (LACT > 0)

- **Rebanho e movimentação**:
  - vacas adultas, vacas em lactação, em lactação no tanque, lote 10 e vacas secas;
  - paridas há até 21 dias;
  - partos: contados pela DtÚltParto do relatório **mais recente**, porque o parto pode ser lançado com atraso;
  - saída de adultas;
  - lote 10: entradas, saídas e saldo;
  - DEL médio.
- **Produção**:
  - produção média nas últimas 24 h com DP entre parênteses;
  - ECM;
  - produção média dos lotes 1 a 6, cada uma com DP;
  - média do tanque, de primíparas e de multíparas;
  - vacas com leite < 20 kg no tanque;
  - vacas com pesagem e % com leitura de leite.
- **ECM** = prod × (0,327 + 0,1295·G + 0,0765·P), com G e P da **análise do tanque**, que substitui os valores do
  DairyPlan.
- **Leite**:
  - "Leite Total dia DairyPlan" é a soma dos lotes 1–6, em kg.
  - **"Leite comercializado no dia"** vem da cooperativa, em litros. **Usar sempre "comercializado", nunca
    "vendido".** É a soma dos volumes por **data de coleta**.
  - Ficam fora a data de emissão do PDF (e as posteriores) e a última data de coleta de cada PDF, porque podem estar
    incompletas.
  - "Diferença DairyPlan × comercializado" = (DP − comercializado) ÷ comercializado, kg contra litros, **sem
    conversão**. Converter (1 L ≈ 1,032 kg) é decisão pendente da usuária.
  - A diferença diária oscila conforme o horário das coletas (ex.: a coleta das 23h é praticamente leite do dia
    seguinte).
  - Leite descartado do lote 10 e % do leite produzido que foi descartado.
- **Análise do tanque**:
  - Todas as análises de uma mesma mensagem formam um grupo, ponderado pelo volume de cada tanque.
  - O grupo vale a partir da primeira data de coleta e continua valendo até chegar o próximo.
- **Reprodução**:
  - Gestantes = DDP ≥ 1, sem DNB. % gestantes = gestantes ÷ (adultas − DNB).
  - DEL > 150 não gestantes (sem DNB) e a % sobre as vacas em lactação.
  - DNB (StatRepro DNB ou Dry DNB) fica fora dos indicadores de reprodução.
  - DEL > 70 sem IA (NumIAs = 0, sem DNB).
  - Inseminadas (Bred) e Vazias com IA há mais de 35 dias, contadas pela coluna DATA da IA.

### Jovens (LACT = 0)

- Total; animais com < 3 meses; nascidas há até 7 dias.
- Novilhas gestantes; novilhas > 15 meses não gestantes.
- Novilhas Bred e Vazias com IA há mais de 35 dias.

---

## 5. Automação diária (Routine)

- **Routine** `trig_016TMVvrfCBFKNtTAUKUc2Jd`, "Monitoramento diário ARCAFLA".
- Roda todo dia às **10h48 (America/Sao_Paulo)**, numa sessão nova a cada execução, com notificação push.
- Passos, nesta ordem, para que o relatório chegue ao celular mesmo se a gravação no GitHub falhar:
  1. Clonar o repositório para leitura e fazer checkout do branch.
  2. Baixar do BoviSync.
  3. Rodar `le_leite_vendido.py`, `monitor_diario.py`, `recalc.py` e `monitor_pdf.py`, e gerar os PNG.
  4. Conferir números estranhos.
  5. **Mandar ao celular** a imagem da página 1, o PDF e a planilha.
  6. Só então registrar o dia nas notas, pedir permissão de gravação (`add_repo`, access "push"), fazer commit e
     push.
  7. Escrever um resumo de 4 a 6 linhas, dizendo se ficou salvo no repositório.
- **Problema em aberto (22/10)**:
  - A execução de 22/10 baixou, gerou e enviou tudo, mas o **push falhou com 403**, porque a sessão da rotina não
    tinha o repositório autorizado. O dia 21/10 foi refeito e salvo manualmente.
  - A rotina foi ajustada para pedir permissão de gravação (`add_repo` com access "push") só no final.
  - Num teste, a sessão nova parou esperando a usuária aprovar o "Add Repo" no app. Se a rotina também parar
    nesse ponto, o relatório já terá sido enviado ao celular.
  - Se continuar falhando, a usuária precisa reconectar o GitHub em https://claude.ai/connect-github.

---

## 6. PADRÃO DO PDF (aprovado pela usuária)

- **Página e cores**:
  - A4 paisagem, **2 páginas**.
  - Cor principal cinza-escuro `#2E3338`; fundo da página `#F3F4F5`; caixas brancas com **cantos arredondados**.
  - Fonte Liberation Sans, com DejaVu para as setas.
- **Cores dos lotes**: L1 amarelo `#EDA100`, L2 azul `#2A78D6`, L3 vermelho `#E34948`, L4 verde `#008300`,
  L5 roxo `#6250D6`, L6 laranja `#EB6834`.
- **Séries dos gráficos**: azul `#2A78D6`, laranja `#EB6834`, verde `#1BAF7A`.

### Página 1 (painel)

1. **Cabeçalho escuro arredondado**:
   - Logo à esquerda, numa faixa branca.
   - Título **"Monitoramento diário"**, sem "ARCAFLA" no título.
   - Subtítulo "Rebanho · N dia(s): dd/mm a dd/mm"; à direita, "Dados de dd/mm/aaaa".
2. **6 cartões**: Vacas em lactação · Produção 24 h (kg/vaca) · DairyPlan × comercializado ·
   Gestantes (sem DNB) · Em tratamento (lote 10) · Vazias com IA há > 35 dias.
   - **Grade fixa**: título, valor, média e linha extra nas mesmas alturas.
   - Título e valor com **um só tamanho para os 6**.
   - Faixa lateral na cor do juízo: verde melhorou, vermelho piorou, cinza neutro.
   - Selo arredondado de **largura fixa** com a variação, e "vs ontem" centrado embaixo dele, na linha da
     "média 10 dias".
   - Linha extra com o número em negrito: no tanque, ECM, vacas gestantes, leite descartado, inseminadas > 35 d.
   - Sparkline embaixo, terminando alinhada à borda do selo.
3. **Gráficos da linha de cima**:
   - **Produção por vaca nos últimos dias**: azul = produção 24 h, verde = ECM. Área suave e valores em cada ponto;
     curva monotônica, que não ultrapassa os dados.
   - **Produção por lote** no último dia: barras arredondadas nas cores dos lotes, com ± DP.
4. **Gráficos da linha de baixo**:
   - **Leite DairyPlan × comercializado**: azul/verde, em mil kg/L, com a linha **"dif."** de % por dia embaixo
     das datas. A linha alterna em duas alturas quando não cabe.
   - **Vacas com leite abaixo de 20 kg**: barras, último dia em destaque.
   - **Vacas gestantes (% sem DNB)**.
   - **Atrasos reprodutivos**: vazias IA > 35 d e DEL > 150 não gestantes.
   - Subtítulos **sem** "bom quando sobe/cai".
   - Em gráficos estreitos, datas são puladas conforme a largura, mantendo sempre a última.
5. **Quadro "⚠ Atenção hoje"**: os 6 indicadores que mais pioraram, em duas colunas.

### Página 2 (tabela completa)

- Cabeçalho "Monitoramento diário · Tabela completa dos indicadores", sem logo.
- Tabela ocupando a largura toda, sem sobra de espaço, com números maiores.
- Cabeçalho da tabela escuro; o último dia em azul.
- Blocos à esquerda: Rebanho e movimentação, Produção por vaca, Leite produzido e entregue, Qualidade do leite do
  tanque, Reprodução, Recria.
- **Linhas dos lotes 1–6** no tom claro da cor do lote, com marca colorida à esquerda.
- **Linha "Leite comercializado no dia" em destaque**: marca verde, fundo verde-claro e números em negrito.
- Variação com fundo verde ou vermelho-claro; "= 0" sem cor.
- Rodapé "Como ler" e "página N de 2".

---

## 7. Pontos em aberto

1. Confirmar se o push da rotina passou a funcionar (teste de 22/10 e execução de 23/10).
2. Decisão da usuária: converter os kg do DairyPlan em litros (÷ 1,032) na diferença DairyPlan × comercializado?
3. Cadastro a corrigir no DairyPlan/BoviSync:
   - 4 vacas "Bred" sem DATA da IA (brincos 5557, 3291, 5541, 5791).
   - A 5791 tem a 1ª IA com 16 DEL, o que parece erro de lançamento.
4. O teste do PDF com 10 dias (o máximo) ainda não foi feito. Com 8 dias está ok, em 2 páginas.
5. A imagem da análise do tanque de 21/10 não foi arquivada: os valores foram transcritos, mas falta o arquivo.

---

## 8. Últimos números (relatório de 21/10/2026)

- Lactação: 1.650 vacas (+4).
- Lote 10: 41 animais (16 entradas, 7 saídas).
- Produção 24 h: 43,8 kg/vaca; ECM 44,7.
- Vacas < 20 kg: 57 (−20). Partos: 7. DNB: 65 (+6).
- Vazias com IA > 35 d: 38 (eram 97). Caiu porque 55 vacas foram reinseminadas (IATF) com data de 22/10.
- DairyPlan: 69.121 kg. Leite comercializado de 21/10: pendente (chega no próximo PDF da cooperativa).
- 20/10: comercializado 62.438 L × DairyPlan 68.881 kg, ou seja, +10,3%.
