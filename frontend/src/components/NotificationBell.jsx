import { useEffect, useState } from 'react'
import { deleteNotification, fetchNotifications, markNotificationRead } from '../api/notificationsApi.js'
import './NotificationBell.css'

// как часто обновляем список уведомлений
const POLL_INTERVAL_MS = 60000

/** Форматирует дату: 19.09.2026 20:20 */
function formatDateTime(isoString) {
  const [datePart, timePart] = isoString.split('T')
  const [year, month, day] = datePart.split('-')
  return `${day}.${month}.${year} ${timePart.slice(0, 5)}`
}

/** Кнопка уведомлений со списком */
function NotificationBell() {
  const [notifications, setNotifications] = useState([])
  const [isOpen, setIsOpen] = useState(false)

  /** Загружает список уведомлений */
  function refresh() {
    fetchNotifications()
      .then(setNotifications)
      .catch(() => {})
  }

  useEffect(() => {
    refresh()
    const timer = setInterval(refresh, POLL_INTERVAL_MS)
    return () => clearInterval(timer)
  }, [])

  const unreadCount = notifications.filter((item) => !item.is_read).length

  /** Открывает и закрывает список */
  function toggleDropdown() {
    setIsOpen((wasOpen) => {
      if (!wasOpen) refresh()
      return !wasOpen
    })
  }

  function handleRead(notificationId) {
    markNotificationRead(notificationId).then((updated) => {
      setNotifications((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      )
    })
  }

  /** Удаляет уведомление */
  function handleDelete(event, notificationId) {
    event.stopPropagation()
    deleteNotification(notificationId).then(() => {
      setNotifications((current) => current.filter((item) => item.id !== notificationId))
    })
  }

  return (
    <div className="notification-bell">
      <button type="button" className="notification-bell-button nav-link" onClick={toggleDropdown}>
        Уведомления
        {unreadCount > 0 && <span className="notification-badge">{unreadCount}</span>}
      </button>

      {isOpen && (
        <div className="notification-dropdown">
          {notifications.length === 0 && (
            <p className="notification-empty">Уведомлений пока нет</p>
          )}
          {notifications.map((item) => (
            <div
              key={item.id}
              className={`notification-item ${item.is_read ? '' : 'notification-item-unread'}`}
              onClick={() => handleRead(item.id)}
            >
              <div className="notification-item-top">
                <span className="notification-time">{formatDateTime(item.created_at)}</span>
                <button
                  type="button"
                  className="notification-delete-button"
                  onClick={(event) => handleDelete(event, item.id)}
                >
                  ×
                </button>
              </div>
              <span className="notification-title">{item.title}</span>
              <span className="notification-message">{item.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default NotificationBell
