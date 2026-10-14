def test_stats_empty(client):
    body = client.get("/api/stats").json()
    assert body["total_topics"] == 0
    assert body["completion"] == 0.0
    assert body["subjects"] == []


def test_stats_summary(client, subject, make_topic):
    make_topic(title="Paging", status="done", estimated_hours=2, difficulty=4)
    make_topic(title="Deadlocks", status="in_progress", estimated_hours=3, difficulty=5)
    make_topic(title="Scheduling", estimated_hours=1.5, difficulty=2)
    make_topic(title="Syscalls", status="done", estimated_hours=0.5, difficulty=1)

    body = client.get("/api/stats").json()
    assert body["total_topics"] == 4
    assert body["done"] == 2
    assert body["in_progress"] == 1
    assert body["todo"] == 1
    assert body["completion"] == 50.0
    assert body["hours_total"] == 7.0
    assert body["hours_left"] == 4.5
    assert body["avg_difficulty"] == 3.0
    assert body["by_difficulty"]["5"] == 1

    os_progress = body["subjects"][0]
    assert os_progress["name"] == "Operating Systems"
    assert os_progress["progress"] == 50.0
    assert os_progress["hours_left"] == 4.5
