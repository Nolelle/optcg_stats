"""
Seed script to populate the database with sample data for testing.
Run with: python seed_data.py
"""
import json
from datetime import datetime, timedelta
import random
from app.database import SessionLocal, engine, Base
from app.models import Leader, Deck, Matchup, Card, CardPrice

# Sample leaders
SAMPLE_LEADERS = [
    {"id": "OP01-001", "name": "Monkey.D.Luffy", "color": "Red"},
    {"id": "OP01-002", "name": "Trafalgar Law", "color": "Blue"},
    {"id": "OP01-003", "name": "Eustass Kid", "color": "Green"},
    {"id": "OP02-001", "name": "Edward Newgate", "color": "Red"},
    {"id": "OP02-002", "name": "Nami", "color": "Yellow"},
    {"id": "OP03-001", "name": "Charlotte Linlin", "color": "Yellow"},
    {"id": "OP03-002", "name": "Zoro", "color": "Green"},
    {"id": "OP04-001", "name": "Kaido", "color": "Purple"},
    {"id": "OP04-002", "name": "Yamato", "color": "Purple/Yellow"},
    {"id": "OP05-001", "name": "Sabo", "color": "Blue/Yellow"},
    {"id": "OP05-002", "name": "Rebecca", "color": "Red/Purple"},
    {"id": "OP06-001", "name": "Rob Lucci", "color": "Black"},
    {"id": "OP06-002", "name": "Perona", "color": "Purple"},
    {"id": "OP07-001", "name": "Bonney", "color": "Blue/Purple"},
    {"id": "OP07-002", "name": "Gecko Moria", "color": "Black/Yellow"},
]

# Sample cards
SAMPLE_CARDS = [
    {"id": "OP01-004", "name": "Roronoa Zoro", "set_code": "OP01", "rarity": "SR", "card_type": "Character", "color": "Red"},
    {"id": "OP01-005", "name": "Nami", "set_code": "OP01", "rarity": "R", "card_type": "Character", "color": "Red"},
    {"id": "OP01-006", "name": "Usopp", "set_code": "OP01", "rarity": "R", "card_type": "Character", "color": "Red"},
    {"id": "OP01-016", "name": "Gum-Gum Red Roc", "set_code": "OP01", "rarity": "SR", "card_type": "Event", "color": "Red"},
    {"id": "OP01-025", "name": "Shanks", "set_code": "OP01", "rarity": "SEC", "card_type": "Character", "color": "Red"},
    {"id": "OP02-004", "name": "Marco", "set_code": "OP02", "rarity": "SR", "card_type": "Character", "color": "Red"},
    {"id": "OP02-013", "name": "Portgas.D.Ace", "set_code": "OP02", "rarity": "SR", "card_type": "Character", "color": "Red"},
    {"id": "OP03-040", "name": "Charlotte Katakuri", "set_code": "OP03", "rarity": "SR", "card_type": "Character", "color": "Yellow"},
    {"id": "OP04-031", "name": "Yamato", "set_code": "OP04", "rarity": "SEC", "card_type": "Character", "color": "Purple"},
    {"id": "OP05-074", "name": "Monkey.D.Luffy", "set_code": "OP05", "rarity": "L", "card_type": "Leader", "color": "Red"},
]


def calculate_tier(win_rate: float) -> str:
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


