def test_stats_start_at_zero(client):
    response = client.get('/api/stats')

    assert response.status_code == 200
    assert response.json() == {
        'total_seated': 0,
        'total_no_show': 0,
        'average_wait_minutes': 15,
    }


def test_stats_count_seated_and_no_show(client):
    seated = client.post(
        '/api/waitlist', json={'name': 'Seated', 'party_size': 2, 'phone': '1', 'notes': ''}
    ).json()
    cancelled = client.post(
        '/api/waitlist', json={'name': 'Cancelled', 'party_size': 2, 'phone': '2', 'notes': ''}
    ).json()

    client.post(f"/api/waitlist/{seated['id']}/seat")
    client.post(f"/api/waitlist/{cancelled['id']}/cancel")

    stats = client.get('/api/stats').json()
    assert stats['total_seated'] == 1
    assert stats['total_no_show'] == 1
