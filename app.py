from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from deliveryrisk.predict import predict

ROOT = Path(__file__).parent
ART = ROOT / 'artifacts'
st.set_page_config(page_title='DeliveryRisk | Inteligência logística',page_icon='📦',layout='wide')
st.markdown('''<style>
.block-container {padding-top:4rem;max-width:1440px}
h1 {letter-spacing:-1.8px!important;font-size:3.1rem!important}
[data-testid="stMetric"] {background:#131E32;border:1px solid #26334A;border-radius:14px;padding:18px}
[data-testid="stMetricLabel"] {color:#9AAFC8}
[data-testid="stMetricValue"] {font-size:1.65rem;white-space:normal}
[data-testid="stMetricLabel"] p {white-space:normal}
@media (min-width: 640px) and (max-width: 1100px) {
[data-testid="stHorizontalBlock"] {flex-wrap:wrap}
[data-testid="stColumn"] {min-width:220px!important;flex:1 1 220px!important}
}
.hero-label {color:#20C7A4;font-size:12px;letter-spacing:3px;font-weight:700;margin-bottom:10px}
.hero-copy {color:#9AAFC8;font-size:17px;max-width:760px;margin-bottom:24px}
</style>''',unsafe_allow_html=True)

@st.cache_data
def load_data():
    d=pd.read_csv(ART/'dashboard.csv.gz',parse_dates=['order_purchase_timestamp'])
    return d,json.loads((ART/'metrics.json').read_text(encoding='utf-8'))
@st.cache_resource
def load_model():
    return joblib.load(ART/'model.joblib')
def chart(fig):
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Arial',color='#C9D5E8'),margin=dict(l=12,r=12,t=40,b=15),height=340)
    if fig.layout.coloraxis.colorbar.title.text == 'Atraso':
        fig.update_layout(coloraxis_colorbar_tickformat='.0%')
    st.plotly_chart(fig,use_container_width=True)
def pct(x): return f'{x:.1%}'
def brl(x): return f'R$ {x:,.0f}'.replace(',','.')

if not (ART/'metrics.json').exists():
    st.error('Artefatos ausentes. Execute python -m deliveryrisk.train após baixar a base.');st.stop()
df,report=load_data()
with st.sidebar:
    st.markdown('## 📦 DeliveryRisk')
    st.caption('DATA SCIENCE / LOGÍSTICA')
    page=st.radio('Navegação',['Visão geral','Explorar entregas','Simular pedido','Desempenho do modelo','Sobre o projeto'],label_visibility='collapsed')
    st.divider()
    st.caption('BASE REAL · OLIST')
    st.write('Jan 2017 — Jul 2018')
    st.caption('Estudo histórico de portfólio. Os scores não representam a operação atual da Olist.')
    st.link_button('Fonte dos dados ↗','https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce')

st.markdown('<div class="hero-label">DELIVERYRISK / INTELIGÊNCIA LOGÍSTICA</div>',unsafe_allow_html=True)

