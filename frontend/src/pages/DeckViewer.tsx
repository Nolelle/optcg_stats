import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "react-router-dom";
import { api } from "../api/client";
import type { CardInDeck } from "../api/client";
import { TierBadge } from "../components/TierBadge";
import { ColorBadge } from "../components/ColorBadge";
import { CostCurveChart } from "../components/CostCurveChart";
import { PageLoader } from "../components/LoadingSpinner";
import {
  ArrowLeft,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Users,
  Copy,
  Check,
  BarChart3,
} from "lucide-react";
import { useState, useMemo } from "react";

type PriceSource = "tcgplayer" | "cardmarket";

export function DeckViewer() {
  const { deckId } = useParams<{ deckId: string }>();
  const [priceSource, setPriceSource] = useState<PriceSource>("tcgplayer");
  const [copied, setCopied] = useState(false);

  const { data: deck, isLoading, error } = useQuery({
    queryKey: ["deck", "detailed", deckId],
    queryFn: () => api.getDeckDetailed(Number(deckId)),
    enabled: !!deckId,
  });

  // Group cards by type
  const cardsByType = useMemo(() => {
    if (!deck?.cards) return {};
    const groups: Record<string, CardInDeck[]> = {
      Leader: [],
      Character: [],
      Event: [],
      Stage: [],
    };
    deck.cards.forEach((card) => {
      const type = card.card_type || "Other";
      if (!groups[type]) groups[type] = [];
      groups[type].push(card);
    });
    return groups;
  }, [deck?.cards]);

  // Generate OPTCG Sim format string
  const generateSimString = () => {
    if (!deck?.deck_list_json) return "";
    try {
      const deckList = JSON.parse(deck.deck_list_json) as Record<string, number>;
      const lines = [`1 ${deck.leader_id}`];
      for (const [cardId, count] of Object.entries(deckList)) {
        if (cardId !== deck.leader_id) {
          lines.push(`${count} ${cardId}`);
        }
      }
      return lines.join("\n");
    } catch {
      return "";
    }
  };

  const handleCopyToSim = async () => {
    const simString = generateSimString();
    if (simString) {
      await navigator.clipboard.writeText(simString);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getCardPrice = (card: CardInDeck) => {
    if (priceSource === "tcgplayer") {
      return card.price_usd;
    }
    return card.price_eur;
  };

  const getCurrencySymbol = () => (priceSource === "tcgplayer" ? "$" : "€");

  if (isLoading) return <PageLoader />;
  if (error || !deck)
    return <div className="text-red-400">Failed to load deck</div>;

  const displayName = deck.leader_color
    ? `${deck.leader_color} ${deck.leader_name || deck.leader_id}`
    : deck.leader_name || deck.leader_id;

  const totalPrice =
    priceSource === "tcgplayer" ? deck.total_cost_usd : deck.total_cost_eur;

  const totalCards = deck.cards.reduce((sum, card) => sum + card.count, 0);

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
        <div className="flex flex-col lg:flex-row lg:items-start gap-6">
          {/* Leader Info */}
          <div className="flex items-start gap-4">
            <div className="w-24 h-32 rounded-xl bg-linear-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center overflow-hidden border border-[#2a2a3a]">
              {deck.leader_image_url ? (
                <img
                  src={deck.leader_image_url}
                  alt={deck.leader_name || deck.leader_id}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-3xl font-bold text-indigo-400">
                  {deck.leader_name?.charAt(0) || deck.leader_id.charAt(0)}
                </span>
              )}
            </div>
            <div>
              <div className="flex items-center gap-2 mb-2 flex-wrap">
                {deck.leader_color && <ColorBadge color={deck.leader_color} />}
                <TierBadge tier={deck.tier} size="md" />
              </div>
              <h1 className="font-display text-2xl font-bold text-white mb-1">
                {displayName}
              </h1>
              <div className="text-gray-400 text-sm">{deck.leader_id}</div>
            </div>
          </div>

          {/* Stats */}
          <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatBox
              icon={<Users size={12} />}
              label="Games"
              value={deck.games_played.toLocaleString()}
              color="text-gray-400"
            />
            <StatBox
              label="Win Rate"
              value={`${deck.win_rate.toFixed(1)}%`}
              color="text-gray-400"
            />
            <StatBox
              icon={<TrendingUp size={12} />}
              label="Going 1st"
              value={`${deck.first_win_rate.toFixed(1)}%`}
              color="text-green-400"
            />
            <StatBox
              icon={<TrendingDown size={12} />}
              label="Going 2nd"
              value={`${deck.second_win_rate.toFixed(1)}%`}
              color="text-blue-400"
            />
          </div>

          {/* Copy to Sim Button */}
          <button
            onClick={handleCopyToSim}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
              ${
                copied
                  ? "bg-green-500 text-white"
                  : "bg-indigo-500 hover:bg-indigo-600 text-white"
              }
            `}
          >
            {copied ? <Check size={18} /> : <Copy size={18} />}
            {copied ? "Copied!" : "Copy to Sim"}
          </button>
        </div>
      </div>

      {/* Cost Curve & Price Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost Curve */}
        <div className="card-container">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="text-indigo-400" size={20} />
            <h2 className="font-display text-lg font-semibold text-white">
              Cost Curve
            </h2>
          </div>
          <CostCurveChart costCurve={deck.cost_curve} />
        </div>

        {/* Price Summary */}
        <div className="card-container">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <DollarSign className="text-green-400" size={20} />
              <h2 className="font-display text-lg font-semibold text-white">
                Deck Cost
              </h2>
            </div>

            {/* Price Source Toggle */}
            <div className="flex gap-1 bg-[#12121a] p-1 rounded-lg">
              <button
                onClick={() => setPriceSource("tcgplayer")}
                className={`
                  px-3 py-1.5 rounded text-sm font-medium transition-all
                  ${
                    priceSource === "tcgplayer"
                      ? "bg-green-500 text-white"
                      : "text-gray-400 hover:text-white"
                  }
                `}
              >
                TCGPlayer
              </button>
              <button
                onClick={() => setPriceSource("cardmarket")}
                className={`
                  px-3 py-1.5 rounded text-sm font-medium transition-all
                  ${
                    priceSource === "cardmarket"
                      ? "bg-blue-500 text-white"
                      : "text-gray-400 hover:text-white"
                  }
                `}
              >
                Cardmarket
              </button>
            </div>
          </div>

          <div className="text-center py-8 bg-[#12121a] rounded-lg">
            <div className="text-sm text-gray-400 mb-1">Total Deck Cost</div>
            <div className="text-4xl font-bold text-white">
              {getCurrencySymbol()}
              {totalPrice?.toFixed(2) || "N/A"}
            </div>
            <div className="text-sm text-gray-500 mt-2">{totalCards} cards</div>
          </div>
        </div>
      </div>

      {/* Card Sections by Type */}
      {(["Leader", "Character", "Event", "Stage"] as const).map((cardType) => {
        const cards = cardsByType[cardType];
        if (!cards || cards.length === 0) return null;

        const typeCount = cards.reduce((sum, c) => sum + c.count, 0);

        return (
          <div key={cardType} className="card-container">
            <h2 className="font-display text-lg font-semibold text-white mb-4">
              {cardType}s ({typeCount})
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {cards.map((card) => (
                <CardRow
                  key={card.id}
                  card={card}
                  price={getCardPrice(card)}
                  currencySymbol={getCurrencySymbol()}
                />
              ))}
            </div>
          </div>
        );
      })}

      {/* Source */}
      {deck.source_url && (
        <div className="text-center text-sm text-gray-500">
          Data from:{" "}
          <a
            href={deck.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-400 hover:underline"
          >
            {deck.source_url}
          </a>
        </div>
      )}
    </div>
  );
}

function StatBox({
  icon,
  label,
  value,
  color,
}: {
  icon?: React.ReactNode;
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div className="text-center p-3 bg-[#12121a] rounded-lg">
      <div className={`flex items-center justify-center gap-1 ${color} text-xs mb-1`}>
        {icon}
        <span>{label}</span>
      </div>
      <div className="text-xl font-bold text-white">{value}</div>
    </div>
  );
}

function CardRow({
  card,
  price,
  currencySymbol,
}: {
  card: CardInDeck;
  price: number | null;
  currencySymbol: string;
}) {
  return (
    <div className="flex items-center gap-3 p-3 bg-[#12121a] rounded-lg hover:bg-[#1a1a24] transition-colors">
      {/* Card Image */}
      <div className="w-12 h-16 rounded bg-linear-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center overflow-hidden shrink-0 border border-[#2a2a3a]">
        {card.image_url ? (
          <img
            src={card.image_url}
            alt={card.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-xs text-indigo-400 text-center px-1">
            {card.id}
          </span>
        )}
      </div>

      {/* Card Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded bg-indigo-500/30 text-indigo-300 text-xs font-bold flex items-center justify-center">
            {card.count}x
          </span>
          <span className="font-medium text-white truncate">{card.name}</span>
        </div>
        <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
          <span>{card.id}</span>
          {card.cost !== null && <span>Cost: {card.cost}</span>}
          {card.rarity && <span>{card.rarity}</span>}
        </div>
      </div>

      {/* Price */}
      <div className="text-right shrink-0">
        {price !== null ? (
          <>
            <div className="font-medium text-white">
              {currencySymbol}
              {price.toFixed(2)}
            </div>
            <div className="text-xs text-gray-500">
              {currencySymbol}
              {(price * card.count).toFixed(2)} total
            </div>
          </>
        ) : (
          <span className="text-gray-500">N/A</span>
        )}
      </div>
    </div>
  );
}
