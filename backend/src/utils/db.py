import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from fastapi_asyncpg import configure_asyncpg

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL EXISTS:", DATABASE_URL is not None)
parsed = urlparse(DATABASE_URL)

print("DB HOST =", parsed.hostname)
print("DB PORT =", parsed.port)

def setup_database(app):
    db = configure_asyncpg(
    app,
    DATABASE_URL,
    ssl="require"
)
    @db.on_init
    async def _(conn):
        print("Database connected")

    return db