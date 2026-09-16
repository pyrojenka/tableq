import { useEffect, useState } from 'react'
import { subscribe } from '../api/mockApi'

// Bumps a counter whenever the mock backend changes so views can refetch.
export function useMockRefresh() {
  const [tick, setTick] = useState(0)

  useEffect(() => {
    const unsubscribe = subscribe(() => setTick((t) => t + 1))
    return () => {
      unsubscribe()
    }
  }, [])

  return tick
}
