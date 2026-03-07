# Influências Research Tools

Pipeline de pesquisa qualitativa para mapear padrões de **"fofoca algorítmica"** no Reddit — discursos de criadores de conteúdo sobre o algoritmo do TikTok.

**Autor:** Giovanni Della Dea
**Instituição:** Universidade Federal da Bahia (UFBA)

---

## Visão Geral

O pipeline é composto por três fases independentes e sequenciais:

```
[Fase 1] Coleta bruta        →  data/raw/raw_reddit_data.jsonl
[Fase 2] Limpeza e estrutura →  data/processed/reddit_corpus_limpo.xlsx
[Fase 3] Análise e relatório →  reports/relatorio_fofoca_algoritmica_YYYYMMDD_HHMM.md
```

---

## Arquitetura

```
influencias-research-tools/
│
├── main.py                        # Fase 1 — entry point do scraper
├── process.py                     # Fase 2 — entry point do processador
├── analise_corpus.py              # Fase 3 — entry point da análise
├── paths.py                       # Caminhos canônicos + criação automática de pastas
├── requirements.txt
│
├── scraper/                       # Módulo da Fase 1
│   ├── config.py                  # Subreddits, keywords, parâmetros
│   ├── browser.py                 # Playwright + configurações anti-bot
│   ├── reddit_scraper.py          # Loop de busca e extração profunda
│   └── storage.py                 # Salvamento incremental em JSONL
│
├── processor/                     # Módulo da Fase 2
│   ├── loader.py                  # Leitura do JSONL
│   ├── cleaner.py                 # Funil de filtros metodológicos
│   └── exporter.py                # Exportação para Excel (.xlsx)
│
├── data/                          # Dados gerados (não versionado)
│   ├── raw/                       # → raw_reddit_data.jsonl
│   └── processed/                 # → reddit_corpus_limpo.xlsx
│
├── logs/                          # Logs de execução (não versionado)
│   └── scraper.log
│
└── reports/                       # Relatórios gerados (não versionado)
    └── relatorio_fofoca_algoritmica_YYYYMMDD_HHMM.md
```

### Dados gerados (não versionados)

| Caminho | Gerado por | Descrição |
|---|---|---|
| `data/raw/raw_reddit_data.jsonl` | Fase 1 | Um post por linha, formato JSON Lines |
| `logs/scraper.log` | Fase 1 | Log completo da coleta |
| `data/processed/reddit_corpus_limpo.xlsx` | Fase 2 | Corpus filtrado, abas Posts e Comentarios |
| `reports/relatorio_fofoca_algoritmica_*.md` | Fase 3 | Relatório com timestamp |

---

## Fase 1 — Coleta Bruta

**Script:** `main.py` | **Módulo:** `scraper/`

Usa Playwright para emular um navegador real e percorrer o Reddit sem usar a API oficial.

**Parâmetros de busca** (em `scraper/config.py`):

- **Subreddits:** TikTokMonetizing, TikTok, socialmedia, NewTubers, ContentCreation, Influencers
- **Grupos semânticos:**
  - Algoritmo: `TikTok algorithm`, `algorithm changed`, `algorithm update`
  - Shadowban: `TikTok shadowban`, `shadow banned`, `account restricted`
  - Visibilidade: `views dropped`, `zero views`, `not on FYP`, `reach down`
  - Métricas: `retention rate`, `watch time`, `engagement dropped`
  - Monetização: `Creator Rewards`, `TikTok monetization`
- Filtro de tempo: último ano (`t=year`)
- Até 40 posts por combinação subreddit × keyword
- Até 20 comentários por post

**Resiliência:**
- Salvamento incremental — dados não são perdidos em caso de interrupção
- Retomada automática — IDs já coletados são ignorados ao reiniciar
- Delays aleatórios de 2–5 s entre requisições
- `try/except` em cada post — erros são logados e o loop continua

**Estrutura do JSONL de saída:**

```json
{
  "post": {
    "id": "abc123",
    "subreddit": "TikTok",
    "keyword_group": "algoritmo",
    "keyword": "TikTok algorithm",
    "url": "https://reddit.com/r/TikTok/comments/abc123/...",
    "title": "Why did my views drop overnight?",
    "author": "username",
    "body": "...",
    "upvotes": 847,
    "comment_count": 0,
    "timestamp": "2024-08-15T14:32:00+00:00"
  },
  "comments": [
    { "author": "user2", "body": "...", "upvotes": 42 }
  ]
}
```

