def test_get_prompt(client, valid_user_token):
    response = client.get('/prompts/prompt/1', headers={'Authorization': f'Bearer {valid_user_token}'})
    assert response.status_code == 200

def test_update_prompt(client, valid_user_token):
    data = {'prompt': 'New Prompt', 'statut_id': 2, 'prix': 5000}
    response = client.put('/prompts/prompt/1', json=data, headers={'Authorization': f'Bearer {valid_user_token}'})
    assert response.status_code == 200

def test_delete_prompt(client, valid_admin_token):
    response = client.delete('/prompts/prompt/1', headers={'Authorization': f'Bearer {valid_admin_token}'})
    assert response.status_code == 200

def test_get_prompts_by_status(client, valid_admin_token):
    response = client.get('/prompts/status/1', headers={'Authorization': f'Bearer {valid_admin_token}'})
    assert response.status_code == 200

def test_get_prompts_by_user(client, valid_admin_token):
    response = client.get('/prompts/user/2', headers={'Authorization': f'Bearer {valid_admin_token}'})
    assert response.status_code == 200

def test_add_prompt(client, valid_admin_token):
    data = {'prompt': 'Test Prompt', 'statut_id': 1, 'prix': 1000}
    response = client.post('/prompts/prompt/add', json=data, headers={'Authorization': f'Bearer {valid_admin_token}'})
    assert response.status_code == 201
