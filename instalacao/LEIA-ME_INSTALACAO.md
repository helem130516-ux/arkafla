# Monitoramento diário ARCAFLA – pacote de instalação

Este pacote tem **tudo** o que é preciso para rodar o monitoramento diário do rebanho da Fazenda ARCAFLA em outro
Claude: scripts, dados atuais, logo, fontes, o modelo aprovado do PDF, os textos das rotinas e a documentação.
Montado em 29/10/2026.

> **Para o Claude que vai receber este pacote:** leia primeiro `claude/TAREFA_MONITORAMENTO_ARCAFLA.md` (regras,
> indicadores, padrão do PDF e preferências da usuária). Depois siga este guia. Responda sempre em português.

---

## 1. O que vem no pacote

| Pasta / arquivo | O que é |
|---|---|
| `scripts/baixa_bovisync.py` | Entra no BoviSync (login nas variáveis `BOV_USER` / `BOV_PASS`) e baixa o relatório "Zootécnico Jorge atualizado" do dia anterior para `dados/zootecnico/`. |
| `scripts/le_leite_vendido.py` | Lê o PDF "Demonstrativo das Coletas de Leite" da cooperativa e soma o leite comercializado por dia. |
| `scripts/monitor_diario.py` | Monta a planilha `monitoramento/Monitoramento_Diario_ARCAFLA.xlsx` (10 últimos dias, só fórmulas). |
| `scripts/recalcula.py` | Recalcula as fórmulas da planilha com o LibreOffice e confere se há erro. |
| `scripts/monitor_pdf.py` | Gera o PDF de 2 páginas no **modelo padrão aprovado** (não mudar o layout sem pedido). |
| `scripts/envia_whatsapp.py` | Envio por WhatsApp via Z-API. **Inativo**: a usuária recusou esse serviço pago. |
| `dados/zootecnico/` | Relatórios do BoviSync, um por dia (`Zootecnico_AAAA-MM-DD.xlsx`). |
| `dados/zootecnico_original/` | Originais de dias corrigidos à mão (ver `dados/correcoes_leite.json`). |
| `dados/leite_vendido/` + `leite_vendido.json` + `coletas_leite.json` | PDFs das coletas e totais por dia (em litros; a planilha converte para kg × 1,032). |
| `dados/analise_tanque.json` + `dados/analise_tanque/` | Análises do tanque (gordura, proteína, CCS, CBT, ureia…) e as imagens recebidas. |
| `dados/logo_arcafla.png` | Logo da fazenda (página 1 do PDF). |
| `fontes/` | Fontes do PDF (Liberation Sans e DejaVu Sans, licenças livres). |
| `monitoramento/` | Última planilha, último PDF e imagens das páginas. |
| `claude/TAREFA_MONITORAMENTO_ARCAFLA.md` | **Documento principal da tarefa.** |
| `claude/notas_analise_ARKAFLA.md` | Histórico de todas as decisões e de cada dia. |
| `claude/TAREFA_WHATSAPP_DESKTOP.md` | Texto pronto para a tarefa do Claude Desktop que envia pelo WhatsApp. |
| `instalacao/rotina_diaria_10h48.txt` | Texto da rotina diária (colar ao criar a rotina). |
| `instalacao/atualizacao_tarde_15h53.txt` | Texto da atualização da tarde (modo aviso). |
| `instalacao/instrucoes_projeto_claude_ai.txt` | Instruções para usar num Projeto do claude.ai (sem automação). |
| `requirements.txt` | Bibliotecas Python. |

---

## 2. Escolha onde instalar

**A) Claude Code (recomendado – tudo automático).** Na nuvem (claude.ai/code) ou no Claude Desktop, aba Code.
Baixa o BoviSync sozinho e roda as rotinas diárias.

**B) Projeto no claude.ai (manual).** Sem acesso ao BoviSync: a usuária envia os arquivos e o Claude gera o
relatório. Siga a seção 6.

---

## 3. Instalação no Claude Code (opção A)

### 3.1 Repositório
1. Crie um repositório no GitHub (privado) e envie o conteúdo deste pacote para ele, **ou** use o repositório que
   já existe: `helem130516-ux/arkafla`, branch `claude/tender-clarke-13z0dx` (já tem tudo isto).
2. Abra uma sessão do Claude Code com esse repositório selecionado.

### 3.2 Ambiente (no claude.ai/code: menu do ambiente no título da sessão → Edit)
- **Variáveis de ambiente** (a usuária cadastra; nunca escrever em arquivo nem pedir no chat):
  - `BOV_USER` – usuário do BoviSync
  - `BOV_PASS` – senha do BoviSync
- **Acesso à rede**: liberar `bovisync.farm` (Allowed domains).
- **Script de configuração** (setup script), para já ter tudo instalado:
  ```bash
  apt-get update && apt-get install -y libreoffice-calc poppler-utils fonts-liberation fonts-dejavu-core
  python3 -m pip install -r requirements.txt
  python3 -m playwright install --with-deps chromium || true
  ```
  (No ambiente de nuvem do Claude o Chromium já vem em `/opt/pw-browsers/chromium` e o script o usa.)

