# Publicar no GitHub

1. Extraia o ZIP e abra a pasta `delivery-risk`.
2. No GitHub, crie um repositório chamado `delivery-risk`. Deixe a inicialização
   automática de README/licença desmarcada: estes arquivos já estão prontos.
3. Use **Add file → Upload files** e envie o conteúdo de `delivery-risk`, não o ZIP.
   Para preservar também os arquivos ocultos (`.github`, `.streamlit`, `.gitignore`),
   prefira GitHub Desktop ou os comandos abaixo.
4. Confira se o README exibe a imagem, as métricas e os links locais.
5. Em About, use: `Previsão de atrasos no e-commerce com dados reais da Olist,
   validação temporal e dashboard interativo em Python.`
6. Topics sugeridos: `python`, `data-science`, `machine-learning`, `streamlit`,
   `scikit-learn`, `olist`, `logistics`, `portfolio`.

Com Git instalado, execute dentro de `delivery-risk`, substituindo SEU_USUARIO:

```bash
git init
git add .
git commit -m "Add DeliveryRisk: Olist analytics and delivery risk model"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/delivery-risk.git
git push -u origin main
```

Não envie a pasta do ambiente virtual nem dados brutos. O `.gitignore` já os exclui.
Os artefatos pequenos que permitem executar a aplicação estão incluídos.
O workflow de testes será executado pelo GitHub no primeiro push; veja a aba Actions.

## Publicar uma demonstração
O aplicativo pode ser hospedado em um serviço compatível com Streamlit apontando
para `app.py`, Python 3.12 e `requirements.txt`. Os artefatos já estão no repositório,
portanto não precisa baixar dados ou treinar no início da aplicação.
Também há Dockerfile: `docker build -t delivery-risk .` e
`docker run --rm -p 8501:8501 delivery-risk`.
Hospedagem e Docker não foram executados nesta entrega. Nenhum serviço foi publicado.

## Depois, LinkedIn
Use `docs/LINKEDIN.md`, substitua o marcador de link pelo endereço real e anexe
`docs/dashboard.png`. Leia `docs/INTERVIEW.md` antes para conseguir explicar as decisões.
