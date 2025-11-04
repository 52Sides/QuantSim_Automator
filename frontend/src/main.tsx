import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App.tsx'
import HistoryPage from './pages/HistoryPage.tsx'
import SimulationDetail from './pages/SimulationDetail.tsx'
import OAuthCallback from './components/OAuthCallback.tsx'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/history/:id" element={<SimulationDetail />} />
        <Route path="/oauth/callback" element={<OAuthCallback />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
)
