"""Gera a amostra de avaliações negativas que será rotulada à mão.

Uso:
    python -m reclamacoes.preparar_dados data/olist_order_reviews_dataset.csv --n 300
"""

import argparse
from pathlib import Path

import pandas as pd

MIN_CARACTERES = 20


def filtrar_negativas(df: pd.DataFrame) -> pd.DataFrame:
    """Mantém avaliações com nota 1 ou 2 e com texto suficiente para classificar."""
    titulo = df["review_comment_title"].fillna("").str.strip()
    mensagem = df["review_comment_message"].fillna("").str.strip()
    texto = (titulo + ". " + mensagem).str.strip(". ").str.replace(r"\s+", " ", regex=True)

    saida = pd.DataFrame(
        {"id": df["review_id"], "nota": df["review_score"], "texto": texto}
    )
    saida = saida[(saida["nota"] <= 2) & (saida["texto"].str.len() >= MIN_CARACTERES)]
    # Textos repetidos (ex.: "não recebi") distorcem a avaliação: fica só um de cada.
    saida = saida.drop_duplicates(subset="texto").drop_duplicates(subset="id")
    return saida.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_olist", type=Path)
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--saida", type=Path, default=Path("data/amostra.csv"))
    args = parser.parse_args()

    df = pd.read_csv(args.csv_olist)
    negativas = filtrar_negativas(df)
    amostra = negativas.sample(n=min(args.n, len(negativas)), random_state=args.seed)
    amostra["rotulo"] = ""

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    amostra.to_csv(args.saida, index=False)
    print(f"{len(negativas)} avaliações negativas com texto; {len(amostra)} salvas em {args.saida}")


if __name__ == "__main__":
    main()
