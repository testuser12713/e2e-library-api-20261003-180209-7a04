from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_api_key
from app.schemas import MemberCreate, MemberOut, MemberUpdate
from app.services import members as members_service

router = APIRouter(prefix="/members", tags=["members"])

_write_guard = [Depends(require_api_key)]


@router.get("", response_model=list[MemberOut])
def list_members(db: Session = Depends(get_db)):
    return members_service.list_members(db)


@router.post(
    "",
    response_model=MemberOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=_write_guard,
)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    return members_service.create_member(db, payload)


@router.get("/{id}", response_model=MemberOut)
def get_member(id: int, db: Session = Depends(get_db)):
    return members_service.get_member(db, id)


@router.put(
    "/{id}",
    response_model=MemberOut,
    dependencies=_write_guard,
)
def update_member(id: int, payload: MemberUpdate, db: Session = Depends(get_db)):
    return members_service.update_member(db, id, payload)


@router.patch(
    "/{id}",
    response_model=MemberOut,
    dependencies=_write_guard,
)
def patch_member(id: int, payload: MemberUpdate, db: Session = Depends(get_db)):
    return members_service.update_member(db, id, payload)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=_write_guard,
)
def delete_member(id: int, db: Session = Depends(get_db)):
    members_service.delete_member(db, id)
