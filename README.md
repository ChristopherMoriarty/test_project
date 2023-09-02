# test_project

Dependency installation:

use python 3.8.10 for virtual environment
pip install requirements.txt


Create .env file in the project's root directory and and place the database paths there

DATABASE_URL=sqlite+aiosqlite:///your_path/my_db.db
DATABASE_URL_TEST=sqlite+aiosqlite:///your_path/my_db_test.db


Perform migrations using Alembic: 

alembic revision --autogenerate -m "db creation"
alembic upgrade head 


Start project:

cd src
uvicorn main:app


Start tests:

pytest tests/
