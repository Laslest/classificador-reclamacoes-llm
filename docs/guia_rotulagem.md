# Guia de rotulagem

Cada avaliação recebe **uma** categoria: a do motivo **principal** da reclamação.
Siga este guia sempre igual. Se mudar uma regra no meio, revise os exemplos já rotulados.

| Categoria | Quando usar | Exemplos |
|---|---|---|
| `atraso` | O produto **chegou**, mas depois do prazo. | "chegou com 15 dias de atraso" |
| `nao_recebido` | O cliente diz que **ainda não recebeu**. | "até hoje não recebi", "consta entregue mas não chegou" |
| `produto_errado` | Chegou algo **diferente do comprado** ou **faltando itens**. | "veio outra cor", "comprei 2 e veio 1" |
| `defeito_qualidade` | Chegou **com defeito, quebrado, danificado** ou de qualidade ruim. | "veio rachado", "parou de funcionar em 2 dias" |
| `atendimento` | A queixa principal é a **loja/vendedor não resolver**: sem resposta, troca, reembolso, cancelamento. | "mandei 5 e-mails e ninguém responde" |
| `outro` | Qualquer outro motivo (frete caro, nota fiscal, embalagem) ou sem motivo claro. | "não gostei" |

Use **descartar** (`d`) para textos que não são reclamação (ex.: elogio com nota baixa por engano).

## Regras de desempate

As regras 1 a 9 também estão em `src/reclamacoes/categorias.py` (`REGRAS_DESEMPATE`) e vão no prompt. Se mudar aqui, mude lá.

1. **Não recebeu + loja não responde/resolve** → `nao_recebido`. **Exceção:** se o pedido foi cancelado ou a loja avisou que não tem o produto (venda sem estoque) e o cliente não espera mais a entrega → `atendimento`.
2. **Faltou um item do pedido** ("comprei 2, veio 1"; kit com unidades faltando) → `produto_errado`.
3. **Atraso + defeito** → `defeito_qualidade`.
4. **Diferente do anúncio:** material/acabamento/qualidade → `defeito_qualidade`; outro modelo, cor ou tamanho → `produto_errado`.
5. **Dúvida real** → anotar em `docs/casos_dificeis.md`.
6. **Produto falsificado/réplica** vendido como original → `produto_errado`.
7. **Demora ou prazo descumprido sem dizer se recebeu** → `atraso`. Só é `nao_recebido` se o cliente disser que não chegou.
8. **Faltam peças/partes dentro de um produto** (brinquedo sem adesivos, cadeira sem borrachinhas) → `defeito_qualidade`.
9. **Produto com problema + loja não resolve a troca/devolução** → a categoria do problema do produto. `atendimento` é só quando a queixa é apenas a loja.
10. **Tempo verbal do atraso:** "a entrega está atrasada" (presente, ainda esperando) → `nao_recebido`; "a entrega atrasou" (passado, sem dizer se chegou) → `atraso`.
11. **Venda sem estoque:** se a loja avisou ou cancelou → `atendimento`; se não avisou e o cliente continua sem o produto → `nao_recebido`. Produto incompatível com o modelo informado → `produto_errado`.
Também são `outro`: frete, embalagem, nota fiscal, pagamento, ter que retirar no correio. Texto sem motivo escrito ("quero devolver", "quero meu dinheiro de volta") → `outro`. Não é reclamação → descartar.

## Concordância (opcional, mas valoriza o projeto)

Peça para outra pessoa rotular 30 exemplos às cegas e calcule a concordância.
Se humanos discordam em 20% dos casos, nenhum modelo vai acertar 100%: isso entra nas limitações.
