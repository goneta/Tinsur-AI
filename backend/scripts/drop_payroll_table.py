from app.core.database import engine
from sqlalchemy import text

def drop_table():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS payroll_transactions CASCADE"))
        conn.commit()
    print("Dropped payroll_transactions table.")

if __name__ == "__main__":
    drop_table()
