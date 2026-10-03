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

AUTH = {"X-API-Key": settings.api_key}


@pytest.fixture()
def api():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    session = testing_session_local()
    with TestClient(app) as client:
        yield client, session
    session.close()
    app.dependency_overrides.clear()


def seed_book(session, isbn="1111111111", total_copies=2):
    book = Book(
        title="Title",
        author="Author",
        isbn=isbn,
        publication_year=2000,
        total_copies=total_copies,
    )
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


def seed_member(session, email="member@example.com"):
    member = Member(name="Name", email=email)
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


def seed_loan(session, book, member, *, due_at, returned_at, borrowed_at=None):
    loan = Loan(
        book_id=book.id,
        member_id=member.id,
        borrowed_at=borrowed_at or date.today(),
        due_at=due_at,
        returned_at=returned_at,
    )
    session.add(loan)
    session.commit()
    session.refresh(loan)
    return loan


def test_return_loan_sets_returned_at(api):
    client, session = api
    book = seed_book(session)
    member = seed_member(session)
    loan = seed_loan(
        session, book, member, due_at=date.today() + timedelta(days=14), returned_at=None
    )

    response = client.post(f"/loans/{loan.id}/return", headers=AUTH)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == loan.id
    assert body["returned_at"] == date.today().isoformat()


def test_return_loan_second_return_conflicts(api):
    client, session = api
    book = seed_book(session)
    member = seed_member(session)
    loan = seed_loan(
        session, book, member, due_at=date.today() + timedelta(days=14), returned_at=None
    )

    first = client.post(f"/loans/{loan.id}/return", headers=AUTH)
    assert first.status_code == 200

    second = client.post(f"/loans/{loan.id}/return", headers=AUTH)
    assert second.status_code == 409
    assert second.json() == {"detail": {"code": "conflict", "message": "Loan already returned"}}


def test_return_unknown_loan_not_found(api):
    client, _ = api
    response = client.post("/loans/999/return", headers=AUTH)
    assert response.status_code == 404
    assert response.json() == {"detail": {"code": "not_found", "message": "Loan not found"}}


def test_return_loan_requires_api_key(api):
    client, session = api
    book = seed_book(session)
    member = seed_member(session)
    loan = seed_loan(
        session, book, member, due_at=date.today() + timedelta(days=14), returned_at=None
    )

    missing = client.post(f"/loans/{loan.id}/return")
    assert missing.status_code == 401

    wrong = client.post(f"/loans/{loan.id}/return", headers={"X-API-Key": "wrong"})
    assert wrong.status_code == 401


def test_overdue_lists_only_open_loans_past_due(api):
    client, session = api
    book = seed_book(session)
    member = seed_member(session)

    overdue = seed_loan(
        session,
        book,
        member,
        due_at=date.today() - timedelta(days=3),
        returned_at=None,
    )
    seed_loan(
        session,
        book,
        member,
        due_at=date.today() + timedelta(days=3),
        returned_at=None,
    )
    seed_loan(
        session,
        book,
        member,
        due_at=date.today() - timedelta(days=5),
        returned_at=date.today(),
    )

    response = client.get("/loans/overdue")

    assert response.status_code == 200
    body = response.json()
    assert [loan["id"] for loan in body] == [overdue.id]
    assert body[0]["returned_at"] is None


def test_overdue_orders_by_due_date(api):
    client, session = api
    book = seed_book(session)
    member = seed_member(session)

    later = seed_loan(
        session,
        book,
        member,
        due_at=date.today() - timedelta(days=1),
        returned_at=None,
    )
    earlier = seed_loan(
        session,
        book,
        member,
        due_at=date.today() - timedelta(days=10),
        returned_at=None,
    )

    response = client.get("/loans/overdue")

    assert response.status_code == 200
    assert [loan["id"] for loan in response.json()] == [earlier.id, later.id]


def test_overdue_is_open_endpoint(api):
    client, session = api
    book = seed_book(session)
    member = seed_member(session)
    seed_loan(
        session,
        book,
        member,
        due_at=date.today() - timedelta(days=1),
        returned_at=None,
    )

    response = client.get("/loans/overdue")

    assert response.status_code == 200
