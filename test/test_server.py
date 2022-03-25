import re

from fastapi.testclient import TestClient

from namegen.server import app


def test_get():
    with TestClient(app) as client:
        r = client.get('/')
        assert r.status_code == 200
        assert 'value' in r.json()
        assert re.match(r'^.+#\d{4}$', r.json()['value'])


def test_import():
    from namegen.server.main import _import_driver
    from namegen import driver_memory, driver_sqlite, driver_hybrid
    assert isinstance(_import_driver('SQLite'), driver_sqlite.SQLiteDriver)
    assert isinstance(_import_driver('Memory'), driver_memory.MemoryDriver)
    assert isinstance(_import_driver('Hybrid'), driver_hybrid.HybridDriver)
    assert isinstance(_import_driver('adwadwdwadwa'), driver_hybrid.HybridDriver)
    assert isinstance(_import_driver(None), driver_hybrid.HybridDriver)
