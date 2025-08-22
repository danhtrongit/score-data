"""
Service layer for fetching and processing Z-Score data from Google Sheets
"""
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.zscore import ZScore
from app.core.config import settings
from app.services.base import parse_numeric_value

# Configure logging
logger = logging.getLogger(__name__)


def fetch_zscore_data() -> Dict[str, Any]:
    """
    Fetch Z-Score data from Google Sheets API.
    
    Returns:
        Dictionary containing the API response
        
    Raises:
        requests.RequestException: If API request fails
    """
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{settings.SPREADSHEET_ID}/values/{settings.ZSCORE_SHEET_NAME}"
    
    try:
        response = requests.get(
            url,
            params={"key": settings.GOOGLE_SHEETS_API_KEY},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch Z-Score data from Google Sheets: {str(e)}")
        raise


def process_zscore_data(sheets_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process raw Google Sheets Z-Score data into structured format.
    
    Args:
        sheets_data: Raw data from Google Sheets API
        
    Returns:
        List of processed Z-Score records
    """
    processed_data = []
    
    try:
        values = sheets_data.get("values", [])
        
        if not values or len(values) < 2:
            logger.warning("No data found in Google Sheets Z-Score response")
            return processed_data
        
        # Extract headers (first row)
        headers = values[0]
        
        # Map headers to database fields
        year_mapping = {
            "2024Y": "year_2024",
            "2023Y": "year_2023",
            "2022Y": "year_2022",
            "2021Y": "year_2021",
            "2020Y": "year_2020"
        }
        
        # Process each data row
        for row in values[1:]:
            if not row or len(row) < 2:
                continue
                
            record = {
                "ticker": row[0].strip().upper() if row[0] else None
            }
            
            # Skip if ticker is missing
            if not record["ticker"]:
                continue
            
            # Process year columns
            for i, header in enumerate(headers[1:], start=1):
                if header in year_mapping and i < len(row):
                    db_field = year_mapping[header]
                    record[db_field] = parse_numeric_value(row[i])
            
            processed_data.append(record)
            
    except Exception as e:
        logger.error(f"Error processing Z-Score sheets data: {str(e)}")
        raise
    
    logger.info(f"Processed {len(processed_data)} Z-Score records from Google Sheets")
    return processed_data


def update_zscore_records(db: Session, records: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Update or insert Z-Score records in the database.
    
    Args:
        db: Database session
        records: List of records to update/insert
        
    Returns:
        Dictionary with update statistics
    """
    stats = {
        "inserted": 0,
        "updated": 0,
        "errors": 0
    }
    
    for record in records:
        try:
            # Check if record exists
            existing = db.query(ZScore).filter(
                ZScore.ticker == record["ticker"]
            ).first()
            
            if existing:
                # Update existing record
                for key, value in record.items():
                    if key != "ticker":
                        setattr(existing, key, value)
                stats["updated"] += 1
            else:
                # Create new record
                new_record = ZScore(**record)
                db.add(new_record)
                stats["inserted"] += 1
                
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error for Z-Score ticker {record.get('ticker')}: {str(e)}")
            stats["errors"] += 1
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing Z-Score record {record.get('ticker')}: {str(e)}")
            stats["errors"] += 1
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to commit Z-Score database changes: {str(e)}")
        raise
    
    logger.info(f"Z-Score database update complete: {stats}")
    return stats


def fetch_and_update_zscores(db: Session) -> Dict[str, Any]:
    """
    Main service function to fetch Z-Score data from Google Sheets and update database.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with operation results
    """
    try:
        # Fetch data from Google Sheets
        sheets_data = fetch_zscore_data()
        
        # Process the data
        processed_records = process_zscore_data(sheets_data)
        
        # Update database
        update_stats = update_zscore_records(db, processed_records)
        
        return {
            "success": True,
            "records_processed": len(processed_records),
            "stats": update_stats,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch and update Z-scores: {str(e)}")
        raise


def get_all_zscores(db: Session) -> List[ZScore]:
    """
    Retrieve all Z-Score records from the database.
    
    Args:
        db: Database session
        
    Returns:
        List of Z-Score records
    """
    return db.query(ZScore).order_by(ZScore.ticker).all()


def get_zscore_by_ticker(db: Session, ticker: str) -> Optional[ZScore]:
    """
    Retrieve a specific Z-Score record by ticker.
    
    Args:
        db: Database session
        ticker: Stock ticker symbol
        
    Returns:
        Z-Score record or None if not found
    """
    return db.query(ZScore).filter(
        ZScore.ticker == ticker.upper()
    ).first()
