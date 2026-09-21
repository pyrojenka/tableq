def test_list_tables_returns_default_fixed_tables(client):
    response = client.get('/api/tables')

    assert response.status_code == 200
    tables = response.json()
    assert len(tables) == 6
    assert all(t['status'] == 'free' for t in tables)
    assert {t['id'] for t in tables} == {'t1', 't2', 't3', 't4', 't5', 't6'}


def test_confirm_table_free_on_unknown_table_is_404(client):
    response = client.post('/api/tables/does-not-exist/confirm-free')

    assert response.status_code == 404


def test_confirm_table_free_reassigns_a_waiting_guest(client, occupy_table):
    # occupy every table, including t6 (capacity 8), before the party arrives
    for table_id in ('t1', 't2', 't3', 't4', 't5', 't6'):
        occupy_table(table_id, occupied_by_guest_id='someone-else')

    big_group = client.post(
        '/api/waitlist', json={'name': 'Big Group', 'party_size': 8, 'phone': '1', 'notes': ''}
    ).json()
    assert big_group['status'] == 'waiting'

    response = client.post('/api/tables/t6/confirm-free')
    assert response.status_code == 200

    waitlist = client.get('/api/waitlist').json()
    big_group_now = next(g for g in waitlist if g['id'] == big_group['id'])
    assert big_group_now['status'] == 'table_ready'
    assert big_group_now['assigned_table_id'] == 't6'
