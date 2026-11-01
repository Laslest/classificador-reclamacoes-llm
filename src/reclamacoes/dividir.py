"""Divide os exemplos rotulados em treino e teste (estratificado por categoria).

- treino: usado para treinar o baseline e escolher os exemplos do few-shot.
- teste: usado SOMENTE para medir o desempenho. Nenhum exemplo de teste entra no prompt.

Uso:
    python -m reclamacoes.dividir data/amostra.csv
"""

import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


def dividir(df: pd.DataFrame, proporcao_teste: float = 0.4, seed: int = 42):
    rotulados = df[df["rotulo"].notna() & ~df["rotulo"].isin(["", "descartado"])]
    return train_test_split(
        rotulados, test_size=proporcao_teste, stratify=rotulados["rotulo"], random_state=seed
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--teste", type=float, default=0.4)
    args = parser.parse_args()

    df = pd.read_csv(args.csv, dtype={"rotulo": str})
    treino, teste = dividir(df, args.teste)
    treino.to_csv("data/treino.csv", index=False)
    teste.to_csv("data/teste.csv", index=False)
    print(f"treino: {len(treino)}  teste: {len(teste)}")
    print("Distribuição no teste:")
    print(teste["rotulo"].value_counts().to_string())


if __name__ == "__main__":
    main()
