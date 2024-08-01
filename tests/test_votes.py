def test_get_vote(client, valid_user_token):
    response = client.get('/votes/vote/1', headers={'Authorization': f'Bearer {valid_user_token}'})
    assert response.status_code == 200

def test_add_vote(client, valid_user_token):
    data = {'prompt_id': 2}
    response = client.post('/votes/add/vote', json=data, headers={'Authorization': f'Bearer {valid_user_token}'})
    assert response.status_code == 201

def test_delete_vote(client, valid_user_token):
    response = client.delete('/votes/vote/1', headers={'Authorization': f'Bearer {valid_user_token}'})
    assert response.status_code == 200

def test_get_votes(client, valid_user_token, monkeypatch, mock_db):

    def mock_votes():
        return [
            {'id': 1, 'username': 'user1', 'prompt_id': 101, 'prompt': 'First prompt'},
            {'id': 2, 'username': 'user2', 'prompt_id': 102, 'prompt': 'Second prompt'}
        ]

    monkeypatch.setattr('app.votes.views.get_votes', mock_votes)
    response = client.get('/votes/', headers={'Authorization': f'Bearer {valid_user_token}'})
    assert response.status_code == 200
