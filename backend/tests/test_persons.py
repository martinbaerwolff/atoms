import uuid


def test_create_person(client):
    resp = client.post("/persons/", json={"name": "Anna Müller"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Anna Müller"
    assert data["organizations"] == []
    assert data["photo_url"] is None
    assert "id" in data


def test_create_person_with_org(client):
    resp = client.post("/persons/", json={"name": "Bob", "organizations": ["Platomo", "TUD"]})
    assert resp.status_code == 201
    assert resp.json()["organizations"] == ["Platomo", "TUD"]


def test_list_persons(client):
    client.post("/persons/", json={"name": "Anna"})
    client.post("/persons/", json={"name": "Bob"})
    resp = client.get("/persons/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_person(client):
    created = client.post("/persons/", json={"name": "Anna"}).json()
    resp = client.get(f"/persons/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Anna"


def test_update_person(client):
    created = client.post("/persons/", json={"name": "Anna"}).json()
    resp = client.patch(f"/persons/{created['id']}", json={"name": "Anna M.", "organizations": ["Platomo"]})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Anna M."
    assert resp.json()["organizations"] == ["Platomo"]


def test_delete_person(client):
    created = client.post("/persons/", json={"name": "Anna"}).json()
    del_resp = client.delete(f"/persons/{created['id']}")
    assert del_resp.status_code == 204
    get_resp = client.get(f"/persons/{created['id']}")
    assert get_resp.status_code == 404


def test_get_nonexistent_person(client):
    resp = client.get(f"/persons/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_deleted_persons_excluded_from_list(client):
    created = client.post("/persons/", json={"name": "Anna"}).json()
    client.delete(f"/persons/{created['id']}")
    resp = client.get("/persons/")
    assert all(p["id"] != created["id"] for p in resp.json())
