import { useState } from 'react'
import Plot from 'react-plotly.js'
import { Moon, Sun } from 'lucide-react'
import api from './api/client'
import { useAuthStore } from './store/auth'
import LoginForm from './components/LoginForm'
import SignUpForm from './components/SignUpForm'
import HistoryModal from './components/HistoryModal'

function App() {
  const [dark, setDark] = useState(false)
  const [command, setCommand] = useState('TSLA-L-50% AAPL-S-50% 2020-01-01 2021-01-01')
  const [loading, setLoading] = useState(false)
  const [showLogin, setShowLogin] = useState(false)
  const [showSignup, setShowSignup] = useState(false)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [result, setResult] = useState<any | null>(null)
  const accessToken = useAuthStore((s) => s.accessToken)
  const [showHistory, setShowHistory] = useState(false)

  const handleSubmit = async () => {
    if (!accessToken) {
      setShowLogin(true)
      return
    }
    setLoading(true)
    try {
      const resp = await api.post('/simulate/async', { command })
      setTaskId(resp.data.task_id)
      // можно добавить polling статуса позже
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`${dark ? 'dark' : ''}`}>
      <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200 transition-colors">

        {/* Navbar */}
        <header className="w-full bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-6xl mx-auto flex justify-between items-center py-3 px-6">
            <div className="text-xl font-semibold text-blue-600 dark:text-blue-400">QuantSim</div>

            <div className="flex items-center gap-3">
              {!accessToken ? (
                <>
                  <button onClick={() => setShowLogin(true)} className="px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-200 hover:text-blue-600 transition">Log in</button>
                  <button onClick={() => setShowSignup(true)} className="px-3 py-1.5 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">Sign up</button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => setShowHistory(true)}
                    className="px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-200 hover:text-blue-600 transition"
                  >
                    History
                  </button>
                  <span className="text-sm text-green-500">Logged in</span>
                </>
              )}
              <button onClick={() => setDark(!dark)} className="ml-2 p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition">
                {dark ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            </div>
          </div>
        </header>

        {/* Main */}
        <main className="flex flex-grow items-center justify-center px-4 py-10">
          <div className="w-full max-w-4xl bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
            <h1 className="text-2xl font-semibold mb-2 text-center text-gray-900 dark:text-gray-100">
              QuantSim Portfolio Simulator
            </h1>
            <p className="text-center text-gray-500 dark:text-gray-400 mb-6">
              Быстрая симуляция мультиактивных стратегий с расчётом метрик
            </p>

            <textarea
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              className="w-full border border-gray-300 dark:border-gray-600 p-3 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              rows={3}
            />

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-700 transition text-white font-medium py-2.5 rounded-lg shadow-sm disabled:opacity-50"
            >
              {loading ? 'Running Simulation...' : 'Simulate'}
            </button>

            {taskId && (
              <p className="mt-3 text-sm text-gray-500 dark:text-gray-400 text-center">
                Simulation started, task ID: {taskId}
              </p>
            )}
          </div>
        </main>

        <footer className="text-center py-6 text-sm text-gray-400 dark:text-gray-500">
          © 2025 QuantSim Automator
        </footer>
      </div>

      {showLogin && <LoginForm onClose={() => setShowLogin(false)} />}
      {showSignup && <SignUpForm onClose={() => setShowSignup(false)} />}
      {showHistory && <HistoryModal onClose={() => setShowHistory(false)} />}
    </div>
  )
}

export default App
