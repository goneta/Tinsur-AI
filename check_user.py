from sqlalchemy import create_engine, MetaData, Table, select

engine = create_engine("sqlite:///insurance.db")
metadata = MetaData()
users = Table('users', metadata, autoload_with=engine)

with engine.connect() as conn:
    stmt = select(users).where(users.c.email == 'test_client@tinsur.ai')
    result = conn.execute(stmt).fetchone()
    if result:
        print(f"User found: {result}")
    else:
        print("User NOT found")
