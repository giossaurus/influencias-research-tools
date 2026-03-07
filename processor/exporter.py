"""
Exportação dos DataFrames relacionais para Excel (.xlsx) com duas abas.
"""

from pathlib import Path

import pandas as pd


def export_to_excel(
    df_posts: pd.DataFrame,
    df_comentarios: pd.DataFrame,
    output_path: str = "reddit_corpus_limpo.xlsx",
) -> None:
    """
    Exporta df_posts → aba 'Posts' e df_comentarios → aba 'Comentarios'
    no mesmo arquivo Excel.
    """
    path = Path(output_path)

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df_posts.to_excel(writer, sheet_name="Posts", index=False)
        df_comentarios.to_excel(writer, sheet_name="Comentarios", index=False)

        # Ajuste automático de largura de coluna para legibilidade
        for sheet_name, df in [("Posts", df_posts), ("Comentarios", df_comentarios)]:
            ws = writer.sheets[sheet_name]
            for col_idx, col_name in enumerate(df.columns, start=1):
                max_len = max(
                    len(str(col_name)),
                    df[col_name].astype(str).str.len().max() if len(df) > 0 else 0,
                )
                # Limita a 80 caracteres para não distorcer a planilha
                ws.column_dimensions[
                    ws.cell(row=1, column=col_idx).column_letter
                ].width = min(max_len + 2, 80)

    print(f"\n  [EXPORTADO] {path.resolve()}")
    print(f"    Aba 'Posts'       : {len(df_posts)} linhas")
    print(f"    Aba 'Comentarios' : {len(df_comentarios)} linhas")
    print(f"{'='*55}\n")
