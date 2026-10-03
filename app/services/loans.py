from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Book, Loan, Member
from app.schemas import LoanCreate, LoanOut

MAX_OPEN_LOANS_PER_MEMBER = 3
LOAN_PERIOD_DAYS = 14


def create_loan(db: Session, payload: LoanCreate) -> LoanOut:
    book = db.get(Book, payload.book_id)
    if book is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": "Book not found"},
        )

    member = db.get(Member, payload.member_id)
    if member is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": "Member not found"},
        )

    open_loans_by_member = db.scalar(
        select(func.count())
        .select_from(Loan)
        .where(
            Loan.member_id == payload.member_id,
            Loan.returned_at.is_(None),
        )
    )
    if open_loans_by_member >= MAX_OPEN_LOANS_PER_MEMBER:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "conflict",
                "message": "Member already has 3 open loans",
            },
        )

    open_loans_for_book = db.scalar(
        select(func.count())
        .select_from(Loan)
        .where(
            Loan.book_id == payload.book_id,
            Loan.returned_at.is_(None),
        )
    )
    if open_loans_for_book >= book.total_copies:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "conflict",
                "message": "No free copies of this book are available",
            },
        )

    borrowed_at = date.today()
    loan = Loan(
        book_id=payload.book_id,
        member_id=payload.member_id,
        borrowed_at=borrowed_at,
        due_at=borrowed_at + timedelta(days=LOAN_PERIOD_DAYS),
        returned_at=None,
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)

    return LoanOut.model_validate(loan)
