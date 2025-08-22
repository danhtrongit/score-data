"""
Service layer for fetching and processing F-Score data from Google Sheets
"""
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.fscore import FScore
from app.core.config import settings
from app.services.base import parse_numeric_value, parse_integer_value, parse_boolean_value

# Configure logging
logger = logging.getLogger(__name__)


def fetch_fscore_data() -> Dict[str, Any]:
    """
    Fetch F-Score data from Google Sheets API.
    
    Returns:
        Dictionary containing the API response
        
    Raises:
        requests.RequestException: If API request fails
    """
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{settings.SPREADSHEET_ID}/values/{settings.FSCORE_SHEET_NAME}"
    
    try:
        response = requests.get(
            url,
            params={"key": settings.GOOGLE_SHEETS_API_KEY},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch F-Score data from Google Sheets: {str(e)}")
        raise


def process_fscore_data(sheets_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process raw Google Sheets F-Score data into structured format.
    
    Args:
        sheets_data: Raw data from Google Sheets API
        
    Returns:
        List of processed F-Score records
    """
    processed_data = []
    
    try:
        values = sheets_data.get("values", [])
        
        if not values or len(values) < 2:
            logger.warning("No data found in Google Sheets F-Score response")
            return processed_data
        
        # Extract headers (first row)
        headers = values[0]
        
        # Create header index mapping
        header_map = {header: i for i, header in enumerate(headers)}
        
        # Define column mappings
        score_mapping = {
            "2024": "score_2024",
            "2023": "score_2023",
            "2022": "score_2022",
            "2021": "score_2021",
            "2020": "score_2020"
        }
        
        metric_mapping = {
            "ROA": "roa",
            "CFO": "cfo",
            "ΔROA": "delta_roa",
            "CFO_LNST": "cfo_lnst",
            "Δno dai han": "delta_long_term_debt",
            "ΔCurrent Ratio": "delta_current_ratio",
            "SLCP_PH": "shares_issued",
            "ΔGross Margin": "delta_gross_margin",
            "ΔAsset Turnover": "delta_asset_turnover"
        }
        
        criteria_mapping = {
            "ROA>0": "roa_positive",
            "CFO>0": "cfo_positive",
            "ΔROA>0": "delta_roa_positive",
            "CFO>LNST": "cfo_greater_than_ni",
            "ΔNợ dài hạn<0": "delta_debt_negative",
            "ΔCurrent Ratio>0": "delta_current_ratio_positive",
            "Không phát hành CP": "no_new_shares",
            "ΔGross Margin>0": "delta_gross_margin_positive",
            "ΔAsset Turnover>0": "delta_asset_turnover_positive"
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
            
            # Process score columns
            for col_name, field_name in score_mapping.items():
                if col_name in header_map:
                    idx = header_map[col_name]
                    if idx < len(row):
                        record[field_name] = parse_integer_value(row[idx])
            
            # Process metric columns
            for col_name, field_name in metric_mapping.items():
                if col_name in header_map:
                    idx = header_map[col_name]
                    if idx < len(row):
                        record[field_name] = parse_numeric_value(row[idx])
            
            # Process criteria columns
            for col_name, field_name in criteria_mapping.items():
                if col_name in header_map:
                    idx = header_map[col_name]
                    if idx < len(row):
                        record[field_name] = parse_boolean_value(row[idx])
            
            processed_data.append(record)
            
    except Exception as e:
        logger.error(f"Error processing F-Score sheets data: {str(e)}")
        raise
    
    logger.info(f"Processed {len(processed_data)} F-Score records from Google Sheets")
    return processed_data


def update_fscore_records(db: Session, records: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Update or insert F-Score records in the database.
    
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
            existing = db.query(FScore).filter(
                FScore.ticker == record["ticker"]
            ).first()
            
            if existing:
                # Update existing record
                for key, value in record.items():
                    if key != "ticker" and hasattr(existing, key):
                        setattr(existing, key, value)
                stats["updated"] += 1
            else:
                # Create new record
                new_record = FScore(**record)
                db.add(new_record)
                stats["inserted"] += 1
                
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error for F-Score ticker {record.get('ticker')}: {str(e)}")
            stats["errors"] += 1
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing F-Score record {record.get('ticker')}: {str(e)}")
            stats["errors"] += 1
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to commit F-Score database changes: {str(e)}")
        raise
    
    logger.info(f"F-Score database update complete: {stats}")
    return stats


def fetch_and_update_fscores(db: Session) -> Dict[str, Any]:
    """
    Main service function to fetch F-Score data from Google Sheets and update database.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with operation results
    """
    try:
        # Fetch data from Google Sheets
        sheets_data = fetch_fscore_data()
        
        # Process the data
        processed_records = process_fscore_data(sheets_data)
        
        # Update database
        update_stats = update_fscore_records(db, processed_records)
        
        return {
            "success": True,
            "records_processed": len(processed_records),
            "stats": update_stats,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch and update F-scores: {str(e)}")
        raise


def get_all_fscores(db: Session) -> List[FScore]:
    """
    Retrieve all F-Score records from the database.
    
    Args:
        db: Database session
        
    Returns:
        List of F-Score records
    """
    return db.query(FScore).order_by(FScore.ticker).all()


def get_fscore_by_ticker(db: Session, ticker: str) -> Optional[FScore]:
    """
    Retrieve a specific F-Score record by ticker.
    
    Args:
        db: Database session
        ticker: Stock ticker symbol
        
    Returns:
        F-Score record or None if not found
    """
    return db.query(FScore).filter(
        FScore.ticker == ticker.upper()
    ).first()
