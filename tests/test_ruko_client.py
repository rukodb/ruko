from uuid import uuid4

from ruko import RDict, RukoClient


def test_ruko():
    rk = RDict(None, RukoClient('127.0.0.1', 8080))
    rk.clear()
    for location in dict(rk.get_mappings()):
        rk.delete_mapping(location)
    assert rk.get() == {}

    users = rk['users']
    devices = rk.create_mapping('devices', 'users.*.devices.*')
    auths = rk.create_mapping('auths', ['users.*.auth', 'users.*.devices.*.auth'])

    raw_users = []
    for i in range(10):
        user = {
            'uuid': str(uuid4()),
            'name': 'user-{}'.format(i),
            'devices': [
                {
                    'uuid': str(uuid4()),
                    'name': 'device-{}-{}'.format(i, j),
                    'auth': {
                        'token': str(uuid4()),
                        'refresh': str(uuid4())
                    }
                } for j in range(3)
            ],
            'auth': {
                'token': str(uuid4()),
                'refresh': str(uuid4())
            }
        }
        raw_users.append(user)
        users.append(user)

    for i, raw_user in enumerate(raw_users):
        assert users.by('uuid')[raw_user['uuid']][()] == raw_user
        assert users.by('name')[raw_user['name']][()] == raw_user
        assert users[i][()] == raw_user

    del users[1]
    assert users.by('uuid').get(raw_users[1]['uuid']) is None
    del raw_users[1]

    for i, raw_user in enumerate(raw_users):
        assert users.by('uuid')[raw_user['uuid']][()] == raw_user
        assert users.by('name')[raw_user['name']][()] == raw_user
        assert users[i][()] == raw_user

    assert users.by('uuid')[raw_users[0]['uuid']][...] == users.get()

    for user in raw_users:
        assert auths.by('token')[user['auth']['token']][()] == user['auth']
        for device in user['devices']:
            assert devices.by('uuid')[device['uuid']][()] == device
            assert auths.by('token')[device['auth']['token']][()] == device['auth']
