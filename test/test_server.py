import re

from fastapi.testclient import TestClient

from namegen.server import app


def test_get():
    with TestClient(app) as client:
        r = client.get('/')
        assert r.status_code == 200
        assert 'value' in r.json()
        assert re.match(r'^.+#\d{4}$', r.json()['value'])
