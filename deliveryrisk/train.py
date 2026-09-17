"""Reproducible training, temporal evaluation and export."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, roc_auc_score, precision_score,
    recall_score, f1_score, brier_score_loss, confusion_matrix, precision_recall_curve)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .data import build_dataset, temporal_split, NUMERIC, CATEGORICAL, FEATURES

def preprocessor():
    return ColumnTransformer([
        ('num', Pipeline([('fill',SimpleImputer(strategy='median')),('scale',StandardScaler())]), NUMERIC),
        ('cat', OneHotEncoder(handle_unknown='infrequent_if_exist', max_categories=20, sparse_output=False), CATEGORICAL)])

def metrics(y, p, threshold):
    pred = p >= threshold
    return { 'average_precision':float(average_precision_score(y,p)),
        'roc_auc':float(roc_auc_score(y,p)), 'precision':float(precision_score(y,pred,zero_division=0)),
        'recall':float(recall_score(y,pred,zero_division=0)), 'f1':float(f1_score(y,pred,zero_division=0)),
        'brier':float(brier_score_loss(y,p)), 'alert_rate':float(pred.mean()),
        'confusion_matrix':confusion_matrix(y,pred,labels=[0,1]).tolist()}

def run(raw, output):
    output = Path(output); output.mkdir(parents=True,exist_ok=True)
    df, audit = build_dataset(raw)
    train, valid, test = temporal_split(df)
    candidates = {'baseline': DummyClassifier(strategy='prior'),
        'logistic_regression':LogisticRegression(max_iter=1000, C=0.2, random_state=42),
        'gradient_boosting':HistGradientBoostingClassifier(max_iter=160,max_leaf_nodes=15,
            learning_rate=0.06,l2_regularization=5,early_stopping=False,random_state=42)}
    fitted, val_scores = {}, {}
    for name, estimator in candidates.items():
        print(f'Training {name}...', flush=True)
        model = Pipeline([('features',preprocessor()),('model',estimator)])
        model.fit(train[FEATURES],train.late)
        p = model.predict_proba(valid[FEATURES])[:,1]
        fitted[name] = model
        val_scores[name] = float(average_precision_score(valid.late,p))
    winner = max((n for n in candidates if n != 'baseline'),key=val_scores.get)
    model = fitted[winner]
    vp = model.predict_proba(valid[FEATURES])[:,1]
    # Operational budget chosen before test: approximately 20% of validation orders.
    threshold = float(np.quantile(vp, 0.80))
    scores = model.predict_proba(test[FEATURES])[:,1]
    test_metrics = metrics(test.late,scores,threshold)
    baseline = metrics(test.late,fitted['baseline'].predict_proba(test[FEATURES])[:,1],threshold)
    importance = permutation_importance(model, test[FEATURES],test.late,
        scoring='average_precision',n_repeats=3,random_state=42,max_samples=4000,n_jobs=1)
    report = {'data':audit,'selected_model':winner,'threshold':threshold,'seed':42,
        'validation_average_precision':val_scores,'test':test_metrics,'baseline_test':baseline,
        'splits':{n:{'rows':len(d),'start':str(d.order_purchase_timestamp.min()),
                    'end':str(d.order_purchase_timestamp.max()),'late_rate':float(d.late.mean())}
                  for n,d in [('train',train),('validation',valid),('test',test)]},
        'runtime':{'python':platform.python_version(),'sklearn':sklearn.__version__},
        'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(raw).glob('*.csv'))}}
    (output/'metrics.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    joblib.dump({'model':model,'threshold':threshold,'features':FEATURES,'sklearn_version':sklearn.__version__},output/'model.joblib',compress=3)
    pd.DataFrame({'feature':FEATURES,'importance':importance.importances_mean,
        'std':importance.importances_std}).sort_values('importance',ascending=False).to_csv(output/'importance.csv',index=False)
    # Publish analysis columns only: no order/customer/seller IDs or exact addresses.
    keep = FEATURES + ['order_purchase_timestamp','late','delay_days','delivery_days']
    df[keep].to_csv(output/'dashboard.csv.gz',index=False,compression='gzip')
    pd.DataFrame({'actual':test.late.to_numpy(),'score':scores}).to_csv(output/'predictions.csv.gz',index=False,compression='gzip')
    precision,recall,_ = precision_recall_curve(test.late,scores)
    idx=np.linspace(0,len(precision)-1,min(300,len(precision))).astype(int)
    pd.DataFrame({'precision':precision[idx],'recall':recall[idx]}).to_csv(output/'pr_curve.csv',index=False)
    print(json.dumps(report,indent=2),flush=True)
    return report

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--raw',default='data/raw');parser.add_argument('--output',default='artifacts')
    args=parser.parse_args();run(args.raw,args.output)
