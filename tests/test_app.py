from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]

def test_app_pages_and_simulator():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    assert not app.exception
    assert len(app.metric)==4
    for page in ['Explorar entregas','Desempenho do modelo','Sobre o projeto','Simular pedido']:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page
    app.button[0].click().run()
    assert not app.exception
    assert len(app.metric)==1

def test_empty_filter_graceful():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    app.multiselect[0].set_value(['RR']).run()
    app.multiselect[1].set_value(['seguros_e_servicos']).run()
    assert not app.exception
    assert len(app.info)>=1
