import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import SimulationDetail from '../../src/pages/SimulationDetail'
import api from '../../src/api/client'

vi.mock('../../src/api/client')

describe('SimulationDetail', () => {
  it('renders simulation metrics and plot', async () => {
    vi.mocked(api.get).mockResolvedValueOnce({
      data: {
        id: 1,
        command: 'TSLA-L-50%',
        created_at: new Date().toISOString(),
        metrics: { cagr: 0.12, sharpe: 1.1, max_drawdown: 0.3 },
        portfolio: [
          { date: '2020-01-01', portfolio_value: 100 },
          { date: '2020-02-01', portfolio_value: 110 },
        ],
      },
    })

    render(
      <MemoryRouter initialEntries={['/history/1']}>
        <Routes>
          <Route path="/history/:id" element={<SimulationDetail />} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText(/TSLA-L-50%/)).toBeInTheDocument()
      expect(screen.getByText(/Sharpe/i)).toBeInTheDocument()
    })
  })
})
