"""Order-grain features. Delivery timestamps are labels, never predictors."""
from pathlib import Path
import numpy as np
import pandas as pd

NUMERIC = ['price', 'freight_value', 'item_count', 'seller_count', 'weight_g',
           'volume_cm3', 'promised_days', 'purchase_weekday', 'purchase_hour', 'interstate']
CATEGORICAL = ['customer_state', 'seller_state', 'category']
FEATURES = NUMERIC + CATEGORICAL

def build_dataset(raw):
    raw = Path(raw)
    def read(name):
        return pd.read_csv(raw / f'olist_{name}_dataset.csv')
    orders, items, customers, products, sellers = [read(n) for n in
        ['orders', 'order_items', 'customers', 'products', 'sellers']]
    for col in ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']:
        orders[col] = pd.to_datetime(orders[col], errors='coerce')
    if orders.order_id.duplicated().any():
        raise ValueError('Duplicate order_id in orders.')
    items = items.merge(products, on='product_id', validate='many_to_one').merge(
        sellers[['seller_id', 'seller_state']], on='seller_id', validate='many_to_one')
    items['volume_cm3'] = items.product_length_cm * items.product_height_cm * items.product_width_cm
    aggregate = items.groupby('order_id').agg(price=('price', 'sum'), freight_value=('freight_value', 'sum'),
        item_count=('order_item_id', 'size'), seller_count=('seller_id', 'nunique'),
        weight_g=('product_weight_g', lambda x: x.sum(min_count=1)),
        volume_cm3=('volume_cm3', lambda x: x.sum(min_count=1)))
    # The most expensive item represents category/state for mixed baskets.
    dominant = items.sort_values(['price', 'order_item_id'], ascending=[False, True]).drop_duplicates('order_id')
    dominant = dominant[['order_id', 'seller_state', 'product_category_name']].rename(columns={'product_category_name':'category'})
    df = orders.merge(customers[['customer_id', 'customer_state']], on='customer_id', validate='many_to_one')
    df = df.merge(aggregate, on='order_id', validate='one_to_one').merge(dominant, on='order_id', validate='one_to_one')
    bought = df.order_purchase_timestamp
    df['promised_days'] = (df.order_estimated_delivery_date.dt.normalize() - bought.dt.normalize()).dt.days
    df['purchase_weekday'], df['purchase_hour'] = bought.dt.dayofweek, bought.dt.hour
    states = items[['order_id', 'seller_state']].merge(df[['order_id', 'customer_state']], on='order_id', validate='many_to_one')
    interstate = states.assign(interstate=states.seller_state.ne(states.customer_state)).groupby('order_id').interstate.max()
    df['interstate'] = df.order_id.map(interstate).astype(int)
    eligible = (df.order_status.eq('delivered') & df.order_delivered_customer_date.notna()
        & bought.notna() & df.order_estimated_delivery_date.notna() & df.promised_days.ge(0)
        & df.order_delivered_customer_date.ge(bought)
        & bought.ge('2017-01-01') & bought.lt('2018-08-01'))
    df = df.loc[eligible].copy()
    # Promise is a calendar day: arrival during that day is on time.
    df['delay_days'] = (df.order_delivered_customer_date.dt.normalize() - df.order_estimated_delivery_date.dt.normalize()).dt.days
    df['late'] = df.delay_days.gt(0).astype(int)
    df['delivery_days'] = (df.order_delivered_customer_date - df.order_purchase_timestamp).dt.total_seconds() / 86400
    df[CATEGORICAL] = df[CATEGORICAL].fillna('desconhecida')
    df = df.replace([np.inf, -np.inf], np.nan).sort_values('order_purchase_timestamp').reset_index(drop=True)
    audit = {'source_orders':len(orders), 'eligible_orders':len(df), 'excluded_orders':len(orders)-len(df),
             'late_rate':float(df.late.mean())}
    return df, audit

def temporal_split(df):
    """Labels must have been observed before each subsequent evaluation window."""
    t, observed = df.order_purchase_timestamp, df.order_delivered_customer_date
    train = df.loc[(t < '2018-03-01') & (observed < '2018-03-01')].copy()
    valid = df.loc[(t >= '2018-03-01') & (t < '2018-05-01') & (observed < '2018-05-01')].copy()
    test = df.loc[(t >= '2018-05-01') & (t < '2018-08-01')].copy()
    for name, part in [('train', train), ('validation', valid), ('test', test)]:
        if len(part) < 20 or part.late.nunique() != 2:
            raise ValueError(f'{name}: insufficient data or only one outcome class.')
    return train, valid, test
