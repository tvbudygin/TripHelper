import { apiClient } from './ApiClient.js'

/** Запросы для перемещений, жилья и активностей (resource: transports, accommodations, activities) */

export function createItem(tripId, resource, data) {
  return apiClient.post(`/trips/${tripId}/${resource}/`, data)
}

export function updateItem(tripId, resource, itemId, data) {
  return apiClient.patch(`/trips/${tripId}/${resource}/${itemId}`, data)
}

export function deleteItem(tripId, resource, itemId) {
  return apiClient.delete(`/trips/${tripId}/${resource}/${itemId}`)
}

/** Обновляет статус рейса */
export function refreshTransportStatus(tripId, transportId) {
  return apiClient.post(`/trips/${tripId}/transports/${transportId}/refresh-status`)
}
