from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.scrapers.base import BaseScraper
from app.models import Leader, Deck, Matchup
from app.schemas.leader import LeaderCreate
from app.schemas.deck import DeckCreate
from app.schemas.matchup import MatchupCreate
from app.services import LeaderService, DeckService, MatchupService


class TCGMatchmakingScraper(BaseScraper):
    """Scraper for TCG Matchmaking OPTCG stats"""
    
    BASE_URL = "https://optcgsim-stats.web.app"  # Example URL - update with actual
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.leader_service = LeaderService(db)
        self.deck_service = DeckService(db)
        self.matchup_service = MatchupService(db)
    
    async def scrape(self) -> Dict[str, int]:
        """Main scraping entry point"""
        results = {
            "leaders": 0,
            "decks": 0,
            "matchups": 0
        }
        
        # Scrape leaders and their stats
        leaders = await self.scrape_leaders()
        results["leaders"] = len(leaders)
        
        # Scrape matchup data
        matchups = await self.scrape_matchups()
        results["matchups"] = len(matchups)
        
        return results
    
    async def scrape_leaders(self) -> List[Leader]:
        """Scrape leader statistics"""
        url = f"{self.BASE_URL}/leaders"  # Adjust endpoint as needed
        html = await self.fetch(url)
        
        if not html:
            return []
        
        leaders = []
        soup = BeautifulSoup(html, "lxml")
        
        # This is a template - adjust selectors based on actual site structure
        leader_rows = soup.select(".leader-row")  # Adjust selector
        
        for row in leader_rows:
            try:
                leader_id = row.get("data-id", "")
                name = row.select_one(".leader-name").text.strip()
                color = row.select_one(".leader-color").text.strip()
                image_url = row.select_one("img")
                image_url = image_url.get("src") if image_url else None
                
                # Stats
                win_rate = float(row.select_one(".win-rate").text.strip().replace("%", ""))
                games = int(row.select_one(".games-played").text.strip().replace(",", ""))
                
                # Create/update leader
                leader_data = LeaderCreate(
                    id=leader_id,
                    name=name,
                    color=color,
                    image_url=image_url
                )
                leader = self.leader_service.upsert(leader_data)
                
                # Create deck entry for aggregate stats
                deck_data = DeckCreate(
                    leader_id=leader_id,
                    win_rate=win_rate,
                    games_played=games,
                    tier=self._calculate_tier(win_rate)
                )
                self.deck_service.create(deck_data)
                
                leaders.append(leader)
                
            except (AttributeError, ValueError) as e:
                print(f"Error parsing leader row: {e}")
                continue
        
        return leaders
    
    async def scrape_matchups(self) -> List[Matchup]:
        """Scrape matchup matrix data"""
        url = f"{self.BASE_URL}/matchups"  # Adjust endpoint as needed
        html = await self.fetch(url)
        
        if not html:
            return []
        
        matchups = []
        soup = BeautifulSoup(html, "lxml")
        
        # This is a template - adjust selectors based on actual site structure
        matchup_cells = soup.select(".matchup-cell")  # Adjust selector
        
        for cell in matchup_cells:
            try:
                leader_a = cell.get("data-leader-a", "")
                leader_b = cell.get("data-leader-b", "")
                win_rate = float(cell.select_one(".win-rate").text.strip().replace("%", ""))
                sample_size = int(cell.get("data-sample", "0"))
                
                # Get first/second rates if available
                first_wr = cell.get("data-first-wr")
                second_wr = cell.get("data-second-wr")
                
                matchup_data = MatchupCreate(
                    leader_a_id=leader_a,
                    leader_b_id=leader_b,
                    win_rate_a=win_rate,
                    sample_size=sample_size,
                    first_win_rate=float(first_wr) if first_wr else None,
                    second_win_rate=float(second_wr) if second_wr else None
                )
                matchup = self.matchup_service.upsert(matchup_data)
                matchups.append(matchup)
                
            except (AttributeError, ValueError) as e:
                print(f"Error parsing matchup cell: {e}")
                continue
        
        return matchups
    
    def _calculate_tier(self, win_rate: float) -> str:
        if win_rate >= 55:
            return "S"
        elif win_rate >= 52:
            return "A"
        elif win_rate >= 49:
            return "B"
        elif win_rate >= 46:
            return "C"
        else:
            return "D"

