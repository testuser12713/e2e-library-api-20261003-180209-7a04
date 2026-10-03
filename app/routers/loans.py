from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_api_key
from app.schemas import LoanCreate, LoanOut
from app.services.loans import create_loan

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post(
    "",
    response_model=LoanOut,
    status_code=201,
    dependencies=[Depends(require_api_key)],
)
def create_loan_endpoint(payload: LoanCreate, db: Session = Depends(get_db)) -> LoanOut:
    return create_loan(db, payload)
