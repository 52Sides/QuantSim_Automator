import { useEffect, useState } from 'react'
import api from '../api/client'
import { useAuthStore } from '../store/auth'
import { useNavigate } from 'react-router-dom'

interface Simulation {
  id: number
  command: string
  created_at: string
  cagr: number | null
  sharpe: number | null
  max_drawdown: number | null
}

export default function HistoryPage() {
  const [simulations, setSimulations] = useState<Simulation[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const { accessToken } = useAuthStore()

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const resp = await api.get('/simulations_history')
        setSimulations(resp.data)
      } catch (err: any) {
        console.error(err)
        alert('Failed to load history')
      } finally {
        setLoading(false)
      }
    }

    if (accessToken) fetchHistory()
  }, [accessToken])

  if (!accessToken) {
    return (
      <div className="text-center py-20 text-gray-500 dark:text-gray-400">
        Please log in to view your simulations.
      </div>
    )
  }

  if (loading) return <div className="text-center py-20">Loading...</div>

  if (!loading && simulations.length === 0) {
  return <p className="text-center text-gray-500 mt-10">No simulations yet</p>
  }

  return (
    <div className="max-w-5xl mx-auto py-10 px-6">
        {loading && (
            <div className="flex justify-center mt-10">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-blue-600" />
            </div>
        )}
      <h1 className="text-2xl font-semibold mb-6 text-center">Simulation History</h1>
      {simulations.length === 0 ? (
        <div className="text-center text-gray-500 dark:text-gray-400">No simulations yet.</div>
      ) : (
        <table className="w-full border border-gray-200 dark:border-gray-700 text-sm">
          <thead className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
            <tr>
              <th className="py-2 px-3 text-left">Command</th>
              <th className="py-2 px-3 text-center">CAGR</th>
              <th className="py-2 px-3 text-center">Sharpe</th>
              <th className="py-2 px-3 text-center">Drawdown</th>
              <th className="py-2 px-3 text-center">Created</th>
              <th className="py-2 px-3 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            {simulations.map((s) => (
              <tr key={s.id} className="border-t border-gray-200 dark:border-gray-700">
                <td className="py-2 px-3">{s.command}</td>
                <td className="py-2 px-3 text-center">{s.cagr?.toFixed(3) ?? '-'}</td>
                <td className="py-2 px-3 text-center">{s.sharpe?.toFixed(3) ?? '-'}</td>
                <td className="py-2 px-3 text-center">
                  {s.max_drawdown ? `${(s.max_drawdown * 100).toFixed(2)}%` : '-'}
                </td>
                <td className="py-2 px-3 text-center">{new Date(s.created_at).toLocaleDateString()}</td>
                <td className="py-2 px-3 text-center">
                  <button
                    onClick={() => navigate(`/history/${s.id}`)}
                    className="text-blue-600 hover:underline"
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
