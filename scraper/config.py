"""
Configurações centrais do scraper — subreddits, keywords e parâmetros operacionais.
"""

SUBREDDITS = [
    "TikTokMonetizing",
    "TikTok",
    "socialmedia",
    "NewTubers",
    "ContentCreation",
    "Influencers",
]

KEYWORD_GROUPS = {
    "algoritmo": [
        "TikTok algorithm",
        "algorithm changed",
        "algorithm update",
    ],
    "shadowban": [
        "TikTok shadowban",
        "shadow banned",
        "account restricted",
    ],
    "visibilidade": [
        "views dropped",
        "zero views",
        "not on FYP",
        "reach down",
    ],
    "metricas": [
        "retention rate",
        "watch time",
        "engagement dropped",
    ],
    "monetizacao": [
        "Creator Rewards",
        "TikTok monetization",
    ],
}

# Todos os keywords em lista plana, mantendo referência ao grupo semântico
KEYWORDS: list[dict] = [
    {"group": group, "keyword": kw}
    for group, keywords in KEYWORD_GROUPS.items()
    for kw in keywords
]

# Parâmetros de busca
SEARCH_TIME_FILTER = "year"       # t=year na URL do Reddit
MAX_POSTS_PER_SEARCH = 40         # links coletados por combinação subreddit+keyword
MAX_COMMENTS_PER_POST = 20        # top comentários extraídos por post

# Delays aleatórios entre requisições (segundos)
DELAY_MIN = 2.0
DELAY_MAX = 5.0

# Modo headless do browser (True = sem janela; False = abre janela para debug)
HEADLESS = True
