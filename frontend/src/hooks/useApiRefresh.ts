import { useEffect, useState } from 'react'
import { subscribe } from '../api/client'

// Bumps a counter on a poll interval (and right after any mutation) so
// views know to refetch from the backend.
export function useApiRefresh() {
  const [tick, setTick] = useState(0)

  useEffect(() => {
    const unsubscribe = subscribe(() => setTick((t) => t + 1))
    return () => {
      unsubscribe()
    }
  }, [])

  return tick
}
