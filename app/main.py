from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import ValidationError

from app.config import get_settings
from app.database import Base, engine
from app.errors import register_error_handlers
from app.routers import books, loan_returns, loans, members


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        get_settings()
    except ValidationError as exc:
        raise RuntimeError(
            "LIBRARY_API_KEY is required but not set in the environment (see RUN.json / README.md)."
        ) from exc
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Library API", lifespan=lifespan)

register_error_handlers(app)

app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)
app.include_router(loan_returns.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
