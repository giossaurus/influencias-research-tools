"""
Carregamento do arquivo JSONL gerado na Fase 1.

Retorna um DataFrame "raw" com colunas achatadas (flattened),
mantendo a lista de comentários como coluna de objetos para
processamento posterior.
"""

import json
from pathlib import Path

import pandas as pd


def load_jsonl(filepath: str) -> pd.DataFrame:
    """
    Lê o arquivo JSONL e retorna um DataFrame com uma linha por post.
    A coluna `comments` contém a lista de dicts de comentários intacta.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

    records: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                post = obj.get("post", {})
                post["comments"] = obj.get("comments", [])
                records.append(post)
            except json.JSONDecodeError as exc:
                print(f"  [AVISO] Linha {lineno} inválida, pulando: {exc}")

    df = pd.DataFrame(records)

    # Garante que colunas essenciais existam mesmo que o JSONL esteja incompleto
    for col in ["id", "subreddit", "keyword", "keyword_group", "title",
                "author", "body", "upvotes", "comment_count", "timestamp",
                "url", "comments"]:
        if col not in df.columns:
            df[col] = None

    # Garante que comments seja sempre uma lista, nunca NaN
    df["comments"] = df["comments"].apply(
        lambda v: v if isinstance(v, list) else []
    )

    print(f"\n{'='*55}")
    print(f"  FASE 2 — Funil de Dados")
    print(f"{'='*55}")
    print(f"  [ENTRADA] Posts carregados do JSONL : {len(df):>6}")

    return df
