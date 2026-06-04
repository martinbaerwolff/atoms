import uuid


def test_create_project(client):
    resp = client.post("/projects/", json={"name": "CRM", "color": "#10B981", "icon": "🏢"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "CRM"
    assert data["color"] == "#10B981"
    assert data["icon"] == "🏢"


def test_create_project_minimal(client):
    resp = client.post("/projects/", json={"name": "Infrastruktur"})
    assert resp.status_code == 201
    assert resp.json()["color"] is None
    assert resp.json()["icon"] is None


def test_list_projects(client):
    client.post("/projects/", json={"name": "A"})
    client.post("/projects/", json={"name": "B"})
    resp = client.get("/projects/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_project(client):
    created = client.post("/projects/", json={"name": "Alt"}).json()
    resp = client.patch(f"/projects/{created['id']}", json={"name": "Neu", "color": "#FF0000"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Neu"
    assert resp.json()["color"] == "#FF0000"


def test_delete_project(client):
    created = client.post("/projects/", json={"name": "Temp"}).json()
    assert client.delete(f"/projects/{created['id']}").status_code == 204
    assert client.get(f"/projects/{created['id']}").status_code == 404


def test_get_nonexistent_project(client):
    assert client.get(f"/projects/{uuid.uuid4()}").status_code == 404
