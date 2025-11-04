import { useEffect, useState } from 'react'
import api from '../api/client'

interface SimulationItem {
  id: number
  command: string
  start_date: string
  end_date: string
  created_at: string
  cagr: number | null
  sharpe: number | null
  max_drawdown: number | null
  assets: string[]
}

export default function HistoryModal({ onClose }: { onClose: () => void }) {
  const [items, setItems] = useState<SimulationItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const resp = await api.get('/simulations_history/')
        setItems(resp.data)
      } catch (err: any) {
        console.error(err)
        alert(err.response?.data?.detail || 'Failed to load history')
      } finally {
        setLoading(false)
      }
    }
    fetchHistory()
  }, [])

  return (
    <div className="fixed inset-0 bg-black/50 flex justify-center items-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 w-[600px] max-h-[80vh] overflow-y-auto">
        <h2 className="text-xl font-semibold mb-4 text-center">Simulation History</h2>

        {loading ? (
          <p className="text-center text-gray-500">Loading...</p>
        ) : items.length === 0 ? (
          <p className="text-center text-gray-500">No simulations yet.</p>
        ) : (
          <div className="space-y-3">
            {items.map((s) => (
              <div
                key={s.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
              >
                <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{s.command}</p>
                <p className="text-xs text-gray-500">
                  {new Date(s.created_at).toLocaleString()} | {s.assets.join(', ')}
                </p>
                <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mt-2">
                  <span>CAGR: {s.cagr?.toFixed(3) ?? '—'}</span>
                  <span>Sharpe: {s.sharpe?.toFixed(3) ?? '—'}</span>
                  <span>Drawdown: {((s.max_drawdown ?? 0) * 100).toFixed(2)}%</span>
                </div>
              </div>
            ))}
          </div>
        )}

        <button
          onClick={onClose}
          className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium"
        >
          Close
        </button>
      </div>
    </div>
  )
}
