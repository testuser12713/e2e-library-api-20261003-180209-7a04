from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_api_key
from app.schemas import BookCreate, BookOut, BookUpdate
from app.services import books as service

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookOut])
def list_books(
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[BookOut]:
    return service.list_books(db, q=q, limit=limit, offset=offset)


@router.post(
    "",
    response_model=BookOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_book(data: BookCreate, db: Session = Depends(get_db)) -> BookOut:
    return service.create_book(db, data)


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)) -> BookOut:
    return service.get_book(db, book_id)


@router.put(
    "/{book_id}",
    response_model=BookOut,
    dependencies=[Depends(require_api_key)],
)
def put_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)) -> BookOut:
    return service.update_book(db, book_id, data)


@router.patch(
    "/{book_id}",
    response_model=BookOut,
    dependencies=[Depends(require_api_key)],
)
def patch_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)) -> BookOut:
    return service.update_book(db, book_id, data)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key)],
)
def delete_book(book_id: int, db: Session = Depends(get_db)) -> Response:
    service.delete_book(db, book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
