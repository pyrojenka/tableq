import { useEffect, useState } from 'react'
import { getStats, getTables, getWaitlist } from '../api/mockApi'
import { AddGuestForm } from '../components/AddGuestForm'
import { StatsPanel } from '../components/StatsPanel'
import { TablesBoard } from '../components/TablesBoard'
import { WaitlistTable } from '../components/WaitlistTable'
import { useMockRefresh } from '../hooks/useMockRefresh'
import type { DailyStats, RestaurantTable, WaitlistGuest } from '../types'

export function HostessPage() {
  const tick = useMockRefresh()
  const [guests, setGuests] = useState<WaitlistGuest[]>([])
  const [tables, setTables] = useState<RestaurantTable[]>([])
  const [stats, setStats] = useState<DailyStats>({ totalSeated: 0, totalNoShow: 0, averageWaitMinutes: 15 })

  useEffect(() => {
    getWaitlist().then(setGuests)
    getTables().then(setTables)
    getStats().then(setStats)
  }, [tick])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <h1 className="text-xl font-semibold text-gray-800">TableQ — Hostess</h1>
      </header>

      <main className="max-w-5xl mx-auto p-4 grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1 space-y-4">
          <AddGuestForm />
          <StatsPanel stats={stats} />
        </div>

        <div className="lg:col-span-2 space-y-4">
          <TablesBoard tables={tables} />
          <WaitlistTable guests={guests} />
        </div>
      </main>
    </div>
  )
}
