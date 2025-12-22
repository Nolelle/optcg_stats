import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { Card, CardWithPrice, PriceMover } from '../api/client';
import { PageLoader } from '../components/LoadingSpinner';
import { useState } from 'react';
import { Search, TrendingUp, TrendingDown, DollarSign, ArrowRight } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export function Market() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCard, setSelectedCard] = useState<string | null>(null);

  const { data: movers, isLoading: loadingMovers } = useQuery({
    queryKey: ['priceMovers'],
    queryFn: () => api.getTopMovers(7, 10),
  });

  const { data: searchResults, isLoading: loadingSearch } = useQuery({
    queryKey: ['cardSearch', searchQuery],
    queryFn: () => api.searchCards(searchQuery, 20),
    enabled: searchQuery.length >= 2,
  });

  const { data: cardWithPrice, isLoading: loadingCard } = useQuery({
    queryKey: ['cardPrice', selectedCard],
    queryFn: () => api.getCardWithPrices(selectedCard!),
    enabled: !!selectedCard,
  });

  const { data: priceHistory } = useQuery({
    queryKey: ['priceHistory', selectedCard],
    queryFn: () => api.getPriceHistory(selectedCard!, 30),
    enabled: !!selectedCard,
  });

  if (loadingMovers) return <PageLoader />;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-display text-4xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
          Market Dashboard
        </h1>
        <p className="text-gray-400 mt-2">
          Card prices from TCGPlayer and Cardmarket
        </p>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
        <input
          type="text"
          placeholder="Search cards..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input-field w-full pl-10"
        />
        
        {/* Search Results Dropdown */}
        {searchQuery.length >= 2 && searchResults && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-[#1a1a24] rounded-lg border border-[#2a2a3a] shadow-xl max-h-80 overflow-y-auto z-20">
            {loadingSearch ? (
              <div className="p-4 text-center text-gray-400">Searching...</div>
            ) : searchResults.length === 0 ? (
              <div className="p-4 text-center text-gray-400">No cards found</div>
            ) : (
              searchResults.map(card => (
                <button
                  key={card.id}
                  onClick={() => {
                    setSelectedCard(card.id);
                    setSearchQuery('');
                  }}
                  className="w-full flex items-center gap-3 p-3 hover:bg-white/5 transition-colors text-left"
                >
                  <div className="w-10 h-14 rounded bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
                    {card.image_url ? (
                      <img src={card.image_url} alt={card.name} className="w-full h-full object-cover rounded" />
                    ) : (
                      <span className="text-xs text-indigo-400">{card.id}</span>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-white truncate">{card.name}</div>
                    <div className="text-sm text-gray-400">{card.id} • {card.rarity}</div>
                  </div>
                  <ArrowRight size={16} className="text-gray-500" />
                </button>
              ))
            )}
          </div>
        )}
      </div>

      {/* Top Movers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Gainers */}
        <div className="card-container">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="text-green-400" size={20} />
            <h2 className="font-display text-lg font-semibold text-white">Top Gainers</h2>
            <span className="text-sm text-gray-500">(7 days)</span>
          </div>
          
          <div className="space-y-2">
            {movers?.gainers.map((mover, index) => (
              <MoverRow 
                key={mover.card_id} 
                mover={mover} 
                rank={index + 1}
                isGainer={true}
                onClick={() => setSelectedCard(mover.card_id)}
              />
            ))}
            {(!movers?.gainers || movers.gainers.length === 0) && (
              <div className="text-center py-4 text-gray-400">No data available</div>
            )}
          </div>
        </div>

        {/* Losers */}
        <div className="card-container">
          <div className="flex items-center gap-2 mb-4">
            <TrendingDown className="text-red-400" size={20} />
            <h2 className="font-display text-lg font-semibold text-white">Top Losers</h2>
            <span className="text-sm text-gray-500">(7 days)</span>
          </div>
          
          <div className="space-y-2">
            {movers?.losers.map((mover, index) => (
              <MoverRow 
                key={mover.card_id} 
                mover={mover} 
                rank={index + 1}
                isGainer={false}
                onClick={() => setSelectedCard(mover.card_id)}
              />
            ))}
            {(!movers?.losers || movers.losers.length === 0) && (
              <div className="text-center py-4 text-gray-400">No data available</div>
            )}
          </div>
        </div>
      </div>

      {/* Selected Card Detail */}
      {selectedCard && cardWithPrice && (
        <CardDetailPanel 
          card={cardWithPrice}
          priceHistory={priceHistory || []}
          onClose={() => setSelectedCard(null)}
          isLoading={loadingCard}
        />
      )}
    </div>
  );
}

