import { apiClient } from './ApiClient.js'

/** Добавляет расход */
export function createExpense(tripId, expenseData) {
  return apiClient.post(`/trips/${tripId}/expenses/`, expenseData)
}

/** Удаляет расход */
export function deleteExpense(tripId, expenseId) {
  return apiClient.delete(`/trips/${tripId}/expenses/${expenseId}`)
}
