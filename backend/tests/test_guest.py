def test_guest_can_look_up_their_own_status_by_token(client):
    created = client.post(
        '/api/waitlist', json={'name': 'Alice', 'party_size': 2, 'phone': '1', 'notes': ''}
    ).json()

    response = client.get(f"/api/guest/{created['token']}")

    assert response.status_code == 200
    guest = response.json()
    assert guest['id'] == created['id']
    assert guest['status'] == 'table_ready'


def test_unknown_token_is_404(client):
    response = client.get('/api/guest/does-not-exist')

    assert response.status_code == 404
