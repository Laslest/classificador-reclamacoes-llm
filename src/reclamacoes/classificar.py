"""Classifica as reclamações do conjunto de teste com o Gemini.

Dois modos:
- zero-shot: o prompt traz só as definições das categorias.
- few-shot:  o prompt traz também exemplos rotulados, escolhidos do TREINO.

As previsões são salvas em resultados/predicoes_<modo>.jsonl, uma por linha.
Se o script parar no meio (limite da API, internet), rodar de novo continua
de onde parou, sem gastar cota com o que já foi classificado.

Uso:
    python -m reclamacoes.classificar --modo zero-shot
    python -m reclamacoes.classificar --modo few-shot
"""

import argparse
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from reclamacoes.categorias import DEFINICOES, REGRAS_DESEMPATE, Classificacao

MODELO_PADRAO = "gemini-3.5-flash"


def montar_instrucoes() -> str:
    linhas = [
        "Você classifica reclamações de clientes de um e-commerce brasileiro.",
        "Escolha exatamente UMA categoria: a do motivo PRINCIPAL da reclamação.",
        "Categorias:",
    ]
    linhas += [f"- {cat.value}: {definicao}" for cat, definicao in DEFINICOES.items()]
    linhas.append("Regras de desempate quando houver mais de um motivo:")
    linhas += [f"- {regra}" for regra in REGRAS_DESEMPATE]
    linhas.append("Responda apenas no formato JSON pedido.")
    return "\n".join(linhas)


def escolher_exemplos(treino: pd.DataFrame, por_categoria: int = 2, seed: int = 42) -> pd.DataFrame:
    """Sorteia alguns exemplos de cada categoria do conjunto de TREINO."""
    por_grupo = [
        grupo.sample(n=min(por_categoria, len(grupo)), random_state=seed)
        for _, grupo in treino.groupby("rotulo")
    ]
    # Embaralha para os exemplos não aparecerem agrupados por categoria no prompt.
    return pd.concat(por_grupo).sample(frac=1, random_state=seed)


def montar_prompt(texto: str, exemplos: pd.DataFrame | None = None) -> str:
    partes = []
    if exemplos is not None and len(exemplos):
        partes.append("Exemplos já classificados:")
        for _, ex in exemplos.iterrows():
            partes.append(f'Texto: "{ex["texto"]}"\nCategoria: {ex["rotulo"]}')
        partes.append("Agora classifique:")
    partes.append(f'Texto: "{texto}"')
    return "\n\n".join(partes)


@dataclass
class Resultado:
    id: str
    previsto: str | None  # None = o modelo não devolveu uma resposta válida
    justificativa: str | None
    tentativas: int
    respostas_invalidas: int
    latencia_s: float
    tokens_entrada: int
    tokens_saida: int
    erro: str | None = None


class ClassificadorGemini:
    def __init__(self, client, modelo: str, exemplos: pd.DataFrame | None = None,
                 max_tentativas: int = 3, espera_base_s: float = 5.0):
        self.client = client
        self.modelo = modelo
        self.exemplos = exemplos
        self.max_tentativas = max_tentativas
        self.espera_base_s = espera_base_s

    def _config(self):
        from google.genai import types

        return types.GenerateContentConfig(
            system_instruction=montar_instrucoes(),
            response_mime_type="application/json",
            response_schema=Classificacao,
            temperature=0,
        )

    def classificar(self, id_: str, texto: str) -> Resultado:
        from google.genai import errors

        prompt = montar_prompt(texto, self.exemplos)
        invalidas, tokens_in, tokens_out, ultimo_erro = 0, 0, 0, None
        inicio = time.perf_counter()

        for tentativa in range(1, self.max_tentativas + 1):
            try:
                resposta = self.client.models.generate_content(
                    model=self.modelo, contents=prompt, config=self._config()
                )
            except (errors.ClientError, errors.ServerError) as e:
                # 429 = limite de requisições; 5xx = instabilidade. Espera e tenta de novo.
                if isinstance(e, errors.ClientError) and e.code != 429:
                    raise
                ultimo_erro = f"API {e.code}"
                time.sleep(self.espera_base_s * 2 ** (tentativa - 1))
                continue

            uso = getattr(resposta, "usage_metadata", None)
            tokens_in += getattr(uso, "prompt_token_count", 0) or 0
            tokens_out += getattr(uso, "candidates_token_count", 0) or 0

            try:
                saida = Classificacao.model_validate_json(resposta.text or "")
            except ValidationError:
                invalidas += 1
                ultimo_erro = "JSON inválido"
                continue

            return Resultado(id_, saida.categoria.value, saida.justificativa, tentativa,
                             invalidas, time.perf_counter() - inicio, tokens_in, tokens_out)

        return Resultado(id_, None, None, self.max_tentativas, invalidas,
                         time.perf_counter() - inicio, tokens_in, tokens_out, ultimo_erro)


def ids_ja_classificados(caminho: Path) -> set[str]:
    if not caminho.exists():
        return set()
    with caminho.open(encoding="utf-8") as f:
        return {json.loads(linha)["id"] for linha in f if linha.strip()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modo", choices=["zero-shot", "few-shot"], required=True)
    parser.add_argument("--teste", type=Path, default=Path("data/teste.csv"))
    parser.add_argument("--treino", type=Path, default=Path("data/treino.csv"))
    parser.add_argument("--exemplos-por-categoria", type=int, default=2)
    parser.add_argument("--intervalo", type=float, default=6.0,
                        help="segundos entre chamadas, para respeitar o limite do plano gratuito")
    args = parser.parse_args()

    from dotenv import load_dotenv
    from google import genai

    load_dotenv()
    modelo = os.environ.get("GEMINI_MODEL", MODELO_PADRAO)
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    exemplos = None
    if args.modo == "few-shot":
        exemplos = escolher_exemplos(pd.read_csv(args.treino), args.exemplos_por_categoria)

    classificador = ClassificadorGemini(client, modelo, exemplos)
    teste = pd.read_csv(args.teste)
    saida = Path(f"resultados/predicoes_{args.modo}.jsonl")
    saida.parent.mkdir(exist_ok=True)
    feitos = ids_ja_classificados(saida)

    pendentes = teste[~teste["id"].isin(feitos)]
    print(f"Modelo {modelo} | modo {args.modo} | {len(feitos)} já feitos, {len(pendentes)} pendentes")
    with saida.open("a", encoding="utf-8") as f:
        for n, (_, linha) in enumerate(pendentes.iterrows(), start=1):
            r = classificador.classificar(linha["id"], linha["texto"])
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{n}/{len(pendentes)}] {r.previsto or 'INVÁLIDO'} (real: {linha['rotulo']})")
            time.sleep(args.intervalo)


if __name__ == "__main__":
    main()
