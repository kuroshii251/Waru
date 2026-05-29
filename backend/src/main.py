from fastapi import Depends, FastAPI
from src.db import setup_database

app = FastAPI()

db = setup_database(app)


@app.get("/health")
async def health_check(conn=Depends(db.connection)):
    await conn.fetchval("SELECT 1")
    return {"status": "ok", "database": "connected"}
