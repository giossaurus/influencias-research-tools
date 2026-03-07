"""
Análise do Corpus: Mapeamento de Padrões de "Fofoca Algorítmica"

Lê `reddit_corpus_limpo.xlsx`, imprime o relatório no console e salva
um arquivo Markdown com timestamp.

Uso:
    python analise_corpus.py
    python analise_corpus.py --input reddit_corpus_limpo.xlsx
"""

import argparse
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd


# ──────────────────────────────────────────────────────────────────────────────
# Padrões linguísticos
# ──────────────────────────────────────────────────────────────────────────────

VOCABULARIO_NATIVO: dict[str, re.Pattern] = {
    term: re.compile(re.escape(term), re.IGNORECASE)
    for term in [
        "shadowban",
        "fyp",
        "algorithm",
        "retention",
        "engagement",
        "reach",
        "viral",
        "300 view jail",
        "metrics",
    ]
}

TATICAS_PATTERN = re.compile(
    r"\b(tested|tried|experimented|changed my|adjusted|worked|didn[''`]?t work)\b",
    re.IGNORECASE,
)

TEORIAS_PATTERN = re.compile(
    r"(post \d+ times?|best time to post|retention rate|3 seconds?|watch time)",
    re.IGNORECASE,
)


# ──────────────────────────────────────────────────────────────────────────────
# Carregamento
# ──────────────────────────────────────────────────────────────────────────────

