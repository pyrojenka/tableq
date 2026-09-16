import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getGuestByToken } from '../api/mockApi'
import { useMockRefresh } from '../hooks/useMockRefresh'
import type { WaitlistGuest } from '../types'

const STATUS_COPY: Record<WaitlistGuest['status'], { title: string; subtitle: string; color: string }> = {
  waiting: { title: "You're on the list", subtitle: 'We\'ll update this page when your table is ready.', color: 'text-amber-600' },
  table_ready: { title: 'Your table is ready!', subtitle: 'Please head to the host stand.', color: 'text-emerald-600' },
  seated: { title: "You're seated", subtitle: 'Enjoy your meal!', color: 'text-blue-600' },
  cancelled_no_show: { title: 'Waitlist entry closed', subtitle: 'This entry was cancelled.', color: 'text-gray-500' },
}

export function GuestPage() {
  const { token } = useParams<{ token: string }>()
  const tick = useMockRefresh()
  const [guest, setGuest] = useState<WaitlistGuest | null | undefined>(undefined)

  useEffect(() => {
    if (!token) return
    getGuestByToken(token).then(setGuest)
  }, [token, tick])

  if (guest === undefined) {
    return <CenteredMessage title="Loading…" subtitle="" />
  }

  if (guest === null) {
    return <CenteredMessage title="We couldn't find this waitlist entry" subtitle="Check the link or ask the host stand for help." />
  }

  const copy = STATUS_COPY[guest.status]

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 max-w-sm w-full text-center space-y-4">
        <p className="text-sm text-gray-400">TableQ</p>
        <h1 className={`text-2xl font-semibold ${copy.color}`}>{copy.title}</h1>
        <p className="text-sm text-gray-500">{copy.subtitle}</p>

        <div className="border-t border-gray-100 pt-4 text-sm text-gray-600 space-y-1">
          <p>{guest.name} · party of {guest.partySize}</p>
          {guest.status === 'waiting' && (
            <p className="text-lg font-semibold text-gray-800">~{guest.estimatedWaitMinutes} min</p>
          )}
        </div>
      </div>
    </div>
  )
}

function CenteredMessage({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="text-center space-y-2">
        <h1 className="text-lg font-medium text-gray-700">{title}</h1>
        {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
      </div>
    </div>
  )
}
