import { test, expect } from '@playwright/test'

test('displays WebSocket notification on simulation.completed', async ({ page }) => {
  // Подменяем WebSocket, чтобы не подключаться к реальному backend
  await page.route('**/ws/simulations', (route) => {
    // эмулируем поведение сервера WebSocket
    const ws = route.request().frame().page().evaluateHandle(() => {
      const ws = new WebSocket('ws://mock')
      return ws
    })
    route.fulfill({ status: 101, body: ws }) // handshake OK
  })

  // Загружаем страницу приложения
  await page.goto('/')

  // В реальном тесте можно вызвать handleSubmit() — здесь мы эмулируем входящее событие:
  await page.evaluate(() => {
    const event = new MessageEvent('message', {
      data: JSON.stringify({ type: 'simulation.completed', job_id: 'job123' }),
    })
    const sockets = (window as any).WebSocket.instances || []
    sockets.forEach((s: WebSocket) => s.dispatchEvent(event))
  })

  // Проверяем, что уведомление появилось
  const notification = page.locator('text=Simulation job123 completed')
  await expect(notification).toBeVisible()
})
