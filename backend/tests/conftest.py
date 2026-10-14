import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, _):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def subject(client):
    res = client.post("/api/subjects", json={"name": "Operating Systems", "code": "CS301", "color": "#0ea5e9"})
    assert res.status_code == 201
    return res.json()


@pytest.fixture()
def make_topic(client, subject):
    def _make(**overrides):
        payload = {"subject_id": subject["id"], "title": "Process scheduling", **overrides}
        res = client.post("/api/topics", json=payload)
        assert res.status_code == 201, res.text
        return res.json()

    return _make
