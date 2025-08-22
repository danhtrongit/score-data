"""
Pydantic schemas for F-Score data validation and serialization
"""
from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.base import ListResponse


class FScoreMetrics(BaseModel):
    """Schema for F-Score financial metrics"""
    roa: Optional[float] = Field(None, description="Return on Assets")
    cfo: Optional[float] = Field(None, description="Cash Flow from Operations")
    delta_roa: Optional[float] = Field(None, description="Change in ROA")
    cfo_lnst: Optional[float] = Field(None, description="CFO vs Net Income")
    delta_long_term_debt: Optional[float] = Field(None, description="Change in long-term debt")
    delta_current_ratio: Optional[float] = Field(None, description="Change in current ratio")
    shares_issued: Optional[float] = Field(None, description="New shares issued")
    delta_gross_margin: Optional[float] = Field(None, description="Change in gross margin")
    delta_asset_turnover: Optional[float] = Field(None, description="Change in asset turnover")


class FScoreCriteria(BaseModel):
    """Schema for F-Score criteria indicators"""
    roa_positive: bool = Field(False, description="ROA > 0")
    cfo_positive: bool = Field(False, description="CFO > 0")
    delta_roa_positive: bool = Field(False, description="ΔROA > 0")
    cfo_greater_than_ni: bool = Field(False, description="CFO > Net Income")
    delta_debt_negative: bool = Field(False, description="ΔLong-term debt < 0")
    delta_current_ratio_positive: bool = Field(False, description="ΔCurrent ratio > 0")
    no_new_shares: bool = Field(False, description="No new shares issued")
    delta_gross_margin_positive: bool = Field(False, description="ΔGross margin > 0")
    delta_asset_turnover_positive: bool = Field(False, description="ΔAsset turnover > 0")


class FScoreBase(BaseModel):
    """Base schema for F-Score data"""
    ticker: str = Field(..., max_length=10, description="Stock ticker symbol")
    score_2024: Optional[int] = Field(None, alias="2024", ge=0, le=9, description="F-Score for 2024")
    score_2023: Optional[int] = Field(None, alias="2023", ge=0, le=9, description="F-Score for 2023")
    score_2022: Optional[int] = Field(None, alias="2022", ge=0, le=9, description="F-Score for 2022")
    score_2021: Optional[int] = Field(None, alias="2021", ge=0, le=9, description="F-Score for 2021")
    score_2020: Optional[int] = Field(None, alias="2020", ge=0, le=9, description="F-Score for 2020")
    
    model_config = ConfigDict(populate_by_name=True)


class FScoreCreate(FScoreBase):
    """Schema for creating F-Score records"""
    metrics: Optional[FScoreMetrics] = None
    criteria: Optional[FScoreCriteria] = None


class FScoreUpdate(BaseModel):
    """Schema for updating F-Score records"""
    score_2024: Optional[int] = Field(None, alias="2024", ge=0, le=9)
    score_2023: Optional[int] = Field(None, alias="2023", ge=0, le=9)
    score_2022: Optional[int] = Field(None, alias="2022", ge=0, le=9)
    score_2021: Optional[int] = Field(None, alias="2021", ge=0, le=9)
    score_2020: Optional[int] = Field(None, alias="2020", ge=0, le=9)
    metrics: Optional[FScoreMetrics] = None
    criteria: Optional[FScoreCriteria] = None
    
    model_config = ConfigDict(populate_by_name=True)


class FScoreResponse(BaseModel):
    """Schema for F-Score API responses"""
    id: int
    ticker: str
    scores: Dict[str, Optional[int]]
    metrics: Dict[str, Optional[float]]
    criteria: Dict[str, bool]
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class FScoreListResponse(ListResponse):
    """Response schema for F-Score list endpoint"""
    pass
