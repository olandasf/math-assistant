"""
Backup modelis - atsarginių kopijų informacija.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from database import Base


class Backup(Base):
    """Atsarginės kopijos įrašas."""

    __tablename__ = "backups"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    backup_type = Column(String(20), default="manual")  # "manual", "auto", "scheduled"
    is_successful = Column(Boolean, default=True)
    notes = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Backup(id={self.id}, file='{self.file_name}', type='{self.backup_type}')>"
