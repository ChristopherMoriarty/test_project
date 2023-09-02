from fastapi import FastAPI

from authors.router import router as authors_router
from books.router import router as books_router


app = FastAPI(title="test_project")

app.include_router(
    authors_router,
    prefix="/authors",
    tags=["Authors"],
)

app.include_router(
    books_router,
    prefix="/books",
    tags=["Books"],
)
