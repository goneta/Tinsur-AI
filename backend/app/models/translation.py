from sqlalchemy import Column, Integer, String, Text, Boolean, UniqueConstraint
from app.core.database import Base

class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, index=True, nullable=False)
    language_code = Column(String, index=True, nullable=False)  # 'fr', 'en'
    value = Column(Text, nullable=False)
    group = Column(String, index=True, nullable=True)  # 'auth', 'common', etc.
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint('key', 'language_code', name='uix_key_language'),
    )
