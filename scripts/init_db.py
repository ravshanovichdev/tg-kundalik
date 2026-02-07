#!/usr/bin/env python3
"""
Database initialization script.
Creates all tables defined in models.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models to register them with SQLAlchemy Base
from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.group import Group
from models.grade import Grade
from models.attendance import Attendance
from models.payment import Payment
from models.schedule import Schedule

from app.database import init_database, create_tables
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize database"""
    try:
        logger.info("Initializing database...")
        logger.info(f"Database URL: {settings.database_url.replace(settings.mysql_password, '***')}")
        
        # Create tables
        create_tables()
        
        logger.info("Database initialized successfully!")
        return 0
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

