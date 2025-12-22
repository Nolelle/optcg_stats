const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// Leader types
export interface Leader {
  id: string;
  name: string;
  color: string;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface LeaderWithStats extends Leader {
  win_rate: number;
  games_played: number;
  first_win_rate: number;
  second_win_rate: number;
  tier: string | null;
  deck_count: number;
}

// Deck types
export interface Deck {
  id: number;
  leader_id: string;
  deck_list_json: string | null;
  win_rate: number;
  games_played: number;
  first_win_rate: number;
  second_win_rate: number;
  tier: string | null;
  source_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface DeckWithCost extends Deck {
  total_cost_usd: number | null;
  total_cost_eur: number | null;
  leader_name: string | null;
  leader_color: string | null;
  card_breakdown: Record<string, number> | null;
}

// Matchup types
export interface MatchupCell {
  leader_a_id: string;
  leader_b_id: string;
  win_rate: number;
  sample_size: number;
  first_win_rate: number | null;
  second_win_rate: number | null;
}

export interface MatchupMatrix {
  leaders: string[];
  leader_names: Record<string, string>;
  matrix: Record<string, Record<string, MatchupCell>>;
}

// Card types
export interface Card {
  id: string;
  name: string;
  set_code: string | null;
  rarity: string | null;
  card_type: string | null;
  color: string | null;
  cost: string | null;
  power: string | null;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface CardPriceInfo {
  source: string;
  price_usd: number | null;
  price_eur: number | null;
  market_price: number | null;
  low_price: number | null;
  high_price: number | null;
  fetched_at: string;
}

export interface CardWithPrice extends Card {
  prices: CardPriceInfo[];
  best_price_usd: number | null;
  best_price_eur: number | null;
}

export interface PriceMover {
  card_id: string;
  card_name: string;
  old_price: number;
  new_price: number;
  change_pct: number;
}

// API functions
export const api = {
  // Leaders
  getLeaders: () => fetchAPI<Leader[]>('/leaders'),
  getTierList: () => fetchAPI<LeaderWithStats[]>('/leaders/tier-list'),
  getLeader: (id: string) => fetchAPI<Leader>(`/leaders/${id}`),

  // Decks
  getDecks: (limit = 100, offset = 0) => 
    fetchAPI<Deck[]>(`/decks?limit=${limit}&offset=${offset}`),
  getMostPlayed: (limit = 20) => 
    fetchAPI<Deck[]>(`/decks/most-played?limit=${limit}`),
  getMostSuccessful: (minGames = 50, limit = 20) => 
    fetchAPI<Deck[]>(`/decks/most-successful?min_games=${minGames}&limit=${limit}`),
  getDecksByLeader: (leaderId: string) => 
    fetchAPI<Deck[]>(`/decks/leader/${leaderId}`),
  getDeck: (id: number) => fetchAPI<Deck>(`/decks/${id}`),
  getDeckWithCost: (id: number) => fetchAPI<DeckWithCost>(`/decks/${id}/with-cost`),

  // Matchups
  getMatchups: () => fetchAPI<MatchupCell[]>('/matchups'),
  getMatchupMatrix: () => fetchAPI<MatchupMatrix>('/matchups/matrix'),
  getMatchupsForLeader: (leaderId: string) => 
    fetchAPI<MatchupCell[]>(`/matchups/leader/${leaderId}`),

  // Cards
  getCards: (limit = 100, offset = 0) => 
    fetchAPI<Card[]>(`/cards?limit=${limit}&offset=${offset}`),
  searchCards: (query: string, limit = 50) => 
    fetchAPI<Card[]>(`/cards/search?q=${encodeURIComponent(query)}&limit=${limit}`),
  getCard: (id: string) => fetchAPI<Card>(`/cards/${id}`),
  getCardWithPrices: (id: string) => fetchAPI<CardWithPrice>(`/cards/${id}/with-prices`),

  // Prices
  getPriceHistory: (cardId: string, days = 30) => 
    fetchAPI<CardPriceInfo[]>(`/prices/card/${cardId}?days=${days}`),
  comparePrices: (cardId: string) => 
    fetchAPI<Record<string, number | null>>(`/prices/card/${cardId}/compare`),
  getTopMovers: (days = 7, limit = 20) => 
    fetchAPI<{ gainers: PriceMover[]; losers: PriceMover[] }>(`/prices/movers?days=${days}&limit=${limit}`),
};

