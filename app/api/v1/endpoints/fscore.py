"""
F-Score API endpoints
"""
import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import requests

from app.db.database import get_db
from app.schemas.fscore import FScoreListResponse, FScoreResponse
from app.services import fscore_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/f-score",
    tags=["F-Score"]
)


@router.get(
    "",
    response_model=FScoreListResponse,
    summary="Fetch and return F-Score data",
    description="Fetches latest F-Score data from Google Sheets, updates the database, and returns the data with all metrics"
)
async def get_fscores(
    db: Session = Depends(get_db),
    refresh: bool = Query(
        True,
        description="Whether to fetch fresh data from Google Sheets (true) or just return cached data (false)"
    )
) -> Any:
    """
    Main endpoint to fetch F-Score data.
    
    This endpoint:
    1. Fetches latest data from Google Sheets API (if refresh=true)
    2. Updates the SQLite database with the new data
    3. Returns all F-Score records as JSON including metrics and criteria
    """
    try:
        # Fetch and update data from Google Sheets if refresh is requested
        if refresh:
            logger.info("Fetching fresh F-Score data from Google Sheets...")
            update_result = fscore_service.fetch_and_update_fscores(db)
            logger.info(f"F-Score update result: {update_result}")
        
        # Get all records from database
        fscores = fscore_service.get_all_fscores(db)
        
        # Convert to response format
        data = [record.to_dict() for record in fscores]
        
        # Get the most recent update time
        last_updated = None
        if fscores:
            update_times = [f.updated_at for f in fscores if f.updated_at]
            if update_times:
                last_updated = max(update_times)
        
        return FScoreListResponse(
            success=True,
            message="Data fetched successfully" if refresh else "Cached data returned",
            data=data,
            total_count=len(data),
            last_updated=last_updated
        )
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch F-Score data from Google Sheets: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "message": "Failed to fetch data from Google Sheets",
                "error_code": "SHEETS_API_ERROR",
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_fscores: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "details": str(e)
            }
        )


@router.get(
    "/{ticker}",
    response_model=FScoreResponse,
    summary="Get F-Score data for a specific ticker",
    description="Returns F-Score data for a specific stock ticker including all metrics and criteria"
)
async def get_fscore_by_ticker(
    ticker: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get F-Score data for a specific ticker.
    """
    try:
        fscore = fscore_service.get_fscore_by_ticker(db, ticker)
        
        if not fscore:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "message": f"F-Score data not found for ticker: {ticker}",
                    "error_code": "NOT_FOUND"
                }
            )
        
        # Return the full F-Score data using to_dict method
        return FScoreResponse(**fscore.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching F-Score for ticker {ticker}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "details": str(e)
            }
        )


@router.post(
    "/refresh",
    summary="Force refresh F-Score data",
    description="Forces a refresh of F-Score data from Google Sheets"
)
async def refresh_fscores(db: Session = Depends(get_db)) -> Any:
    """
    Force refresh of F-Score data from Google Sheets.
    """
    try:
        logger.info("Force refresh of F-Score data requested...")
        update_result = fscore_service.fetch_and_update_fscores(db)
        
        return {
            "success": True,
            "message": "F-Score data refreshed successfully",
            **update_result
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh F-Score data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Failed to refresh data",
                "error_code": "REFRESH_ERROR",
                "details": str(e)
            }
        )
