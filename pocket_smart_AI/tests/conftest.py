import os

os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["GEMINI_API_KEY"] = ""

import pytest
from fastapi.testclient import TestClient

from app.db import DB_PATH, init_db
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):

    import app.db as db_module

    test_db = tmp_path / "test.db"

    monkeypatch.setattr(
        db_module,
        "DB_PATH",
        test_db,
    )

    init_db()

    with TestClient(app) as test_client:
        yield test_client