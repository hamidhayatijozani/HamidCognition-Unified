import storage


def test_rate_limit_is_durable(tmp_path):
    storage.SQLITE_PATH = str(tmp_path / "rate.db")
    storage.DATABASE_URL = None
    storage.init_db()

    assert storage.allow_rate_limit("tenant-a:token", 2, 60, 1000.0)
    assert storage.allow_rate_limit("tenant-a:token", 2, 60, 1001.0)
    assert not storage.allow_rate_limit("tenant-a:token", 2, 60, 1002.0)
    assert storage.allow_rate_limit("tenant-a:token", 2, 60, 1061.0)


def test_rate_limits_are_tenant_keyed(tmp_path):
    storage.SQLITE_PATH = str(tmp_path / "rate.db")
    storage.DATABASE_URL = None
    storage.init_db()

    assert storage.allow_rate_limit("tenant-a:token", 1, 60, 1000.0)
    assert storage.allow_rate_limit("tenant-b:token", 1, 60, 1000.0)
