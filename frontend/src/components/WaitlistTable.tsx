import { useState } from 'react'
import { cancelGuest, seatGuest } from '../api/mockApi'
import type { WaitlistGuest } from '../types'
import { GuestQrModal } from './GuestQrModal'

const STATUS_LABEL: Record<WaitlistGuest['status'], string> = {
  waiting: 'Waiting',
  table_ready: 'Table ready',
  seated: 'Seated',
  cancelled_no_show: 'Cancelled / no-show',
}

const STATUS_STYLE: Record<WaitlistGuest['status'], string> = {
  waiting: 'bg-amber-100 text-amber-800',
  table_ready: 'bg-emerald-100 text-emerald-800',
  seated: 'bg-blue-100 text-blue-800',
  cancelled_no_show: 'bg-gray-200 text-gray-500',
}

export function WaitlistTable({ guests }: { guests: WaitlistGuest[] }) {
  const [qrGuest, setQrGuest] = useState<WaitlistGuest | null>(null)
  const active = guests.filter((g) => g.status !== 'cancelled_no_show' && g.status !== 'seated')
  const finished = guests.filter((g) => g.status === 'cancelled_no_show' || g.status === 'seated')

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <h2 className="text-lg font-semibold text-gray-800 px-4 pt-4">Waitlist</h2>

      {active.length === 0 && <p className="px-4 py-6 text-sm text-gray-400">No one is waiting right now.</p>}

      <ul className="divide-y divide-gray-100">
        {active.map((guest) => (
          <li key={guest.id} className="px-4 py-3 flex items-center gap-3">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-800 truncate">{guest.name}</span>
                <span className="text-xs text-gray-400">party of {guest.partySize}</span>
              </div>
              <div className="text-xs text-gray-400 truncate">
                {guest.phone}
                {guest.notes && ` · ${guest.notes}`}
              </div>
            </div>

            <span className={`text-xs font-medium px-2 py-1 rounded-full whitespace-nowrap ${STATUS_STYLE[guest.status]}`}>
              {STATUS_LABEL[guest.status]}
            </span>

            {guest.status === 'waiting' && (
              <span className="text-xs text-gray-400 whitespace-nowrap">~{guest.estimatedWaitMinutes} min</span>
            )}

            <button
              onClick={() => setQrGuest(guest)}
              className="text-xs font-medium text-violet-600 hover:text-violet-800 whitespace-nowrap"
            >
              QR
            </button>

            {guest.status === 'table_ready' && (
              <button
                onClick={() => seatGuest(guest.id)}
                className="text-xs font-medium bg-emerald-600 text-white px-3 py-1.5 rounded-lg hover:bg-emerald-700 whitespace-nowrap"
              >
                Seat
              </button>
            )}

            <button
              onClick={() => cancelGuest(guest.id)}
              className="text-xs font-medium text-red-500 hover:text-red-700 whitespace-nowrap"
            >
              Cancel
            </button>
          </li>
        ))}
      </ul>

      {finished.length > 0 && (
        <details className="px-4 py-3 border-t border-gray-100">
          <summary className="text-xs text-gray-400 cursor-pointer">History ({finished.length})</summary>
          <ul className="mt-2 space-y-1">
            {finished.map((guest) => (
              <li key={guest.id} className="text-xs text-gray-400 flex justify-between">
                <span>{guest.name} · party of {guest.partySize}</span>
                <span className={`px-2 py-0.5 rounded-full ${STATUS_STYLE[guest.status]}`}>{STATUS_LABEL[guest.status]}</span>
              </li>
            ))}
          </ul>
        </details>
      )}

      {qrGuest && <GuestQrModal guest={qrGuest} onClose={() => setQrGuest(null)} />}
    </div>
  )
}
