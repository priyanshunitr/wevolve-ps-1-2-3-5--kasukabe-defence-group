"""
Application Settings & Configuration
Centralized configuration management for Wevolve API
"""
from typing import List


class Settings:
    """Application settings - can be extended to use environment variables"""
    
    # App Info
    APP_NAME: str = "Wevolve API"
    APP_DESCRIPTION: str = "AI-Powered Career Acceleration Ecosystem"
    APP_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./wevolve.db"
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # CRA default
    ]
    
    # Matching Engine Weights
    MATCHING_WEIGHTS: dict = {
        "skills": 0.40,      # 40%
        "location": 0.20,    # 20%
        "salary": 0.15,      # 15%
        "experience": 0.15,  # 15%
        "role": 0.10         # 10%
    }
    
    # Match Tier Thresholds
    MATCH_TIERS: dict = {
        "excellent": 85,
        "good": 70,
        "fair": 50,
        "poor": 0
    }


# Singleton settings instance
settings = Settings()
