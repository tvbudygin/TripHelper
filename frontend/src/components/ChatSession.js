import { fetchMessages, sendMessage } from '../api/chatApi.js'

const GREETING = { role: 'assistant', content: 'Здравствуйте! Спросите что-нибудь о вашей поездке.' }

/** История сообщений чата и отправка новых */
class ChatSession {
  constructor() {
    this.messages = [GREETING]
  }

  /** Загружает историю чата (если её нет — остаётся приветствие) */
  async loadHistory() {
    const history = await fetchMessages()
    if (history.length > 0) {
      this.messages = history
    }
    return this.messages
  }

  /** Добавляет сообщение пользователя */
  addUserMessage(text) {
    this.messages = [...this.messages, { role: 'user', content: text }]
    return this.messages
  }

  /** Получает ответ помощника и добавляет его в историю */
  async fetchAssistantReply(text) {
    const assistantMessage = await sendMessage(text)
    this.messages = [...this.messages, assistantMessage]
    return this.messages
  }
}

export default ChatSession
