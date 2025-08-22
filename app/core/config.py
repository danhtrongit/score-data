"""
Core configuration for the application
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Financial Score API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./financial_scores.db", env="DATABASE_URL")
    
    # Google Sheets API
    GOOGLE_SHEETS_API_KEY: str = Field(
        default="AIzaSyB9PPBCGbWFv1TxH_8s_AsiqiChLs9MqXU",
        env="GOOGLE_SHEETS_API_KEY"
    )
    SPREADSHEET_ID: str = Field(
        default="1ekb2bYAQJZbtmqMUzsagb4uWBdtkAzTq3kuIMHQ22RI",
        env="SPREADSHEET_ID"
    )
    
    # Sheets configuration
    ZSCORE_SHEET_NAME: str = "Zscore"
    FSCORE_SHEET_NAME: str = "FScore"
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    ADMIN_PREFIX: str = "/admin/sheet"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
