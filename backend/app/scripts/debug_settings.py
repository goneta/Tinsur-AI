try:
    from app.core.config import settings
    print(f"Settings loaded successfully.")
    print(f"DB URL: {settings.DATABASE_URL}")
except Exception as e:
    import traceback
    traceback.print_exc()
