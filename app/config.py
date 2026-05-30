import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(..., validation_alias="GEMINI_API_KEY")
    CLAUDE_API_KEY: str = Field(..., validation_alias="CLAUDE_API_KEY")
    PHONE_NUMBER_ID: str = Field(..., validation_alias="PHONE_NUMBER_ID")
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = Field(..., validation_alias="WHATSAPP_BUSINESS_ACCOUNT_ID")
    WHATSAPP_TOKEN: str = Field(..., validation_alias="WHATSAPP_TOKEN")
    VERIFY_TOKEN: str = Field("my-secret-token", validation_alias="VERIFY_TOKEN")
    DATABASE_URL: str = Field("sqlite:///./cake_shop.db", validation_alias="DATABASE_URL")
    HOST: str = Field("0.0.0.0", validation_alias="HOST")
    PORT: int = Field(8000, validation_alias="PORT")
    GEMINI_MODEL_NAME: str = Field("gemini-2.5-flash", validation_alias="GEMINI_MODEL_NAME")

    # Load environment variables from .env file
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
