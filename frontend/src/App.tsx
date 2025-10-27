import { useState } from 'react'
import axios from 'axios'
import Plot from 'react-plotly.js'

interface Metrics {
  cagr: number
  sharpe: number
  max_drawdown: number
}

function App() {
  const [ticker, setTicker] = useState('AAPL')
  const [start, setStart] = useState('2020-01-01')
  const [end, setEnd] = useState('2021-01-01')
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [prices, setPrices] = useState<{ x: string[]; y: number[] } | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
  try {
    setLoading(true);
    const resp = await axios.post('/simulate', { ticker, start, end });
    const data = resp.data;

    setMetrics({
      cagr: data.cagr,
      sharpe: data.sharpe,
      max_drawdown: data.max_drawdown,
    });

    setPrices({
      x: data.prices.map((p: any) => p.date),
      y: data.prices.map((p: any) => p.close),
    });

  } catch (err) {
    alert('Simulation failed');
  } finally {
    setLoading(false);
  }
  };


<button
  onClick={handleSubmit}
  disabled={loading}
  className="bg-blue-600 text-white px-4 py-2 rounded"
>
  {loading ? 'Running...' : 'Simulate'}
</button>


  return (
    <div className="min-h-screen flex flex-col items-center justify-start p-8 bg-gray-50 text-gray-800">
      <div className="w-full max-w-3xl">
        <h1 className="text-3xl font-bold mb-4 text-center">QuantSim Dashboard</h1>

        <div className="flex flex-wrap justify-center gap-2 mb-6">
          <input
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="Ticker"
            className="border p-2 rounded w-32"
          />
          <input
            type="date"
            value={start}
            onChange={(e) => setStart(e.target.value)}
            className="border p-2 rounded"
          />
          <input
            type="date"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
            className="border p-2 rounded"
          />
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            {loading ? 'Running...' : 'Simulate'}
          </button>
        </div>

        {metrics && (
          <div className="bg-white shadow rounded p-4 mb-6 text-center">
            <p><strong>CAGR:</strong> {metrics.cagr.toFixed(3)}</p>
            <p><strong>Sharpe Ratio:</strong> {metrics.sharpe.toFixed(3)}</p>
            <p><strong>Max Drawdown:</strong> {(metrics.max_drawdown * 100).toFixed(2)}%</p>
          </div>
        )}

        {prices && (
          <Plot
            data={[{ x: prices.x, y: prices.y, type: 'scatter', mode: 'lines', name: ticker }]}
            layout={{ title: `${ticker} Price Chart`, autosize: true }}
            style={{ width: '100%', height: '500px' }}
          />
        )}
      </div>
    </div>
  )
}

export default App
