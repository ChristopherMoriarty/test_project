from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE_URL_TEST = os.environ.get("DATABASE_URL_TEST")