import os
import pytest
from app import create_app
from app.db import get_db, init_db
from dotenv import load_dotenv
from unittest.mock import MagicMock
from werkzeug.security import generate_password_hash
from flask import url_for
from app.extensions import jwt


load_dotenv()

with open('./app/schema.sql', 'rb') as f:
    _data_schema = f.read().decode('utf-8')

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf-8')


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE': os.environ.get('CONNINFOTEST'),
        'SERVER_NAME': 'localhost'
    })

    with app.app_context():
        init_db()
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(_data_schema)
            cur.execute(_data_sql)

            """Hash the password for the first you will run the test
                for i in range(5):
                    cur.execute("UPDATE users SET password = %s WHERE id = %s;", (generate_password_hash('Azertyuiop@12') ,i))  
            """
            conn.commit()
        yield app
    

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def mock_db(monkeypatch):

    def mock_get_db():
        return MagicMock()

    monkeypatch.setattr('app.db.get_db', mock_get_db)
    return MagicMock()

@pytest.fixture
def send_activation_email(monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('app.authentification.views.send_activation_email', mock_send_email)
    return mock_send_email

@pytest.fixture
def create_test_user(client):
    response = client.post(url_for('auth.register'), json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Azertyuiop@12',
        'confirm_password': 'Azertyuiop@12'
    })
    assert response.status_code == 201
    return response

import pytest
from flask_jwt_extended import create_access_token

@pytest.fixture
def valid_admin_token():
    user = 1
    additional_claims = {"user_role": "admin"}
    token = create_access_token(identity=user, additional_claims=additional_claims)
    return token
@pytest.fixture
def valid_user_token():
    user = 2
    additional_claims = {"user_role": "user"}
    token = create_access_token(identity=user, additional_claims=additional_claims)
    return token
