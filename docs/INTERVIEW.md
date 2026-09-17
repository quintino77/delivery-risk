# Como apresentar o projeto

**Em 30 segundos:** O DeliveryRisk estuda entregas históricas de e-commerce e
estima quais pedidos merecem revisão por risco de atraso. Fiz uma análise por
região e categoria, comparei modelos com divisão temporal e disponibilizei um
simulador com os limites do experimento explícitos.

**Por que separar por tempo?** Para medir generalização em compras posteriores
às usadas para aprender. Uma divisão aleatória misturaria contextos operacionais.

**Como evitar vazamento?** Usando apenas atributos do pedido na compra, ajustando
transformações no treino e exigindo que o rótulo já fosse conhecido em cada corte.

**Por que average precision?** Os atrasos são minoria. A métrica avalia a capacidade
de concentrar atrasos entre os maiores scores. Sua referência depende da prevalência.

**O que significa o limiar?** Um orçamento hipotético de revisão de aproximadamente
20% da validação. A fração no teste pode mudar; isso também é resultado do experimento.

**O modelo economiza dinheiro?** Isso não foi medido. Primeiro seria necessário
validar a ação operacional, seu custo, seu efeito e o comportamento em dados recentes.

**Por que score e não certeza?** Não houve calibração externa nem uso em produção.
O modelo foi treinado em uma operação antiga e sua distribuição pode ter mudado.

**O que eu melhoraria?** Backtesting, avaliação de grupos, calibração, dados recentes,
monitoramento e experimento operacional antes de qualquer decisão automática.
