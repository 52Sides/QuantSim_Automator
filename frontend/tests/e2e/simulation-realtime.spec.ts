import { test, expect } from '@playwright/test'
import { exec } from 'child_process'
import util from 'util'

const execAsync = util.promisify(exec)

test('receives real simulation.completed event via WebSocket', async ({ page }) => {
  // 1. Загружаем фронт
  await page.goto('/')
  await expect(page.locator('text=QuantSim Portfolio Simulator')).toBeVisible()

  // 2. Отправляем реальное Kafka событие
  await execAsync('docker exec quantsim-backend python scripts/send_kafka_event.py')

  // 3. Ждём, пока уведомление появится на фронте
  const notification = page.locator('text=Simulation job777 completed')
  await expect(notification).toBeVisible({ timeout: 7000 })
})