function MoverRow({ 
  mover, 
  rank, 
  isGainer,
  onClick 
}: { 
  mover: PriceMover; 
  rank: number;
  isGainer: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 p-3 bg-[#12121a] rounded-lg hover:bg-[#1a1a24] transition-colors text-left"
    >
      <span className="text-gray-500 font-medium w-6">#{rank}</span>
      <div className="flex-1 min-w-0">
        <div className="font-medium text-white truncate">{mover.card_name}</div>
        <div className="text-sm text-gray-400">{mover.card_id}</div>
      </div>
      <div className="text-right">
        <div className="font-semibold text-white">${mover.new_price.toFixed(2)}</div>
        <div className={`text-sm font-medium ${isGainer ? 'text-green-400' : 'text-red-400'}`}>
          {isGainer ? '+' : ''}{mover.change_pct.toFixed(1)}%
        </div>
      </div>
    </button>
  );
}

function CardDetailPanel({ 
  card, 
  priceHistory,
  onClose,
  isLoading 
}: { 
  card: CardWithPrice;
  priceHistory: { fetched_at: string; price_usd: number | null }[];
  onClose: () => void;
  isLoading: boolean;
}) {
  const chartData = priceHistory.map(p => ({
    date: new Date(p.fetched_at).toLocaleDateString(),
    price: p.price_usd || 0,
  }));

  return (
    <div className="card-container">
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-start gap-4">
          <div className="w-20 h-28 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center overflow-hidden">
            {card.image_url ? (
              <img src={card.image_url} alt={card.name} className="w-full h-full object-cover" />
            ) : (
              <span className="text-xl font-bold text-indigo-400">{card.id.slice(0, 4)}</span>
            )}
          </div>
          <div>
            <h3 className="font-display text-xl font-bold text-white">{card.name}</h3>
            <div className="text-gray-400 mt-1">
              {card.id} • {card.set_code} • {card.rarity}
            </div>
            <div className="flex items-center gap-2 mt-2">
              {card.color && (
                <span className="px-2 py-1 bg-[#12121a] rounded text-xs text-gray-300">
                  {card.color}
                </span>
              )}
              {card.card_type && (
                <span className="px-2 py-1 bg-[#12121a] rounded text-xs text-gray-300">
                  {card.card_type}
                </span>
              )}
            </div>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
        >
          ×
        </button>
      </div>

      {/* Prices */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {card.prices.map(price => (
          <div key={price.source} className="bg-[#12121a] rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1 capitalize">{price.source}</div>
            <div className="text-2xl font-bold text-white">
              {price.source === 'tcgplayer' 
                ? `$${price.price_usd?.toFixed(2) || 'N/A'}`
                : `€${price.price_eur?.toFixed(2) || 'N/A'}`}
            </div>
            {price.low_price && (
              <div className="text-xs text-gray-500 mt-1">
                Low: ${price.low_price.toFixed(2)}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Price Chart */}
      {chartData.length > 1 && (
        <div className="bg-[#12121a] rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-4">Price History (30 days)</div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <XAxis 
                  dataKey="date" 
                  tick={{ fill: '#666', fontSize: 12 }}
                  axisLine={{ stroke: '#333' }}
                />
                <YAxis 
                  tick={{ fill: '#666', fontSize: 12 }}
                  axisLine={{ stroke: '#333' }}
                  tickFormatter={(value) => `$${value}`}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1a1a24', 
                    border: '1px solid #2a2a3a',
                    borderRadius: '8px'
                  }}
                  labelStyle={{ color: '#999' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#6366f1" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

