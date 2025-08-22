"""
Base schemas for common functionality
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool = True
    message: str
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class ListResponse(BaseResponse):
    """Base list response schema"""
    data: List[Dict[str, Any]]
    total_count: int
    last_updated: Optional[datetime] = None


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
