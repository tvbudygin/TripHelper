/** Сегодняшняя дата на устройстве пользователя: 2026-11-03 */
export function getLocalToday() {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}
