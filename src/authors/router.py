from fastapi import APIRouter
from fastapi import HTTPException, Depends

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.exc import NoResultFound

from database import get_async_session
from models import Author
from authors.schemas import AuthorRead, AuthorCreate, AuthorUpdate

router = APIRouter()


@router.get("", response_model=dict)
async def get_authors(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_session)
):
    try:
        stmt = select(Author).offset(skip).limit(limit)
        authors = await db.execute(stmt)
        author_data = [
            AuthorRead(id=author.id, name=author.name).model_dump()
            for author in authors.unique().scalars().all()
        ]
        return {
            "status": "success",
            "data": author_data,
            "detail": None,
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "data": None,
                "detail": "Error while fetching authors",
            },
        )


@router.get("/{author_id}", response_model=dict)
async def get_author(author_id: int, db: AsyncSession = Depends(get_async_session)):
    try:
        stmt = select(Author).where(Author.id == author_id)
        db_author = await db.execute(stmt)
        db_author = db_author.unique().scalar_one_or_none()
        print(db_author)

        if db_author is None:
            raise NoResultFound

        return {
            "status": "success",
            "data": AuthorRead(id=db_author.id, name=db_author.name).model_dump(),
            "detail": None,
        }
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "data": None,
                "detail": "Author not found",
            },
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "data": None,
                "detail": "Error while fetching the author",
            },
        )


@router.post("", response_model=dict)
async def create_author(
    author: AuthorCreate, db: AsyncSession = Depends(get_async_session)
):
    try:
        db_author = Author(**author.model_dump())
        db.add(db_author)
        await db.commit()
        await db.refresh(db_author)

        return {
            "status": "success",
            "data": AuthorRead(id=db_author.id, name=db_author.name).model_dump(),
            "detail": None,
        }
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "data": None,
                "detail": "Error while creating the author",
            },
        )


@router.patch("/{author_id}", response_model=dict)
async def update_author(
    author_id: int,
    updated_author: AuthorUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    try:
        stmt = (
            update(Author)
            .where(Author.id == author_id)
            .values(**updated_author.model_dump())
            .returning(Author)
        )
        updated_author_data = await db.execute(stmt)
        updated_author_data = updated_author_data.unique().scalar_one_or_none()

        if updated_author_data is None:
            raise NoResultFound

        await db.commit()

        return {
            "status": "success",
            "data": AuthorRead(
                id=updated_author_data.id, name=updated_author_data.name
            ),
            "detail": None,
        }
    except NoResultFound:
        await db.rollback()
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "data": None,
                "detail": "Author not found",
            },
        )
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "data": None,
                "detail": "Error while updating the author",
            },
        )


@router.delete("/{author_id}", response_model=dict)
async def delete_author(author_id: int, db: AsyncSession = Depends(get_async_session)):
    try:
        stmt = delete(Author).where(Author.id == author_id)
        result = await db.execute(stmt)

        if result is None:
            raise NoResultFound

        await db.commit()

        return {
            "status": "success",
            "data": {"message": "Author deleted successfully"},
            "detail": None,
        }
    except NoResultFound:
        await db.rollback()
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "data": None,
                "detail": "Author not found",
            },
        )

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "data": None,
                "detail": "Error while deleting the author",
            },
        )
