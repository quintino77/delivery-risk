# Metodologia

## Problema e população
Priorizar pedidos com risco de chegar após a data prometida usando informações
que, em uma integração real, estariam disponíveis ao concluir a compra.
O experimento é retrospectivo e condicionado a pedidos que terminaram entregues.
Ele NÃO estima risco de cancelamento ou de nunca receber o produto.

Unidade: um pedido. Itens são agregados antes da junção para evitar multiplicar
contagens e valores. Categoria e estado principal são os do item mais caro
(desempate por ordem do item). O indicador interestadual considera qualquer vendedor.

## Elegibilidade
Status `delivered`; compra, promessa e entrega válidas; entrega não anterior à compra;
promessa com zero ou mais dias corridos; compra de 2017-01-01 a 2018-07-31.
O recorte exclui agosto de 2018, próximo ao fim da base, para reduzir censura.
Isso não elimina completamente o viés de seleção em favor de entregas observadas.

## Alvo
`late = normalize(delivered_date) > normalize(estimated_date)`.
Entrega em qualquer horário da própria data prometida é pontual. Datas sem fuso
são interpretadas no calendário local fornecido pela base, sem conversão para UTC.

## Variáveis e disponibilidade
Valor e frete somados, número de itens/vendedores, peso e volume totais, prazo
prometido, dia da semana e hora da compra, estados de origem/destino, categoria,
indicador interestadual. Não entram avaliação, status, data de entrega, data de
expedição nem aprovação do pagamento. IDs não entram no modelo.
A disponibilidade real do prazo prometido e dos atributos de catálogo no checkout
é uma hipótese: a base não contém versões temporais do cadastro para comprová-la.

## Separação temporal
- Treino: compras anteriores a 2018-03-01, com entrega observada antes dessa data.
- Validação: compras de março/abril de 2018, com entrega observada antes de 2018-05-01.
- Teste: compras de maio/junho/julho de 2018, entre as entregues elegíveis.

Pedidos sem desfecho observado no corte são removidos do respectivo conjunto.
Essa purga evita usar rótulos futuros, mas sub-representa os casos mais demorados
nos limites. O dashboard contém também pedidos elegíveis removidos dos splits por
essa regra; por isso a soma dos splits pode ser menor que o total do dashboard.

## Treinamento
Imputação por mediana e escala padronizada para numéricas. One-hot para categorias,
com no máximo 20 grupos por variável e tratamento de desconhecidas. Tudo é ajustado
apenas no treino. Baseline constante, regressão logística e gradient boosting são
comparados por average precision na validação. Entre os dois modelos aprendidos,
o de melhor validação é selecionado; a baseline permanece como referência.
O artefato final preserva o ajuste no treino, sem retreino após seleção.

O limiar é o percentil 80 dos scores de validação: orçamento experimental de cerca
de 20% dos pedidos para revisão. Não é uma política operacional comprovada nem um
limite que garante 20% em períodos futuros. Empates também podem alterar essa fração.

## Avaliação
Average precision é a métrica principal por haver poucos atrasos. ROC AUC mede
ordenação; precisão indica a proporção de alertas corretos; recall indica os atrasos
capturados; Brier mede erro dos scores probabilísticos. Acurácia isolada seria
enganosa neste problema. Não houve calibração pós-treino ou validação externa.
A permutação no teste serve apenas à interpretação; não foi usada para selecionar
variáveis ou ajustar modelos. Não é uma análise causal.

## Limitações e próximos experimentos
Mudança temporal forte, corte apenas em entregues, poucos exemplos por segmento,
catálogos sem histórico de versões, categorias mistas representadas pelo maior item,
ausência de transportadora/clima/capacidade. Não houve teste em produção, validação
geográfica independente, intervalos de confiança ou demonstração de retorno financeiro.
Próximos passos: backtesting em múltiplas janelas, calibração em janela independente,
avaliação por estado e monitoramento de drift com dados autorizados recentes.
