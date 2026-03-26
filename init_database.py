#!/usr/bin/env python
"""Initialize Tinsur-AI database with all tables"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from datetime import datetime

# Database connection
DATABASE_URL = "sqlite:///./insurance.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    """Initialize all database tables"""
    try:
        print("=" * 60)
        print("INITIALIZING TINSUR-AI DATABASE")
        print("=" * 60)
        print()
        print("Creating all tables...")
        
        # Create all tables from models
        Base.metadata.create_all(bind=engine)
        
        print("[OK] All tables created successfully")
        print()
        
        # List created tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"Database: SQLite (insurance.db)")
        print(f"Total tables: {len(tables)}")
        print()
        print("Tables created:")
        for table in sorted(tables):
            columns = inspector.get_columns(table)
            print(f"  - {table} ({len(columns)} columns)")
        
        print()
        print("=" * 60)
        print("DATABASE INITIALIZATION COMPLETE")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
