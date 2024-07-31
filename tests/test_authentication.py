from flask import url_for

def test_register_success(client):

    response = client.post(url_for('auth.register'), json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Azertyuiop@12',
        'confirm_password': 'Azertyuiop@12'
    })

    assert response.status_code == 201
    assert b'Account created successfully' in response.data


def test_register_password_mismatch(client):
    response = client.post(url_for('auth.register'), json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Azertyuiop@12',
        'confirm_password': 'Password1234!'
    })

    assert response.status_code == 409
    assert b'Password not conforme' in response.data

def test_register_existing_email(client):

    response = client.post(url_for('auth.register'), json={
        'username': 'user1',
        'email': 'test@example.com',
        'password': 'Azertyuiop@12',
        'confirm_password': 'Azertyuiop@12'
    })

    assert response.status_code == 409
    assert b'Username already used.' in response.data

def test_register_existing_username(client):

    response = client.post(url_for('auth.register'), json={
        'username': 'testuser',
        'email': 'user1@example.com',
        'password': 'Azertyuiop@12',
        'confirm_password': 'Azertyuiop@12'
    })

    assert response.status_code == 409
    assert b'Email already used' in response.data

def test_login_success(client, create_test_user):

    response_login = client.post(url_for('auth.login'), json={
        'email': 'test@example.com',
        'password': 'Azertyuiop@12'
    })

    assert response_login.status_code == 200
    assert b'tokens' in response_login.data
def test_login_success(client, create_test_user):


    response_login = client.post(url_for('auth.login'), json={
        'email': 'test@example.com',
        'password': 'Azertyuiop@12'
    })
    assert response_login.status_code == 200
    assert b'tokens' in response_login.data
def test_login_success(client, create_test_user):


    response_login = client.post(url_for('auth.login'), json={
        'email': 'test@example.com',
        'password': 'Azertyuiop@12'
    })
    assert response_login.status_code == 200
    assert b'tokens' in response_login.data

def test_login_invalid_password(client, create_test_user):


    response_login = client.post(url_for('auth.login'), json={
        'email': 'test@example.com',
        'password': 'WrongPassword'
    })
    assert response_login.status_code == 401
    assert b'Invalid password' in response_login.data

def test_login_user_not_exist(client, create_test_user):


    response_login = client.post(url_for('auth.login'), json={
        'email': 'nonexistent@example.com',
        'password': 'Azertyuiop@12'
    })
    assert response_login.status_code == 404
    assert b'User does not exist' in response_login.data
