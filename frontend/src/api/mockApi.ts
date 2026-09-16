import type { DailyStats, GuestStatus, RestaurantTable, WaitlistGuest } from '../types'

// All "backend calls" for the app live in this file. State is persisted to
// localStorage (instead of a plain in-memory variable) so the hostess tab
// and a guest tab opened via QR link stay in sync, the way they would
// through a real backend. Swap the function bodies for real HTTP calls
// later without touching any component.

const NETWORK_DELAY_MS = 250
const STORAGE_KEY = 'tableq_mock_state_v1'

// Meal duration is accelerated for the demo so the "table likely free" flow
// is visible without waiting real minutes.
const MOCK_MEAL_DURATION_MS = 20_000

interface MockState {
  tables: RestaurantTable[]
  guests: WaitlistGuest[]
  averageWaitMinutes: number
  seatedCount: number
  noShowCount: number
}

function defaultState(): MockState {
  return {
    tables: [
      { id: 't1', name: 'Table 1', capacity: 2, status: 'free' },
      { id: 't2', name: 'Table 2', capacity: 2, status: 'free' },
      { id: 't3', name: 'Table 3', capacity: 4, status: 'free' },
      { id: 't4', name: 'Table 4', capacity: 4, status: 'free' },
      { id: 't5', name: 'Table 5', capacity: 6, status: 'free' },
      { id: 't6', name: 'Table 6', capacity: 8, status: 'free' },
    ],
    guests: [],
    averageWaitMinutes: 15,
    seatedCount: 0,
    noShowCount: 0,
  }
}

function loadState(): MockState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw) as MockState
  } catch {
    // fall through to defaults
  }
  return defaultState()
}

let state = loadState()

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

const listeners = new Set<() => void>()

function notify() {
  for (const listener of listeners) listener()
}

if (typeof window !== 'undefined') {
  window.addEventListener('storage', (event) => {
    if (event.key !== STORAGE_KEY) return
    state = loadState()
    notify()
  })
}

function delay<T>(value: T): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), NETWORK_DELAY_MS))
}

function makeToken() {
  return Math.random().toString(36).slice(2, 10)
}

function waitingGuestsByPriority() {
  // Largest party first: fills the biggest free tables efficiently and
  // avoids stranding a big party behind several small ones.
  return state.guests
    .filter((g) => g.status === 'waiting')
    .sort((a, b) => b.partySize - a.partySize || a.createdAt - b.createdAt)
}

function recalcAssignments() {
  const freeTables = state.tables
    .filter((t) => t.status === 'free')
    .sort((a, b) => a.capacity - b.capacity)

  for (const guest of waitingGuestsByPriority()) {
    const table = freeTables.find((t) => t.capacity >= guest.partySize && t.status === 'free')
    if (!table) continue

    table.status = 'occupied'
    table.occupiedByGuestId = guest.id
    guest.status = 'table_ready'
    guest.assignedTableId = table.id
  }

  recalcEstimatedWaits()
  persist()
  notify()
}

function recalcEstimatedWaits() {
  const waiting = waitingGuestsByPriority()
  waiting.forEach((guest, index) => {
    guest.estimatedWaitMinutes = Math.max(5, Math.round((index + 1) * state.averageWaitMinutes))
  })
}

function recordWaitDuration(guest: WaitlistGuest) {
  const actualMinutes = (Date.now() - guest.createdAt) / 60_000
  state.averageWaitMinutes = Math.round(
    (state.averageWaitMinutes * state.seatedCount + actualMinutes) / (state.seatedCount + 1),
  )
  state.seatedCount += 1
}

export function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

export async function getWaitlist(): Promise<WaitlistGuest[]> {
  return delay([...state.guests].sort((a, b) => a.createdAt - b.createdAt))
}

export async function getTables(): Promise<RestaurantTable[]> {
  return delay([...state.tables])
}

export async function getStats(): Promise<DailyStats> {
  return delay({
    totalSeated: state.seatedCount,
    totalNoShow: state.noShowCount,
    averageWaitMinutes: state.averageWaitMinutes,
  })
}

export async function addGuest(input: {
  name: string
  partySize: number
  phone: string
  notes: string
}): Promise<WaitlistGuest> {
  const guest: WaitlistGuest = {
    id: crypto.randomUUID(),
    token: makeToken(),
    name: input.name,
    partySize: input.partySize,
    phone: input.phone,
    notes: input.notes,
    status: 'waiting',
    createdAt: Date.now(),
    estimatedWaitMinutes: state.averageWaitMinutes,
  }
  state.guests.push(guest)
  recalcAssignments()
  return delay(guest)
}

export async function seatGuest(guestId: string): Promise<void> {
  const guest = state.guests.find((g) => g.id === guestId)
  if (!guest || guest.status !== 'table_ready') return

  guest.status = 'seated'
  recordWaitDuration(guest)
  persist()
  notify()

  const tableId = guest.assignedTableId
  setTimeout(() => {
    const table = state.tables.find((t) => t.id === tableId)
    if (table && table.status === 'occupied') {
      table.status = 'pending_free'
      persist()
      notify()
    }
  }, MOCK_MEAL_DURATION_MS)

  return delay(undefined)
}

export async function cancelGuest(guestId: string): Promise<void> {
  const guest = state.guests.find((g) => g.id === guestId)
  if (!guest) return

  const wasTableReady = guest.status === 'table_ready'
  guest.status = 'cancelled_no_show' as GuestStatus
  state.noShowCount += 1

  if (wasTableReady && guest.assignedTableId) {
    const table = state.tables.find((t) => t.id === guest.assignedTableId)
    if (table) {
      table.status = 'free'
      table.occupiedByGuestId = undefined
    }
    guest.assignedTableId = undefined
    recalcAssignments()
  } else {
    persist()
    notify()
  }

  return delay(undefined)
}

export async function confirmTableFree(tableId: string): Promise<void> {
  const table = state.tables.find((t) => t.id === tableId)
  if (!table) return

  table.status = 'free'
  table.occupiedByGuestId = undefined
  recalcAssignments()
  return delay(undefined)
}

export async function getGuestByToken(token: string): Promise<WaitlistGuest | null> {
  const guest = state.guests.find((g) => g.token === token) ?? null
  return delay(guest)
}
