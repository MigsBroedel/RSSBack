from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Personalized RSS Feed"
    BACKEND_CORS_ORIGINS: List[str] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    SECRET_KEY: str = "change_me_super_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    POSTGRES_SERVER: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_PORT: str = "5432"
    
    SQLALCHEMY_DATABASE_URI: str | None = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, any]) -> any:
        if isinstance(v, str):
            return v
        
        # Check if we have a generic DATABASE_URL (common in PaaS like Render)
        # We might need to ensure it uses asyncpg driver
        import os
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif db_url.startswith("postgresql://") and "asyncpg" not in db_url:
                 db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return db_url

        return f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"

    REDIS_HOST: str | None = None
    REDIS_PORT: int = 6379
    REDIS_URL: str | None = None

    @validator("REDIS_URL", pre=True)
    def assemble_redis_url(cls, v: str | None, values: dict[str, any]) -> any:
        if isinstance(v, str):
            return v
        
        if values.get("REDIS_HOST"):
             return f"redis://{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/0"
        
        return None

    class Config:
        case_sensitive = True
        env_file = ".env.example"

settings = Settings()
