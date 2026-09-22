import { apiClient } from './ApiClient.js'

/** Список уведомлений */
export function fetchNotifications() {
  return apiClient.get('/notifications/')
}

/** Отмечает уведомление прочитанным */
export function markNotificationRead(notificationId) {
  return apiClient.post(`/notifications/${notificationId}/read`)
}

/** Удаляет уведомление */
export function deleteNotification(notificationId) {
  return apiClient.delete(`/notifications/${notificationId}`)
}
