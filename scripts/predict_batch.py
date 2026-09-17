import argparse
import joblib
import pandas as pd
from deliveryrisk.predict import predict

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');a=p.parse_args()
    result=predict(joblib.load('artifacts/model.joblib'),pd.read_csv(a.input))
    result.to_csv(a.output,index=False)
    print(f'{len(result)} previsões salvas em {a.output}')
