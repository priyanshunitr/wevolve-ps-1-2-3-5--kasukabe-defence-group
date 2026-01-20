"""
Application Settings & Configuration
Centralized configuration management for Wevolve API
"""
import os
from typing import List

class Settings:
    """Application settings - can be extended to use environment variables"""
    
    # App Info
    APP_NAME: str = "Wevolve API"
    APP_DESCRIPTION: str = "AI-Powered Career Acceleration Ecosystem"
    APP_VERSION: str = "1.0.0"
    
    # Database
    # Render provides DATABASE_URL, fallback to local SQLite
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_0CKXwm5fiMNk@ep-damp-field-a15xjbgu-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
    # DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./wevolve.db")
    
    # Fix for SQLAlchemy using postgres:// (deprecated) instead of postgresql://
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # CRA default
        "http://localhost:3001",  # Next.js on port 3001
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://wevolve-frontend.onrender.com" # Add your production frontend URL here
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
