"""
Setting modelis - sistemos nustatymai.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text

from database import Base


class Setting(Base):
    """Sistemos nustatymai key-value formatu."""

    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    description = Column(String(500), nullable=True)
    category = Column(String(50), default="general", index=True)  # "general", "ocr", "grading"

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Setting(key='{self.key}', category='{self.category}')>"
