import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import pytest
from deliveryrisk.data import build_dataset, temporal_split, FEATURES
from deliveryrisk.predict import predict, validate_features
from deliveryrisk.train import metrics

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def example(): return pd.read_csv(ROOT/'examples/orders.csv')

@pytest.fixture
def bundle(): return joblib.load(ROOT/'artifacts/model.joblib')

def test_prediction_round_trip(bundle,example):
    out=predict(bundle,example)
    assert len(out)==2 and out.risk_score.between(0,1).all()
    assert out.alert.equals(out.risk_score.ge(bundle['threshold']))

def test_unknown_category_supported(bundle,example):
    example['category']='never_seen_before'
    assert predict(bundle,example).risk_score.notna().all()

@pytest.mark.parametrize('column,value', [('price',-1),('price',float('inf')),('weight_g',float('nan')),
    ('seller_count',2),('item_count',0),('purchase_hour',24),('purchase_weekday',7),('interstate',2),('item_count',1.5)])
def test_invalid_input_rejected(example,column,value):
    example[column]=value
    with pytest.raises(ValueError): validate_features(example)

def test_missing_column(example):
    with pytest.raises(ValueError): validate_features(example.drop(columns='price'))

def test_no_outcome_features():
    forbidden={'late','delay_days','delivery_days','order_status','order_delivered_customer_date',
               'order_delivered_carrier_date','review_score','order_approved_at'}
    assert forbidden.isdisjoint(FEATURES)

def test_published_metrics_match_predictions():
    p=pd.read_csv(ROOT/'artifacts/predictions.csv.gz')
    report=json.loads((ROOT/'artifacts/metrics.json').read_text())
    actual=metrics(p.actual,p.score,report['threshold'])
    for key in actual:
        if key=='confusion_matrix': assert actual[key]==report['test'][key]
        else: assert actual[key]==pytest.approx(report['test'][key])

def test_temporal_purge_and_disjointness():
    parts=[]
    for month in ['2018-01','2018-03','2018-06']:
        for i in range(40):
            parts.append({'order_id':f'{month}-{i}','order_purchase_timestamp':pd.Timestamp(month+'-01'),
                'order_delivered_customer_date':pd.Timestamp(month+'-12'),'late':i%2})
    parts.append({'order_id':'future_label','order_purchase_timestamp':pd.Timestamp('2018-02-28'),
        'order_delivered_customer_date':pd.Timestamp('2018-03-10'),'late':1})
    train,valid,test=temporal_split(pd.DataFrame(parts))
    assert 'future_label' not in set(train.order_id)
    assert train.order_delivered_customer_date.max()<valid.order_purchase_timestamp.min()
    assert valid.order_delivered_customer_date.max()<test.order_purchase_timestamp.min()
    assert set(train.order_id).isdisjoint(test.order_id)

def test_order_grain_day_deadline_and_interstate(tmp_path):
    def save(name,rows): pd.DataFrame(rows).to_csv(tmp_path/f'olist_{name}_dataset.csv',index=False)
    save('orders',[dict(order_id='a',customer_id='c',order_status='delivered',
        order_purchase_timestamp='2018-01-01 14:00',order_estimated_delivery_date='2018-01-10',
        order_delivered_customer_date='2018-01-10 22:00')])
    save('customers',[dict(customer_id='c',customer_state='SP')])
    save('products',[dict(product_id='p',product_category_name='books',product_weight_g=100,
        product_length_cm=10,product_height_cm=2,product_width_cm=10)])
    save('sellers',[dict(seller_id='s1',seller_state='SP'),dict(seller_id='s2',seller_state='RJ')])
    save('order_items',[dict(order_id='a',order_item_id=1,product_id='p',seller_id='s1',price=20,freight_value=2),
        dict(order_id='a',order_item_id=2,product_id='p',seller_id='s2',price=10,freight_value=3)])
    df,audit=build_dataset(tmp_path)
    assert len(df)==1 and df.iloc[0].price==30 and df.iloc[0].freight_value==5
    assert df.iloc[0].late==0 and df.iloc[0].promised_days==9
    assert df.iloc[0].interstate==1 and df.iloc[0].seller_state=='SP'
    assert df.iloc[0].weight_g==200 and df.iloc[0].volume_cm3==400
