import type { DailyStats } from '../types'

export function StatsPanel({ stats }: { stats: DailyStats }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <h2 className="text-lg font-semibold text-gray-800 mb-3">Today</h2>

      <div className="grid grid-cols-3 gap-3 text-center">
        <div>
          <div className="text-2xl font-semibold text-gray-800">{stats.totalSeated}</div>
          <div className="text-xs text-gray-500">seated</div>
        </div>
        <div>
          <div className="text-2xl font-semibold text-gray-800">{stats.totalNoShow}</div>
          <div className="text-xs text-gray-500">no-shows</div>
        </div>
        <div>
          <div className="text-2xl font-semibold text-gray-800">{stats.averageWaitMinutes}m</div>
          <div className="text-xs text-gray-500">avg wait</div>
        </div>
      </div>
    </div>
  )
}
