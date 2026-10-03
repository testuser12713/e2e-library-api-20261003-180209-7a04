from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_api_key
from app.schemas import LoanOut
from app.services import loan_returns

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("/{loan_id}/return", response_model=LoanOut)
def return_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_api_key),
) -> LoanOut:
    return loan_returns.return_loan(db, loan_id)


@router.get("/overdue", response_model=list[LoanOut])
def list_overdue(db: Session = Depends(get_db)) -> list[LoanOut]:
    return loan_returns.list_overdue(db)
