import { useQuery } from '@tanstack/react-query';
import { api, MatchupMatrix as MatchupMatrixType, MatchupCell } from '../api/client';
import { PageLoader } from '../components/LoadingSpinner';
import { useState } from 'react';

type ViewMode = 'overall' | 'first' | 'second';

export function Matchups() {
  const [viewMode, setViewMode] = useState<ViewMode>('overall');
  const [hoveredCell, setHoveredCell] = useState<{ a: string; b: string } | null>(null);

  const { data: matrix, isLoading, error } = useQuery({
    queryKey: ['matchupMatrix'],
    queryFn: api.getMatchupMatrix,
  });

  if (isLoading) return <PageLoader />;
  if (error || !matrix) return <div className="text-red-400">Failed to load matchup data</div>;

  const getWinRate = (cell: MatchupCell): number => {
    if (viewMode === 'first' && cell.first_win_rate !== null) {
      return cell.first_win_rate;
    }
    if (viewMode === 'second' && cell.second_win_rate !== null) {
      return cell.second_win_rate;
    }
    return cell.win_rate;
  };

  const getCellColor = (winRate: number): string => {
    if (winRate >= 60) return 'bg-green-600';
    if (winRate >= 55) return 'bg-green-500/80';
    if (winRate >= 52) return 'bg-green-400/60';
    if (winRate >= 48) return 'bg-gray-600';
    if (winRate >= 45) return 'bg-red-400/60';
    if (winRate >= 40) return 'bg-red-500/80';
    return 'bg-red-600';
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-display text-4xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
          Matchup Matrix
        </h1>
        <p className="text-gray-400 mt-2">
          Win rates for each leader matchup
        </p>
      </div>

      {/* View Mode Toggle */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setViewMode('overall')}
          className={`
            px-4 py-2 rounded-lg font-medium transition-all
            ${viewMode === 'overall' 
              ? 'bg-indigo-500 text-white' 
              : 'bg-[#1a1a24] text-gray-400 hover:text-white'}
          `}
        >
          Overall
        </button>
        <button
          onClick={() => setViewMode('first')}
          className={`
            px-4 py-2 rounded-lg font-medium transition-all
            ${viewMode === 'first' 
              ? 'bg-green-500 text-white' 
              : 'bg-[#1a1a24] text-gray-400 hover:text-white'}
          `}
        >
          Going First
        </button>
        <button
          onClick={() => setViewMode('second')}
          className={`
            px-4 py-2 rounded-lg font-medium transition-all
            ${viewMode === 'second' 
              ? 'bg-blue-500 text-white' 
              : 'bg-[#1a1a24] text-gray-400 hover:text-white'}
          `}
        >
          Going Second
        </button>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 flex-wrap">
        <span className="text-sm text-gray-400">Win Rate:</span>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-green-600" />
          <span className="text-sm text-gray-300">60%+</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-green-400/60" />
          <span className="text-sm text-gray-300">52-59%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-gray-600" />
          <span className="text-sm text-gray-300">48-52%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-red-400/60" />
          <span className="text-sm text-gray-300">41-48%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-red-600" />
          <span className="text-sm text-gray-300">40%-</span>
        </div>
      </div>

      {/* Matrix */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          <table className="border-collapse">
            <thead>
              <tr>
                <th className="sticky left-0 z-10 bg-[#0a0a0f] p-2 text-left text-xs text-gray-400 min-w-[100px]">
                  Row vs Column
                </th>
                {matrix.leaders.map(leaderId => (
                  <th 
                    key={leaderId}
                    className="p-2 text-center text-xs text-gray-400 min-w-[60px] writing-mode-vertical"
                    style={{ writingMode: 'vertical-rl', textOrientation: 'mixed' }}
                  >
                    {matrix.leader_names[leaderId] || leaderId}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.leaders.map(leaderA => (
                <tr key={leaderA}>
                  <td className="sticky left-0 z-10 bg-[#0a0a0f] p-2 text-sm text-gray-300 font-medium whitespace-nowrap">
                    {matrix.leader_names[leaderA] || leaderA}
                  </td>
                  {matrix.leaders.map(leaderB => {
                    const cell = matrix.matrix[leaderA]?.[leaderB];
                    if (!cell) return <td key={leaderB} className="p-1" />;
                    
                    const winRate = getWinRate(cell);
                    const isHovered = hoveredCell?.a === leaderA && hoveredCell?.b === leaderB;
                    const isMirror = leaderA === leaderB;

                    return (
                      <td 
                        key={leaderB}
                        className="p-1"
                        onMouseEnter={() => setHoveredCell({ a: leaderA, b: leaderB })}
                        onMouseLeave={() => setHoveredCell(null)}
                      >
                        <div
                          className={`
                            w-14 h-10 rounded flex items-center justify-center
                            text-xs font-medium text-white
                            transition-all duration-150
                            ${isMirror ? 'bg-gray-800' : getCellColor(winRate)}
                            ${isHovered ? 'ring-2 ring-white scale-110 z-10 relative' : ''}
                          `}
                        >
                          {isMirror ? '-' : `${winRate.toFixed(0)}%`}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Hovered Cell Info */}
      {hoveredCell && matrix.matrix[hoveredCell.a]?.[hoveredCell.b] && (
        <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50">
          <div className="card-container flex items-center gap-4 shadow-xl">
            <div className="text-center">
              <div className="text-xs text-gray-400">Row (You)</div>
              <div className="font-semibold text-white">
                {matrix.leader_names[hoveredCell.a] || hoveredCell.a}
              </div>
            </div>
            <div className="text-gray-500">vs</div>
            <div className="text-center">
              <div className="text-xs text-gray-400">Column (Opponent)</div>
              <div className="font-semibold text-white">
                {matrix.leader_names[hoveredCell.b] || hoveredCell.b}
              </div>
            </div>
            <div className="border-l border-[#2a2a3a] pl-4 ml-2">
              <div className="text-xs text-gray-400">Win Rate</div>
              <div className="text-xl font-bold text-white">
                {getWinRate(matrix.matrix[hoveredCell.a][hoveredCell.b]).toFixed(1)}%
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-400">Sample</div>
              <div className="font-medium text-gray-300">
                {matrix.matrix[hoveredCell.a][hoveredCell.b].sample_size.toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

