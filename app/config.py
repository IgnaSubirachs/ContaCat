import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application configuration
APP_ENV = os.getenv("APP_ENV", "development")
APP_DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Database configuration from environment
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "erpdb")
DB_USER = os.getenv("DB_USER", "erpuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "erppass")

# Prefer DATABASE_URL when provided, but keep the MySQL parts for Docker/local defaults.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Spring Boot ERP bridge configuration
JAVA_ERP_BASE_URL = os.getenv("JAVA_ERP_BASE_URL", "http://localhost:8080")
JAVA_ERP_COMPANY_ID = os.getenv("JAVA_ERP_COMPANY_ID")
JAVA_ERP_TIMEOUT_SECONDS = float(os.getenv("JAVA_ERP_TIMEOUT_SECONDS", "10"))
