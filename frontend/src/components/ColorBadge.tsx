interface ColorBadgeProps {
  color: string;
  size?: 'sm' | 'md';
}

const colorMap: Record<string, string> = {
  red: 'bg-red-500',
  blue: 'bg-blue-500',
  green: 'bg-green-500',
  purple: 'bg-purple-500',
  yellow: 'bg-yellow-500',
  black: 'bg-gray-800',
  'red/green': 'bg-gradient-to-r from-red-500 to-green-500',
  'blue/yellow': 'bg-gradient-to-r from-blue-500 to-yellow-500',
  'purple/yellow': 'bg-gradient-to-r from-purple-500 to-yellow-500',
  'red/blue': 'bg-gradient-to-r from-red-500 to-blue-500',
  'green/blue': 'bg-gradient-to-r from-green-500 to-blue-500',
  'black/yellow': 'bg-gradient-to-r from-gray-800 to-yellow-500',
  'red/purple': 'bg-gradient-to-r from-red-500 to-purple-500',
  'green/yellow': 'bg-gradient-to-r from-green-500 to-yellow-500',
  'blue/purple': 'bg-gradient-to-r from-blue-500 to-purple-500',
  'red/black': 'bg-gradient-to-r from-red-500 to-gray-800',
};

export function ColorBadge({ color, size = 'md' }: ColorBadgeProps) {
  const colorClass = colorMap[color.toLowerCase()] || 'bg-gray-500';
  const sizeClass = size === 'sm' ? 'w-4 h-4' : 'w-6 h-6';

  return (
    <div
      className={`${sizeClass} rounded-full ${colorClass} ring-2 ring-white/20`}
      title={color}
    />
  );
}

