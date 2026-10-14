def test_create_and_list_subjects(client):
    client.post("/api/subjects", json={"name": "Linear Algebra"})
    client.post("/api/subjects", json={"name": "Computer Networks", "code": "CS302"})

    res = client.get("/api/subjects")
    assert res.status_code == 200
    names = [s["name"] for s in res.json()]
    assert names == ["Computer Networks", "Linear Algebra"]


def test_subject_rejects_bad_color(client):
    res = client.post("/api/subjects", json={"name": "Physics", "color": "blue"})
    assert res.status_code == 422


def test_update_subject(client, subject):
    res = client.put(f"/api/subjects/{subject['id']}", json={"exam_date": "2026-12-05"})
    assert res.status_code == 200
    assert res.json()["exam_date"] == "2026-12-05"
    assert res.json()["name"] == "Operating Systems"


def test_subject_progress_counts(client, subject, make_topic):
    make_topic(title="Paging", status="done")
    make_topic(title="Deadlocks")

    res = client.get(f"/api/subjects/{subject['id']}")
    body = res.json()
    assert body["topic_count"] == 2
    assert body["done_count"] == 1
    assert body["progress"] == 50.0


def test_deleting_subject_removes_its_topics(client, subject, make_topic):
    topic = make_topic()

    assert client.delete(f"/api/subjects/{subject['id']}").status_code == 204
    assert client.get(f"/api/subjects/{subject['id']}").status_code == 404
    assert client.get(f"/api/topics/{topic['id']}").status_code == 404
