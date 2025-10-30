from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Finance Planner API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    

    DATABASE_URL: str = "sqlite:///./finance.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
