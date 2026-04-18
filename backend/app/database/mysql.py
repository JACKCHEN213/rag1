"""
MySQL Database Connection Management
"""

from typing import Optional
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
import pymysql

from app.config import settings

# Install MySQL driver
pymysql.install_as_MySQLdb()

# Global engine and session variables
engine = None


async def init_mysql():
    """Initialize MySQL connection"""
    global engine
    
    try:
        # Create engine with connection pooling
        engine = create_engine(
            settings.MYSQL_URL,
            poolclass=StaticPool,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG,
        )
        
        # Create all tables
        SQLModel.metadata.create_all(engine)
        
        print("✓ MySQL initialized successfully")
        
    except Exception as e:
        print(f"✗ MySQL initialization failed: {e}")
        raise


def get_db():
    """Get database session"""
    global engine
    
    if engine is None:
        raise RuntimeError("MySQL not initialized")
    
    with Session(engine) as session:
        yield session


def check_mysql_connection() -> bool:
    """Check if MySQL connection is alive"""
    global engine
    
    if engine is None:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False