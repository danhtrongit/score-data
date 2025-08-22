"""
Base service with common functionality
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def parse_numeric_value(value: str) -> Optional[float]:
    """
    Parse numeric value from string format.
    Handles comma as decimal separator (European format).
    
    Args:
        value: String value from Google Sheets
        
    Returns:
        Parsed float value or None if invalid
    """
    if not value or value.strip() == "":
        return None
    
    try:
        # Replace comma with dot for decimal separator
        cleaned_value = value.replace(",", ".")
        return float(cleaned_value)
    except (ValueError, AttributeError):
        logger.warning(f"Could not parse value: {value}")
        return None


def parse_integer_value(value: str) -> Optional[int]:
    """
    Parse integer value from string format.
    
    Args:
        value: String value from Google Sheets
        
    Returns:
        Parsed integer value or None if invalid
    """
    if not value or value.strip() == "":
        return None
    
    try:
        return int(value)
    except (ValueError, AttributeError):
        logger.warning(f"Could not parse integer value: {value}")
        return None


def parse_boolean_value(value: str) -> bool:
    """
    Parse boolean value from string format.
    
    Args:
        value: String value from Google Sheets (typically "1" or "0")
        
    Returns:
        Boolean value
    """
    if not value or value.strip() == "":
        return False
    
    return value.strip() in ["1", "true", "True", "TRUE"]
