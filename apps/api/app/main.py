from fastapi import FastAPI

app = FastAPI(title="Revealing Revealed API")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report that the server is running."""
    return {"status": "ok"}
