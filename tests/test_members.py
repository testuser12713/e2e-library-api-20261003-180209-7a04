def _headers(api_key):
    return {"X-API-Key": api_key}


def _create_member(client, api_key, name="Alice", email="alice@example.com"):
    return client.post(
        "/members",
        json={"name": name, "email": email},
        headers=_headers(api_key),
    )


def test_create_member(client, api_key):
    resp = _create_member(client, api_key)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"
    assert body["id"] == 1
    assert "joined_at" in body


def test_list_members(client, api_key):
    _create_member(client, api_key, name="Alice", email="alice@example.com")
    _create_member(client, api_key, name="Bob", email="bob@example.com")
    resp = client.get("/members")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    assert {m["email"] for m in body} == {"alice@example.com", "bob@example.com"}


def test_get_member(client, api_key):
    created = _create_member(client, api_key).json()
    resp = client.get(f"/members/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


def test_get_member_404(client, api_key):
    resp = client.get("/members/999")
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "not_found"


def test_update_member_put(client, api_key):
    created = _create_member(client, api_key).json()
    resp = client.put(
        f"/members/{created['id']}",
        json={"name": "Alicia"},
        headers=_headers(api_key),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alicia"
    assert resp.json()["email"] == "alice@example.com"


def test_update_member_patch(client, api_key):
    created = _create_member(client, api_key).json()
    resp = client.patch(
        f"/members/{created['id']}",
        json={"email": "new@example.com"},
        headers=_headers(api_key),
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "new@example.com"
    assert resp.json()["name"] == "Alice"


def test_delete_member(client, api_key):
    created = _create_member(client, api_key).json()
    resp = client.delete(f"/members/{created['id']}", headers=_headers(api_key))
    assert resp.status_code == 204
    assert client.get(f"/members/{created['id']}").status_code == 404


def test_create_duplicate_email(client, api_key):
    _create_member(client, api_key)
    resp = _create_member(client, api_key, name="Alice Two")
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "conflict"


def test_update_duplicate_email(client, api_key):
    _create_member(client, api_key, name="Alice", email="alice@example.com")
    second = _create_member(client, api_key, name="Bob", email="bob@example.com").json()
    resp = client.patch(
        f"/members/{second['id']}",
        json={"email": "alice@example.com"},
        headers=_headers(api_key),
    )
    assert resp.status_code == 409


def test_update_member_404(client, api_key):
    resp = client.put("/members/999", json={"name": "Nobody"}, headers=_headers(api_key))
    assert resp.status_code == 404


def test_delete_member_404(client, api_key):
    resp = client.delete("/members/999", headers=_headers(api_key))
    assert resp.status_code == 404


def test_reads_open_without_key(client, api_key):
    assert client.get("/members").status_code == 200
    assert client.get("/members/999").status_code == 404


def test_create_without_api_key_401(client, api_key):
    resp = client.post("/members", json={"name": "Alice", "email": "alice@example.com"})
    assert resp.status_code == 401


def test_create_wrong_api_key_401(client, api_key):
    resp = client.post(
        "/members",
        json={"name": "Alice", "email": "alice@example.com"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code == 401


def test_put_without_api_key_401(client, api_key):
    resp = client.put("/members/1", json={"name": "Alice"})
    assert resp.status_code == 401


def test_patch_wrong_api_key_401(client, api_key):
    resp = client.patch("/members/1", json={"name": "Alice"}, headers={"X-API-Key": "wrong-key"})
    assert resp.status_code == 401


def test_delete_without_api_key_401(client, api_key):
    resp = client.delete("/members/1")
    assert resp.status_code == 401
