from pathlib import Path
import sqlite3
import pandas as pd

def main():
    out=Path('reports/sql');out.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(':memory:') as db:
        pd.read_csv('artifacts/dashboard.csv.gz').to_sql('orders',db,index=False)
        text=Path('sql/analysis.sql').read_text(encoding='utf-8')
        queries='\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('--')).split(';')
        for i,query in enumerate(queries):
            if query.strip():
                result=pd.read_sql_query(query,db)
                result.to_csv(out/f'query_{i+1}.csv',index=False)
                print(result.to_string(index=False))
if __name__=='__main__': main()
