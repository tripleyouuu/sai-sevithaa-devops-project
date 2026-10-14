def test_create_topic_defaults(make_topic):
    topic = make_topic()
    assert topic["status"] == "todo"
    assert topic["difficulty"] == 3
    assert topic["completed_at"] is None


def test_create_topic_needs_existing_subject(client):
    res = client.post("/api/topics", json={"subject_id": 999, "title": "Orphan"})
    assert res.status_code == 400


def test_difficulty_must_be_between_1_and_5(client, subject):
    res = client.post("/api/topics", json={"subject_id": subject["id"], "title": "Hard", "difficulty": 9})
    assert res.status_code == 422


def test_marking_done_sets_completed_at(client, make_topic):
    topic = make_topic()

    done = client.put(f"/api/topics/{topic['id']}", json={"status": "done"}).json()
    assert done["status"] == "done"
    assert done["completed_at"] is not None

    reopened = client.put(f"/api/topics/{topic['id']}", json={"status": "in_progress"}).json()
    assert reopened["completed_at"] is None


def test_filter_topics_by_status(client, make_topic):
    make_topic(title="Threads", status="in_progress")
    make_topic(title="Semaphores")
    make_topic(title="File systems", status="done")

    res = client.get("/api/topics", params={"status": "in_progress"})
    assert [t["title"] for t in res.json()] == ["Threads"]


def test_search_topics(client, make_topic):
    make_topic(title="Virtual memory")
    make_topic(title="Memory allocation")
    make_topic(title="Interrupts")

    res = client.get("/api/topics", params={"search": "memory"})
    assert len(res.json()) == 2


def test_delete_topic(client, make_topic):
    topic = make_topic()
    assert client.delete(f"/api/topics/{topic['id']}").status_code == 204
    assert client.get(f"/api/topics/{topic['id']}").status_code == 404
    assert client.delete(f"/api/topics/{topic['id']}").status_code == 404
