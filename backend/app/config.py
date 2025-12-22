from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "OPTCG Stats API"
    database_url: str = "sqlite:///./optcg_stats.db"
    debug: bool = True
    
    # Scraper settings
    scrape_interval_hours: int = 6
    request_delay_seconds: float = 1.0
    
    # Price cache TTL in hours
    price_cache_ttl_hours: int = 4
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