if page in ['Visão geral','Explorar entregas']:
    st.title('Cada entrega conta.')
    st.markdown('<div class="hero-copy">Explore onde os atrasos se concentram e transforme o histórico de pedidos em perguntas melhores para a operação.</div>',unsafe_allow_html=True)
    a,b,c=st.columns([2,2,2])
    dates=a.date_input('Período da compra',(df.order_purchase_timestamp.min().date(),df.order_purchase_timestamp.max().date()),
        min_value=df.order_purchase_timestamp.min().date(),max_value=df.order_purchase_timestamp.max().date())
    states=b.multiselect('Estado de destino',sorted(df.customer_state.unique()),placeholder='Todos os estados')
    cats=c.multiselect('Categoria principal',sorted(df.category.unique()),placeholder='Todas as categorias')
    view=df.copy()
    if isinstance(dates,(tuple,list)) and len(dates)==2:
        view=view.loc[view.order_purchase_timestamp.dt.date.between(*dates)]
    if states: view=view.loc[view.customer_state.isin(states)]
    if cats: view=view.loc[view.category.isin(cats)]
    if view.empty: st.info('Nenhum pedido encontrado para estes filtros.');st.stop()
    cards=st.columns(4)
    cards[0].metric('Pedidos entregues',f'{len(view):,}'.replace(',','.'))
    cards[1].metric('Taxa de atraso',pct(view.late.mean()))
    cards[2].metric('Prazo real mediano',f'{view.delivery_days.median():.1f} dias')
    cards[3].metric('Valor dos produtos',brl(view.price.sum()))
    st.caption('Atraso = entrega após o dia prometido. Valor dos produtos exclui frete. Apenas pedidos entregues elegíveis.')
    left,right=st.columns([1.6,1])
    monthly=view.assign(month=view.order_purchase_timestamp.dt.to_period('M').astype(str)).groupby('month',as_index=False).agg(orders=('late','size'),late_rate=('late','mean'))
    with left:
        st.subheader('Como o atraso mudou no tempo')
        fig=px.line(monthly,x='month',y='late_rate',markers=True,labels={'month':'Mês da compra','late_rate':'Taxa de atraso'},color_discrete_sequence=['#20C7A4'])
        fig.update_yaxes(tickformat='.0%');chart(fig)
    with right:
        st.subheader('Destinos com mais pedidos')
        grouped=view.groupby('customer_state',as_index=False).agg(orders=('late','size'),late_rate=('late','mean')).nlargest(10,'orders').sort_values('orders')
        chart(px.bar(grouped,x='orders',y='customer_state',orientation='h',color='late_rate',color_continuous_scale=['#20C7A4','#FFB454'],labels={'orders':'Pedidos','customer_state':'UF','late_rate':'Atraso'}))
    if page=='Visão geral':
        st.subheader('Do histórico à priorização')
        x,y,z=st.columns(3)
        x.markdown('**01 / Entenda a operação**\n\nCompare períodos, destinos e categorias com o volume de pedidos sempre visível.')
        y.markdown('**02 / Estime o risco**\n\nTeste um pedido usando informações disponíveis na compra e um modelo treinado na base histórica.')
        z.markdown('**03 / Confira a evidência**\n\nVeja desempenho fora do período de treino, falsos alertas e limitações antes de interpretar os scores.')
    else:
        st.subheader('Comparação de segmentos')
        group=st.selectbox('Agrupar por',['customer_state','seller_state','category'],format_func=lambda x:{'customer_state':'Estado de destino','seller_state':'Estado do vendedor principal','category':'Categoria principal'}[x])
        minimum=st.slider('Mínimo de pedidos por segmento',1,500,100)
        segments=view.groupby(group).agg(pedidos=('late','size'),atrasos=('late','sum'),taxa_atraso=('late','mean'),prazo_mediano=('delivery_days','median')).reset_index()
        segments=segments.loc[segments.pedidos>=minimum].sort_values('taxa_atraso',ascending=False)
        st.dataframe(segments,use_container_width=True,hide_index=True,column_config={'taxa_atraso':st.column_config.NumberColumn('Taxa de atraso',format='percent')})
        st.download_button('Baixar análise filtrada',segments.to_csv(index=False).encode('utf-8-sig'),'segmentos.csv','text/csv')
        st.caption('Associação não implica causa. Pequenos segmentos podem variar bastante; compare também seus volumes.')

