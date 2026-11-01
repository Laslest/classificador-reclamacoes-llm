# Classificação de reclamações de clientes com LLM

Classifica avaliações negativas de um e-commerce brasileiro em 6 motivos de reclamação usando o **Gemini com saída estruturada (JSON validado com Pydantic)** e compara o resultado com um **baseline de ML clássico** (TF-IDF + regressão logística), em um conjunto de teste rotulado à mão.

A pergunta do projeto: **um LLM sem treinamento classifica reclamações melhor que um modelo simples treinado com poucos exemplos? A que custo?**

## Resultados

> _A preencher após rodar `python -m reclamacoes.avaliar` (a tabela sai em `resultados/metricas.md`)._

| Abordagem | Acurácia | F1 macro | Respostas inválidas | Latência média | Tokens/avaliação |
|---|---|---|---|---|---|
| Baseline (TF-IDF + regressão logística) | | | | | |
| Gemini zero-shot | | | | | |
| Gemini few-shot | | | | | |

Conjunto de teste: **N** avaliações rotuladas à mão, sem nenhuma sobreposição com os exemplos do prompt ou do treino do baseline.

## Análise de erros

> _A preencher: leia `resultados/erros_*.csv` e descreva os padrões (ex.: confusão entre `nao_recebido` e `atendimento`, ironia, textos com dois motivos)._

## Como funciona

1. **Dados:** avaliações com nota 1 ou 2 do [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Textos com menos de 20 caracteres e duplicados são removidos.
2. **Rotulagem:** amostra rotulada à mão seguindo o [guia de rotulagem](docs/guia_rotulagem.md), com regras de desempate.
3. **Divisão:** 60% treino / 40% teste, estratificada por categoria (`dividir.py`).
4. **LLM:** o Gemini recebe as definições das categorias (zero-shot) ou também exemplos do treino (few-shot), com `temperature=0` e um schema JSON. A saída é validada com Pydantic; respostas inválidas são refeitas até 3 vezes e, se continuarem inválidas, **contam como erro** na avaliação.
5. **Baseline:** TF-IDF (unigramas e bigramas) + regressão logística, treinado só com o conjunto de treino.
6. **Avaliação:** acurácia, F1 macro (peso igual para categorias raras), matriz de confusão, taxa de respostas inválidas, latência e tokens.

## Como rodar

```bash
pip install -e ".[dev]"
cp .env.example .env            # coloque sua GEMINI_API_KEY

python -m reclamacoes.preparar_dados data/olist_order_reviews_dataset.csv --n 500
python -m reclamacoes.rotular data/amostra.csv      # rotulagem manual
python -m reclamacoes.dividir data/amostra.csv
python -m reclamacoes.baseline
python -m reclamacoes.classificar --modo zero-shot
python -m reclamacoes.classificar --modo few-shot
python -m reclamacoes.avaliar

pytest -q                       # testes não chamam a API
```

## Limitações

> _A preencher: tamanho do conjunto de teste, rotulagem feita por uma só pessoa, categorias definidas por mim, dados de 2016–2018 de um único marketplace._

## Estrutura

```
src/reclamacoes/
  categorias.py      categorias e schema da resposta (fonte única de verdade)
  preparar_dados.py  filtra avaliações negativas e sorteia a amostra
  rotular.py         rotulagem manual pelo terminal
  dividir.py         divisão treino/teste estratificada
  classificar.py     chamada ao Gemini com saída estruturada, retentativas e retomada
  baseline.py        TF-IDF + regressão logística
  avaliar.py         métricas, matriz de confusão e arquivo de erros
tests/               testes com o cliente do Gemini simulado
```

## Dados e licença

Os dados são do Brazilian E-Commerce Public Dataset by Olist, publicado no Kaggle sob licença CC BY-NC-SA 4.0. A amostra rotulada neste repositório segue a mesma licença.

## Uso de IA no desenvolvimento

> _Escreva com as suas palavras, com detalhes concretos: em que partes você usou IA (qual ferramenta, para quê) e o que você fez sozinho (decisões, rotulagem/perguntas, experimentos, análise). Não copie de outro projeto._
