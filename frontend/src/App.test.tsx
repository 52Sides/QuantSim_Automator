import { render, screen } from '@testing-library/react'
import App from './App'
import { describe, it, expect } from 'vitest'

describe('App component', () => {
  it('renders the main title', () => {
    render(<App />)
    expect(screen.getByText(/QuantSim Portfolio Simulator/i)).toBeInTheDocument()
  })
})
