import { apiClient } from './ApiClient.js'
import { getLocalToday } from '../utils/localDate.js'

/** Список поездок */
export function fetchTrips() {
  return apiClient.get(`/trips/?today=${getLocalToday()}`)
}

/** Поездка со всеми перемещениями, жильём и активностями */
export function fetchTripDetails(tripId) {
  return apiClient.get(`/trips/${tripId}`)
}

/** Создаёт поездку */
export function createTrip(tripData) {
  return apiClient.post('/trips/', tripData)
}

/** Меняет поездку */
export function updateTrip(tripId, tripData) {
  return apiClient.patch(`/trips/${tripId}`, tripData)
}

/** Скачивает все поездки файлом календаря для Google или Apple Calendar */
export async function downloadCalendar() {
  const blob = await apiClient.getBlob('/trips/export.ics')
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'TripHelper.ics'
  link.click()
  URL.revokeObjectURL(url)
}

/** Удаляет поездку */
export function deleteTrip(tripId) {
  return apiClient.delete(`/trips/${tripId}`)
}
