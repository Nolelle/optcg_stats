import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';
import type { DeckWithCost } from '../api/client';
import { TierBadge } from '../components/TierBadge';
import { WinRateBar } from '../components/WinRateBar';
import { ColorBadge } from '../components/ColorBadge';
import { PageLoader } from '../components/LoadingSpinner';
import { ArrowLeft, DollarSign, TrendingUp, TrendingDown, Users } from 'lucide-react';
import { useState } from 'react';

export function DeckViewer() {
  const { deckId } = useParams<{ deckId: string }>();
  const [priceSource, setPriceSource] = useState<'tcgplayer' | 'cardmarket'>('tcgplayer');

  const { data: deck, isLoading, error } = useQuery({
    queryKey: ['deck', 'cost', deckId],
    queryFn: () => api.getDeckWithCost(Number(deckId)),
    enabled: !!deckId,
  });

  if (isLoading) return <PageLoader />;
  if (error || !deck) return <div className="text-red-400">Failed to load deck</div>;

  const deckList = deck.deck_list_json ? JSON.parse(deck.deck_list_json) : {};
  const cardEntries = Object.entries(deckList) as [string, number][];

  const totalPrice = priceSource === 'tcgplayer' 
    ? deck.total_cost_usd 
    : deck.total_cost_eur;

  return (
    <div className="space-y-8">
      {/* Back Button */}
      <Link 
        to="/decks"
        className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft size={20} />
        Back to Deck Browser
      </Link>

      {/* Header */}
      <div className="card-container">
        <div className="flex flex-col md:flex-row md:items-start gap-6">
          {/* Leader Info */}
          <div className="flex items-start gap-4">
            <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
              <span className="text-3xl font-bold text-indigo-400">
                {deck.leader_name?.charAt(0) || deck.leader_id.charAt(0)}
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <TierBadge tier={deck.tier} size="md" />
                <h1 className="font-display text-2xl font-bold text-white">
                  {deck.leader_name || deck.leader_id}
                </h1>
              </div>
              <div className="flex items-center gap-2">
                {deck.leader_color && <ColorBadge color={deck.leader_color} />}
                <span className="text-gray-400">{deck.leader_id}</span>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-[#12121a] rounded-lg">
              <div className="flex items-center justify-center gap-1 text-gray-400 text-xs mb-1">
                <Users size={12} />
                <span>Games</span>
              </div>
              <div className="text-xl font-bold text-white">
                {deck.games_played.toLocaleString()}
              </div>
            </div>
            <div className="text-center p-3 bg-[#12121a] rounded-lg">
              <div className="text-xs text-gray-400 mb-1">Win Rate</div>
              <div className="text-xl font-bold text-white">
                {deck.win_rate.toFixed(1)}%
              </div>
            </div>
            <div className="text-center p-3 bg-[#12121a] rounded-lg">
              <div className="flex items-center justify-center gap-1 text-green-400 text-xs mb-1">
                <TrendingUp size={12} />
                <span>1st</span>
              </div>
              <div className="text-xl font-bold text-white">
                {deck.first_win_rate.toFixed(1)}%
              </div>
            </div>
            <div className="text-center p-3 bg-[#12121a] rounded-lg">
              <div className="flex items-center justify-center gap-1 text-blue-400 text-xs mb-1">
                <TrendingDown size={12} />
                <span>2nd</span>
              </div>
              <div className="text-xl font-bold text-white">
                {deck.second_win_rate.toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Price Section */}
      <div className="card-container">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <DollarSign className="text-green-400" size={20} />
            <h2 className="font-display text-lg font-semibold text-white">Deck Cost</h2>
          </div>
          
          {/* Price Source Toggle */}
          <div className="flex gap-1 bg-[#12121a] p-1 rounded-lg">
            <button
              onClick={() => setPriceSource('tcgplayer')}
              className={`
                px-3 py-1.5 rounded text-sm font-medium transition-all
                ${priceSource === 'tcgplayer' 
                  ? 'bg-green-500 text-white' 
                  : 'text-gray-400 hover:text-white'}
              `}
            >
              TCGPlayer (USD)
            </button>
            <button
              onClick={() => setPriceSource('cardmarket')}
              className={`
                px-3 py-1.5 rounded text-sm font-medium transition-all
                ${priceSource === 'cardmarket' 
                  ? 'bg-blue-500 text-white' 
                  : 'text-gray-400 hover:text-white'}
              `}
            >
              Cardmarket (EUR)
            </button>
          </div>
        </div>

        <div className="text-center py-6 bg-[#12121a] rounded-lg mb-6">
          <div className="text-sm text-gray-400 mb-1">Total Deck Cost</div>
          <div className="text-4xl font-bold text-white">
            {priceSource === 'tcgplayer' ? '$' : '€'}
            {totalPrice?.toFixed(2) || 'N/A'}
          </div>
        </div>

        {/* Card Breakdown */}
        {deck.card_breakdown && Object.keys(deck.card_breakdown).length > 0 && (
          <div>
            <h3 className="font-semibold text-white mb-3">Card Price Breakdown</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-96 overflow-y-auto">
              {Object.entries(deck.card_breakdown)
                .sort(([, a], [, b]) => b - a)
                .map(([cardId, price]) => {
                  const count = deckList[cardId] || 1;
                  return (
                    <div 
                      key={cardId}
                      className="flex items-center justify-between p-3 bg-[#12121a] rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <span className="w-6 h-6 rounded bg-indigo-500/20 text-indigo-400 text-xs font-bold flex items-center justify-center">
                          {count}x
                        </span>
                        <span className="text-gray-300">{cardId}</span>
                      </div>
                      <span className="font-medium text-white">
                        ${price.toFixed(2)}
                      </span>
                    </div>
                  );
                })}
            </div>
          </div>
        )}
      </div>

      {/* Deck List */}
      {cardEntries.length > 0 && (
        <div className="card-container">
          <h2 className="font-display text-lg font-semibold text-white mb-4">
            Deck List ({cardEntries.reduce((sum, [, count]) => sum + count, 0)} cards)
          </h2>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {cardEntries.map(([cardId, count]) => (
              <div 
                key={cardId}
                className="relative group"
              >
                <div className="aspect-[3/4] rounded-lg bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-[#2a2a3a] flex items-center justify-center group-hover:border-indigo-500/50 transition-colors">
                  <span className="text-sm text-gray-400">{cardId}</span>
                </div>
                <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-indigo-500 text-white text-xs font-bold flex items-center justify-center">
                  {count}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Source */}
      {deck.source_url && (
        <div className="text-center text-sm text-gray-500">
          Data from: <a href={deck.source_url} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline">{deck.source_url}</a>
        </div>
      )}
    </div>
  );
}

