from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@demoinsurance.com').first()
if user:
    user.hashed_password = get_password_hash('admin123')
    db.commit()
    print("Password reset successfully for admin@demoinsurance.com")
else:
    print("User not found")
