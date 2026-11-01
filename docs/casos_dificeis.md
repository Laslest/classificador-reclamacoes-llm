\# Casos difíceis da rotulagem



Casos em que a decisão não foi óbvia, com o rótulo dado e o motivo. Servem de base para a análise de erros.



\## Ambíguos por falta de informação no texto

\- "preciso de um parecer do meu produto e da minha entrega" → outro. Não diz se recebeu; não inferi.

\- "Quero meu dinheiro de volta" / "Quero devolver o produto" → outro. Sem motivo escrito.

\- "Mais de mês que comprei e não tive nenhum retorno" → atraso. Não diz se recebeu (regra 7).

\- "No aguardo de um retorno urgente" → atendimento. Muito vago; poderia ser outro.



\## Erro de digitação ou texto truncado

\- "Atraso na entrega. Ainda recebi o produto, já passou do prazo" → atraso. Provável "não recebi"; rotulei pelo texto escrito.

\- "Não exatamente o que eu e. Não é um espelho" → defeito\_qualidade. Truncado; pode ser produto trocado ou qualidade ruim.



\## Dois motivos no mesmo texto

\- "Não recebi o produto e depois me falaram que meu vale de reembolso já estava disponível, mas era mentira" → nao\_recebido. A parte mais revoltante é o atendimento, mas o problema de origem é a entrega (regra 1).

\- "meu produto foi roubado na entrega e me disseram que entregariam um novo, mas depois me negaram" → nao\_recebido. Mesmo raciocínio (regra 1).

\- "Decepcionada com a compra. O produto foi entregue com atraso, o pior não foi isso, chegou em uma caixa suja" → outro. O próprio cliente diz qual foi a queixa principal.

\- "A CADEIRA... NÃO VEIO COM A COR QUE ESTÁ NA FOTO... E É BAMBA" → defeito\_qualidade. Cor diferente (produto\_errado) + defeito; ficou o defeito.

\- "garrafa térmica 1,2 L não comporta nem 800 ml, além de sinal de uso/avaria" → produto\_errado. Capacidade diferente da anunciada + avaria.



\## Fronteira entre categorias

\- "Dava impressão do frasco ser maior" → produto\_errado. Tamanho diferente do esperado; pode ser só anúncio enganoso.

\- "Colocaram nos status como entregue, quando na verdade recebi apenas um cadeado e uma carta de justificação de atraso" → nao\_recebido. Consta entregue, mas o produto não veio.

\- "Fui no correio buscar meu produto, só deram um produto, e outro disseram que não estava lá" → produto\_errado. Faltou parte do pedido; culpa parece ser dos Correios.

\- "Vocês venderam algo que não tinham no estoque... Minha filha ainda aguarda a boneca" → nao\_recebido. Sem estoque, mas o pedido não foi cancelado e a cliente ainda espera.

\- "veio a caixa do brinquedo com um rasgo, a cartela de adesivo veio sem 2 adesivos, as cores não foram legais" → defeito\_qualidade. Faltar peça dentro de um produto ≠ faltar item do pedido (regra 8).



\## Observações sobre os dados (para o README)

\- Alguns textos estão truncados no dataset original (limite do formulário da Olist).

\- Os nomes das lojas foram anonimizados pela Olist com nomes de casas de Game of Thrones (lannister, targaryen, stark, baratheon).

\- Muitos clientes recebem o pedido de avaliação antes do produto chegar ("Por que desta avaliação? Cadê meu produto?"), o que explica a alta frequência de `nao\_recebido`.

## Rodada 2
- "FABRICAÇÃO. Origem do produto china, qualidade ruim... pirata" → defeito_qualidade. Não diz que foi anunciado como original; diferente de falsificado vendido como original (produto_errado).
- "Demorou n veio a cor q escolhi... sofá... nada de entregar" → produto_errado. Texto contraditório: fala de cor errada e de não entrega.
- "a colcha não é um cobre leito e o tecido é de lençol fino... capas descosturadas" → defeito_qualidade. Poderia ser produto_errado.
- "Fora dos padroes nacionais, não cabe nenhum documento" → defeito_qualidade. Produto não atende à expectativa; poderia ser produto_errado (tamanho).
- "Não recebi porque está no correio" → nao_recebido. Poderia ser outro (retirada no correio).
- "Fiz a compra e não entregou... Fiz o cancelamento e ainda recebo estes e-mail" → nao_recebido. O cancelamento foi consequência da não entrega.
- "Falta entre lojas e clientes" → outro. Provável palavra faltando ("comunicação").
- "As camisas compradas, recebidas e devolvidas foram três maquinetada" → outro. Devolução sem motivo legível.

## Convenções criadas durante a rotulagem
- Tempo verbal: "está atrasada" → nao_recebido; "atrasou" → atraso.
- Toda queixa de "demora" sem dizer que não chegou → atraso (não distingui prazo longo de prazo descumprido).
- Peça de um produto ≠ item do pedido (regra 8).