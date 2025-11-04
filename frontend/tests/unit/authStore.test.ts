import { useAuthStore } from '../../src/store/auth'

describe('Auth store', () => {
  beforeEach(() => {
    localStorage.clear()
    useAuthStore.setState({ accessToken: null, refreshToken: null })
  })

  it('sets tokens correctly', () => {
    const { setTokens } = useAuthStore.getState()
    setTokens('access123', 'refresh123')

    const state = useAuthStore.getState()
    expect(state.accessToken).toBe('access123')
    expect(state.refreshToken).toBe('refresh123')

    expect(localStorage.getItem('access_token')).toBe('access123')
    expect(localStorage.getItem('refresh_token')).toBe('refresh123')
  })

  it('clears tokens correctly', () => {
    const { setTokens, clear } = useAuthStore.getState()
    setTokens('a', 'b')
    clear()

    const state = useAuthStore.getState()
    expect(state.accessToken).toBeNull()
    expect(state.refreshToken).toBeNull()
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })
})