def seed_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(CardPrice).delete()
        db.query(Card).delete()
        db.query(Matchup).delete()
        db.query(Deck).delete()
        db.query(Leader).delete()
        db.commit()
        
        print("Cleared existing data")
        
        # Seed leaders
        leaders = []
        for leader_data in SAMPLE_LEADERS:
            leader = Leader(
                id=leader_data["id"],
                name=leader_data["name"],
                color=leader_data["color"],
                image_url=None
            )
            db.add(leader)
            leaders.append(leader)
        db.commit()
        print(f"Seeded {len(leaders)} leaders")
        
        # Seed decks with random stats
        decks = []
        for leader in leaders:
            # Create 1-3 deck variants per leader
            for variant in range(random.randint(1, 3)):
                win_rate = random.uniform(42, 58)
                first_wr = win_rate + random.uniform(-3, 5)  # Usually better going first
                second_wr = win_rate + random.uniform(-5, 2)
                games = random.randint(100, 5000)
                
                deck = Deck(
                    leader_id=leader.id,
                    deck_list_json=json.dumps({
                        "OP01-004": 4,
                        "OP01-005": 4,
                        "OP01-006": 4,
                        "OP01-016": 4,
                        "OP01-025": 2,
                    }),
                    win_rate=round(win_rate, 2),
                    games_played=games,
                    first_win_rate=round(first_wr, 2),
                    second_win_rate=round(second_wr, 2),
                    tier=calculate_tier(win_rate),
                    source_url="https://tcgmatchmaking.com"
                )
                db.add(deck)
                decks.append(deck)
        db.commit()
        print(f"Seeded {len(decks)} decks")
        
        # Seed matchups
        matchups_count = 0
        for i, leader_a in enumerate(leaders):
            for leader_b in leaders[i+1:]:
                # Random win rate for leader_a
                win_rate_a = random.uniform(35, 65)
                sample = random.randint(50, 500)
                first_wr = win_rate_a + random.uniform(-5, 5)
                second_wr = win_rate_a + random.uniform(-5, 5)
                
                matchup = Matchup(
                    leader_a_id=leader_a.id,
                    leader_b_id=leader_b.id,
                    win_rate_a=round(win_rate_a, 2),
                    sample_size=sample,
                    first_win_rate=round(first_wr, 2),
                    second_win_rate=round(second_wr, 2)
                )
                db.add(matchup)
                matchups_count += 1
        db.commit()
        print(f"Seeded {matchups_count} matchups")
        
        # Seed cards
        cards = []
        for card_data in SAMPLE_CARDS:
            card = Card(
                id=card_data["id"],
                name=card_data["name"],
                set_code=card_data["set_code"],
                rarity=card_data["rarity"],
                card_type=card_data["card_type"],
                color=card_data["color"],
                image_url=None
            )
            db.add(card)
            cards.append(card)
        db.commit()
        print(f"Seeded {len(cards)} cards")
        
        # Seed prices with history
        prices_count = 0
        for card in cards:
            # Base price depends on rarity
            base_price = {
                "C": random.uniform(0.10, 0.50),
                "UC": random.uniform(0.25, 1.00),
                "R": random.uniform(1.00, 5.00),
                "SR": random.uniform(5.00, 25.00),
                "SEC": random.uniform(20.00, 100.00),
                "L": random.uniform(2.00, 10.00),
            }.get(card.rarity, random.uniform(0.50, 2.00))
            
            # Create price history for last 30 days
            for days_ago in range(30, -1, -7):
                price_variation = base_price * random.uniform(0.85, 1.15)
                
                # TCGPlayer price
                tcg_price = CardPrice(
                    card_id=card.id,
                    source="tcgplayer",
                    price_usd=round(price_variation, 2),
                    market_price=round(price_variation * 0.95, 2),
                    low_price=round(price_variation * 0.80, 2),
                    high_price=round(price_variation * 1.20, 2),
                    fetched_at=datetime.utcnow() - timedelta(days=days_ago)
                )
                db.add(tcg_price)
                
                # Cardmarket price (in EUR)
                eur_rate = 0.92
                cm_price = CardPrice(
                    card_id=card.id,
                    source="cardmarket",
                    price_eur=round(price_variation * eur_rate, 2),
                    price_usd=round(price_variation, 2),
                    market_price=round(price_variation * eur_rate * 0.95, 2),
                    low_price=round(price_variation * eur_rate * 0.80, 2),
                    fetched_at=datetime.utcnow() - timedelta(days=days_ago)
                )
                db.add(cm_price)
                prices_count += 2
        
        db.commit()
        print(f"Seeded {prices_count} price entries")
        
        print("\n✅ Database seeded successfully!")
        print(f"   Leaders: {len(leaders)}")
        print(f"   Decks: {len(decks)}")
        print(f"   Matchups: {matchups_count}")
        print(f"   Cards: {len(cards)}")
        print(f"   Prices: {prices_count}")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

