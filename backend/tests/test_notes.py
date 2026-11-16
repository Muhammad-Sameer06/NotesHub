def make(client, title="Note", content="", tags=None):
    r = client.post("/api/notes", json={"title": title, "content": content, "tags": tags or []})
    assert r.status_code == 201, r.text
    return r.json()


def test_create_and_get(client):
    note = make(client, "Learn Docker", "images vs containers", [" DevOps", "devops", "Docker"])
    assert note["id"] > 0
    assert note["tags"] == ["devops", "docker"]  # trimmed, lowercased, de-duplicated

    r = client.get(f"/api/notes/{note['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Learn Docker"


def test_list(client):
    make(client, "A")
    make(client, "B")
    r = client.get("/api/notes")
    assert r.status_code == 200
    assert {n["title"] for n in r.json()} == {"A", "B"}


def test_search_title_and_content(client):
    make(client, "Kubernetes basics", "pods and services")
    make(client, "Shopping", "milk, eggs")
    make(client, "Infra", "learn KUBERNETES with kind")
    titles = {n["title"] for n in client.get("/api/notes", params={"search": "kubernetes"}).json()}
    assert titles == {"Kubernetes basics", "Infra"}  # case-insensitive, title OR content


def test_search_treats_percent_literally(client):
    make(client, "Discount", "50% off")
    make(client, "Other", "500 items")
    titles = {n["title"] for n in client.get("/api/notes", params={"search": "50%"}).json()}
    assert titles == {"Discount"}


def test_filter_by_tag(client):
    make(client, "One", tags=["work"])
    make(client, "Two", tags=["home"])
    make(client, "Three", tags=["work", "urgent"])
    titles = {n["title"] for n in client.get("/api/notes", params={"tag": "WORK"}).json()}
    assert titles == {"One", "Three"}


def test_update_partial(client):
    note = make(client, "Old", "keep me", ["a"])
    r = client.patch(f"/api/notes/{note['id']}", json={"title": "New", "tags": ["b", "c"]})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "New"
    assert body["content"] == "keep me"  # untouched
    assert body["tags"] == ["b", "c"]


def test_delete(client):
    note = make(client)
    assert client.delete(f"/api/notes/{note['id']}").status_code == 204
    assert client.get(f"/api/notes/{note['id']}").status_code == 404


def test_not_found(client):
    assert client.get("/api/notes/999").status_code == 404
    assert client.patch("/api/notes/999", json={"title": "x"}).status_code == 404
    assert client.delete("/api/notes/999").status_code == 404


def test_validation_errors(client):
    assert client.post("/api/notes", json={"title": ""}).status_code == 422
    assert client.post("/api/notes", json={"title": "x" * 201}).status_code == 422
    assert client.post("/api/notes", json={"title": "ok", "tags": ["t"] * 11}).status_code == 422
    assert client.get("/api/notes", params={"limit": 0}).status_code == 422
