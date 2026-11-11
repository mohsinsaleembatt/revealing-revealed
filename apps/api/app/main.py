from app.routers import quran
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine

app = FastAPI(title="Revealing Revealed API")
app.include_router(quran.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report that the server is running."""
    return {"status": "ok"}


@app.get("/health/database")
def database_health_check() -> dict[str, str]:
    """Report whether the API can reach the database."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ok"}
