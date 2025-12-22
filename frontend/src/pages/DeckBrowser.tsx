import { useQuery } from '@tanstack/react-query';
import { api, Deck, DeckWithCost } from '../api/client';
import { TierBadge } from '../components/TierBadge';
import { WinRateBar } from '../components/WinRateBar';
import { PageLoader } from '../components/LoadingSpinner';
import { Link, useSearchParams } from 'react-router-dom';
import { DollarSign, Users, Trophy, Eye, ArrowUpDown } from 'lucide-react';
import { useState } from 'react';

type ViewMode = 'most-played' | 'most-successful' | 'all';
type SortKey = 'win_rate' | 'games_played';

export function DeckBrowser() {
  const [searchParams] = useSearchParams();
  const leaderFilter = searchParams.get('leader');
  
  const [viewMode, setViewMode] = useState<ViewMode>('most-played');
  const [sortBy, setSortBy] = useState<SortKey>('games_played');
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null);

  const { data: mostPlayed, isLoading: loadingPlayed } = useQuery({
    queryKey: ['decks', 'most-played'],
    queryFn: () => api.getMostPlayed(50),
    enabled: viewMode === 'most-played' && !leaderFilter,
  });

  const { data: mostSuccessful, isLoading: loadingSuccessful } = useQuery({
    queryKey: ['decks', 'most-successful'],
    queryFn: () => api.getMostSuccessful(50, 50),
    enabled: viewMode === 'most-successful' && !leaderFilter,
  });

  const { data: leaderDecks, isLoading: loadingLeader } = useQuery({
    queryKey: ['decks', 'leader', leaderFilter],
    queryFn: () => api.getDecksByLeader(leaderFilter!),
    enabled: !!leaderFilter,
  });

  const { data: deckWithCost, isLoading: loadingCost } = useQuery({
    queryKey: ['deck', 'cost', selectedDeck],
    queryFn: () => api.getDeckWithCost(selectedDeck!),
    enabled: !!selectedDeck,
  });

  const isLoading = loadingPlayed || loadingSuccessful || loadingLeader;

  let decks: Deck[] = [];
  if (leaderFilter) {
    decks = leaderDecks || [];
  } else if (viewMode === 'most-played') {
    decks = mostPlayed || [];
  } else if (viewMode === 'most-successful') {
    decks = mostSuccessful || [];
  }

  // Sort decks
  const sortedDecks = [...decks].sort((a, b) => {
    if (sortBy === 'win_rate') return b.win_rate - a.win_rate;
    return b.games_played - a.games_played;
  });

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-display text-4xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
          Deck Browser
        </h1>
        <p className="text-gray-400 mt-2">
          {leaderFilter 
            ? `Viewing decks for ${leaderFilter}` 
            : 'Browse the most played and successful decks'}
        </p>
      </div>

      {/* View Mode Tabs */}
      {!leaderFilter && (
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('most-played')}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
              ${viewMode === 'most-played' 
                ? 'bg-indigo-500 text-white' 
                : 'bg-[#1a1a24] text-gray-400 hover:text-white'}
            `}
          >
            <Users size={18} />
            Most Played
          </button>
          <button
            onClick={() => setViewMode('most-successful')}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
              ${viewMode === 'most-successful' 
                ? 'bg-indigo-500 text-white' 
                : 'bg-[#1a1a24] text-gray-400 hover:text-white'}
            `}
          >
            <Trophy size={18} />
            Most Successful
          </button>
        </div>
      )}

      {/* Sort */}
      <div className="flex items-center gap-2">
        <ArrowUpDown size={16} className="text-gray-400" />
        <span className="text-sm text-gray-400">Sort:</span>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as SortKey)}
          className="input-field text-sm"
        >
          <option value="games_played">Games Played</option>
          <option value="win_rate">Win Rate</option>
        </select>
      </div>

      {/* Decks Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {sortedDecks.map((deck, index) => (
          <DeckCard 
            key={deck.id} 
            deck={deck} 
            rank={index + 1}
            isSelected={selectedDeck === deck.id}
            onSelect={() => setSelectedDeck(deck.id === selectedDeck ? null : deck.id)}
          />
        ))}
      </div>

      {sortedDecks.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          No decks found
        </div>
      )}

      {/* Deck Cost Modal */}
      {selectedDeck && deckWithCost && (
        <DeckCostModal 
          deck={deckWithCost} 
          onClose={() => setSelectedDeck(null)} 
        />
      )}
    </div>
  );
}

