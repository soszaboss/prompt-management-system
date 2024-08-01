import json

def test_get_groupe(client, valid_admin_token):
    response = client.get('/groupes/groupe/1', headers={'Authorization': f'Bearer {valid_admin_token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'id' in data
    assert 'name' in data
    
def test_get_nonexistent_groupe(client, valid_admin_token):
    response = client.get('/groupes/groupe/999', headers={'Authorization': f'Bearer {valid_admin_token}'})
    assert response.status_code == 404

def test_delete_groupe(client, valid_admin_token):
    response = client.delete('/groupes/groupe/1', headers={'Authorization': f'Bearer {valid_admin_token}'})
    print(f'Response status code: {response.status_code}')
    print(f'Response data: {response.data}')
    assert response.status_code == 200



def test_delete_nonexistent_groupe(client, valid_admin_token):
    response = client.delete('/groupes/groupe/999', headers={'Authorization': f'Bearer {valid_admin_token}'})
    assert response.status_code == 404

def test_put_groupe(client, valid_admin_token):
    update_data = {
        "name": "New Group Name",
        "description": "Updated Description"
    }
    response = client.put('/groupes/groupe/1', data=json.dumps(update_data),  headers={'Authorization': f'Bearer {valid_admin_token}'})
    assert response.status_code == 200
