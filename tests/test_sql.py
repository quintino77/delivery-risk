from pathlib import Path
import sqlite3
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def test_sql_queries_preserve_order_total():
    source=pd.read_csv(ROOT/'artifacts/dashboard.csv.gz')
    text=(ROOT/'sql/analysis.sql').read_text()
    queries='\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('--')).split(';')
    with sqlite3.connect(':memory:') as db:
        source.to_sql('orders',db,index=False)
        results=[pd.read_sql_query(q,db) for q in queries if q.strip()]
    assert len(results)==3
    assert results[0].orders.sum()==len(source)
    assert all(not result.empty for result in results)
