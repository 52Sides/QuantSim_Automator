import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'
import Plot from 'react-plotly.js'

export default function SimulationDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resp = await api.get(`/simulations_history/${id}`)
        setData(resp.data)
      } catch {
        alert('Failed to load simulation details')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  if (loading) {
  return (
    <div className="flex justify-center mt-10">
      <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-blue-600" />
    </div>
  )
}
  if (!data) return <div className="text-center py-20">No data</div>

  return (
    <div className="max-w-5xl mx-auto py-10 px-6">
      <button
        onClick={() => navigate('/history')}
        className="mb-6 text-blue-600 hover:underline text-sm"
      >
        ← Back to History
      </button>

      <h1 className="text-2xl font-semibold mb-2">{data.command}</h1>
      <p className="text-gray-500 mb-6">Created: {new Date(data.created_at).toLocaleString()}</p>

      <div className="grid grid-cols-3 gap-4 text-center mb-8">
        <MetricCard label="CAGR" value={data.metrics.cagr?.toFixed(3) ?? '-'} />
        <MetricCard label="Sharpe" value={data.metrics.sharpe?.toFixed(3) ?? '-'} />
        <MetricCard
          label="Max Drawdown"
          value={data.metrics.max_drawdown ? `${(data.metrics.max_drawdown * 100).toFixed(2)}%` : '-'}
        />
      </div>

      <Plot
        data={[
          {
            x: data.portfolio.map((p: any) => p.date),
            y: data.portfolio.map((p: any) => p.portfolio_value),
            type: 'scatter',
            mode: 'lines',
            line: { color: '#2563eb', width: 2 },
          },
        ]}
        layout={{
          margin: { l: 40, r: 20, t: 10, b: 40 },
          autosize: true,
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '420px' }}
      />
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-4 shadow-sm">
      <p className="text-gray-600 dark:text-gray-300 text-sm">{label}</p>
      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">{value}</p>
    </div>
  )
}
