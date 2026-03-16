#============================================================#
#              RENDER DATABASE SETUP                         #
#============================================================#

# ── Imports ──────────────────────────────────────────────── #
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
from dotenv import load_dotenv
import os


# ────────────────────────── Environment Variables ────────────────────────────── #
load_dotenv()

RENDER_DATABASE_URL = os.getenv("RENDER_DATABASE_URL")


# ──────────────────────────Database Engine ────────────────────────────── #
engine = create_engine(RENDER_DATABASE_URL)


# ──────────────────────────Session Factory───────────────────────────── #
RenderSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ────────────────────────── Base Model ───────────────────────────────── #
Base = declarative_base()


# ──────────────────── Database Dependency ──────────────────────────── #
def connect_database():
    """
    Yields a database session and ensures it is 
    closed after the request is complete.
    """
    db_session = RenderSession()

    try:
        yield db_session
    finally:
        db_session.close()


# ───────────────────── Entry Point ────────────────────────────── #
if __name__ == "__main__":
    connect_database()
    print("Database connection successful")