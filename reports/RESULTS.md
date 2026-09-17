# Resultados da execução — 17/09/2026

Base oficial baixada e pipeline executado localmente. Métricas calculadas a partir
de previsões reais, disponíveis em `artifacts/predictions.csv.gz`.

## Principais observações

- 89.852 pedidos elegíveis, taxa geral de atraso de 6,83%.
- Março de 2018 teve 18,96% de atrasos no recorte do painel; junho teve 1,16%.
  A diferença não deve ser atribuída a uma causa sem dados adicionais.
- AP de validação: baseline 0,1088; regressão logística 0,2500; boosting 0,2545.
- AP de teste: 0.0750, aproximadamente 1.97 vezes a referência de
  prevalência do teste (0.0380). Essa razão não representa ganho financeiro.
- O desempenho de teste ficou abaixo do de validação. A prevalência também mudou.
- 332 verdadeiros positivos, 4.293 falsos positivos, 390 falsos negativos,
  13.986 verdadeiros negativos.
- Precisão baixa e Brier sem melhora sobre a baseline limitam o uso dos scores.

## Verificação

O pipeline completo foi executado com a base real. As consultas SQLite foram
executadas e os resultados estão em `reports/sql/`. Inferência em lote testada com
`examples/orders.csv`. A interface foi verificada por testes automatizados e
inspeção no navegador. Docker e hospedagem externa não foram executados.

## Interpretação prática

O projeto demonstra um fluxo de trabalho reproduzível e revela um problema real de
modelagem: melhorar o ranking não basta para justificar intervenção operacional.
Um próximo experimento deve testar estabilidade em várias janelas, custo por alerta
e calibração antes de tentar uso em produção.
