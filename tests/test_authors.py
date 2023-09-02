import pytest
from httpx import AsyncClient
from sqlalchemy import select
from src.models import Author
from conftest import async_session_maker
from random import randint


@pytest.mark.asyncio
async def test_get_authors(ac: AsyncClient):
    # Create authors
    async with async_session_maker() as db_session:
        author1 = Author(name="Author 1")
        author2 = Author(name="Author 2")
        author3 = Author(name="Author 3")
        db_session.add(author1)
        db_session.add(author2)
        db_session.add(author3)
        await db_session.commit()

    response = await ac.get("/authors")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) == 3
    assert data["data"][0]["name"] == "Author 1"
    assert data["data"][1]["name"] == "Author 2"
    assert data["data"][2]["name"] == "Author 3"


@pytest.mark.asyncio
async def test_get_author(ac: AsyncClient):
    async with async_session_maker() as db_session:
        author = await db_session.execute(
            select(Author).filter(Author.id == randint(1, 3))
        )
        author = author.unique().scalar_one_or_none()

    response = await ac.get(f"/authors/{author.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["id"] == author.id
    assert data["data"]["name"] == author.name
    assert data["detail"] is None

    # Try to request an author with a non-existent ID
    response = await ac.get("/authors/999")
    assert response.status_code == 404

    error_data = response.json()
    assert error_data["detail"]["status"] == "error"  # "status" внутри "detail"
    assert error_data["detail"]["data"] is None
    assert error_data["detail"]["detail"] == "Author not found"


@pytest.mark.asyncio
async def test_create_author(ac: AsyncClient):
    # Create new author
    author_data = {
        "name": "Author 4",
    }

    response = await ac.post("/authors", json=author_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "id" in data["data"]
    assert data["data"]["name"] == author_data["name"]
    assert data["detail"] is None

    # Try to create an author with incorrect data (for example, without a name)
    invalid_author_data = {
        # Missing "name" field
    }

    response = await ac.post("/authors", json=invalid_author_data)
    assert response.status_code == 422  # Data validation error

    error_data = response.json()
    assert error_data["detail"][0]["msg"] == "Field required"


@pytest.mark.asyncio
async def test_update_author(ac: AsyncClient):
    # Create an author to update his data later
    author_data = {
        "name": "Author 5",
    }

    create_response = await ac.post("/authors", json=author_data)
    assert create_response.status_code == 200
    created_data = create_response.json()
    created_author_id = created_data["data"]["id"]

    # Updating the author's data
    updated_author_data = {
        "name": "Author 6",
    }

    update_response = await ac.patch(
        f"/authors/{created_author_id}", json=updated_author_data
    )
    assert update_response.status_code == 200

    data = update_response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "id" in data["data"]
    assert data["data"]["name"] == updated_author_data["name"]
    assert data["detail"] is None

    # Trying to update a non-existent author
    non_existing_author_id = 999

    update_response = await ac.patch(
        f"/authors/{non_existing_author_id}", json=updated_author_data
    )
    assert update_response.status_code == 404

    error_data = update_response.json()
    assert error_data["detail"]["status"] == "error"  
    assert error_data["detail"]["data"] is None
    assert error_data["detail"]["detail"] == "Author not found"


@pytest.mark.asyncio
async def test_delete_author(ac: AsyncClient):
    # Create an author, then delete it
    author_data = {
        "name": "Test Author",
    }

    create_response = await ac.post("/authors", json=author_data)
    assert create_response.status_code == 200
    created_data = create_response.json()
    created_author_id = created_data["data"]["id"]

    # Delete author
    delete_response = await ac.delete(f"/authors/{created_author_id}")
    assert delete_response.status_code == 200

    data = delete_response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"]["message"] == "Author deleted successfully"
    assert data["detail"] is None

    # Checking if the author has indeed been deleted
    verify_deleted_response = await ac.get(f"/authors/{created_author_id}")
    assert verify_deleted_response.status_code == 404

    error_data = verify_deleted_response.json()
    assert error_data["detail"]["status"] == "error" 
    assert error_data["detail"]["data"] is None
    assert error_data["detail"]["detail"] == "Author not found"
