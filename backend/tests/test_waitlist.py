def test_add_guest_gets_matched_to_a_free_table_immediately(client):
    response = client.post(
        '/waitlist',
        json={'name': 'Alice', 'party_size': 2, 'phone': '555-1', 'notes': 'window seat'},
    )

    assert response.status_code == 201
    guest = response.json()
    assert guest['name'] == 'Alice'
    assert guest['status'] == 'table_ready'
    assert guest['assigned_table_id'] in ('t1', 't2')
    assert guest['token']


def test_add_guest_waits_when_no_table_fits(client, occupy_all_tables):
    occupy_all_tables()

    response = client.post('/waitlist', json={'name': 'C', 'party_size': 2, 'phone': '3', 'notes': ''})
    guest = response.json()

    assert guest['status'] == 'waiting'
    assert guest['estimated_wait_minutes'] > 0


def test_larger_party_is_prioritized_over_earlier_smaller_party(client, occupy_all_tables):
    occupy_all_tables()

    small = client.post(
        '/waitlist', json={'name': 'Small', 'party_size': 2, 'phone': '1', 'notes': ''}
    ).json()
    big = client.post(
        '/waitlist', json={'name': 'Big', 'party_size': 4, 'phone': '2', 'notes': ''}
    ).json()
    assert small['status'] == 'waiting'
    assert big['status'] == 'waiting'

    # a 4-top opens up; both parties would fit, but the larger one goes first
    client.post('/tables/t3/confirm-free')

    listed = {g['id']: g for g in client.get('/waitlist').json()}
    assert listed[big['id']]['status'] == 'table_ready'
    assert listed[big['id']]['assigned_table_id'] == 't3'
    assert listed[small['id']]['status'] == 'waiting'


def test_list_waitlist_returns_guests_in_creation_order(client):
    client.post('/waitlist', json={'name': 'First', 'party_size': 2, 'phone': '1', 'notes': ''})
    client.post('/waitlist', json={'name': 'Second', 'party_size': 2, 'phone': '2', 'notes': ''})

    names = [g['name'] for g in client.get('/waitlist').json()]
    assert names == ['First', 'Second']


def test_seat_guest_transitions_status(client):
    guest = client.post(
        '/waitlist', json={'name': 'Alice', 'party_size': 2, 'phone': '1', 'notes': ''}
    ).json()
    assert guest['status'] == 'table_ready'

    response = client.post(f"/waitlist/{guest['id']}/seat")

    assert response.status_code == 200
    assert response.json()['status'] == 'seated'


def test_seat_guest_not_ready_yet_is_conflict(client, occupy_all_tables):
    occupy_all_tables()

    waiting_guest = client.post(
        '/waitlist', json={'name': 'C', 'party_size': 2, 'phone': '3', 'notes': ''}
    ).json()
    assert waiting_guest['status'] == 'waiting'

    response = client.post(f"/waitlist/{waiting_guest['id']}/seat")

    assert response.status_code == 409


def test_seat_unknown_guest_is_404(client):
    response = client.post('/waitlist/does-not-exist/seat')

    assert response.status_code == 404


def test_cancel_guest_frees_up_the_table_for_the_next_waiting_guest(client, occupy_all_tables):
    occupy_all_tables(except_ids=('t1',))

    first = client.post(
        '/waitlist', json={'name': 'First', 'party_size': 2, 'phone': '1', 'notes': ''}
    ).json()
    assert first['status'] == 'table_ready'
    assert first['assigned_table_id'] == 't1'

    second = client.post(
        '/waitlist', json={'name': 'Second', 'party_size': 2, 'phone': '2', 'notes': ''}
    ).json()
    third = client.post(
        '/waitlist', json={'name': 'Third', 'party_size': 2, 'phone': '3', 'notes': ''}
    ).json()
    assert second['status'] == 'waiting'
    assert third['status'] == 'waiting'

    response = client.post(f"/waitlist/{first['id']}/cancel")
    assert response.status_code == 200
    assert response.json()['status'] == 'cancelled_no_show'

    listed = {g['id']: g for g in client.get('/waitlist').json()}
    # same party size for both, so the earlier arrival (Second) gets the table
    assert listed[second['id']]['status'] == 'table_ready'
    assert listed[second['id']]['assigned_table_id'] == 't1'
    assert listed[third['id']]['status'] == 'waiting'


def test_cancel_unknown_guest_is_404(client):
    response = client.post('/waitlist/does-not-exist/cancel')

    assert response.status_code == 404
