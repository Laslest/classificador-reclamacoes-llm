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

As regras 1 a 4 também estão em `src/reclamacoes/categorias.py` (`REGRAS_DESEMPATE`) e vão no prompt. Se mudar aqui, mude lá.

1. **Não recebido + atendimento** ("não chegou e a loja não responde") → `nao_recebido`. O problema de origem é a entrega.
2. **Faltou parte do pedido** ("chegou só 1 de 2 itens") → `produto_errado`.
3. **Atraso + defeito** ("demorou e veio quebrado") → `defeito_qualidade`. O defeito é mais grave e exige ação.
4. **Diferente do anúncio** na qualidade ("material parece frágil, não é o da foto") → `defeito_qualidade`; produto de outro modelo/cor → `produto_errado`.
5. Na dúvida real entre duas categorias, anote o id em `docs/casos_dificeis.md`. Esses casos entram na análise de erros.

## Concordância (opcional, mas valoriza o projeto)

Peça para outra pessoa rotular 30 exemplos às cegas e calcule a concordância.
Se humanos discordam em 20% dos casos, nenhum modelo vai acertar 100%: isso entra nas limitações.
