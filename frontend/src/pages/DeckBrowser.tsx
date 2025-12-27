import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { Deck, Leader } from "../api/client";
import { TierBadge } from "../components/TierBadge";
import { WinRateBar } from "../components/WinRateBar";
import { ColorBadge } from "../components/ColorBadge";
import { PageLoader } from "../components/LoadingSpinner";
import { useSearchParams, Link } from "react-router-dom";
import { Users, Trophy, ArrowUpDown, ChevronRight } from "lucide-react";
import { useState, useMemo } from "react";

type ViewMode = "most-played" | "most-successful";
type SortKey = "win_rate" | "games_played";

export function DeckBrowser() {
  const [searchParams] = useSearchParams();
  const leaderFilter = searchParams.get("leader");

  const [viewMode, setViewMode] = useState<ViewMode>("most-played");
  const [sortBy, setSortBy] = useState<SortKey>("games_played");

  // Fetch leaders to get color/name mapping
  const { data: leaders } = useQuery({
    queryKey: ["leaders"],
    queryFn: api.getLeaders
  });

  // Create leader lookup map
  const leaderMap = useMemo(() => {
    const map: Record<string, Leader> = {};
    leaders?.forEach((leader) => {
      map[leader.id] = leader;
    });
    return map;
  }, [leaders]);

  const { data: mostPlayed, isLoading: loadingPlayed } = useQuery({
    queryKey: ["decks", "most-played"],
    queryFn: () => api.getMostPlayed(50),
    enabled: viewMode === "most-played" && !leaderFilter
  });

  const { data: mostSuccessful, isLoading: loadingSuccessful } = useQuery({
    queryKey: ["decks", "most-successful"],
    queryFn: () => api.getMostSuccessful(50, 50),
    enabled: viewMode === "most-successful" && !leaderFilter
  });

  const { data: leaderDecks, isLoading: loadingLeader } = useQuery({
    queryKey: ["decks", "leader", leaderFilter],
    queryFn: () => api.getDecksByLeader(leaderFilter!),
    enabled: !!leaderFilter
  });

  const isLoading = loadingPlayed || loadingSuccessful || loadingLeader;

  let decks: Deck[] = [];
  if (leaderFilter) {
    decks = leaderDecks || [];
  } else if (viewMode === "most-played") {
    decks = mostPlayed || [];
  } else if (viewMode === "most-successful") {
    decks = mostSuccessful || [];
  }

  // Sort decks
  const sortedDecks = [...decks].sort((a, b) => {
    if (sortBy === "win_rate") return b.win_rate - a.win_rate;
    return b.games_played - a.games_played;
  });

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-display text-4xl font-bold bg-linear-to-r from-white to-gray-400 bg-clip-text text-transparent">
          Deck Browser
        </h1>
        <p className="text-gray-400 mt-2">
          {leaderFilter
            ? `Viewing decks for ${
                leaderMap[leaderFilter]?.name || leaderFilter
              }`
            : "Browse the most played and successful decks"}
        </p>
      </div>

      {/* View Mode Tabs */}
      {!leaderFilter && (
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode("most-played")}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
              ${
                viewMode === "most-played"
                  ? "bg-indigo-500 text-white"
                  : "bg-[#1a1a24] text-gray-400 hover:text-white"
              }
            `}
          >
            <Users size={18} />
            Most Played
          </button>
          <button
            onClick={() => setViewMode("most-successful")}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
              ${
                viewMode === "most-successful"
                  ? "bg-indigo-500 text-white"
                  : "bg-[#1a1a24] text-gray-400 hover:text-white"
              }
            `}
          >
            <Trophy size={18} />
            Most Successful
          </button>
        </div>
      )}

      {/* Sort */}
      <div className="flex items-center gap-2">
        <ArrowUpDown
          size={16}
          className="text-gray-400"
        />
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
            leader={leaderMap[deck.leader_id]}
            rank={index + 1}
          />
        ))}
      </div>

      {sortedDecks.length === 0 && (
        <div className="text-center py-12 text-gray-400">No decks found</div>
      )}
    </div>
  );
}

function DeckCard({
  deck,
  leader,
  rank
}: {
  deck: Deck;
  leader?: Leader;
  rank: number;
}) {
  const displayName = leader
    ? `${leader.color} ${leader.name}`
    : deck.leader_id;

  return (
    <Link
      to={`/decks/${deck.id}`}
      className="card-container cursor-pointer transition-all hover:ring-2 hover:ring-indigo-500/50 group"
    >
      <div className="flex items-start gap-4">
        {/* Rank */}
        <div className="shrink-0 w-10 h-10 rounded-lg bg-[#12121a] flex items-center justify-center">
          <span className="font-bold text-lg text-gray-400">#{rank}</span>
        </div>

        {/* Deck Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            {leader?.color && <ColorBadge color={leader.color} />}
            <TierBadge
              tier={deck.tier}
              size="sm"
            />
            <h3 className="font-semibold text-white truncate">{displayName}</h3>
          </div>

          <WinRateBar
            winRate={deck.win_rate}
            height="sm"
          />
        </div>

        {/* Stats & Arrow */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-sm text-gray-400">Games</div>
            <div className="font-semibold text-white">
              {deck.games_played.toLocaleString()}
            </div>
          </div>
          <ChevronRight
            size={20}
            className="text-gray-500 group-hover:text-indigo-400 transition-colors"
          />
        </div>
      </div>

      {/* First/Second Stats */}
      <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-[#2a2a3a]">
        <div>
          <div className="text-xs text-green-400 mb-1">Going First</div>
          <WinRateBar
            winRate={deck.first_win_rate}
            height="sm"
          />
        </div>
        <div>
          <div className="text-xs text-blue-400 mb-1">Going Second</div>
          <WinRateBar
            winRate={deck.second_win_rate}
            height="sm"
          />
        </div>
      </div>
    </Link>
  );
}
