from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.routers import auth, learn, quran

app = FastAPI(title="Revealing Revealed API")

app.include_router(quran.router)
app.include_router(learn.router)
app.include_router(auth.router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Return only where the problem is and a readable message.

    The submitted value is deliberately left out: it could be a password.
    """
    errors = [
        {"loc": list(error["loc"]),
         "msg": error["msg"].removeprefix("Value error, ")}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


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
