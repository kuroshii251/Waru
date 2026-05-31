import os
from dotenv import load_dotenv
from pathlib import Path
import asyncpg

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL tidak ditemukan di .env!")

pool = None

async def get_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL, ssl="require")
    return pool

async def get_conn():
    p = await get_pool()
    async with p.acquire() as conn:
        yield conn

def setup_database(app):
    @app.on_event("startup")
    async def startup():
        await get_pool()

    @app.on_event("shutdown")
    async def shutdown():
        global pool
        if pool:
            await pool.close()