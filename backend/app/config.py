import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-replace-in-production")
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret-key-replace-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "30"))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "sqlite:///portal_dev.sqlite"
    )
    # Fix postgresql:// vs postgres:// URL scheme if using older drivers
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # CORS
    CORS_ORIGINS = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000").split(",")
    ]

    # Agent & Monitoring Configuration
    AGENT_SHARED_SECRET = os.getenv("AGENT_SHARED_SECRET", "agent-enrollment-secret-default")
    HEARTBEAT_TIMEOUT_SECONDS = int(os.getenv("HEARTBEAT_TIMEOUT_SECONDS", "60"))
    IDLE_THRESHOLD_SECONDS = int(os.getenv("IDLE_THRESHOLD_SECONDS", "300"))


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    ENV = "development"


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret-key"
    SECRET_KEY = "test-secret-key"
    REDIS_URL = "redis://mock"


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    ENV = "production"
    # Ensure SQLALCHEMY_ENGINE_OPTIONS has proper connection pool sizes for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 20,
        "max_overflow": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
