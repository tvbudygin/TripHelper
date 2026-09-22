import { apiClient } from './ApiClient.js'

/** Загружает документ и распознаёт из него поля формы (kind: transport, accommodation или activity) */
export function uploadAndParseDocument(file, kind) {
  return apiClient.uploadFile(`/uploads/parse?kind=${kind}`, file)
}
