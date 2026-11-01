"""Testes do classificador sem chamar a API: o cliente do Gemini é simulado."""

from types import SimpleNamespace

import pandas as pd
import pytest
from google.genai import errors

from reclamacoes.categorias import Categoria
from reclamacoes.classificar import (
    ClassificadorGemini,
    escolher_exemplos,
    montar_instrucoes,
    montar_prompt,
)


class ClienteFalso:
    """Imita client.models.generate_content devolvendo respostas pré-definidas."""

    def __init__(self, respostas):
        self._respostas = list(respostas)
        self.chamadas = 0
        self.models = self

    def generate_content(self, model, contents, config):
        self.chamadas += 1
        resposta = self._respostas.pop(0)
        if isinstance(resposta, Exception):
            raise resposta
        uso = SimpleNamespace(prompt_token_count=100, candidates_token_count=20)
        return SimpleNamespace(text=resposta, usage_metadata=uso)


VALIDA = '{"categoria": "atraso", "justificativa": "chegou 10 dias depois"}'


def test_resposta_valida_na_primeira_tentativa():
    cliente = ClienteFalso([VALIDA])
    r = ClassificadorGemini(cliente, "modelo").classificar("a1", "chegou atrasado")
    assert r.previsto == "atraso"
    assert r.tentativas == 1 and r.respostas_invalidas == 0
    assert r.tokens_entrada == 100 and r.tokens_saida == 20


def test_json_invalido_tenta_de_novo():
    cliente = ClienteFalso(["isso não é json", VALIDA])
    r = ClassificadorGemini(cliente, "modelo").classificar("a1", "chegou atrasado")
    assert r.previsto == "atraso"
    assert r.tentativas == 2 and r.respostas_invalidas == 1


def test_categoria_inexistente_e_invalida():
    resposta = '{"categoria": "frete_caro", "justificativa": "x"}'
    cliente = ClienteFalso([resposta, resposta, resposta])
    r = ClassificadorGemini(cliente, "modelo").classificar("a1", "frete caro")
    assert r.previsto is None
    assert r.respostas_invalidas == 3
    assert r.erro == "JSON inválido"


def test_limite_da_api_espera_e_tenta_de_novo():
    erro_429 = errors.ClientError(429, {"error": {"message": "quota"}})
    cliente = ClienteFalso([erro_429, VALIDA])
    r = ClassificadorGemini(cliente, "modelo", espera_base_s=0).classificar("a1", "x")
    assert r.previsto == "atraso"
    assert cliente.chamadas == 2


def test_erro_de_autenticacao_nao_e_mascarado():
    erro_403 = errors.ClientError(403, {"error": {"message": "chave inválida"}})
    cliente = ClienteFalso([erro_403])
    with pytest.raises(errors.ClientError):
        ClassificadorGemini(cliente, "modelo").classificar("a1", "x")


def test_instrucoes_citam_todas_as_categorias():
    instrucoes = montar_instrucoes()
    for cat in Categoria:
        assert cat.value in instrucoes


def test_few_shot_usa_so_exemplos_do_treino():
    treino = pd.DataFrame({
        "id": [f"t{i}" for i in range(12)],
        "texto": [f"texto de treino {i}" for i in range(12)],
        "rotulo": [c.value for c in Categoria] * 2,
    })
    exemplos = escolher_exemplos(treino, por_categoria=1)
    assert len(exemplos) == len(Categoria)
    assert set(exemplos["rotulo"]) == {c.value for c in Categoria}

    prompt = montar_prompt("texto do teste", exemplos)
    assert prompt.count("Categoria:") == len(Categoria)
    assert prompt.rstrip().endswith('Texto: "texto do teste"')


def test_zero_shot_nao_tem_exemplos():
    assert "Exemplos" not in montar_prompt("texto", None)
