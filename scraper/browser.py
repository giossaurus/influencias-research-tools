"""
Gerenciamento do browser Playwright com configurações anti-bot básicas.
"""

import logging
from contextlib import contextmanager

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)

# User-agent de um Chrome real para minimizar detecção
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


@contextmanager
def create_browser(headless: bool = True):
    """
    Context manager que inicia o Playwright, cria um browser Chromium
    e encerra tudo ao sair do bloco.

    Uso:
        with create_browser(headless=True) as (browser, context):
            page = context.new_page()
    """
    with sync_playwright() as pw:
        browser: Browser = pw.chromium.launch(headless=headless)
        context: BrowserContext = browser.new_context(
            user_agent=_USER_AGENT,
            locale="en-US",
            timezone_id="America/New_York",
            viewport={"width": 1280, "height": 800},
        )
        # Bloqueia recursos pesados desnecessários para scraping
        context.route(
            "**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf,otf,eot}",
            lambda route: route.abort(),
        )
        logger.info("Browser iniciado (headless=%s).", headless)
        try:
            yield browser, context
        finally:
            context.close()
            browser.close()
            logger.info("Browser encerrado.")


def new_page(context: BrowserContext) -> Page:
    """Cria uma nova aba com timeout padrão aumentado."""
    page = context.new_page()
    page.set_default_timeout(30_000)  # 30 s
    return page
