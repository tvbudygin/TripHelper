import { apiClient } from './ApiClient.js'

/** Список поездок */
export function fetchTrips() {
  return apiClient.get('/trips/')
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

/** Календарь поездки (.ics) */
export function exportTripCalendar(tripId) {
  return apiClient.getBlob(`/trips/${tripId}/export.ics`)
}

/** Удаляет поездку */
export function deleteTrip(tripId) {
  return apiClient.delete(`/trips/${tripId}`)
}
