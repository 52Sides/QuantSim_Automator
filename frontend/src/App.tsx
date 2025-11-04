import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js'
import api from './api/client'
import Navbar from './components/Navbar'
import LoginForm from './components/LoginForm'
import SignUpForm from './components/SignUpForm'
import MetricCard from './components/MetricCard'

function App() {
  const [dark, setDark] = useState(false)
  const [command, setCommand] = useState('TSLA-L-50% AAPL-S-50% 2020-01-01 2021-01-01')
  const [metrics, setMetrics] = useState<any | null>(null)
  const [portfolio, setPortfolio] = useState<{ x: string[]; y: number[] } | null>(null)
  const [loading, setLoading] = useState(false)
  const [showLogin, setShowLogin] = useState(false)
  const [showSignup, setShowSignup] = useState(false)

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const resp = await api.post('/simulate/async', { command }) // async версия
      const data = resp.data.result || resp.data
      setMetrics(data)
      if (data?.portfolio) {
        const x = data.portfolio.map((p: any) => p.date)
        const y = data.portfolio.map((p: any) => p.portfolio_value)
        setPortfolio({ x, y })
      }
    } catch (err: any) {
      alert(`Simulation failed: ${err.response?.data?.detail || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  useEffect(() => {
    const showLogin = () => setShowLogin(true)
    window.addEventListener('unauthorized', showLogin)
    return () => window.removeEventListener('unauthorized', showLogin)
  }, [])

  return (
    <div className={`${dark ? 'dark' : ''}`}>
      <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200 transition-colors">
        <Navbar
          dark={dark}
          setDark={setDark}
          onShowLogin={() => setShowLogin(true)}
          onShowSignup={() => setShowSignup(true)}
        />

        <main className="flex flex-grow items-center justify-center px-4 py-10">
          <div className="w-full max-w-4xl bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
            <h1 className="text-2xl font-semibold mb-2 text-center">QuantSim Portfolio Simulator</h1>
            <p className="text-center text-gray-500 dark:text-gray-400 mb-6">
              Быстрая симуляция мультиактивных стратегий с расчётом метрик
            </p>

            <textarea
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              className="w-full border border-gray-300 dark:border-gray-600 p-3 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              rows={3}
              placeholder="Пример: TSLA-L-20% AAPL-S-80% 2020-01-01 2021-01-01"
            />
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-700 transition text-white font-medium py-2.5 rounded-lg shadow-sm disabled:opacity-50"
            >
              {loading ? 'Running Simulation...' : 'Simulate'}
            </button>

            {metrics && (
              <div className="grid grid-cols-3 gap-4 text-center mt-6">
                <MetricCard label="CAGR" value={metrics.cagr?.toFixed(3) ?? '-'} />
                <MetricCard label="Sharpe Ratio" value={metrics.sharpe?.toFixed(3) ?? '-'} />
                <MetricCard
                  label="Max Drawdown"
                  value={
                    metrics.max_drawdown
                      ? `${(metrics.max_drawdown * 100).toFixed(2)}%`
                      : '-'
                  }
                />
              </div>
            )}

            {portfolio && (
              <div className="mt-8">
                <Plot
                  data={[
                    {
                      x: portfolio.x,
                      y: portfolio.y,
                      type: 'scatter',
                      mode: 'lines',
                      line: { color: '#2563eb', width: 2 },
                      hovertemplate: '%{y:.2f} USD<br>%{x}<extra></extra>',
                    },
                  ]}
                  layout={{
                    margin: { l: 40, r: 20, t: 10, b: 40 },
                    autosize: true,
                    plot_bgcolor: dark ? '#1f2937' : '#ffffff',
                    paper_bgcolor: dark ? '#1f2937' : '#ffffff',
                    font: { color: dark ? '#e5e7eb' : '#374151' },
                  }}
                  config={{ displayModeBar: false, responsive: true }}
                  style={{ width: '100%', height: '420px' }}
                />
              </div>
            )}
          </div>
        </main>

        <footer className="text-center py-6 text-sm text-gray-400 dark:text-gray-500">
          © 2025 QuantSim Automator
        </footer>
      </div>

      {showLogin && <LoginForm onClose={() => setShowLogin(false)} />}
      {showSignup && <SignUpForm onClose={() => setShowSignup(false)} />}
    </div>
  )
}

export default App
