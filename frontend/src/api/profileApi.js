import { apiClient } from './ApiClient.js'

/** Данные профиля */
export function fetchProfile() {
  return apiClient.get('/profile/')
}

/** Статистика путешествий */
export function fetchStats() {
  return apiClient.get('/profile/stats')
}

/** Страны для карты */
export function fetchVisitedCountries() {
  return apiClient.get('/profile/visited-countries')
}

/** Включает или выключает уведомления */
export function updateNotificationSettings(notificationsEnabled) {
  return apiClient.patch('/profile/settings', { notifications_enabled: notificationsEnabled })
}
