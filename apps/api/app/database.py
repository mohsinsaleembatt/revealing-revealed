"""Database connection for the API."""

import os
from collections.abc import Iterator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Read settings from the .env file into environment variables.
load_dotenv()

# Fails immediately with a clear KeyError if the setting is missing.
DATABASE_URL = os.environ["DATABASE_URL"]

# The engine manages the connections to PostgreSQL.
engine = create_engine(DATABASE_URL)

# A factory that creates one session (one "conversation" with the database).
SessionLocal = sessionmaker(engine)


def get_session() -> Iterator[Session]:
    """Give each request its own session, and close it when the request ends."""
    with SessionLocal() as session:
        yield session
