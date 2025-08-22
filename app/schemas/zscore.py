"""
Pydantic schemas for Z-Score data validation and serialization
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.base import ListResponse


class ZScoreBase(BaseModel):
    """Base schema for Z-Score data"""
    ticker: str = Field(..., max_length=10, description="Stock ticker symbol")
    year_2024: Optional[float] = Field(None, alias="2024Y", description="Z-Score for 2024")
    year_2023: Optional[float] = Field(None, alias="2023Y", description="Z-Score for 2023")
    year_2022: Optional[float] = Field(None, alias="2022Y", description="Z-Score for 2022")
    year_2021: Optional[float] = Field(None, alias="2021Y", description="Z-Score for 2021")
    year_2020: Optional[float] = Field(None, alias="2020Y", description="Z-Score for 2020")
    
    model_config = ConfigDict(populate_by_name=True)


class ZScoreCreate(ZScoreBase):
    """Schema for creating Z-Score records"""
    pass


class ZScoreUpdate(BaseModel):
    """Schema for updating Z-Score records"""
    year_2024: Optional[float] = Field(None, alias="2024Y")
    year_2023: Optional[float] = Field(None, alias="2023Y")
    year_2022: Optional[float] = Field(None, alias="2022Y")
    year_2021: Optional[float] = Field(None, alias="2021Y")
    year_2020: Optional[float] = Field(None, alias="2020Y")
    
    model_config = ConfigDict(populate_by_name=True)


class ZScoreResponse(ZScoreBase):
    """Schema for Z-Score API responses"""
    id: int
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class ZScoreListResponse(ListResponse):
    """Response schema for Z-Score list endpoint"""
    pass
