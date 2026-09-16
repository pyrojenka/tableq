export type GuestStatus = 'waiting' | 'table_ready' | 'seated' | 'cancelled_no_show'

export type TableStatus = 'free' | 'occupied' | 'pending_free'

export interface RestaurantTable {
  id: string
  name: string
  capacity: number
  status: TableStatus
  occupiedByGuestId?: string
}

export interface WaitlistGuest {
  id: string
  token: string
  name: string
  partySize: number
  phone: string
  notes: string
  status: GuestStatus
  createdAt: number
  estimatedWaitMinutes: number
  assignedTableId?: string
}

export interface DailyStats {
  totalSeated: number
  totalNoShow: number
  averageWaitMinutes: number
}
