from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Member
from app.schemas import MemberCreate, MemberUpdate


def _member_not_found() -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={"code": "not_found", "message": "Member not found"},
    )


def _email_conflict() -> HTTPException:
    return HTTPException(
        status_code=409,
        detail={"code": "conflict", "message": "A member with this email already exists"},
    )


def _find_by_email(db: Session, email: str, exclude_id: int | None = None) -> Member | None:
    stmt = select(Member).where(Member.email == email)
    if exclude_id is not None:
        stmt = stmt.where(Member.id != exclude_id)
    return db.scalars(stmt).first()


def list_members(db: Session) -> list[Member]:
    return list(db.scalars(select(Member).order_by(Member.id)).all())


def get_member(db: Session, member_id: int) -> Member:
    member = db.get(Member, member_id)
    if member is None:
        raise _member_not_found()
    return member


def create_member(db: Session, data: MemberCreate) -> Member:
    if _find_by_email(db, data.email) is not None:
        raise _email_conflict()
    member = Member(name=data.name, email=data.email)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_member(db: Session, member_id: int, data: MemberUpdate) -> Member:
    member = get_member(db, member_id)
    updates = data.model_dump(exclude_unset=True)
    new_email = updates.get("email")
    if (
        new_email is not None
        and new_email != member.email
        and _find_by_email(db, new_email, exclude_id=member_id) is not None
    ):
        raise _email_conflict()
    for field, value in updates.items():
        setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return member


def delete_member(db: Session, member_id: int) -> None:
    member = get_member(db, member_id)
    db.delete(member)
    db.commit()
