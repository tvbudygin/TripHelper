import { useEffect, useRef, useState } from 'react'
import ChatSession from './ChatSession.js'
import { getErrorMessage } from '../api/errors.js'
import './ChatWidget.css'

/** Показывает сообщение: **текст** становится жирным, длинное тире заменяется дефисом */
function renderMessageContent(text) {
  const parts = text.replaceAll('—', '-').split(/(\*\*[^*]+\*\*)/g)
  return parts.map((part, index) => {
    const boldMatch = part.match(/^\*\*([^*]+)\*\*$/)
    return boldMatch ? <strong key={index}>{boldMatch[1]}</strong> : part
  })
}

/** Кнопка чата и боковая панель с чатом */
function ChatWidget() {
  const sessionRef = useRef(new ChatSession())
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState(sessionRef.current.messages)
  const [draft, setDraft] = useState('')
  const [isWaiting, setIsWaiting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [showScrollButton, setShowScrollButton] = useState(false)
  const messagesRef = useRef(null)
  // true, пока пользователь не прокрутил чат вверх
  const isNearBottomRef = useRef(true)

  useEffect(() => {
    sessionRef.current.loadHistory().then(setMessages)
  }, [])

  // при новых сообщениях прокручиваем вниз
  useEffect(() => {
    if (isNearBottomRef.current) scrollToBottom(false)
  }, [messages, isWaiting, isOpen])

  /** Прокручивает сообщения вниз */
  function scrollToBottom(smooth = true) {
    const list = messagesRef.current
    if (list) list.scrollTo({ top: list.scrollHeight, behavior: smooth ? 'smooth' : 'auto' })
  }

  /** Показывает стрелку вниз, если чат прокручен вверх */
  function handleScroll() {
    const list = messagesRef.current
    const distanceFromBottom = list.scrollHeight - list.scrollTop - list.clientHeight
    isNearBottomRef.current = distanceFromBottom < 80
    setShowScrollButton(distanceFromBottom > 80)
  }

  function toggleChat() {
    setIsOpen((wasOpen) => !wasOpen)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const text = draft.trim()
    if (!text || isWaiting) return

    setDraft('')
    setErrorMessage('')
    setMessages(sessionRef.current.addUserMessage(text))
    setIsWaiting(true)
    try {
      const updatedHistory = await sessionRef.current.fetchAssistantReply(text)
      setMessages(updatedHistory)
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Не удалось отправить сообщение'))
    } finally {
      setIsWaiting(false)
    }
  }

  return (
    <>
      <button type="button" className="chat-toggle-button" onClick={toggleChat}>
        {isOpen ? 'Закрыть' : 'Чат'}
      </button>

      <aside className={`chat-panel ${isOpen ? 'chat-panel-open' : ''}`}>
        <div className="chat-panel-header">
          <span>Помощник TripHelper</span>
          <button type="button" className="chat-close-button" onClick={toggleChat}>
            ×
          </button>
        </div>

        <div className="chat-panel-body">
          <div className="chat-panel-messages" ref={messagesRef} onScroll={handleScroll}>
            {messages.map((message, index) => (
              <div key={index} className={`chat-message chat-message-${message.role}`}>
                {renderMessageContent(message.content)}
              </div>
            ))}
            {isWaiting && <div className="chat-message chat-message-assistant chat-message-pending">Печатает...</div>}
          </div>

          {showScrollButton && (
            <button
              type="button"
              className="chat-scroll-button"
              onClick={() => scrollToBottom(true)}
              aria-label="Вниз, к последним сообщениям"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 5v14M5 12l7 7 7-7" />
              </svg>
            </button>
          )}
        </div>

        {errorMessage && <div className="alert-error chat-panel-error">{errorMessage}</div>}

        <form className="chat-panel-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Написать сообщение..."
            disabled={isWaiting}
          />
          <button type="submit" className="btn btn-primary btn-sm" disabled={isWaiting}>
            Отправить
          </button>
        </form>
      </aside>
    </>
  )
}

export default ChatWidget
