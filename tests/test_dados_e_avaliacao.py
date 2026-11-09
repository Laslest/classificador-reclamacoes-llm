import pandas as pd
import pytest

from reclamacoes.avaliar import calcular_metricas
from reclamacoes.dividir import dividir
from reclamacoes.preparar_dados import filtrar_negativas


def test_filtra_notas_altas_textos_curtos_e_duplicados():
    df = pd.DataFrame({
        "review_id": ["a", "b", "c", "d", "e"],
        "review_score": [1, 5, 2, 1, 1],
        "review_comment_title": [None, None, "Ruim", None, None],
        "review_comment_message": [
            "Até hoje não recebi meu pedido",   # fica
            "Adorei, chegou antes do prazo",    # nota 5: sai
            "veio quebrado o produto inteiro",  # fica (com título)
            "ruim",                             # curto demais: sai
            "Até hoje não recebi meu pedido",   # duplicado: sai
        ],
    })
    saida = filtrar_negativas(df)
    assert list(saida["id"]) == ["a", "c"]
    assert saida.loc[1, "texto"] == "Ruim. veio quebrado o produto inteiro"


def test_divisao_estratificada_ignora_descartados():
    df = pd.DataFrame({
        "id": range(22),
        "texto": ["x"] * 22,
        "rotulo": ["atraso"] * 10 + ["outro"] * 10 + ["descartado", ""],
    })
    treino, teste = dividir(df, proporcao_teste=0.4)
    assert len(treino) + len(teste) == 20
    assert set(teste["rotulo"].value_counts()) == {4}  # 4 de cada categoria no teste
    assert set(treino["id"]).isdisjoint(teste["id"])


def test_resposta_invalida_conta_como_erro():
    teste = pd.DataFrame({"id": ["1", "2", "3", "4"], "texto": "x",
                          "rotulo": ["atraso", "atraso", "outro", "outro"]})
    pred = pd.DataFrame({
        "id": ["1", "2", "3", "4"],
        "previsto": ["atraso", None, "outro", "atraso"],
        "justificativa": None, "latencia_s": 1.0, "tokens_entrada": 10, "tokens_saida": 5,
    })
    m = calcular_metricas(teste, pred)
    assert m["acuracia"] == pytest.approx(0.5)
    assert m["invalidas_pct"] == pytest.approx(25.0)
    assert m["tokens_medios"] == pytest.approx(15.0)


def test_previsoes_duplicadas_ou_faltando_geram_erro():
    teste = pd.DataFrame({"id": ["1", "2"], "texto": "x", "rotulo": ["atraso", "outro"]})
    base = {"justificativa": None, "latencia_s": 1.0, "tokens_entrada": 1, "tokens_saida": 1}
    duplicada = pd.DataFrame([{"id": "1", "previsto": "atraso", **base}] * 2)
    with pytest.raises(ValueError, match="repetidos"):
        calcular_metricas(teste, duplicada)
    faltando = pd.DataFrame([{"id": "1", "previsto": "atraso", **base}])
    with pytest.raises(ValueError, match="sem previsão"):
        calcular_metricas(teste, faltando)