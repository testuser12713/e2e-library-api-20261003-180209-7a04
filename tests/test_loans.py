from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import Book, Loan, Member

API_KEY = settings.api_key


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        session = session_local()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield session_local
    app.dependency_overrides.clear()


@pytest.fixture()
def client(db):
    with TestClient(app) as c:
        yield c


def _make_book(db, total_copies=1, **kwargs):
    defaults = {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "978-0132350884",
        "publication_year": 2008,
        "total_copies": total_copies,
    }
    defaults.update(kwargs)
    with db() as session:
        book = Book(**defaults)
        session.add(book)
        session.commit()
        session.refresh(book)
        return book.id


def _make_member(db, **kwargs):
    defaults = {"name": "Jane Doe", "email": "jane@example.com"}
    defaults.update(kwargs)
    with db() as session:
        member = Member(**defaults)
        session.add(member)
        session.commit()
        session.refresh(member)
        return member.id


def _make_open_loan(db, book_id, member_id):
    with db() as session:
        loan = Loan(
            book_id=book_id,
            member_id=member_id,
            borrowed_at=date.today(),
            due_at=date.today() + timedelta(days=14),
            returned_at=None,
        )
        session.add(loan)
        session.commit()


def test_create_loan_sets_borrowed_at_to_today(client, db):
    book_id = _make_book(db)
    member_id = _make_member(db)

    response = client.post(
        "/loans",
        json={"book_id": book_id, "member_id": member_id},
        headers={"X-API-Key": API_KEY},
    )

    assert response.status_code == 201
    assert response.json()["borrowed_at"] == str(date.today())


def test_create_loan_sets_due_at_fourteen_days_later(client, db):
    book_id = _make_book(db)
    member_id = _make_member(db)

    response = client.post(
        "/loans",
        json={"book_id": book_id, "member_id": member_id},
        headers={"X-API-Key": API_KEY},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["due_at"] == str(date.today() + timedelta(days=14))
    assert body["due_at"] == str(date.fromisoformat(body["borrowed_at"]) + timedelta(days=14))


def test_create_loan_sets_returned_at_to_none(client, db):
    book_id = _make_book(db)
    member_id = _make_member(db)

    response = client.post(
        "/loans",
        json={"book_id": book_id, "member_id": member_id},
        headers={"X-API-Key": API_KEY},
    )

    assert response.status_code == 201
    assert response.json()["returned_at"] is None


def test_create_loan_allows_up_to_three_open_loans(client, db):
    book_id = _make_book(db, total_copies=10)
    member_id = _make_member(db)

    for _ in range(3):
        response = client.post(
            "/loans",
            json={"book_id": book_id, "member_id": member_id},
            headers={"X-API-Key": API_KEY},
        )
        assert response.status_code == 201


def test_create_loan_rejects_fourth_open_loan(client, db):
    book_id = _make_book(db, total_copies=10)
    member_id = _make_member(db)
    for _ in range(3):
        _make_open_loan(db, book_id, member_id)

    response = client.post(
        "/loans",
        json={"book_id": book_id, "member_id": member_id},
        headers={"X-API-Key": API_KEY},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "conflict"


def test_create_loan_rejects_when_no_free_copy(client, db):
    book_id = _make_book(db, total_copies=1)
    first_member_id = _make_member(db, name="First", email="first@example.com")
    second_member_id = _make_member(db, name="Second", email="second@example.com")
    _make_open_loan(db, book_id, first_member_id)

    response = client.post(
        "/loans",
        json={"book_id": book_id, "member_id": second_member_id},
        headers={"X-API-Key": API_KEY},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "conflict"


def test_create_loan_succeeds_when_a_copy_is_free(client, db):
    book_id = _make_book(db, total_copies=2)
    first_member_id = _make_member(db, name="First", email="first@example.com")
    second_member_id = _make_member(db, name="Second", email="second@example.com")
    _make_open_loan(db, book_id, first_member_id)

    response = client.post(
        "/loans",
        json={"book_id": book_id, "member_id": second_member_id},
        headers={"X-API-Key": API_KEY},
    )

    assert response.status_code == 201


def test_create_loan_requires_api_key(client, db):
    book_id = _make_book(db)
    member_id = _make_member(db)

    response = client.post("/loans", json={"book_id": book_id, "member_id": member_id})

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "unauthorized"


def test_create_loan_rejects_wrong_api_key(client, db):
    book_id = _make_book(db)
    member_id = _make_member(db)

    response = client.post(
        "/loans",
        json={"book_id": book_id, "member_id": member_id},
        headers={"X-API-Key": "not-the-key"},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "unauthorized"


def test_create_loan_book_not_found(client, db):
    member_id = _make_member(db)

    response = client.post(
        "/loans",
        json={"book_id": 9999, "member_id": member_id},
        headers={"X-API-Key": API_KEY},
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_found"


def test_create_loan_member_not_found(client, db):
    book_id = _make_book(db)

    response = client.post(
        "/loans",
        json={"book_id": book_id, "member_id": 9999},
        headers={"X-API-Key": API_KEY},
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_found"
