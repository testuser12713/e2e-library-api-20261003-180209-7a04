from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    isbn: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    publication_year: Mapped[int] = mapped_column(Integer, nullable=False)
    total_copies: Mapped[int] = mapped_column(Integer, nullable=False)

    loans: Mapped[list["Loan"]] = relationship(back_populates="book")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    joined_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    loans: Mapped[list["Loan"]] = relationship(back_populates="member")


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    borrowed_at: Mapped[date] = mapped_column(Date, nullable=False)
    due_at: Mapped[date] = mapped_column(Date, nullable=False)
    returned_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    book: Mapped["Book"] = relationship(back_populates="loans")
    member: Mapped["Member"] = relationship(back_populates="loans")
