interface TierBadgeProps {
  tier: string | null;
  size?: 'sm' | 'md' | 'lg';
}

export function TierBadge({ tier, size = 'md' }: TierBadgeProps) {
  const sizeClasses = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-10 h-10 text-base',
  };

  const tierClasses: Record<string, string> = {
    S: 'bg-gradient-to-br from-yellow-400 to-amber-600 text-black shadow-lg shadow-yellow-500/30',
    A: 'bg-gradient-to-br from-slate-300 to-slate-500 text-black',
    B: 'bg-gradient-to-br from-orange-400 to-orange-700 text-white',
    C: 'bg-gradient-to-br from-blue-400 to-blue-600 text-white',
    D: 'bg-gradient-to-br from-gray-500 to-gray-700 text-white',
  };

  const tierClass = tier ? tierClasses[tier.toUpperCase()] || tierClasses.D : tierClasses.D;

  return (
    <div
      className={`
        inline-flex items-center justify-center rounded-lg font-bold
        ${sizeClasses[size]}
        ${tierClass}
      `}
    >
      {tier?.toUpperCase() || '-'}
    </div>
  );
}

