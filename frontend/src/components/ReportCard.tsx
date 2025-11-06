import api from '../api/client'
import { useState } from 'react'

export default function ReportCard({ simulationId }: { simulationId: number }) {
  const [downloading, setDownloading] = useState(false)

  const handleDownload = async () => {
    setDownloading(true)
    try {
      const response = await api.get(`/report/${simulationId}`, { responseType: 'blob' })
      const blob = new Blob([response.data], { type: response.headers['content-type'] })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `simulation_${simulationId}.xlsx`
      link.click()
    } catch {
      alert('Report not ready or failed to generate.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="text-center mt-6">
      <button
        onClick={handleDownload}
        disabled={downloading}
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
      >
        {downloading ? 'Generating…' : 'Download Report (XLSX)'}
      </button>
    </div>
  )
}
