"""
OCRResult modelis - OCR atpažinimo rezultatas.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship

from database import Base


class OCRResult(Base):
    """OCR atpažinimo rezultatas vienam puslapiui/regionui."""
    
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    page_number = Column(Integer, default=1)  # Puslapio numeris
    region = Column(String(100), nullable=True)  # "x1,y1,x2,y2" arba "full"
    
    # OCR šaltinis
    ocr_source = Column(String(50), nullable=False)  # "mathpix", "google_vision", "tesseract"
    
    # Rezultatai
    raw_text = Column(Text, nullable=True)  # Atpažintas tekstas
    latex = Column(Text, nullable=True)  # LaTeX formatas
    confidence = Column(Float, default=0.0)  # 0.0 - 1.0
    
    # Metadata
    processing_time_ms = Column(Integer, default=0)  # Apdorojimo laikas
    api_response = Column(Text, nullable=True)  # Pilnas API atsakymas (JSON)
    
    # Foreign key
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    submission = relationship("Submission", back_populates="ocr_results")

    def __repr__(self) -> str:
        return f"<OCRResult(id={self.id}, source='{self.ocr_source}', confidence={self.confidence})>"
