from app.config import settings


def _auth() -> dict[str, str]:
    return {"X-API-Key": settings.api_key}


def _book_payload(**overrides) -> dict:
    payload = {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "978-0132350884",
        "publication_year": 2008,
        "total_copies": 3,
    }
    payload.update(overrides)
    return payload


def _create(client, **overrides):
    return client.post("/books", json=_book_payload(**overrides), headers=_auth())


def test_create_and_get_book(client):
    resp = _create(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["title"] == "Clean Code"
    assert body["author"] == "Robert C. Martin"

    resp = client.get("/books/1")
    assert resp.status_code == 200
    assert resp.json()["isbn"] == "978-0132350884"


def test_list_books(client):
    _create(client)
    _create(
        client,
        title="The Pragmatic Programmer",
        author="Andrew Hunt",
        isbn="978-0201616224",
    )
    resp = client.get("/books")
    assert resp.status_code == 200
    titles = [book["title"] for book in resp.json()]
    assert titles == ["Clean Code", "The Pragmatic Programmer"]


def test_put_book(client):
    _create(client)
    resp = client.put(
        "/books/1",
        json={"title": "Clean Code (2nd ed.)", "total_copies": 5},
        headers=_auth(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Clean Code (2nd ed.)"
    assert body["total_copies"] == 5
    assert body["author"] == "Robert C. Martin"


def test_patch_book(client):
    _create(client)
    resp = client.patch(
        "/books/1",
        json={"author": "Uncle Bob"},
        headers=_auth(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["author"] == "Uncle Bob"
    assert body["title"] == "Clean Code"


def test_delete_book(client):
    _create(client)
    resp = client.delete("/books/1", headers=_auth())
    assert resp.status_code == 204

    resp = client.get("/books/1")
    assert resp.status_code == 404


def test_duplicate_isbn_rejected(client):
    _create(client)
    resp = _create(client, title="Other Book", author="Someone Else")
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "conflict"


def test_update_to_duplicate_isbn_rejected(client):
    _create(client)
    _create(
        client,
        title="The Pragmatic Programmer",
        author="Andrew Hunt",
        isbn="978-0201616224",
    )
    resp = client.put(
        "/books/2",
        json={"isbn": "978-0132350884"},
        headers=_auth(),
    )
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "conflict"


def test_search_title_case_insensitive(client):
    _create(client)
    _create(
        client,
        title="The Pragmatic Programmer",
        author="Andrew Hunt",
        isbn="978-0201616224",
    )
    resp = client.get("/books", params={"q": "CLEAN"})
    assert resp.status_code == 200
    titles = [book["title"] for book in resp.json()]
    assert titles == ["Clean Code"]


def test_search_author_case_insensitive(client):
    _create(client)
    _create(
        client,
        title="The Pragmatic Programmer",
        author="Andrew Hunt",
        isbn="978-0201616224",
    )
    resp = client.get("/books", params={"q": "hunt"})
    assert resp.status_code == 200
    titles = [book["title"] for book in resp.json()]
    assert titles == ["The Pragmatic Programmer"]


def test_pagination_limit_and_offset(client):
    for i in range(5):
        _create(
            client,
            title=f"Book {i}",
            isbn=f"isbn-{i}",
        )
    resp = client.get("/books", params={"limit": 2, "offset": 1})
    assert resp.status_code == 200
    titles = [book["title"] for book in resp.json()]
    assert titles == ["Book 1", "Book 2"]


def test_get_book_not_found(client):
    resp = client.get("/books/999")
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "not_found"


def test_update_book_not_found(client):
    resp = client.put("/books/999", json={"title": "X"}, headers=_auth())
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "not_found"


def test_delete_book_not_found(client):
    resp = client.delete("/books/999", headers=_auth())
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "not_found"


def test_write_without_api_key_401(client):
    resp = client.post("/books", json=_book_payload())
    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "unauthorized"


def test_write_with_wrong_api_key_401(client):
    resp = client.post(
        "/books",
        json=_book_payload(),
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "unauthorized"


def test_reads_open_without_key(client):
    _create(client)
    assert client.get("/books").status_code == 200
    assert client.get("/books/1").status_code == 200
