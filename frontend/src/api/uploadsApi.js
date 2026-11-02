import { apiClient } from './ApiClient.js'

/** Загружает документ и распознаёт из него поля формы (kind: transport, accommodation или activity) */
export function uploadAndParseDocument(file, kind) {
  return apiClient.uploadFile(`/uploads/parse?kind=${kind}`, file)
}

/** Открывает загруженный файл в новой вкладке (файл доступен только с токеном) */
export async function openDocument(documentUrl) {
  const tab = window.open('', '_blank')
  try {
    const blob = await apiClient.getBlob(documentUrl)
    const url = URL.createObjectURL(blob)
    tab.location.href = url
    setTimeout(() => URL.revokeObjectURL(url), 60000)
  } catch (error) {
    tab.close()
    throw error
  }
}