elif page=='Simular pedido':
    st.title('Antecipe a pergunta.')
    st.markdown('<div class="hero-copy">Informe um pedido hipotético e veja como o modelo histórico o classificaria.</div>',unsafe_allow_html=True)
    st.info('Score experimental, sem calibração externa. Use cenários semelhantes a 2017–2018; não interprete como probabilidade garantida de atraso hoje.')
    with st.form('simulate'):
        a,b,c=st.columns(3)
        with a:
            customer=st.selectbox('Estado de destino',sorted(df.customer_state.unique()),index=sorted(df.customer_state.unique()).index('RJ'))
            seller=st.selectbox('Estado do vendedor principal',sorted(df.seller_state.unique()),index=sorted(df.seller_state.unique()).index('SP'))
            category=st.selectbox('Categoria principal',sorted(df.category.unique()),index=sorted(df.category.unique()).index('cama_mesa_banho'))
            price=st.number_input('Valor dos produtos (R$)',min_value=0.0,value=149.9)
        with b:
            freight=st.number_input('Frete total (R$)',min_value=0.0,value=24.9)
            items=st.number_input('Quantidade de itens',min_value=1,value=1,step=1)
            sellers=st.number_input('Quantidade de vendedores',min_value=1,value=1,step=1)
            weight=st.number_input('Peso total (g)',min_value=0.0,value=800.0)
        with c:
            volume=st.number_input('Volume total dos itens (cm³)',min_value=0.0,value=6000.0)
            promise=st.number_input('Dias corridos até a data prometida',min_value=0,value=15,step=1)
            weekday=st.selectbox('Dia da compra',range(7),format_func=lambda v:['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo'][v])
            hour=st.slider('Hora da compra',0,23,14)
        extra_interstate=st.checkbox('Há outro vendedor em estado diferente do destino',value=False)
        submitted=st.form_submit_button('Estimar risco →',type='primary',use_container_width=True)
    if submitted:
        row=pd.DataFrame([dict(price=price,freight_value=freight,item_count=items,seller_count=sellers,weight_g=weight,
            volume_cm3=volume,promised_days=promise,purchase_weekday=weekday,purchase_hour=hour,
            interstate=int(customer!=seller or extra_interstate),customer_state=customer,seller_state=seller,category=category)])
        try:
            result=predict(load_model(),row).iloc[0]
            a,b=st.columns([1,2]);a.metric('Score de risco',pct(result.risk_score))
            if result.alert: b.warning('Acima do limiar experimental: pedido entraria na fila de revisão.')
            else: b.success('Abaixo do limiar experimental. Isso não garante entrega no prazo.')
            st.caption(f'Limiar: {report["threshold"]:.1%}, definido na validação para sinalizar aproximadamente 20% dos pedidos daquele período.')
            extreme=[c for c in ['price','freight_value','weight_g','volume_cm3','promised_days'] if row[c].iloc[0] > df[c].quantile(.99)]
            if extreme: st.warning('Valores fora da faixa usual do histórico: '+', '.join(extreme)+'. A previsão pode ser menos confiável.')
        except ValueError as exc: st.error(str(exc))
    st.divider();st.subheader('Previsões em lote')
    st.caption('Envie CSV com as 13 colunas do arquivo examples/orders.csv. Limite: 5.000 pedidos.')
    upload=st.file_uploader('Arquivo de pedidos',type=['csv'])
    if upload is not None:
        try:
            batch=pd.read_csv(upload,nrows=5001)
            if batch.empty or len(batch)>5000: raise ValueError('Envie entre 1 e 5.000 pedidos.')
            results=predict(load_model(),batch)
            st.dataframe(results.head(20),hide_index=True)
            st.download_button('Baixar previsões',results.to_csv(index=False),'previsoes.csv','text/csv')
        except (ValueError,TypeError) as exc: st.error(str(exc))

