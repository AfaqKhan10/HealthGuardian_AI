# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# .env file ko pehle explicitly load kar lete hain (sab se safe tareeqa)
load_dotenv()   # yeh line bohat important hai local development mein

class Settings(BaseSettings):
    # Required fields from your .env
    DATABASE_URL: str
    GROQ_API_KEY: str

    # Optional / future fields (default values de sakte ho)
    SECRET_KEY: str = "change-this-to-a-very-long-random-secret-key-immediately"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Pydantic v2 style config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"          # .env mein extra keys ignore kar dega
    )


# Single global instance (most common & simple way)
settings = Settings()

