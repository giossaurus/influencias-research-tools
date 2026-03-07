"""
Entry point da Fase 1 — Coleta Bruta do Reddit.

Uso:
    python main.py              # executa em modo headless
    python main.py --no-headless  # abre janela do browser (debug)
"""

import argparse
import logging
import sys

import paths
from scraper import config
from scraper.browser import create_browser
from scraper.reddit_scraper import run_scraper
from scraper.storage import JsonlStorage


def setup_logging() -> None:
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(paths.SCRAPER_LOG, encoding="utf-8"),
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fase 1 — Coleta bruta de posts do Reddit sobre TikTok."
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Abre o browser visualmente (útil para debug).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging()

    logger = logging.getLogger("main")
    headless = not args.no_headless

    logger.info("=" * 60)
    logger.info("Iniciando Fase 1 — Reddit Raw Scraper")
    logger.info("Saída: %s", paths.RAW_JSONL)
    logger.info("Subreddits: %s", config.SUBREDDITS)
    logger.info("Keywords: %d total", len(config.KEYWORDS))
    logger.info("=" * 60)

    storage = JsonlStorage(paths.RAW_JSONL)

    with create_browser(headless=headless) as (_, context):
        run_scraper(context, storage)

    logger.info("Fase 1 concluída. Arquivo: %s", paths.RAW_JSONL)


if __name__ == "__main__":
    main()
