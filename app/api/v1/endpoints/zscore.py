"""
Z-Score API endpoints
"""
import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import requests

from app.db.database import get_db
from app.schemas.zscore import ZScoreListResponse, ZScoreResponse
from app.services import zscore_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/z-score",
    tags=["Z-Score"]
)


@router.get(
    "",
    response_model=ZScoreListResponse,
    summary="Fetch and return Z-Score data",
    description="Fetches latest Z-Score data from Google Sheets, updates the database, and returns the data"
)
async def get_zscores(
    db: Session = Depends(get_db),
    refresh: bool = Query(
        True,
        description="Whether to fetch fresh data from Google Sheets (true) or just return cached data (false)"
    )
) -> Any:
    """
    Main endpoint to fetch Z-Score data.
    
    This endpoint:
    1. Fetches latest data from Google Sheets API (if refresh=true)
    2. Updates the SQLite database with the new data
    3. Returns all Z-Score records as JSON
    """
    try:
        # Fetch and update data from Google Sheets if refresh is requested
        if refresh:
            logger.info("Fetching fresh Z-Score data from Google Sheets...")
            update_result = zscore_service.fetch_and_update_zscores(db)
            logger.info(f"Z-Score update result: {update_result}")
        
        # Get all records from database
        zscores = zscore_service.get_all_zscores(db)
        
        # Convert to response format
        data = [record.to_dict() for record in zscores]
        
        # Get the most recent update time
        last_updated = None
        if zscores:
            update_times = [z.updated_at for z in zscores if z.updated_at]
            if update_times:
                last_updated = max(update_times)
        
        return ZScoreListResponse(
            success=True,
            message="Data fetched successfully" if refresh else "Cached data returned",
            data=data,
            total_count=len(data),
            last_updated=last_updated
        )
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch Z-Score data from Google Sheets: {str(e)}")
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
        logger.error(f"Unexpected error in get_zscores: {str(e)}")
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
    response_model=ZScoreResponse,
    summary="Get Z-Score data for a specific ticker",
    description="Returns Z-Score data for a specific stock ticker"
)
async def get_zscore_by_ticker(
    ticker: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get Z-Score data for a specific ticker.
    """
    try:
        zscore = zscore_service.get_zscore_by_ticker(db, ticker)
        
        if not zscore:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "message": f"Z-Score data not found for ticker: {ticker}",
                    "error_code": "NOT_FOUND"
                }
            )
        
        return zscore
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Z-Score for ticker {ticker}: {str(e)}")
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
    summary="Force refresh Z-Score data",
    description="Forces a refresh of Z-Score data from Google Sheets"
)
async def refresh_zscores(db: Session = Depends(get_db)) -> Any:
    """
    Force refresh of Z-Score data from Google Sheets.
    """
    try:
        logger.info("Force refresh of Z-Score data requested...")
        update_result = zscore_service.fetch_and_update_zscores(db)
        
        return {
            "success": True,
            "message": "Z-Score data refreshed successfully",
            **update_result
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh Z-Score data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Failed to refresh data",
                "error_code": "REFRESH_ERROR",
                "details": str(e)
            }
        )
