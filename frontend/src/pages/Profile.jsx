import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { getStats } from '../api/profile.js'
import './Profile.css'

function Profile() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getStats()
      .then((data) => setStats(data))
      .catch((err) => console.error('Статистика не загрузилась:', err))
      .finally(() => setLoading(false))
  }, [])

  const statCards = [
    { icon: '✈', value: stats?.total_trips ?? 0, label: 'Поездок' },
    { icon: '🌏', value: stats?.countries_visited ?? 0, label: 'Стран' },
    { icon: '📍', value: stats?.cities_visited ?? 0, label: 'Городов' },
    { icon: '🎭', value: stats?.total_activities ?? 0, label: 'Активностей' },
    { icon: '🚆', value: stats?.total_transports ?? 0, label: 'Перемещений' },
    { icon: '🏨', value: stats?.total_accommodations ?? 0, label: 'Жилья' },
  ]

  return (
    <div className="page-wrapper">
      <div className="profile container">
        <div className="profile-header">
          <div className="profile-avatar">
            {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div className="profile-info">
            <h1>{user?.full_name}</h1>
            <p className="profile-email">{user?.email}</p>
          </div>
        </div>

        <div className="profile-section">
          <h2 className="profile-section-title">Статистика путешествий</h2>

          {loading ? (
            <div className="loading-screen" style={{ padding: '40px 0' }}>Загрузка...</div>
          ) : (
            <div className="stats-grid">
              {statCards.map((card, i) => (
                <div className="stat-card" key={i}>
                  <div className="stat-icon">{card.icon}</div>
                  <div className="stat-value">{card.value}</div>
                  <div className="stat-label">{card.label}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Profile
