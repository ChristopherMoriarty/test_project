import pytest
from httpx import AsyncClient
from sqlalchemy import select
from src.models import Book
from conftest import async_session_maker
from random import randint


@pytest.mark.asyncio
async def test_get_books(ac: AsyncClient):
    # Create several books for authors
    async with async_session_maker() as db_session:
        book1 = Book(name="Book 1", author_id=1)
        book2 = Book(name="Book 2", author_id=2)
        db_session.add(book1)
        db_session.add(book2)
        await db_session.commit()

    # Get a list of all books
    response = await ac.get("/books")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert len(data["data"]) == 2 
    assert data["data"][0]["name"] == "Book 1"
    assert data["data"][1]["name"] == "Book 2"
    assert data["data"][0]["author_id"] == 1
    assert data["data"][1]["author_id"] == 2
    assert data["detail"] is None

    # Getting a list of books for a specific author
    author_id = 1
    response = await ac.get(f"/books?author_id={author_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert len(data["data"]) == 1  
    assert data["data"][0]["name"] == "Book 1"
    assert data["data"][0]["author_id"] == 1
    assert data["detail"] is None

    # Attempt to get books with invalid parameters
    invalid_author_id = 999
    response = await ac.get(f"/books?author_id={invalid_author_id}")
    assert response.status_code == 404  

    data = response.json()
    assert data["detail"]["status"] == "error"
    assert data["detail"]["data"] is None
    assert data["detail"]["detail"] == "Book not found"
    

@pytest.mark.asyncio
async def test_get_book(ac: AsyncClient):
    # Create book in database
    async with async_session_maker() as db_session:
        book = await db_session.execute(
            select(Book).filter(Book.id == randint(1, 2))
        )
        book = book.unique().scalar_one_or_none()

    # Getting a book by its ID
    response = await ac.get(f"/books/{book.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["id"] == book.id
    assert data["data"]["name"] == book.name
    assert data["detail"] is None

    # Let's try to request a book with a non-existent ID
    response = await ac.get("/books/999")
    assert response.status_code == 404

    error_data = response.json()
    assert error_data["detail"]["status"] == "error"  
    assert error_data["detail"]["data"] is None
    assert error_data["detail"]["detail"] == "Book not found"


@pytest.mark.asyncio
async def test_create_book(ac: AsyncClient):
    # Creating data for a New Book
    book_data = {
        "name": "Test Book",
        "author_id": 1,  
    }

    response = await ac.post("/books", json=book_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "id" in data["data"]
    assert data["data"]["name"] == book_data["name"]
    assert data["data"]["author_id"] == book_data["author_id"]
    assert data["detail"] is None

    # Let's try to create a book with incorrect data (for example, without a name)
    invalid_book_data = {
        "author_id": 1,
        # Missing "name" field
    }

    response = await ac.post("/books", json=invalid_book_data)
    assert response.status_code == 422  # Data validation error

    error_data = response.json()
    assert error_data["detail"][0]["msg"] == "Field required"


@pytest.mark.asyncio
async def test_update_book(ac: AsyncClient):
    # Create a book to update its data later
    book_data = {
        "name": "Test Book1",
        "author_id": 1, 
    }

    create_response = await ac.post("/books", json=book_data)
    assert create_response.status_code == 200
    created_data = create_response.json()
    created_book_id = created_data["data"]["id"]

    # Updating book data
    updated_book_data = {
        "name": "Updated Book",
    }

    update_response = await ac.patch(
        f"/books/{created_book_id}", json=updated_book_data
    )
    assert update_response.status_code == 200

    data = update_response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "id" in data["data"]
    assert data["data"]["name"] == updated_book_data["name"]
    assert data["detail"] is None

    # Attempt to update a non-existent workbook
    non_existing_book_id = 999

    update_response = await ac.patch(
        f"/books/{non_existing_book_id}", json=updated_book_data
    )
    assert update_response.status_code == 404

    error_data = update_response.json()
    assert error_data["detail"]["status"] == "error"  
    assert error_data["detail"]["data"] is None
    assert error_data["detail"]["detail"] == "Book not found"


@pytest.mark.asyncio
async def test_delete_book(ac: AsyncClient):
    # Create a book to delete it later
    book_data = {
        "name": "Test Book2",
        "author_id": 1,  
    }

    create_response = await ac.post("/books", json=book_data)
    assert create_response.status_code == 200
    created_data = create_response.json()
    created_book_id = created_data["data"]["id"]

    # Delete book
    delete_response = await ac.delete(f"/books/{created_book_id}")
    assert delete_response.status_code == 200

    data = delete_response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"]["message"] == "Book deleted successfully"
    assert data["detail"] is None

    # Verify that the book has indeed been deleted
    verify_deleted_response = await ac.get(f"/books/{created_book_id}")
    assert verify_deleted_response.status_code == 404

    error_data = verify_deleted_response.json()
    assert error_data["detail"]["status"] == "error" 
    assert error_data["detail"]["data"] is None
    assert error_data["detail"]["detail"] == "Book not found"