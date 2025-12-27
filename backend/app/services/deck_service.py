from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import json
from app.models import Deck, Leader, Card, CardPrice
from app.schemas.deck import DeckCreate, DeckWithCost, DeckDetailedResponse, CardInDeck


class DeckService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Deck]:
        return self.db.query(Deck).order_by(desc(Deck.games_played)).offset(offset).limit(limit).all()
    
    def get_by_id(self, deck_id: int) -> Optional[Deck]:
        return self.db.query(Deck).filter(Deck.id == deck_id).first()
    
    def get_by_leader(self, leader_id: str) -> List[Deck]:
        return self.db.query(Deck).filter(Deck.leader_id == leader_id).order_by(desc(Deck.win_rate)).all()
    
    def create(self, deck: DeckCreate) -> Deck:
        db_deck = Deck(**deck.model_dump())
        self.db.add(db_deck)
        self.db.commit()
        self.db.refresh(db_deck)
        return db_deck
    
    def get_most_played(self, limit: int = 20) -> List[Deck]:
        return self.db.query(Deck).order_by(desc(Deck.games_played)).limit(limit).all()
    
    def get_most_successful(self, min_games: int = 50, limit: int = 20) -> List[Deck]:
        return self.db.query(Deck).filter(
            Deck.games_played >= min_games
        ).order_by(desc(Deck.win_rate)).limit(limit).all()
    
    def get_with_cost(self, deck_id: int) -> Optional[DeckWithCost]:
        deck = self.get_by_id(deck_id)
        if not deck:
            return None
        
        leader = self.db.query(Leader).filter(Leader.id == deck.leader_id).first()
        
        total_usd = 0.0
        total_eur = 0.0
        card_breakdown = {}
        
        if deck.deck_list_json:
            try:
                deck_list = json.loads(deck.deck_list_json)
                for card_id, count in deck_list.items():
                    price = self.db.query(CardPrice).filter(
                        CardPrice.card_id == card_id
                    ).order_by(desc(CardPrice.fetched_at)).first()
                    
                    if price:
                        card_price_usd = (price.price_usd or price.market_price or 0) * count
                        card_price_eur = (price.price_eur or 0) * count
                        total_usd += card_price_usd
                        total_eur += card_price_eur
                        card_breakdown[card_id] = card_price_usd
            except json.JSONDecodeError:
                pass
        
        return DeckWithCost(
            id=deck.id,
            leader_id=deck.leader_id,
            deck_list_json=deck.deck_list_json,
            win_rate=deck.win_rate,
            games_played=deck.games_played,
            first_win_rate=deck.first_win_rate,
            second_win_rate=deck.second_win_rate,
            tier=deck.tier,
            source_url=deck.source_url,
            created_at=deck.created_at,
            updated_at=deck.updated_at,
            total_cost_usd=round(total_usd, 2) if total_usd > 0 else None,
            total_cost_eur=round(total_eur, 2) if total_eur > 0 else None,
            leader_name=leader.name if leader else None,
            leader_color=leader.color if leader else None,
            card_breakdown=card_breakdown if card_breakdown else None
        )
    
    def get_detailed(self, deck_id: int) -> Optional[DeckDetailedResponse]:
        """Get deck with full card details for deck viewer"""
        deck = self.get_by_id(deck_id)
        if not deck:
            return None
        
        leader = self.db.query(Leader).filter(Leader.id == deck.leader_id).first()
        
        cards: List[CardInDeck] = []
        total_usd = 0.0
        total_eur = 0.0
        cost_curve: dict[str, int] = {}
        
        if deck.deck_list_json:
            try:
                deck_list = json.loads(deck.deck_list_json)
                for card_id, count in deck_list.items():
                    # Get card details
                    card = self.db.query(Card).filter(Card.id == card_id).first()
                    
                    # Get latest price
                    price = self.db.query(CardPrice).filter(
                        CardPrice.card_id == card_id
                    ).order_by(desc(CardPrice.fetched_at)).first()
                    
                    price_usd = None
                    price_eur = None
                    if price:
                        price_usd = price.price_usd or price.market_price
                        price_eur = price.price_eur
                        if price_usd:
                            total_usd += price_usd * count
                        if price_eur:
                            total_eur += price_eur * count
                    
                    # Parse cost for curve
                    card_cost = None
                    if card and card.cost:
                        try:
                            card_cost = int(card.cost)
                            cost_key = str(card_cost) if card_cost <= 10 else "10+"
                            cost_curve[cost_key] = cost_curve.get(cost_key, 0) + count
                        except ValueError:
                            pass
                    
                    cards.append(CardInDeck(
                        id=card_id,
                        name=card.name if card else card_id,
                        card_type=card.card_type if card else None,
                        cost=card_cost,
                        power=int(card.power) if card and card.power and card.power.isdigit() else None,
                        color=card.color if card else None,
                        rarity=card.rarity if card else None,
                        image_url=card.image_url if card else None,
                        count=count,
                        price_usd=price_usd,
                        price_eur=price_eur
                    ))
            except json.JSONDecodeError:
                pass
        
        # Sort cards by type then cost
        type_order = {"Leader": 0, "Character": 1, "Event": 2, "Stage": 3}
        cards.sort(key=lambda c: (type_order.get(c.card_type or "", 99), c.cost or 0))
        
        return DeckDetailedResponse(
            id=deck.id,
            leader_id=deck.leader_id,
            deck_list_json=deck.deck_list_json,
            win_rate=deck.win_rate,
            games_played=deck.games_played,
            first_win_rate=deck.first_win_rate,
            second_win_rate=deck.second_win_rate,
            tier=deck.tier,
            source_url=deck.source_url,
            created_at=deck.created_at,
            updated_at=deck.updated_at,
            total_cost_usd=round(total_usd, 2) if total_usd > 0 else None,
            total_cost_eur=round(total_eur, 2) if total_eur > 0 else None,
            leader_name=leader.name if leader else None,
            leader_color=leader.color if leader else None,
            leader_image_url=leader.image_url if leader else None,
            cards=cards,
            cost_curve=cost_curve
        )

