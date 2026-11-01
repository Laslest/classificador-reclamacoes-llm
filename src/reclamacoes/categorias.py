"""Categorias de reclamação e o formato (schema) da resposta esperada do LLM.

As definições aqui são a fonte única de verdade: o guia de rotulagem
(docs/guia_rotulagem.md), o prompt e a avaliação usam as mesmas categorias.
"""

from enum import Enum

from pydantic import BaseModel, Field


class Categoria(str, Enum):
    ATRASO = "atraso"
    NAO_RECEBIDO = "nao_recebido"
    PRODUTO_ERRADO = "produto_errado"
    DEFEITO_QUALIDADE = "defeito_qualidade"
    ATENDIMENTO = "atendimento"
    OUTRO = "outro"


# Definições curtas usadas no prompt e no guia de rotulagem.
DEFINICOES: dict[Categoria, str] = {
    Categoria.ATRASO: "O produto chegou, mas depois do prazo prometido.",
    Categoria.NAO_RECEBIDO: "O cliente diz que ainda não recebeu o pedido (nenhum item chegou).",
    Categoria.PRODUTO_ERRADO: "Chegou um produto diferente do comprado (modelo, cor, tamanho) ou faltando itens do pedido.",
    Categoria.DEFEITO_QUALIDADE: "O produto chegou com defeito, danificado, quebrado ou com qualidade abaixo do esperado.",
    Categoria.ATENDIMENTO: "A queixa principal é sobre a loja/vendedor: não responde, não resolve troca, reembolso ou cancelamento.",
    Categoria.OUTRO: "Qualquer outra queixa, ou texto sem motivo claro.",
}


# Regras de desempate: as mesmas do guia de rotulagem, para o LLM ser cobrado
# só pelas regras que ele recebeu.
REGRAS_DESEMPATE: list[str] = [
    "Não recebeu e a loja não responde: nao_recebido (o problema de origem é a entrega).",
    "Chegou só parte do pedido: produto_errado.",
    "Atrasou e veio com defeito: defeito_qualidade.",
    "Qualidade diferente do anúncio (material, acabamento): defeito_qualidade; outro modelo, cor ou tamanho: produto_errado.",
    "Produto falsificado ou réplica vendido como original: produto_errado.",
]


class Classificacao(BaseModel):
    """Resposta estruturada que o LLM deve devolver."""

    categoria: Categoria
    justificativa: str = Field(
        description="Uma frase curta citando o trecho do texto que motivou a categoria.",
        max_length=300,
    )
