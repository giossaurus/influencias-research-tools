"""
Caminhos canônicos do projeto.

Importar este módulo garante que todos os diretórios de saída
existam antes de qualquer leitura ou escrita de arquivo.
"""

from pathlib import Path

# Raiz do projeto (onde este arquivo está)
ROOT = Path(__file__).parent

# Diretórios
DATA_RAW       = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
LOGS           = ROOT / "logs"
REPORTS        = ROOT / "reports"

# Cria todos os diretórios ao importar (idempotente)
for _dir in (DATA_RAW, DATA_PROCESSED, LOGS, REPORTS):
    _dir.mkdir(parents=True, exist_ok=True)

# Arquivos
RAW_JSONL   = DATA_RAW / "raw_reddit_data.jsonl"
CORPUS_XLSX = DATA_PROCESSED / "reddit_corpus_limpo.xlsx"
SCRAPER_LOG = LOGS / "scraper.log"