def load_data(filepath: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    xl = pd.read_excel(filepath, sheet_name=None, engine="openpyxl")
    df_posts = xl["Posts"].fillna("")
    df_comments = xl["Comentarios"].fillna("")
    return df_posts, df_comments


# ──────────────────────────────────────────────────────────────────────────────
# Processamento linguístico
# ──────────────────────────────────────────────────────────────────────────────

def _count_term(pattern: re.Pattern, series: pd.Series) -> int:
    return series.apply(lambda t: len(pattern.findall(str(t)))).sum()


def map_vocabulario(df_posts: pd.DataFrame, df_comments: pd.DataFrame) -> Counter:
    """Conta frequência de cada termo nativo em posts + comentários."""
    # Texto dos posts: título + corpo
    post_text = (df_posts["Titulo"].astype(str) + " " + df_posts["Texto"].astype(str))
    comment_text = df_comments["Texto_Comentario"].astype(str)

    counts: Counter = Counter()
    for term, pattern in VOCABULARIO_NATIVO.items():
        counts[term] = _count_term(pattern, post_text) + _count_term(pattern, comment_text)
    return counts


def map_taticas(df_posts: pd.DataFrame, df_comments: pd.DataFrame) -> dict:
    """Conta posts e comentários que mencionam experimentação prática."""
    post_text = df_posts["Titulo"].astype(str) + " " + df_posts["Texto"].astype(str)
    posts_com_tatica = post_text.apply(
        lambda t: bool(TATICAS_PATTERN.search(t))
    ).sum()
    comments_com_tatica = df_comments["Texto_Comentario"].apply(
        lambda t: bool(TATICAS_PATTERN.search(str(t)))
    ).sum()
    return {"posts": int(posts_com_tatica), "comentarios": int(comments_com_tatica)}


def map_teorias(df_posts: pd.DataFrame, df_comments: pd.DataFrame) -> dict:
    """Conta posts e comentários que mencionam regras/métricas criadas pela comunidade."""
    post_text = df_posts["Titulo"].astype(str) + " " + df_posts["Texto"].astype(str)
    posts_com_teoria = post_text.apply(
        lambda t: bool(TEORIAS_PATTERN.search(t))
    ).sum()
    comments_com_teoria = df_comments["Texto_Comentario"].apply(
        lambda t: bool(TEORIAS_PATTERN.search(str(t)))
    ).sum()
    return {"posts": int(posts_com_teoria), "comentarios": int(comments_com_teoria)}


# ──────────────────────────────────────────────────────────────────────────────
# Geração do relatório
# ──────────────────────────────────────────────────────────────────────────────

def build_report(df_posts: pd.DataFrame, df_comments: pd.DataFrame) -> str:
    """
    Constrói o relatório completo como uma string Markdown.
    Legível tanto no console quanto renderizado como .md.
    """
    lines: list[str] = []
    L = lines.append  # atalho local

    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ── Cabeçalho ─────────────────────────────────────────────────────────
    L("# Relatório de Análise — Fofoca Algorítmica")
    L("")
    L("> **Fase 3** · Padrões de discurso sobre o algoritmo do TikTok no Reddit")
    L(f"> Gerado em: {generated_at}")
    L("")
    L("---")

    # ── 1. Estatísticas Gerais ────────────────────────────────────────────
    L("")
    L("## 1. Estatísticas Gerais")
    L("")
    L(f"| Métrica | Valor |")
    L(f"|---|---:|")
    L(f"| Total de posts | **{len(df_posts)}** |")
    L(f"| Total de comentários | **{len(df_comments)}** |")
    L("")
    L("### Distribuição por Subreddit")
    L("")
    L("| Subreddit | Posts | Barra |")
    L("|---|---:|---|")
    dist = (
        df_posts["Subreddit"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "Posts"})
    )
    max_posts = max(dist["Posts"]) if len(dist) else 1
    for _, row in dist.iterrows():
        bar = "█" * min(int(row["Posts"] / max_posts * 20), 20)
        L(f"| r/{row['Subreddit']} | {row['Posts']} | `{bar}` |")

    L("")
    L("---")

    # ── 2. Posts de Criadores ─────────────────────────────────────────────
    L("")
    L("## 2. Posts de Criadores (`is_creator_suspect`)")
    L("")
    n_suspect = int(df_posts["is_creator_suspect"].astype(str).str.lower().eq("true").sum())
    pct = n_suspect / len(df_posts) * 100 if len(df_posts) else 0
    L(f"- Posts marcados como **criador suspeito**: **{n_suspect}** ({pct:.1f}% do total)")
    L(f"- Posts de outros usuários: {len(df_posts) - n_suspect}")
    L("")
    L("---")

    # ── 3. Vocabulário Nativo ─────────────────────────────────────────────
    L("")
    L("## 3. Mapeamento de Vocabulário Nativo")
    L("")
    L("Frequência dos termos em posts **e** comentários combinados.")
    L("")
    L("| # | Termo | Ocorrências |")
    L("|---:|---|---:|")
    vocab_counts = map_vocabulario(df_posts, df_comments)
    for rank, (term, count) in enumerate(vocab_counts.most_common(10), start=1):
        L(f"| {rank} | `{term}` | {count} |")
    L("")
    L("---")

    # ── 4. Táticas e Experimentações ──────────────────────────────────────
    L("")
    L("## 4. Táticas e Experimentações")
    L("")
    L("Menções a padrões de **especulação como ação** (tested, tried, worked…):")
    L("")
    taticas = map_taticas(df_posts, df_comments)
    L(f"| Contexto | Contagem |")
    L(f"|---|---:|")
    L(f"| Posts com menção a testes práticos | {taticas['posts']} |")
    L(f"| Comentários com menção a testes práticos | {taticas['comentarios']} |")
    L("")
    L("Menções a **métricas e regras criadas pela comunidade** (watch time, retention rate…):")
    L("")
    teorias = map_teorias(df_posts, df_comments)
    L(f"| Contexto | Contagem |")
    L(f"|---|---:|")
    L(f"| Posts com métricas/regras | {teorias['posts']} |")
    L(f"| Comentários com métricas/regras | {teorias['comentarios']} |")
    L("")
    L("---")

    # ── 5. Ranking de Discussão ───────────────────────────────────────────
    L("")
    L("## 5. Ranking de Discussão — Top 5 (O Ouro da Fofoca)")
    L("")
    L("Posts com maior número de comentários — candidatos prioritários para codificação manual.")
    L("")
    top5 = df_posts.sort_values("Num_Comentarios", ascending=False).head(5)
    for rank, (_, row) in enumerate(top5.iterrows(), start=1):
        is_creator = str(row.get("is_creator_suspect", "")).lower() == "true"
        creator_badge = " `★ CRIADOR`" if is_creator else ""
        titulo = str(row["Titulo"])[:100]
        L(f"### #{rank} — r/{row['Subreddit']}{creator_badge}")
        L("")
        L(f"**Título:** {titulo}")
        L("")
        L(f"| Comentários | Upvotes |")
        L(f"|---:|---:|")
        L(f"| {row['Num_Comentarios']} | {row['Upvotes']} |")
        L("")
        L(f"**URL:** <{row['URL']}>")
        L("")

    L("---")
    L("")
    L(f"*Relatório gerado automaticamente em {generated_at}.*")
    L("")

    return "\n".join(lines)


def save_report(content: str) -> Path:
    """Salva o relatório em reports/ com timestamp no nome."""
    import paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = paths.REPORTS / f"relatorio_fofoca_algoritmica_{timestamp}.md"
    filename.write_text(content, encoding="utf-8")
    return filename


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    import paths
    parser = argparse.ArgumentParser(
        description="Fase 3 — Análise de padrões de fofoca algorítmica no corpus Reddit."
    )
    parser.add_argument(
        "--input",
        default=str(paths.CORPUS_XLSX),
        help="Arquivo Excel gerado pela Fase 2.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df_posts, df_comments = load_data(args.input)
    report = build_report(df_posts, df_comments)
    print(report)
    saved_to = save_report(report)
    print(f"Relatorio salvo em: {saved_to.resolve()}")


if __name__ == "__main__":
    main()
