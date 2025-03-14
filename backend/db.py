# backend/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# For demonstration, we use SQLite. In production, replace with your DSN:
# e.g.: postgresql://user:pass@localhost/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./grammarbot.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
