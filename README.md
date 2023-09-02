# Test Project

## Dependency Installation

To install the project dependencies, follow these steps:

1. Use Python version 3.8.10 to create a virtual environment:

    ```bash
    python3.8.10 -m venv venv
    ```

2. Install the dependencies from the `requirements.txt` file using pip:

    ```bash
    pip install -r requirements.txt
    ```

## Database Configuration

1. Create a `.env` file in the project's root directory and specify the database paths:

    ```plaintext
    DATABASE_URL=sqlite+aiosqlite:///your_path/my_db.db
    DATABASE_URL_TEST=sqlite+aiosqlite:///your_path/my_db_test.db
    ```

## Performing Migrations Using Alembic

To perform database migrations using Alembic, follow these commands:

###Before creating migrations, create a 'versions' folder in the 'migrations' directory! 

1. Create a migration:

    ```bash
    alembic revision --autogenerate -m "Database creation"
    ```

2. Apply the migration:

    ```bash
    alembic upgrade head
    ```

## Starting the Project

Navigate to the `src` directory:

  ```bash
  cd src
  ```

Launch the project using Uvicorn:

  ```bash
  uvicorn main:app 
  ```

## Running Tests

To run tests, use the following command:

  ```bash
  pytest tests/
  ```

