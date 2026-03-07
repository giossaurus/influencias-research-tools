"""
Filtros metodológicos da Fase 2.

Aplica o funil de limpeza e retorna dois DataFrames relacionais:
  - df_posts      : um post por linha
  - df_comentarios: um comentário por linha (chave estrangeira Post_ID)
"""

import re

import pandas as pd

# Expressões que indicam que o autor é um criador de conteúdo
_CREATOR_PATTERNS = [
    r"my video",
    r"my videos",
    r"my channel",
    r"meu canal",
    r"meus v[ií]deos",
    r"tested",
    r"tried",
    r"testei",
    r"experimentei",
    r"my followers",
    r"my niche",
]
_CREATOR_REGEX = re.compile(
    "|".join(_CREATOR_PATTERNS), flags=re.IGNORECASE
)

MIN_COMMENTS = 3
MIN_CHARS = 30


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica o funil de limpeza e retorna o DataFrame de posts filtrado."""

    # ── Pré-processamento ──────────────────────────────────────────────────

    # Contagem real de comentários a partir da lista (comment_count original é 0)
    df = df.copy()
    df["qtd_comentarios_reais"] = df["comments"].apply(len)

    # Normaliza campos de texto para evitar erros com NaN
    df["title"] = df["title"].fillna("").astype(str)
    df["body"] = df["body"].fillna("").astype(str)

    # ── Deduplicação ───────────────────────────────────────────────────────
    before = len(df)
    df = df.drop_duplicates(subset="id", keep="first")
    after_dedup = len(df)
    print(f"  [DEDUP]   Após remover duplicatas         : {after_dedup:>6}  "
          f"(-{before - after_dedup})")

    # ── Regra 1: Discussão Coletiva ────────────────────────────────────────
    df = df[df["qtd_comentarios_reais"] >= MIN_COMMENTS]
    after_r1 = len(df)
    print(f"  [REGRA 1] >= {MIN_COMMENTS} comentários reais           : {after_r1:>6}  "
          f"(-{after_dedup - after_r1})")

    # ── Regra 2: Relevância — is_creator_suspect ───────────────────────────
    df["is_creator_suspect"] = (
        df["title"].str.contains(_CREATOR_REGEX, regex=True)
        | df["body"].str.contains(_CREATOR_REGEX, regex=True)
    )
    # (A coluna é apenas informativa — não descartamos posts aqui)
    suspects = df["is_creator_suspect"].sum()
    print(f"  [REGRA 2] is_creator_suspect = True       : {suspects:>6}  (coluna adicionada, sem descarte)")

    # ── Regra 3: Tamanho mínimo ────────────────────────────────────────────
    df["_content_len"] = df["title"].str.len() + df["body"].str.len()
    df = df[df["_content_len"] >= MIN_CHARS]
    df = df.drop(columns=["_content_len"])
    after_r3 = len(df)
    print(f"  [REGRA 3] título+body >= {MIN_CHARS} chars         : {after_r3:>6}  "
          f"(-{after_r1 - after_r3})")

    print(f"  {'─'*45}")
    print(f"  [SAÍDA]   Posts aprovados no funil        : {after_r3:>6}")

    return df


def build_dataframes(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Constrói df_posts e df_comentarios a partir do DataFrame filtrado.
    """

    # ── df_posts ───────────────────────────────────────────────────────────
    df_posts = df[[
        "id", "subreddit", "keyword", "title", "author",
        "body", "upvotes", "qtd_comentarios_reais", "timestamp",
        "url", "is_creator_suspect",
    ]].copy()

    df_posts.columns = [
        "ID", "Subreddit", "Keyword", "Titulo", "Autor",
        "Texto", "Upvotes", "Num_Comentarios", "Data",
        "URL", "is_creator_suspect",
    ]

    # ── df_comentarios ─────────────────────────────────────────────────────
    rows: list[dict] = []
    for _, row in df.iterrows():
        post_id = row["id"]
        for comment in row["comments"]:
            rows.append({
                "Post_ID": post_id,
                "Autor_Comentario": comment.get("author", ""),
                "Texto_Comentario": comment.get("body", ""),
                "Upvotes_Comentario": comment.get("upvotes", 0),
            })

    df_comentarios = pd.DataFrame(
        rows,
        columns=["Post_ID", "Autor_Comentario", "Texto_Comentario", "Upvotes_Comentario"],
    )

    print(f"\n  Linhas em df_posts        : {len(df_posts)}")
    print(f"  Linhas em df_comentarios  : {len(df_comentarios)}")

    return df_posts, df_comentarios
