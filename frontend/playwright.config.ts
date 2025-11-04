import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:5173', // Vite dev-сервер или готовый build
    headless: true,
    screenshot: 'only-on-failure',
  },
  timeout: 15000,
})
