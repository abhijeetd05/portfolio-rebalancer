import { useCallback, useEffect, useState } from 'react'
import { ApiError } from '../api/client'

interface ResourceState<T> {
  data: T | null
  loading: boolean
  error: string | null
  retry: () => void
}

function messageForError(error: unknown): string {
  if (error instanceof ApiError && error.status === 401) {
    return 'Your session has expired. Please sign in again.'
  }
  if (error instanceof ApiError && error.status === 403) {
    return 'You do not have permission to view this portfolio.'
  }
  return 'We could not load this portfolio data right now. Please try again.'
}

export function usePortfolioResource<T>(
  portfolioId: string | undefined,
  load: (id: string) => Promise<T>,
  onUnauthorized?: () => void,
): ResourceState<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(Boolean(portfolioId))
  const [error, setError] = useState<string | null>(null)
  const [attempt, setAttempt] = useState(0)

  const retry = useCallback(() => setAttempt((value) => value + 1), [])

  useEffect(() => {
    if (!portfolioId) {
      return
    }

    const id = portfolioId
    let active = true
    async function fetchResource() {
      setLoading(true)
      setError(null)
      try {
        const result = await load(id)
        if (active) setData(result)
      } catch (requestError: unknown) {
        if (active) {
          if (requestError instanceof ApiError && requestError.status === 401) onUnauthorized?.()
          setData(null)
          setError(messageForError(requestError))
        }
      } finally {
        if (active) setLoading(false)
      }
    }
    void fetchResource()

    return () => {
      active = false
    }
  }, [attempt, load, onUnauthorized, portfolioId])

  return { data, loading, error, retry }
}
