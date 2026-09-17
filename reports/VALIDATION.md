# Verificação da entrega

Data: 17/09/2026. Ambiente: Windows, Python 3.12.14.

- Treinamento completo executado sobre CSVs oficiais da Olist.
- 19 testes aprovados com pytest (7,80 segundos na execução final).
- Métricas publicadas conferidas contra as previsões de teste.
- Todas as cinco páginas exercitadas pelo Streamlit AppTest.
- Simulação, categorias desconhecidas, entradas inválidas e filtro sem dados testados.
- Três consultas SQLite executadas, com teste da contagem total por mês.
- Inferência em lote executada para examples/orders.csv.
- Dashboard e simulador inspecionados visualmente no navegador; layouts de janela
  estreita e desktop conferidos. Screenshots reais em docs/.
- ZIP verificado, sem ambiente virtual, cache, credenciais ou dados brutos.

Não executados: Docker, GitHub Actions remoto, deploy público, uso em produção.
O workflow está incluído para execução após o primeiro push.
Versões completas do ambiente de teste: requirements-lock.txt.
