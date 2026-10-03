from datetime import date

from pydantic import BaseModel, ConfigDict


class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    publication_year: int
    total_copies: int


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    isbn: str | None = None
    publication_year: int | None = None
    total_copies: int | None = None


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    isbn: str
    publication_year: int
    total_copies: int


class MemberCreate(BaseModel):
    name: str
    email: str


class MemberUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    joined_at: date


class LoanCreate(BaseModel):
    book_id: int
    member_id: int


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    member_id: int
    borrowed_at: date
    due_at: date
    returned_at: date | None