function DeckCard({ 
  deck, 
  rank, 
  isSelected, 
  onSelect 
}: { 
  deck: Deck; 
  rank: number;
  isSelected: boolean;
  onSelect: () => void;
}) {
  return (
    <div 
      className={`
        card-container cursor-pointer transition-all
        ${isSelected ? 'ring-2 ring-indigo-500' : ''}
      `}
      onClick={onSelect}
    >
      <div className="flex items-start gap-4">
        {/* Rank */}
        <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-[#12121a] flex items-center justify-center">
          <span className="font-bold text-lg text-gray-400">#{rank}</span>
        </div>

        {/* Deck Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <TierBadge tier={deck.tier} size="sm" />
            <h3 className="font-semibold text-white">{deck.leader_id}</h3>
          </div>

          <WinRateBar winRate={deck.win_rate} height="sm" />
        </div>

        {/* Stats */}
        <div className="text-right">
          <div className="text-sm text-gray-400">Games</div>
          <div className="font-semibold text-white">
            {deck.games_played.toLocaleString()}
          </div>
        </div>
      </div>

      {/* First/Second Stats */}
      <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-[#2a2a3a]">
        <div>
          <div className="text-xs text-green-400 mb-1">Going First</div>
          <WinRateBar winRate={deck.first_win_rate} height="sm" />
        </div>
        <div>
          <div className="text-xs text-blue-400 mb-1">Going Second</div>
          <WinRateBar winRate={deck.second_win_rate} height="sm" />
        </div>
      </div>

      {/* View Details Hint */}
      <div className="flex items-center justify-center gap-2 mt-4 text-sm text-gray-500">
        <Eye size={14} />
        <span>Click to view deck cost</span>
      </div>
    </div>
  );
}

function DeckCostModal({ deck, onClose }: { deck: DeckWithCost; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="card-container max-w-lg w-full max-h-[80vh] overflow-auto">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h3 className="font-display text-xl font-bold text-white">
              {deck.leader_name || deck.leader_id}
            </h3>
            <p className="text-gray-400 text-sm">Deck Cost Breakdown</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/10 transition-colors"
          >
            ×
          </button>
        </div>

        {/* Total Cost */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-[#12121a] rounded-lg p-4 text-center">
            <div className="flex items-center justify-center gap-1 text-green-400 mb-1">
              <DollarSign size={16} />
              <span className="text-sm">TCGPlayer (USD)</span>
            </div>
            <div className="text-2xl font-bold text-white">
              ${deck.total_cost_usd?.toFixed(2) || 'N/A'}
            </div>
          </div>
          <div className="bg-[#12121a] rounded-lg p-4 text-center">
            <div className="flex items-center justify-center gap-1 text-blue-400 mb-1">
              <span className="text-sm">Cardmarket (EUR)</span>
            </div>
            <div className="text-2xl font-bold text-white">
              €{deck.total_cost_eur?.toFixed(2) || 'N/A'}
            </div>
          </div>
        </div>

        {/* Card Breakdown */}
        {deck.card_breakdown && Object.keys(deck.card_breakdown).length > 0 && (
          <div>
            <h4 className="font-semibold text-white mb-3">Card Prices</h4>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {Object.entries(deck.card_breakdown)
                .sort(([, a], [, b]) => b - a)
                .map(([cardId, price]) => (
                  <div 
                    key={cardId}
                    className="flex items-center justify-between py-2 px-3 bg-[#12121a] rounded-lg"
                  >
                    <span className="text-gray-300">{cardId}</span>
                    <span className="font-medium text-white">${price.toFixed(2)}</span>
                  </div>
                ))}
            </div>
          </div>
        )}

        <button
          onClick={onClose}
          className="w-full btn-primary mt-6"
        >
          Close
        </button>
      </div>
    </div>
  );
}

