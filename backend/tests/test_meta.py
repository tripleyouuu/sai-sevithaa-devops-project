def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_ready_checks_database(client):
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.json()["database"] == "ok"


def test_metrics_exposed(client):
    client.get("/api/subjects")
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "http_requests_total" in res.text
