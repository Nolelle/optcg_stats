import { useQuery } from '@tanstack/react-query';
import { api, LeaderWithStats } from '../api/client';
import { TierBadge } from '../components/TierBadge';
import { ColorBadge } from '../components/ColorBadge';
import { WinRateBar } from '../components/WinRateBar';
import { PageLoader } from '../components/LoadingSpinner';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, Users, ArrowRight } from 'lucide-react';
import { useState } from 'react';

type SortKey = 'win_rate' | 'games_played' | 'first_win_rate' | 'second_win_rate';

export function TierList() {
  const [sortBy, setSortBy] = useState<SortKey>('win_rate');
  const [colorFilter, setColorFilter] = useState<string>('all');

  const { data: leaders, isLoading, error } = useQuery({
    queryKey: ['tierList'],
    queryFn: api.getTierList,
  });

  if (isLoading) return <PageLoader />;
  if (error) return <div className="text-red-400">Failed to load tier list</div>;

  const colors = ['all', ...new Set(leaders?.map(l => l.color.toLowerCase()) || [])];
  
  const filteredLeaders = leaders
    ?.filter(l => colorFilter === 'all' || l.color.toLowerCase() === colorFilter)
    .sort((a, b) => b[sortBy] - a[sortBy]) || [];

  // Group by tier
  const tiers: Record<string, LeaderWithStats[]> = { S: [], A: [], B: [], C: [], D: [] };
  filteredLeaders.forEach(leader => {
    const tier = leader.tier?.toUpperCase() || 'D';
    if (tiers[tier]) {
      tiers[tier].push(leader);
    }
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-display text-4xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
          Tier List
        </h1>
        <p className="text-gray-400 mt-2">
          Leaders ranked by performance from TCG Matchmaking data
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        {/* Color Filter */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Color:</span>
          <div className="flex gap-1">
            {colors.map(color => (
              <button
                key={color}
                onClick={() => setColorFilter(color)}
                className={`
                  px-3 py-1.5 rounded-lg text-sm font-medium capitalize transition-all
                  ${colorFilter === color 
                    ? 'bg-indigo-500 text-white' 
                    : 'bg-[#1a1a24] text-gray-400 hover:text-white'}
                `}
              >
                {color}
              </button>
            ))}
          </div>
        </div>

        {/* Sort */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortKey)}
            className="input-field text-sm"
          >
            <option value="win_rate">Win Rate</option>
            <option value="games_played">Games Played</option>
            <option value="first_win_rate">Going First</option>
            <option value="second_win_rate">Going Second</option>
          </select>
        </div>
      </div>

      {/* Tier Sections */}
      {Object.entries(tiers).map(([tier, tierLeaders]) => (
        tierLeaders.length > 0 && (
          <div key={tier} className="space-y-4">
            <div className="flex items-center gap-3">
              <TierBadge tier={tier} size="lg" />
              <h2 className="font-display text-xl font-semibold text-white">
                {tier} Tier
              </h2>
              <span className="text-gray-500">({tierLeaders.length} leaders)</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {tierLeaders.map(leader => (
                <LeaderCard key={leader.id} leader={leader} />
              ))}
            </div>
          </div>
        )
      ))}

      {filteredLeaders.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          No leaders found matching your filters
        </div>
      )}
    </div>
  );
}

function LeaderCard({ leader }: { leader: LeaderWithStats }) {
  const firstSecondDiff = leader.first_win_rate - leader.second_win_rate;

  return (
    <Link
      to={`/decks?leader=${leader.id}`}
      className="card-container group hover:scale-[1.02]"
    >
      <div className="flex items-start gap-4">
        {/* Leader Image */}
        <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center overflow-hidden">
          {leader.image_url ? (
            <img 
              src={leader.image_url} 
              alt={leader.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <span className="text-2xl font-bold text-indigo-400">
              {leader.name.charAt(0)}
            </span>
          )}
        </div>

        {/* Leader Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <TierBadge tier={leader.tier} size="sm" />
            <h3 className="font-semibold text-white truncate">{leader.name}</h3>
          </div>
          
          <div className="flex items-center gap-2 mb-3">
            <ColorBadge color={leader.color} size="sm" />
            <span className="text-sm text-gray-400">{leader.id}</span>
          </div>

          {/* Win Rate */}
          <WinRateBar winRate={leader.win_rate} />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-[#2a2a3a]">
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-gray-400 text-xs mb-1">
            <Users size={12} />
            <span>Games</span>
          </div>
          <div className="font-semibold text-white">
            {leader.games_played.toLocaleString()}
          </div>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-green-400 text-xs mb-1">
            <TrendingUp size={12} />
            <span>1st</span>
          </div>
          <div className="font-semibold text-white">
            {leader.first_win_rate.toFixed(1)}%
          </div>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-blue-400 text-xs mb-1">
            <TrendingDown size={12} />
            <span>2nd</span>
          </div>
          <div className="font-semibold text-white">
            {leader.second_win_rate.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* First/Second Advantage */}
      {Math.abs(firstSecondDiff) > 2 && (
        <div className={`
          mt-3 px-3 py-1.5 rounded-lg text-xs font-medium text-center
          ${firstSecondDiff > 0 
            ? 'bg-green-500/10 text-green-400' 
            : 'bg-blue-500/10 text-blue-400'}
        `}>
          {firstSecondDiff > 0 
            ? `+${firstSecondDiff.toFixed(1)}% going first advantage`
            : `+${Math.abs(firstSecondDiff).toFixed(1)}% going second advantage`}
        </div>
      )}

      {/* View Arrow */}
      <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <ArrowRight size={20} className="text-indigo-400" />
      </div>
    </Link>
  );
}

