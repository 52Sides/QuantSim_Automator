import { useState } from 'react'
import api from '../api/client'

export default function SignUpForm({ onClose }: { onClose: () => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const resp = await api.post('/auth/register', { email, password })
      if (resp.status === 201) {
        alert('Registration successful! Please log in.')
        onClose()
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex justify-center items-center z-50">
      <form
        onSubmit={handleSubmit}
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 w-96"
      >
        <h2 className="text-xl font-semibold mb-4 text-center">Sign up</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full mb-3 p-2 rounded border dark:bg-gray-700 dark:border-gray-600"
          required
        />
        <input
          type="password"
          placeholder="Password (min 6 chars)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full mb-4 p-2 rounded border dark:bg-gray-700 dark:border-gray-600"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium disabled:opacity-50"
        >
          {loading ? 'Signing up...' : 'Sign up'}
        </button>
        <button
          type="button"
          onClick={onClose}
          className="w-full mt-3 text-gray-500 hover:text-gray-700 text-sm"
        >
          Cancel
        </button>
      </form>
    </div>
  )
}
