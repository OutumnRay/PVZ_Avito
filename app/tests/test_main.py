from main import initialize_db


def test_initialize_db(monkeypatch):
    monkeypatch.setenv("INITIALIZE_DB", "True")

    called = {}

    def mock_init_tables():
        called["called"] = True

    monkeypatch.setattr("main.init_tables", mock_init_tables)
    initialize_db()
    assert called["called"] is True
