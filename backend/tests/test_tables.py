def test_list_tables_returns_default_fixed_tables(client):
    response = client.get('/tables')

    assert response.status_code == 200
    tables = response.json()
    assert len(tables) == 6
    assert all(t['status'] == 'free' for t in tables)
    assert {t['id'] for t in tables} == {'t1', 't2', 't3', 't4', 't5', 't6'}


def test_confirm_table_free_on_unknown_table_is_404(client):
    response = client.post('/tables/does-not-exist/confirm-free')

    assert response.status_code == 404


def test_confirm_table_free_reassigns_a_waiting_guest(client, store):
    from app.models import TableStatus

    # party too big for the smallest tables, gets stuck waiting
    client.post('/waitlist', json={'name': 'Big Group', 'party_size': 8, 'phone': '1', 'notes': ''})
    # occupy every table except t6 (capacity 8) so the big group must wait for it
    for table_id in ('t1', 't2', 't3', 't4', 't5'):
        store.tables[table_id].status = TableStatus.OCCUPIED

    store.tables['t6'].status = TableStatus.OCCUPIED
    store.tables['t6'].occupied_by_guest_id = 'someone-else'

    response = client.post('/tables/t6/confirm-free')
    assert response.status_code == 200

    waitlist = client.get('/waitlist').json()
    big_group = next(g for g in waitlist if g['name'] == 'Big Group')
    assert big_group['status'] == 'table_ready'
    assert big_group['assigned_table_id'] == 't6'
