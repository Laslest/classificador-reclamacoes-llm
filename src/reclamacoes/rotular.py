"""Ferramenta de terminal para rotular a amostra à mão.

Mostra um texto por vez; você digita o número da categoria.
O progresso é salvo a cada resposta, então dá para parar e continuar depois.

Uso:
    python -m reclamacoes.rotular data/amostra.csv
"""

import argparse
from pathlib import Path

import pandas as pd

from reclamacoes.categorias import DEFINICOES, Categoria

OPCOES = {str(i): c for i, c in enumerate(Categoria, start=1)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()

    df = pd.read_csv(args.csv, dtype={"rotulo": str}).fillna({"rotulo": ""})
    pendentes = df.index[df["rotulo"] == ""].tolist()
    print(f"{len(df) - len(pendentes)} rotulados, {len(pendentes)} pendentes.\n")
    for numero, cat in OPCOES.items():
        print(f"  {numero} = {cat.value:<18} {DEFINICOES[cat]}")
    print("  d = descartar (texto não é reclamação)   q = sair\n")

    for n, i in enumerate(pendentes, start=1):
        print("-" * 70, f"[{n}/{len(pendentes)}]")
        print(df.at[i, "texto"])
        while True:
            resposta = input("> ").strip().lower()
            if resposta in OPCOES:
                df.at[i, "rotulo"] = OPCOES[resposta].value
                break
            if resposta == "d":
                df.at[i, "rotulo"] = "descartado"
                break
            if resposta == "q":
                df.to_csv(args.csv, index=False)
                print("Progresso salvo.")
                return
            print("Opção inválida.")
        df.to_csv(args.csv, index=False)

    print("Tudo rotulado.")


if __name__ == "__main__":
    main()
