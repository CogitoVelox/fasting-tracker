from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:////data/fasting.db"
    fast_start_hour: int = 19
    fast_end_hour: int = 9


settings = Settings()

timezone_name: str = "America/New_York"
