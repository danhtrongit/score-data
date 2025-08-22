"""
SQLAlchemy model for Z-Score data
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func

from app.db.database import Base


class ZScore(Base):
    """
    Model for storing Z-Score data fetched from Google Sheets
    """
    __tablename__ = "zscores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker = Column(String(10), unique=True, index=True, nullable=False)
    year_2024 = Column(Float, nullable=True)
    year_2023 = Column(Float, nullable=True)
    year_2022 = Column(Float, nullable=True)
    year_2021 = Column(Float, nullable=True)
    year_2020 = Column(Float, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Add composite index for better query performance
    __table_args__ = (
        Index('idx_zscore_ticker_updated', 'ticker', 'updated_at'),
    )
    
    def to_dict(self):
        """Convert model to dictionary for JSON response"""
        return {
            "id": self.id,
            "ticker": self.ticker,
            "2024Y": self.year_2024,
            "2023Y": self.year_2023,
            "2022Y": self.year_2022,
            "2021Y": self.year_2021,
            "2020Y": self.year_2020,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
