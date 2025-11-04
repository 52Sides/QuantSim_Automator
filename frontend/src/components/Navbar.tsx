import { useNavigate } from 'react-router-dom'
import { Moon, Sun, LogOut, History } from 'lucide-react'
import { useAuthStore } from '../store/auth'
import { useState } from 'react'

interface NavbarProps {
  dark: boolean
  setDark: (v: boolean) => void
  onShowLogin: () => void
  onShowSignup: () => void
}

export default function Navbar({ dark, setDark, onShowLogin, onShowSignup }: NavbarProps) {
  const { accessToken, clear } = useAuthStore()
  const navigate = useNavigate()
  const [hover, setHover] = useState(false)

  return (
    <header className="w-full bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-6xl mx-auto flex justify-between items-center py-3 px-6">
        <div
          className="text-xl font-semibold text-blue-600 dark:text-blue-400 cursor-pointer"
          onClick={() => navigate('/')}
        >
          QuantSim
        </div>

        {/* --- Center: History --- */}
        {accessToken && (
          <button
            onClick={() => navigate('/history')}
            className="flex items-center gap-1 text-gray-700 dark:text-gray-200 hover:text-blue-600 transition text-sm font-medium"
          >
            <History size={16} />
            History
          </button>
        )}

        {/* --- Right controls --- */}
        <div className="flex items-center gap-3">
          {!accessToken ? (
            <>
              <button
                onClick={onShowLogin}
                className="px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-200 hover:text-blue-600 transition"
              >
                Log in
              </button>
              <button
                onClick={onShowSignup}
                className="px-3 py-1.5 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Sign up
              </button>
            </>
          ) : (
            <button
              onClick={clear}
              className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-red-500 transition"
            >
              <LogOut size={16} />
              Logout
            </button>
          )}

          <button
            onClick={() => setDark(!dark)}
            className="ml-2 p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition"
          >
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </div>
    </header>
  )
}