### 3.3 Teste manual (rodar uma vez para conferir)
```bash
python3 scripts/baixa_bovisync.py            # baixa o dia anterior (não sobrescreve se já existir)
python3 scripts/le_leite_vendido.py          # refaz os totais de leite comercializado
python3 scripts/monitor_diario.py            # monta a planilha
python3 scripts/recalcula.py monitoramento/Monitoramento_Diario_ARCAFLA.xlsx 600   # precisa: success, 0 erros
python3 scripts/monitor_pdf.py               # precisa: 2 páginas
pdftoppm -r 130 -png monitoramento/Monitoramento_Diario_ARCAFLA_AAAA-MM-DD.pdf monitoramento/imagens/ARCAFLA_AAAA-MM-DD_pagina
```
Envie à usuária a imagem da página 1, o PDF e a planilha.

### 3.4 Rotinas automáticas
Crie as rotinas **dentro da própria conversa** que tem o repositório com permissão de gravação (assim o push
funciona sem pedir aprovação às 11h — rotina que abre sessão nova falhava com 403):
1. **Rotina diária** – todo dia às **10h48 (America/Sao_Paulo)** – texto em `instalacao/rotina_diaria_10h48.txt`.
2. **Atualização da tarde** – todo dia às **15h53** – texto em `instalacao/atualizacao_tarde_15h53.txt`
   (modo aviso: compara e avisa, **não** troca o relatório oficial – ver seção 5).

Peça ao Claude: *"crie uma rotina nesta conversa, todo dia às 10h48 de Brasília, com o texto do arquivo
instalacao/rotina_diaria_10h48.txt"* (e o mesmo para a da tarde).

---

## 4. O que a usuária manda e o que fazer

| Arquivo | Quando | O que fazer |
|---|---|---|
| PDF "Demonstrativo das Coletas de Leite" | Dias úteis (a cooperativa não lança no fim de semana) | `python3 scripts/le_leite_vendido.py arquivo.pdf`, depois planilha → recálculo → PDF → enviar. |
| Print da análise do tanque | Quando o laticínio manda | Novo grupo em `dados/analise_tanque.json` (valores transcritos + imagem em `dados/analise_tanque/`); gerar de novo. |
| Excel "Zootécnico Jorge atualizado" (se mandar à mão) | Quando o BoviSync falhar | Data do relatório = data de exportação − 1 (DtNasc + IdadeDias − 1); salvar em `dados/zootecnico/Zootecnico_AAAA-MM-DD.xlsx`. |

Arquivos chegam como anexo (clipe). Imagem colada no texto não chega como arquivo.

O portal do cooperado Castrolanda (`cooperado.castrolanda.coop.br`) **recusa conexões vindas da nuvem**; por isso
o PDF das coletas e as análises continuam chegando pela usuária.

---

## 5. Cuidados aprendidos (não repetir erros)

1. **Partos**: contados pela `DtÚltParto` do relatório **mais recente**. Parto lançado com atraso entra sozinho no
   dia certo no relatório seguinte.
2. **Não substituir o relatório inteiro à tarde**: o BoviSync é uma foto do momento. O download das 16h do dia D
   (gravado como D−1) já traz os movimentos de D (secagens, entradas no lote 10) e os joga no dia errado.
   - Se a usuária pedir "rodar de novo com os partos lançados": baixar numa cópia separada e levar ao relatório
     oficial **só** `DtÚltParto` e `LACT` dos animais com parto até o dia do relatório. Guardar o original em
     `dados/zootecnico_original/` e registrar em `dados/correcoes_leite.json`.
3. **Pesagens com erro**: conferir sempre a mediana de `Leite ÷ Leite7` nas vacas do tanque (normal ≈ 1,0).
   - Em 25/10 deu 0,42 (ordenhas incompletas). A usuária pediu para usar as pesagens do dia seguinte. Foi feito
     trocando a coluna Leite vaca a vaca, com o original guardado.
   - **Não rodar `--substituir` em 25/10**, senão o erro volta.
4. **Saltos grandes** (vazias com IA > 35 d, novilhas gestantes, lote 10): conferir no arquivo bruto antes de
   enviar. Quase sempre é um lote de IATF cruzando os 35 dias, um diagnóstico de prenhez ou um tratamento em lote.
5. Usar o termo **"leite comercializado"** (nunca "vendido"). Ele aparece **em kg** (litros × 1,032).
6. **Modelo do PDF aprovado**: não mudar o layout sem pedido explícito.

---

## 6. Uso num Projeto do claude.ai (opção B, manual)

1. Crie um Projeto "Monitoramento ARCAFLA".
2. Em *Instruções do projeto*, cole o conteúdo de `instalacao/instrucoes_projeto_claude_ai.txt`.
3. Em *Conhecimento do projeto*, envie:
   - `claude/TAREFA_MONITORAMENTO_ARCAFLA.md`;
   - os scripts da pasta `scripts/`;
   - a logo e as fontes.
4. A cada dia, a usuária envia o Excel do BoviSync (e o PDF das coletas, quando houver).
5. O Claude roda os scripts na ferramenta de análise e devolve a planilha, o PDF e a imagem.

Sem rotina automática e sem acesso ao BoviSync nesse modo. O histórico dos 10 dias precisa ir junto: envie os 10
últimos `Zootecnico_*.xlsx`, `leite_vendido.json` e `analise_tanque.json`.

---

## 7. Segurança

- Nenhum arquivo deste pacote tem login, senha, token ou telefone. Mantenha assim.
- Credenciais só em variáveis de ambiente do ambiente de execução.