elif page=='Desempenho do modelo':
    st.title('Resultados, sem atalhos.')
    st.markdown('<div class="hero-copy">Treino no passado. Seleção na validação. Avaliação final em pedidos de maio a julho de 2018.</div>',unsafe_allow_html=True)
    m=report['test'];baseline=report['baseline_test']
    a,b,c,d=st.columns(4)
    a.metric('Average precision',f'{m["average_precision"]:.3f}',f'{m["average_precision"]-baseline["average_precision"]:+.3f} vs. baseline')
    b.metric('ROC AUC',f'{m["roc_auc"]:.3f}')
    c.metric('Atrasos identificados',pct(m['recall']))
    d.metric('Pedidos sinalizados',pct(m['alert_rate']))
    st.caption(f'Modelo escolhido: {report["selected_model"]}. Precisão dos alertas: {m["precision"]:.1%}. Brier score: {m["brier"]:.4f} (menor é melhor).')
    a,b=st.columns(2)
    with a:
        st.subheader('Comparação na validação')
        comparison=pd.DataFrame(report['validation_average_precision'].items(),columns=['Modelo','Average precision'])
        chart(px.bar(comparison,x='Average precision',y='Modelo',orientation='h',color_discrete_sequence=['#20C7A4']))
        st.caption('A escolha do modelo usa somente a validação. O conjunto de teste não escolhe o vencedor.')
    with b:
        st.subheader('Matriz de confusão · teste')
        matrix=np.array(m['confusion_matrix'])
        fig=px.imshow(matrix,text_auto=True,x=['Sem alerta','Com alerta'],y=['No prazo','Atrasado'],color_continuous_scale=['#131E32','#20C7A4'],labels={'x':'Previsão','y':'Resultado real','color':'Pedidos'})
        chart(fig)
    a,b=st.columns(2)
    with a:
        st.subheader('Quais variáveis ajudam o modelo?')
        imp=pd.read_csv(ART/'importance.csv').head(8).sort_values('importance')
        chart(px.bar(imp,x='importance',y='feature',error_x='std',orientation='h',color_discrete_sequence=['#FFB454'],labels={'importance':'Queda na average precision','feature':'Variável'}))
        st.caption('Importância por permutação no teste, amostras de até 4.000 pedidos, 3 repetições. Não representa causalidade nem explicação individual.')
    with b:
        st.subheader('Precisão × cobertura de atrasos')
        curve=pd.read_csv(ART/'pr_curve.csv')
        fig=px.line(curve,x='recall',y='precision',color_discrete_sequence=['#20C7A4'])
        fig.add_hline(y=report['splits']['test']['late_rate'],line_dash='dot',annotation_text='Prevalência no teste')
        fig.update_xaxes(tickformat='.0%');fig.update_yaxes(tickformat='.0%');chart(fig)
    st.subheader('Separação temporal auditável')
    st.dataframe(pd.DataFrame(report['splits']).T,use_container_width=True)
    st.warning('Apenas pedidos entregues entram na análise. Cancelamentos e pedidos ainda abertos ficam fora. A exigência de rótulo conhecido nos cortes também pode sub-representar entregas muito demoradas.')
else:
    st.title('Um projeto de ponta a ponta.')
    st.write('DeliveryRisk conecta preparação de dados, análise exploratória, machine learning e uma interface para experimentar previsões.')
    st.markdown('''**Pergunta:** com as informações disponíveis na compra, quais pedidos merecem atenção por risco de atraso?

**Unidade de análise:** um pedido, mesmo quando contém vários itens ou vendedores. A categoria e o estado principal vêm do item de maior preço.

**Rótulo:** entrega em dia posterior à data prometida. Uma entrega às 18h no próprio dia prometido conta como pontual.

**Proteção contra vazamento:** datas reais de entrega, avaliação do cliente, status final e prazo efetivo não entram como variáveis preditoras. As transformações são ajustadas apenas no treino.

**Limitações:** base histórica de 2017–2018, somente pedidos entregues, mudança de distribuição ao longo do tempo e ausência de validação em operação atual. Não há estimativa comprovada de economia financeira.

**Tecnologias:** Python · pandas · SQL/SQLite · scikit-learn · Streamlit · Plotly · pytest · GitHub Actions.

**Reprodução:** consulte README.md, docs/METHODOLOGY.md e artifacts/metrics.json. Dados e derivados seguem a licença da Olist; código autoral sob MIT.''')
    st.json(report['data'])
