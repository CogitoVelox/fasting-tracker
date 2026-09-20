from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:////data/fasting.db"
    fast_goal_hours: float = 16
    timezone_name: str = "America/New_York"


settings = Settings()
