"""
Entry point da limpeza e exportação.

Uso:
    python process.py
    python process.py --input data/raw/raw_reddit_data.jsonl --output data/processed/reddit_corpus_limpo.xlsx
"""

import argparse

import paths
from processor.loader import load_jsonl
from processor.cleaner import apply_filters, build_dataframes
from processor.exporter import export_to_excel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fase 2 — Limpeza e exportação do corpus Reddit."
    )
    parser.add_argument(
        "--input",
        default=str(paths.RAW_JSONL),
        help="Arquivo JSONL gerado pela Fase 1.",
    )
    parser.add_argument(
        "--output",
        default=str(paths.CORPUS_XLSX),
        help="Arquivo Excel de saída.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # 1. Carregamento
    df_raw = load_jsonl(args.input)

    # 2. Filtros metodológicos
    df_filtered = apply_filters(df_raw)

    # 3. Estruturação relacional
    df_posts, df_comentarios = build_dataframes(df_filtered)

    # 4. Exportação
    export_to_excel(df_posts, df_comentarios, args.output)


if __name__ == "__main__":
    main()
