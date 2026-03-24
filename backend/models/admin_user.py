"""
AdminUser modelis - administratoriaus prisijungimo duomenys.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class AdminUser(Base):
    """Administratoriaus vartotojas."""

    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AdminUser(username='{self.username}')>"
