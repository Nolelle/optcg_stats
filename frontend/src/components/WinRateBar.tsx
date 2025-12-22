interface WinRateBarProps {
  winRate: number;
  showLabel?: boolean;
  height?: 'sm' | 'md';
}

export function WinRateBar({ winRate, showLabel = true, height = 'md' }: WinRateBarProps) {
  const getColor = (rate: number) => {
    if (rate >= 55) return 'from-green-400 to-emerald-600';
    if (rate >= 52) return 'from-lime-400 to-green-500';
    if (rate >= 48) return 'from-yellow-400 to-amber-500';
    if (rate >= 45) return 'from-orange-400 to-red-500';
    return 'from-red-400 to-red-600';
  };

  const heightClass = height === 'sm' ? 'h-2' : 'h-3';

  return (
    <div className="flex items-center gap-2 w-full">
      <div className={`flex-1 bg-gray-800 rounded-full ${heightClass} overflow-hidden`}>
        <div
          className={`${heightClass} rounded-full bg-gradient-to-r ${getColor(winRate)} transition-all duration-500`}
          style={{ width: `${Math.min(100, Math.max(0, winRate))}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-sm font-medium text-gray-300 min-w-[3rem] text-right">
          {winRate.toFixed(1)}%
        </span>
      )}
    </div>
  );
}

