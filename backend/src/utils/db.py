import os

from dotenv import load_dotenv
from fastapi_asyncpg import configure_asyncpg

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL EXISTS:", DATABASE_URL is not None)

def setup_database(app):
    db = configure_asyncpg(app, DATABASE_URL)

    @db.on_init
    async def _(conn):
        print("Database connected")

    return db