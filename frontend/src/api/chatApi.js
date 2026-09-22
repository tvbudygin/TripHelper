import { apiClient } from './ApiClient.js'

/** История чата */
export function fetchMessages() {
  return apiClient.get('/chat/messages')
}

/** Отправляет сообщение, возвращает ответ помощника */
export function sendMessage(content) {
  return apiClient.post('/chat/messages', { content })
}
