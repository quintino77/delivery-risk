"""Shared validation for UI and batch inference."""
import numpy as np
import pandas as pd
from .data import NUMERIC, CATEGORICAL, FEATURES

def validate_features(df):
    missing = set(FEATURES)-set(df.columns)
    if missing: raise ValueError('Colunas ausentes: '+', '.join(sorted(missing)))
    x=df[FEATURES].copy()
    for c in NUMERIC:
        x[c]=pd.to_numeric(x[c],errors='raise')
    if not np.isfinite(x[NUMERIC].to_numpy()).all():
        raise ValueError('Preencha todos os campos numéricos com valores finitos.')
    if (x[NUMERIC] < 0).any().any(): raise ValueError('Valores negativos não são aceitos.')
    if (x.item_count < 1).any() or (x.seller_count < 1).any() or (x.seller_count > x.item_count).any():
        raise ValueError('Use pelo menos um item/vendedor; vendedores não podem superar itens.')
    for c in ['item_count','seller_count','purchase_weekday','purchase_hour','interstate']:
        if (x[c] % 1 != 0).any(): raise ValueError(f'{c} deve ser inteiro.')
    if (x.purchase_weekday > 6).any() or (x.purchase_hour > 23).any() or not x.interstate.isin([0,1]).all():
        raise ValueError('Dia da semana, hora ou indicador interestadual inválido.')
    for c in CATEGORICAL:
        if x[c].isna().any() or x[c].astype(str).str.strip().eq('').any(): raise ValueError(f'Preencha {c}.')
        x[c]=x[c].astype(str)
    return x

def predict(bundle, df):
    x=validate_features(df)
    scores=bundle['model'].predict_proba(x)[:,1]
    return pd.DataFrame({'risk_score':scores,'alert':scores >= bundle['threshold']})
