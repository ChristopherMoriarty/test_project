from typing import Optional

from fastapi import APIRouter
from fastapi import HTTPException, Depends

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.exc import NoResultFound

from database import get_async_session
from models import Book, Author
from books.schemas import BookRead, BookCreate, BookUpdate

router = APIRouter()


@router.get("", response_model=dict)
async def get_books(
    author_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        stmt = select(Book).offset(skip).limit(limit)
        if author_id is not None:
            stmt = stmt.where(Book.author_id == author_id)
            
        books = await db.execute(stmt)
        
        book_data = [
            BookRead(id=book.id, name=book.name, author_id=book.author_id).model_dump()
            for book in books.unique().scalars().all()
        ]
        
        if not book_data and author_id is not None:
            raise NoResultFound

        return {
            "status": "success",
            "data": book_data,
            "detail": None,
        }

    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "data": None,
                "detail": "Book not found",
            },
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "data": None,
                "detail": "Error while fetching books",
            },
        )


@router.get("/{book_id}", response_model=dict)
async def get_book(book_id: int, db: AsyncSession = Depends(get_async_session)):
    try:
        stmt = select(Book).where(Book.id == book_id)
        db_book = await db.execute(stmt)
        db_book = db_book.unique().scalar_one_or_none()

        if db_book is None:
            raise NoResultFound

        return {
            "status": "success",
            "data": BookRead(
                id=db_book.id, name=db_book.name, author_id=db_book.author_id
            ).model_dump(),
            "detail": None,
        }
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "data": None,
                "detail": "Book not found",
            },
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "data": None,
                "detail": "Error while fetching book",
            },
        )


@router.post("", response_model=dict)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        author = await db.execute(select(Author).where(Author.id == book.author_id))
        author = author.unique().scalar_one_or_none()
        if author is None:
            raise HTTPException(status_code=400, detail="Author does not exist")

        db_book = Book(**book.model_dump())
        db.add(db_book)
        await db.commit()
        await db.refresh(db_book)

        return {
            "status": "success",
            "data": BookRead(
                id=db_book.id, name=db_book.name, author_id=db_book.author_id
            ).model_dump(),
            "detail": None,
        }
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "data": None,
                "detail": "Error while creating the book",
            },
        )


@router.patch("/{book_id}", response_model=dict)
async def update_book(
    book_id: int, book_data: BookUpdate, db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = (
            update(Book)
            .where(Book.id == book_id)
            .values(**book_data.model_dump(exclude_unset=True))
            .returning(Book)
        )
        result = await db.execute(stmt)
        db_book = result.scalars().first()

        if db_book is None:
            raise NoResultFound

        await db.commit()

        return {
            "status": "success",
            "data": BookRead(
                id=db_book.id, name=db_book.name, author_id=db_book.author_id
            ).model_dump(),
            "detail": None,
        }
    except NoResultFound:
        await db.rollback()
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "data": None,
                "detail": "Book not found",
            },
        )
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "data": None,
                "detail": "Error while updating the book",
            },
        )


@router.delete("/{book_id}", response_model=dict)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_async_session)):
    try:
        stmt = delete(Book).where(Book.id == book_id)
        result = await db.execute(stmt)

        if result.rowcount == 0:
            raise NoResultFound

        await db.commit()

        return {
            "status": "success",
            "data": {"message": "Book deleted successfully"},
            "detail": None,
        }
    except NoResultFound:
        await db.rollback()
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "data": None,
                "detail": "Book not found",
            },
        )
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "data": None,
                "detail": "Error while deleting the book",
            },
        )


