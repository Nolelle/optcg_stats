import httpx
import asyncio
from abc import ABC, abstractmethod
from typing import Optional
from app.config import get_settings

settings = get_settings()


class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self):
        self.delay = settings.request_delay_seconds
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    
    async def fetch(self, url: str) -> Optional[str]:
        """Fetch a URL with rate limiting"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                await asyncio.sleep(self.delay)
                return response.text
            except httpx.HTTPError as e:
                print(f"Error fetching {url}: {e}")
                return None
    
    @abstractmethod
    async def scrape(self):
        """Main scraping method to be implemented by subclasses"""
        pass

