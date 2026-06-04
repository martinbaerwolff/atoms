import uuid
from datetime import UTC, datetime


def make_person(client, name="Anna"):
    return client.post("/persons/", json={"name": name}).json()


def make_project(client, name="CRM"):
    return client.post("/projects/", json={"name": name}).json()


def test_create_note(client):
    resp = client.post("/atoms/", json={"title": "Kundengespräch", "type": "note"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Kundengespräch"
    assert data["type"] == "note"
    assert data["captured"] is False
    assert data["content"] == ""
    assert data["responsible"] == []
    assert data["participants"] == []
    assert data["projects"] == []


def test_create_task_with_all_fields(client):
    person = make_person(client)
    project = make_project(client)
    resp = client.post("/atoms/", json={
        "title": "Report schreiben",
        "type": "task",
        "status": "open",
        "priority": "high",
        "complexity": "deep",
        "deadline_date": "2026-07-01T12:00:00Z",
        "responsible_ids": [person["id"]],
        "project_ids": [project["id"]],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "open"
    assert data["priority"] == "high"
    assert data["complexity"] == "deep"
    assert len(data["responsible"]) == 1
    assert data["responsible"][0]["name"] == "Anna"
    assert len(data["projects"]) == 1


def test_list_atoms(client):
    client.post("/atoms/", json={"title": "A", "type": "note"})
    client.post("/atoms/", json={"title": "B", "type": "thought"})
    resp = client.get("/atoms/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_atom(client):
    created = client.post("/atoms/", json={"title": "Test", "type": "decision"}).json()
    resp = client.get(f"/atoms/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test"


def test_update_atom_title(client):
    created = client.post("/atoms/", json={"title": "Alt", "type": "note"}).json()
    resp = client.patch(f"/atoms/{created['id']}", json={"title": "Neu"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Neu"


def test_update_captured(client):
    created = client.post("/atoms/", json={"title": "Inbox item", "type": "thought"}).json()
    assert created["captured"] is False
    resp = client.patch(f"/atoms/{created['id']}", json={"captured": True})
    assert resp.status_code == 200
    assert resp.json()["captured"] is True


def test_update_relations(client):
    person = make_person(client, "Bob")
    project = make_project(client, "Infra")
    created = client.post("/atoms/", json={"title": "X", "type": "task"}).json()
    resp = client.patch(f"/atoms/{created['id']}", json={
        "participant_ids": [person["id"]],
        "project_ids": [project["id"]],
    })
    assert resp.status_code == 200
    assert len(resp.json()["participants"]) == 1
    assert len(resp.json()["projects"]) == 1


def test_delete_atom(client):
    created = client.post("/atoms/", json={"title": "Temp", "type": "note"}).json()
    assert client.delete(f"/atoms/{created['id']}").status_code == 204
    assert client.get(f"/atoms/{created['id']}").status_code == 404


def test_deleted_excluded_from_list(client):
    created = client.post("/atoms/", json={"title": "X", "type": "note"}).json()
    client.delete(f"/atoms/{created['id']}")
    resp = client.get("/atoms/")
    assert all(a["id"] != created["id"] for a in resp.json())


def test_filter_by_type(client):
    client.post("/atoms/", json={"title": "N", "type": "note"})
    client.post("/atoms/", json={"title": "T", "type": "task"})
    resp = client.get("/atoms/?type=note")
    assert resp.status_code == 200
    assert all(a["type"] == "note" for a in resp.json())


def test_filter_inbox(client):
    client.post("/atoms/", json={"title": "Uncaptured", "type": "note"})
    captured = client.post("/atoms/", json={"title": "Captured", "type": "note"}).json()
    client.patch(f"/atoms/{captured['id']}", json={"captured": True})
    resp = client.get("/atoms/?filter_badge=inbox")
    assert resp.status_code == 200
    assert all(a["captured"] is False for a in resp.json())


def test_filter_overdue(client):
    resp = client.post("/atoms/", json={
        "title": "Overdue task",
        "type": "task",
        "status": "open",
        "deadline_date": "2020-01-01T00:00:00Z",
    })
    assert resp.status_code == 201
    result = client.get("/atoms/?filter_badge=overdue").json()
    assert any(a["title"] == "Overdue task" for a in result)


def test_get_nonexistent_atom(client):
    assert client.get(f"/atoms/{uuid.uuid4()}").status_code == 404
