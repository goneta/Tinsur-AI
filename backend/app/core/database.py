"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from redis import Redis

from app.core.config import settings

from sqlalchemy.pool import NullPool

# PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    poolclass=NullPool
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB
mongo_client = MongoClient(settings.MONGODB_URL)
mongodb = mongo_client.get_database()

# Redis
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongodb():
    """Dependency to get MongoDB database."""
    return mongodb


def get_redis():
    """Dependency to get Redis client."""
    return redis_client
