# Model card — DeliveryRisk v1

- Tarefa: classificar atraso de pedidos entregues, no momento hipotético da compra.
- Modelo: HistGradientBoostingClassifier, 160 iterações, 15 folhas, seed 42.
- Seleção: maior average precision na validação entre logística e boosting.
- Fonte: Olist, ver DATA_LICENSE.md. Python 3.12.14, scikit-learn 1.7.2.
- Entrada: 13 atributos; consulte DATA_DICTIONARY.md.
- Saída: score entre 0 e 1 e alerta experimental acima de 0.075828.
- Artefato: artifacts/model.joblib. Nenhum ajuste foi feito com os rótulos de teste.

## Desempenho e uso pretendido
AP 0.0750; ROC AUC 0.6756; recall 45.98%;
precisão 7.18%; alertas 24.34% no teste histórico.
Uso educacional e exploração de técnicas de análise, validação e priorização.
Não usar para prometer datas de entrega, penalizar vendedores ou tomar decisões
automáticas em uma operação atual sem nova validação.

## Calibração e mudança temporal
A prevalência passou de 5.07% no treino para
10.88% na validação e 3.80% no teste.
O Brier score do modelo (0.03677) ficou ligeiramente pior que o da baseline
(0.03672). Isso contrasta com a melhora de ranking: ordenar melhor não
implica probabilidades mais confiáveis. Não houve calibração pós-treino.

## Riscos conhecidos
Censura, condicionamento a entregues, recorte temporal único, grupos geográficos
com amostras pequenas, atributos de catálogo sem histórico de versão e falsa
sensação de certeza. Não há garantia de desempenho por estado/categoria.
Avaliação completa e decisões do pipeline em METHODOLOGY.md.
