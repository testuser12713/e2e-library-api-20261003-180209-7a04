from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Loan


def return_loan(db: Session, loan_id: int) -> Loan:
    loan = db.get(Loan, loan_id)
    if loan is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": "Loan not found"},
        )
    if loan.returned_at is not None:
        raise HTTPException(
            status_code=409,
            detail={"code": "conflict", "message": "Loan already returned"},
        )
    loan.returned_at = date.today()
    db.commit()
    db.refresh(loan)
    return loan


def list_overdue(db: Session) -> list[Loan]:
    today = date.today()
    stmt = select(Loan).where(Loan.returned_at.is_(None), Loan.due_at < today).order_by(Loan.due_at)
    return list(db.scalars(stmt).all())
