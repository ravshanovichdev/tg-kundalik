"""
Application configuration for SamIT Global educational system.
Centralized configuration management using Pydantic settings.
"""
from pydantic import BaseSettings, validator
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """

    # Application settings
    app_name: str = "SamIT Global"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database settings
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "samit_global")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))

    # Telegram Bot settings
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_bot_username: Optional[str] = None

    # Telegram WebApp settings
    webapp_url: str = os.getenv("WEBAPP_URL", "https://your-domain.com")

    # Security settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Logging settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    logs_group_id: int = int(os.getenv("LOGS_GROUP_ID", "0"))

    @validator("telegram_bot_username", pre=True, always=True)
    def set_bot_username(cls, v, values):
        """Extract bot username from token if not provided"""
        if v:
            return v
        token = values.get("telegram_bot_token", "")
        if token and "@" in token:
            return token.split("@")[1]
        return None

    @property
    def database_url(self) -> str:
        """Construct database URL from settings"""
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
