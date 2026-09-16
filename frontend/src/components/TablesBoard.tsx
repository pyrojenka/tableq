import { confirmTableFree } from '../api/client'
import type { RestaurantTable } from '../types'

const STATUS_STYLE: Record<RestaurantTable['status'], string> = {
  free: 'border-emerald-300 bg-emerald-50',
  occupied: 'border-gray-300 bg-gray-50',
  pending_free: 'border-amber-400 bg-amber-50',
}

const STATUS_LABEL: Record<RestaurantTable['status'], string> = {
  free: 'Free',
  occupied: 'Occupied',
  pending_free: 'Likely free — confirm?',
}

export function TablesBoard({ tables }: { tables: RestaurantTable[] }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <h2 className="text-lg font-semibold text-gray-800 mb-3">Tables</h2>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {tables.map((table) => (
          <div key={table.id} className={`rounded-lg border p-3 text-center ${STATUS_STYLE[table.status]}`}>
            <div className="font-medium text-gray-800">{table.name}</div>
            <div className="text-xs text-gray-500">seats {table.capacity}</div>
            <div className="text-xs mt-1 font-medium text-gray-600">{STATUS_LABEL[table.status]}</div>

            {table.status === 'pending_free' && (
              <button
                onClick={() => confirmTableFree(table.id)}
                className="mt-2 w-full text-xs font-medium bg-amber-500 text-white rounded-lg py-1 hover:bg-amber-600"
              >
                Confirm free
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
