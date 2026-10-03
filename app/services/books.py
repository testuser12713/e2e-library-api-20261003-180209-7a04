from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Book
from app.schemas import BookCreate, BookUpdate


def _not_found(book_id: int) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={"code": "not_found", "message": f"Book {book_id} not found"},
    )


def _conflict(isbn: str) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail={"code": "conflict", "message": f"A book with ISBN {isbn} already exists"},
    )


def _isbn_taken(db: Session, isbn: str, exclude_id: int | None = None) -> bool:
    stmt = select(Book.id).where(Book.isbn == isbn)
    if exclude_id is not None:
        stmt = stmt.where(Book.id != exclude_id)
    return db.scalars(stmt).first() is not None


def list_books(db: Session, q: str | None = None, limit: int = 20, offset: int = 0) -> list[Book]:
    stmt = select(Book)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(or_(Book.title.ilike(pattern), Book.author.ilike(pattern)))
    stmt = stmt.order_by(Book.id).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())


def get_book(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise _not_found(book_id)
    return book


def create_book(db: Session, data: BookCreate) -> Book:
    if _isbn_taken(db, data.isbn):
        raise _conflict(data.isbn)
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(db: Session, book_id: int, data: BookUpdate) -> Book:
    book = get_book(db, book_id)
    values = data.model_dump(exclude_none=True)
    if (
        "isbn" in values
        and values["isbn"] != book.isbn
        and _isbn_taken(db, values["isbn"], exclude_id=book_id)
    ):
        raise _conflict(values["isbn"])
    for field, value in values.items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> None:
    book = get_book(db, book_id)
    db.delete(book)
    db.commit()
