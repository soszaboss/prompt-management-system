# import json

# def test_get_note_by_id(client, valid_user_token):
#     response = client.get('/notes/note/1', headers={'Authorization': f'Bearer {valid_user_token}'})
#     assert response.status_code == 200
#     data = response.get_json()
#     assert 'note' in data


# def test_delete_note_by_id(client, valid_admin_token):
#     response = client.delete('/notes/note/1', headers={'Authorization': f'Bearer {valid_admin_token}'})
#     assert response.status_code == 200

# def test_add_note_valid(client, valid_user_token):
#     note_data = {
#         "note": 8,
#         "prompt_id": 1
#     }
#     response = client.post('/notes/note/add', data=json.dumps(note_data), content_type='application/json', headers={'Authorization': f'Bearer {valid_user_token}'})
#     assert response.status_code == 201
#     data = response.get_json()
#     assert data['message'] == 'Note added successfully'

# def test_add_note_invalid(client, valid_user_token):
#     note_data = {
#         "note": 12,  # Invalid value
#         "prompt_id": 1
#     }
#     response = client.post('/notes/note/add', data=json.dumps(note_data), content_type='application/json', headers={'Authorization': f'Bearer {valid_user_token}'})
#     assert response.status_code == 400
#     data = response.get_json()
#     assert data['message'] == 'Note must be between -10 and 10.'
