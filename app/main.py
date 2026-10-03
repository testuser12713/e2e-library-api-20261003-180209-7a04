from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.errors import register_error_handlers
from app.routers import books, loan_returns, loans, members


@asynccontextmanager
async def lifespan(app: FastAPI):
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
