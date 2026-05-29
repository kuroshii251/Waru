from fastapi import Depends, FastAPI
from fastapi.templating import Jinja2Templates
from src.db import setup_database

app = FastAPI()
templates = Jinja2Templates(directory="frontend/src/templates")

db = setup_database(app)


@app.get("/health")
async def health_check(conn=Depends(db.connection)):
    await conn.fetchval("SELECT 1")
    return {"status": "ok", "database": "connected"}
