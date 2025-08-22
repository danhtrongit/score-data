"""
SQLAlchemy model for F-Score data
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Index
from sqlalchemy.sql import func

from app.db.database import Base


class FScore(Base):
    """
    Model for storing F-Score data fetched from Google Sheets
    Includes Piotroski F-Score metrics and indicators
    """
    __tablename__ = "fscores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker = Column(String(10), unique=True, index=True, nullable=False)
    
    # F-Score values by year
    score_2024 = Column(Integer, nullable=True)
    score_2023 = Column(Integer, nullable=True)
    score_2022 = Column(Integer, nullable=True)
    score_2021 = Column(Integer, nullable=True)
    score_2020 = Column(Integer, nullable=True)
    
    # Financial metrics (raw values)
    roa = Column(Float, nullable=True)  # Return on Assets
    cfo = Column(Float, nullable=True)  # Cash Flow from Operations
    delta_roa = Column(Float, nullable=True)  # Change in ROA
    cfo_lnst = Column(Float, nullable=True)  # CFO vs Net Income
    delta_long_term_debt = Column(Float, nullable=True)  # Change in long-term debt
    delta_current_ratio = Column(Float, nullable=True)  # Change in current ratio
    shares_issued = Column(Float, nullable=True)  # New shares issued
    delta_gross_margin = Column(Float, nullable=True)  # Change in gross margin
    delta_asset_turnover = Column(Float, nullable=True)  # Change in asset turnover
    
    # F-Score criteria indicators (1 or 0)
    roa_positive = Column(Boolean, default=False)  # ROA > 0
    cfo_positive = Column(Boolean, default=False)  # CFO > 0
    delta_roa_positive = Column(Boolean, default=False)  # ΔROA > 0
    cfo_greater_than_ni = Column(Boolean, default=False)  # CFO > Net Income
    delta_debt_negative = Column(Boolean, default=False)  # ΔLong-term debt < 0
    delta_current_ratio_positive = Column(Boolean, default=False)  # ΔCurrent ratio > 0
    no_new_shares = Column(Boolean, default=False)  # No new shares issued
    delta_gross_margin_positive = Column(Boolean, default=False)  # ΔGross margin > 0
    delta_asset_turnover_positive = Column(Boolean, default=False)  # ΔAsset turnover > 0
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Add composite index for better query performance
    __table_args__ = (
        Index('idx_fscore_ticker_updated', 'ticker', 'updated_at'),
    )
    
    def to_dict(self):
        """Convert model to dictionary for JSON response"""
        return {
            "id": self.id,
            "ticker": self.ticker,
            "scores": {
                "2024": self.score_2024,
                "2023": self.score_2023,
                "2022": self.score_2022,
                "2021": self.score_2021,
                "2020": self.score_2020
            },
            "metrics": {
                "roa": self.roa,
                "cfo": self.cfo,
                "delta_roa": self.delta_roa,
                "cfo_lnst": self.cfo_lnst,
                "delta_long_term_debt": self.delta_long_term_debt,
                "delta_current_ratio": self.delta_current_ratio,
                "shares_issued": self.shares_issued,
                "delta_gross_margin": self.delta_gross_margin,
                "delta_asset_turnover": self.delta_asset_turnover
            },
            "criteria": {
                "roa_positive": self.roa_positive,
                "cfo_positive": self.cfo_positive,
                "delta_roa_positive": self.delta_roa_positive,
                "cfo_greater_than_ni": self.cfo_greater_than_ni,
                "delta_debt_negative": self.delta_debt_negative,
                "delta_current_ratio_positive": self.delta_current_ratio_positive,
                "no_new_shares": self.no_new_shares,
                "delta_gross_margin_positive": self.delta_gross_margin_positive,
                "delta_asset_turnover_positive": self.delta_asset_turnover_positive
            },
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