---

## Fase 2 — Limpeza e Estruturação

**Script:** `process.py` | **Módulo:** `processor/`

Aplica um funil metodológico e exporta os dados em formato relacional.

**Funil de filtros:**

| Etapa | Regra |
|---|---|
| Deduplicação | Remove posts com ID repetido |
| Regra 1 | Mantém apenas posts com ≥ 3 comentários reais |
| Regra 2 | Cria coluna `is_creator_suspect` (True se título/body menciona "my video", "tested", "my channel" etc.) |
| Regra 3 | Descarta posts onde título + body < 30 caracteres |

**Saída — Excel com duas abas:**

- **Posts:** ID, Subreddit, Keyword, Titulo, Autor, Texto, Upvotes, Num\_Comentarios, Data, URL, is\_creator\_suspect
- **Comentarios:** Post\_ID, Autor\_Comentario, Texto\_Comentario, Upvotes\_Comentario

---

## Fase 3 — Análise e Relatório

**Script:** `analise_corpus.py`

Lê o Excel e gera um relatório Markdown com mapeamento linguístico do corpus.

**Seções do relatório:**

1. **Estatísticas Gerais** — total de posts, comentários, distribuição por subreddit
2. **Posts de Criadores** — quantos posts têm `is_creator_suspect = True`
3. **Vocabulário Nativo** — top 10 termos mais citados (`shadowban`, `fyp`, `algorithm`…)
4. **Táticas e Experimentações** — menções a `tested`, `tried`, `worked`, `didn't work`…
5. **Ranking de Discussão** — Top 5 posts por número de comentários (prioridade para codificação manual)

O relatório é salvo com timestamp para não sobrescrever versões anteriores.

---

## How to Use

### 1. Instalação

```bash
# Clone o repositório e entre na pasta
cd influencias-research-tools

# Instale as dependências Python
pip install -r requirements.txt

# Instale o browser do Playwright
playwright install chromium
```

### 2. Fase 1 — Coleta

```bash
# Modo headless (produção)
python main.py

# Modo com janela aberta (debug)
python main.py --no-headless
```

> O arquivo `data/raw/raw_reddit_data.jsonl` será criado/atualizado incrementalmente.
> Se interrompido, basta rodar novamente — posts já coletados são ignorados.

### 3. Fase 2 — Processamento

```bash
python process.py

# Caminhos customizados (opcional)
python process.py --input data/raw/raw_reddit_data.jsonl --output data/processed/reddit_corpus_limpo.xlsx
```

> Imprime o funil no console mostrando quantos posts sobreviveram a cada filtro.

### 4. Fase 3 — Análise

```bash
python analise_corpus.py

# Arquivo de entrada customizado (opcional)
python analise_corpus.py --input data/processed/reddit_corpus_limpo.xlsx
```

> Imprime o relatório no console **e** salva em `reports/` com timestamp.

### Sequência completa (do zero)

```bash
python main.py && python process.py && python analise_corpus.py
```

---

## Ajustes Rápidos

| O que mudar | Onde |
|---|---|
| Subreddits e keywords alvo | `scraper/config.py` |
| Limite de posts por busca | `scraper/config.py` → `MAX_POSTS_PER_SEARCH` |
| Limite de comentários por post | `scraper/config.py` → `MAX_COMMENTS_PER_POST` |
| Delays entre requisições | `scraper/config.py` → `DELAY_MIN` / `DELAY_MAX` |
| Mínimo de comentários (Regra 1) | `processor/cleaner.py` → `MIN_COMMENTS` |
| Mínimo de caracteres (Regra 3) | `processor/cleaner.py` → `MIN_CHARS` |
| Termos do vocabulário nativo | `analise_corpus.py` → `VOCABULARIO_NATIVO` |
| Arquivo de entrada/saída | Flags `--input` / `--output` nos scripts |

---

## Dependências

```
playwright>=1.44.0   # automação de browser (Fase 1)
pandas>=2.2.0        # manipulação de dados (Fase 2 e 3)
openpyxl>=3.1.0      # leitura/escrita de Excel (Fase 2 e 3)
```
