"""Compara todas as abordagens no conjunto de teste.

Lê resultados/predicoes_*.jsonl e gera:
- resultados/metricas.md: tabela comparativa (acurácia, F1 macro, inválidas, latência, tokens)
- resultados/erros_<modo>.csv: os erros de cada abordagem, para a análise manual

Uso:
    python -m reclamacoes.avaliar
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

from reclamacoes.categorias import Categoria

ROTULOS = [c.value for c in Categoria]
SEM_RESPOSTA = "(inválido)"


def carregar_predicoes(caminho: Path) -> pd.DataFrame:
    with caminho.open(encoding="utf-8") as f:
        return pd.DataFrame([json.loads(l) for l in f if l.strip()])


def calcular_metricas(teste: pd.DataFrame, pred: pd.DataFrame) -> dict:
    """Respostas inválidas (previsto = None) contam como ERRO, não são descartadas."""
    if not pred["id"].is_unique:
        raise ValueError("Há ids repetidos nas previsões.")
    faltando = set(teste["id"]) - set(pred["id"])
    if faltando:
        raise ValueError(f"{len(faltando)} itens do teste sem previsão. Rode o classificar de novo.")
    pred = pred.copy()
    if "tokens_raciocinio" not in pred:
        pred["tokens_raciocinio"] = 0    
    junto = teste[["id", "texto", "rotulo"]].merge(pred, on="id", how="left")
    previsto = junto["previsto"].fillna(SEM_RESPOSTA)
    return {
        "n": len(junto),
        "acuracia": accuracy_score(junto["rotulo"], previsto),
        # F1 macro dá o mesmo peso a todas as categorias, inclusive as raras.
        "f1_macro": f1_score(junto["rotulo"], previsto, labels=ROTULOS, average="macro", zero_division=0),
        "invalidas_pct": 100 * junto["previsto"].isna().mean(),
        "latencia_media_s": junto["latencia_s"].mean(),
        "tokens_medios": (junto["tokens_entrada"] + junto["tokens_saida"]
                          + junto["tokens_raciocinio"].fillna(0)).mean(),
        "junto": junto.assign(previsto=previsto),
    }


def tabela_markdown(metricas: dict[str, dict]) -> str:
    linhas = [
        "| Abordagem | Acurácia | F1 macro | Respostas inválidas | Latência média | Tokens/avaliação |",
        "|---|---|---|---|---|---|",
    ]
    for nome, m in metricas.items():
        linhas.append(
            f"| {nome} | {m['acuracia']:.1%} | {m['f1_macro']:.3f} | {m['invalidas_pct']:.1f}% "
            f"| {m['latencia_media_s']:.2f} s | {m['tokens_medios']:.0f} |"
        )
    return "\n".join(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teste", type=Path, default=Path("data/teste.csv"))
    args = parser.parse_args()

    teste = pd.read_csv(args.teste)
    resultados = {}
    for arquivo in sorted(Path("resultados").glob("predicoes_*.jsonl")):
        nome = arquivo.stem.removeprefix("predicoes_")
        m = calcular_metricas(teste, carregar_predicoes(arquivo))
        resultados[nome] = m

        junto = m.pop("junto")
        erros = junto[junto["rotulo"] != junto["previsto"]]
        erros[["id", "texto", "rotulo", "previsto", "justificativa"]].to_csv(
            f"resultados/erros_{nome}.csv", index=False)

        print(f"\n=== {nome} (n={m['n']}) — matriz de confusão (linhas = real) ===")
        colunas = ROTULOS + ([SEM_RESPOSTA] if (junto["previsto"] == SEM_RESPOSTA).any() else [])
        matriz = confusion_matrix(junto["rotulo"], junto["previsto"], labels=colunas)
        print(pd.DataFrame(matriz, index=colunas, columns=colunas).to_string())

    if not resultados:
        print("Nenhum arquivo resultados/predicoes_*.jsonl encontrado.")
        return
    tabela = tabela_markdown(resultados)
    Path("resultados/metricas.md").write_text(tabela + "\n", encoding="utf-8")
    print("\n" + tabela)


if __name__ == "__main__":
    main()
