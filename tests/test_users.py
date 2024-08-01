def test_get_user(client, valid_admin_token):
    response = client.get('/users/user/2', headers={'Authorization': f'Bearer {valid_admin_token}'})
    assert response.status_code == 200

def test_update_user(client, valid_user_token):
    data = {'username': 'user1', 'email': 'user1@example.com'}
    response = client.put('/users/user/2', json=data, headers={'Authorization': f'Bearer {valid_user_token}'})
    assert response.status_code == 200

def test_delete_user(client, valid_user_token):
    response = client.delete('/users/user/2', headers={'Authorization': f'Bearer {valid_user_token}'})
    assert response.status_code == 200

def test_get_users(client, valid_admin_token):
    response = client.get('/users/', headers={'Authorization': f'Bearer {valid_admin_token}'})
    assert response.status_code == 200