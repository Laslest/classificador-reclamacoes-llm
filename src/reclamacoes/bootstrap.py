"""Intervalo de confiança (95%) da diferença de F1 macro entre abordagens.

Bootstrap pareado: sorteia 198 itens do teste COM reposição (os mesmos itens
para as duas abordagens), calcula o F1 de cada uma nessa amostra e guarda a
diferença. Repete 1.000 vezes. Se o intervalo contém 0, a diferença pode ser
só sorte do conjunto de teste.

Uso:
    python -m reclamacoes.bootstrap
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

from reclamacoes.avaliar import ROTULOS, SEM_RESPOSTA, carregar_predicoes

REFERENCIA = "zero-shot"


def f1(real, previsto) -> float:
    return f1_score(real, previsto, labels=ROTULOS, average="macro", zero_division=0)


def intervalo_diferenca(real, prev_a, prev_b, n_amostras=1000, seed=0):
    """Diferença F1(a) - F1(b) no teste inteiro e o intervalo de 95% do bootstrap."""
    real, prev_a, prev_b = map(np.asarray, (real, prev_a, prev_b))
    rng = np.random.default_rng(seed)
    n = len(real)
    diferencas = []
    for _ in range(n_amostras):
        idx = rng.integers(0, n, size=n)  # mesmos índices para as duas: é isso que torna pareado
        diferencas.append(f1(real[idx], prev_a[idx]) - f1(real[idx], prev_b[idx]))
    baixo, alto = np.percentile(diferencas, [2.5, 97.5])
    return f1(real, prev_a) - f1(real, prev_b), baixo, alto


def main() -> None:
    teste = pd.read_csv("data/teste.csv")
    previsoes = {}
    for arquivo in sorted(Path("resultados").glob("predicoes_*.jsonl")):
        pred = carregar_predicoes(arquivo).set_index("id")["previsto"]
        # Alinha pela ordem do teste; resposta inválida conta como erro.
        previsoes[arquivo.stem.removeprefix("predicoes_")] = (
            teste["id"].map(pred).fillna(SEM_RESPOSTA).to_numpy()
        )

    linhas = [
        f"Diferença de F1 macro em relação ao {REFERENCIA} (bootstrap pareado, 1.000 amostras, IC 95%)",
        "",
        "| Abordagem | Diferença | IC 95% |",
        "|---|---|---|",
    ]
    for nome, prev in previsoes.items():
        if nome == REFERENCIA:
            continue
        dif, baixo, alto = intervalo_diferenca(teste["rotulo"], prev, previsoes[REFERENCIA])
        linhas.append(f"| {nome} | {dif:+.3f} | [{baixo:+.3f}, {alto:+.3f}] |")

    texto = "\n".join(linhas)
    print(texto)
    Path("resultados/bootstrap.md").write_text(texto + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
