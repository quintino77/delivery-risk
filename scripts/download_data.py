"""Download the official public dataset; no credentials embedded."""
from pathlib import Path
import urllib.request
import zipfile
import tempfile

URL='https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce'
def main():
    target=Path('data/raw');target.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        archive=Path(tmp)/'olist.zip'
        print('Baixando Olist / Kaggle...')
        try:
            urllib.request.urlretrieve(URL,archive)
            with zipfile.ZipFile(archive) as z:
                for entry in z.infolist():
                    # Only flat CSV files, never trust archive paths.
                    if entry.filename.endswith('.csv') and '/' not in entry.filename and '\\' not in entry.filename:
                        (target/entry.filename).write_bytes(z.read(entry))
        except Exception as exc:
            raise SystemExit('Falha no download. Baixe manualmente no Kaggle e extraia os CSVs em data/raw. '+str(exc))
    print('Dados salvos em data/raw. Licença dos dados: CC BY-NC-SA 4.0; veja DATA_LICENSE.md.')
if __name__=='__main__': main()
