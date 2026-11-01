"""Baseline de ML clássico: TF-IDF + regressão logística.

Serve de comparação: se o LLM não for melhor que um modelo simples
treinado nos mesmos dados, ele não se justifica (custo, latência).

Uso:
    python -m reclamacoes.baseline
"""

import argparse
import json
import time
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline


def treinar(textos, rotulos):
    modelo = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode", lowercase=True, min_df=1),
        LogisticRegression(max_iter=1000, class_weight="balanced"),
    )
    return modelo.fit(textos, rotulos)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--treino", type=Path, default=Path("data/treino.csv"))
    parser.add_argument("--teste", type=Path, default=Path("data/teste.csv"))
    args = parser.parse_args()

    treino, teste = pd.read_csv(args.treino), pd.read_csv(args.teste)
    modelo = treinar(treino["texto"], treino["rotulo"])

    inicio = time.perf_counter()
    previstos = modelo.predict(teste["texto"])
    latencia = (time.perf_counter() - inicio) / len(teste)

    saida = Path("resultados/predicoes_baseline.jsonl")
    saida.parent.mkdir(exist_ok=True)
    with saida.open("w", encoding="utf-8") as f:
        for id_, previsto in zip(teste["id"], previstos):
            linha = {"id": id_, "previsto": previsto, "justificativa": None, "tentativas": 1,
                     "respostas_invalidas": 0, "latencia_s": latencia,
                     "tokens_entrada": 0, "tokens_saida": 0, "erro": None}
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    print(f"Baseline treinado com {len(treino)} exemplos; previsões salvas em {saida}")


if __name__ == "__main__":
    main()
