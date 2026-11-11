"""Database connection for the API."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

# Read settings from the .env file into environment variables.
load_dotenv()

# Fails immediately with a clear KeyError if the setting is missing.
DATABASE_URL = os.environ["DATABASE_URL"]

# The engine manages the connections to PostgreSQL.
engine = create_engine(DATABASE_URL)
