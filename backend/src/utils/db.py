import os

from dotenv import load_dotenv
from fastapi_asyncpg import configure_asyncpg

load_dotenv()
DATABASE_URL = str(os.getenv("DATABASE_URL"))


def setup_database(app):
    db = configure_asyncpg(app, DATABASE_URL)

    @db.on_init
    async def _(conn):
        pass

<<<<<<< HEAD
    return db
=======
    return db
>>>>>>> 3fe070cb4d321a56b6fa04e374161ddb5bf0094c
