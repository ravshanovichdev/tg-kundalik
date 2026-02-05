"""
Database connection and session management for SamIT Global.
Provides SQLAlchemy engine, session factory, and base model class.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,          # Maximum number of connections in pool
    max_overflow=20,       # Maximum overflow connections
    pool_pre_ping=True,    # Verify connections before use
    pool_recycle=3600,     # Recycle connections after 1 hour
    echo=settings.debug,   # SQL query logging in debug mode
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all database models
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency function to get database session.
    Used in FastAPI dependency injection.

    Yields:
        Session: Database session instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables defined in models.
    Should be called on application startup.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """
    Drop all database tables.
    Use with caution - this will delete all data!
    """
    try:
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def init_database():
    """
    Initialize database connection and create tables.
    Called during application startup.
    """
    try:
        logger.info("Initializing database connection...")
        # Test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection established")

        # Create tables
        create_tables()

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def reset_database():
    """
    Reset database by dropping and recreating all tables.
    WARNING: This will delete all data!
    """
    logger.warning("Resetting database - all data will be lost!")
    drop_tables()
    create_tables()
    logger.info("Database reset completed")
