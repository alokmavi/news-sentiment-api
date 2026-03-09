import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_CONNECTION_URI = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://sentiment_user:sentiment_password@localhost:5432/sentiment_db"
)

db_engine = create_engine(DB_CONNECTION_URI, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)