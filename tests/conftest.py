import os
import pytest
from app import create_app
from app.db import get_db, init_db
from dotenv import load_dotenv


load_dotenv()

with open('app\schema.sql', 'rb') as f:
    _data_schema = f.read().decode('utf-8')

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf-8')

@pytest.fixture
def app():
    
    app = create_app({
        'TESTING': True,
        'DATABASE': os.environ.get('CONNINFOTEST')
    })

    with app.app_context():
        init_db()
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(_data_schema)
            cur.execute(_data_sql)
            conn.commit()
    
    yield app


@pytest.fixture
def client(app):
    """
    The client fixture calls app.test_client()
    with the application object created by the app fixture.
    Tests will use the client to make requests to the application without running the server.
    """
    
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    The runner fixture is similar to client.
    app.test_cli_runner() creates a runner that can call the Click commands registered with the application.
    """
    
    return app.test_cli_runner()
