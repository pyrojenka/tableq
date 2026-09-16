import type { DailyStats, GuestStatus, RestaurantTable, TableStatus, WaitlistGuest } from '../types'

// All backend calls for the app live in this file, talking to the FastAPI
// backend described in openapi.yaml.

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const POLL_INTERVAL_MS = 3000

const listeners = new Set<() => void>()
let pollHandle: ReturnType<typeof setInterval> | undefined

function notify() {
  for (const listener of listeners) listener()
}

export function subscribe(listener: () => void) {
  listeners.add(listener)
  pollHandle ??= setInterval(notify, POLL_INTERVAL_MS)
  return () => {
    listeners.delete(listener)
    if (listeners.size === 0 && pollHandle !== undefined) {
      clearInterval(pollHandle)
      pollHandle = undefined
    }
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? `Request to ${path} failed with ${response.status}`)
  }

  return response.json() as Promise<T>
}

interface ApiGuest {
  id: string
  token: string
  name: string
  party_size: number
  phone: string
  notes: string
  status: GuestStatus
  created_at: string
  estimated_wait_minutes: number
  assigned_table_id?: string | null
}

interface ApiTable {
  id: string
  name: string
  capacity: number
  status: TableStatus
  occupied_by_guest_id?: string | null
}

interface ApiStats {
  total_seated: number
  total_no_show: number
  average_wait_minutes: number
}

function toGuest(g: ApiGuest): WaitlistGuest {
  return {
    id: g.id,
    token: g.token,
    name: g.name,
    partySize: g.party_size,
    phone: g.phone,
    notes: g.notes,
    status: g.status,
    createdAt: Date.parse(g.created_at),
    estimatedWaitMinutes: g.estimated_wait_minutes,
    assignedTableId: g.assigned_table_id ?? undefined,
  }
}

function toTable(t: ApiTable): RestaurantTable {
  return {
    id: t.id,
    name: t.name,
    capacity: t.capacity,
    status: t.status,
    occupiedByGuestId: t.occupied_by_guest_id ?? undefined,
  }
}

function toStats(s: ApiStats): DailyStats {
  return {
    totalSeated: s.total_seated,
    totalNoShow: s.total_no_show,
    averageWaitMinutes: s.average_wait_minutes,
  }
}

export async function getWaitlist(): Promise<WaitlistGuest[]> {
  const guests = await request<ApiGuest[]>('/waitlist')
  return guests.map(toGuest)
}

export async function getTables(): Promise<RestaurantTable[]> {
  const tables = await request<ApiTable[]>('/tables')
  return tables.map(toTable)
}

export async function getStats(): Promise<DailyStats> {
  return toStats(await request<ApiStats>('/stats'))
}

export async function addGuest(input: {
  name: string
  partySize: number
  phone: string
  notes: string
}): Promise<WaitlistGuest> {
  const guest = await request<ApiGuest>('/waitlist', {
    method: 'POST',
    body: JSON.stringify({
      name: input.name,
      party_size: input.partySize,
      phone: input.phone,
      notes: input.notes,
    }),
  })
  notify()
  return toGuest(guest)
}

export async function seatGuest(guestId: string): Promise<void> {
  await request(`/waitlist/${guestId}/seat`, { method: 'POST' })
  notify()
}

export async function cancelGuest(guestId: string): Promise<void> {
  await request(`/waitlist/${guestId}/cancel`, { method: 'POST' })
  notify()
}

export async function confirmTableFree(tableId: string): Promise<void> {
  await request(`/tables/${tableId}/confirm-free`, { method: 'POST' })
  notify()
}

export async function getGuestByToken(token: string): Promise<WaitlistGuest | null> {
  try {
    return toGuest(await request<ApiGuest>(`/guest/${token}`))
  } catch {
    return null
  }
}
