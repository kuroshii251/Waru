import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from fastapi_asyncpg import configure_asyncpg
import asyncpg

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL EXISTS:", DATABASE_URL is not None)
parsed = urlparse(DATABASE_URL)

print("DB HOST =", parsed.hostname)
print("DB PORT =", parsed.port)

async def test_connection():
    conn = await asyncpg.connect(
        DATABASE_URL,
        ssl=False
    )

    print("DATABASE CONNECTED")
    await conn.close()
    
def setup_database(app):
    db = configure_asyncpg(
        app,
        DATABASE_URL,
        ssl=False
    )

    @db.on_init
    async def _(conn):
        print("Database connected")

    return db