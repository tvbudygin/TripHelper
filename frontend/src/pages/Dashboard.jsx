import { useState, useEffect } from 'react'
import { getTrips, createTrip, deleteTrip } from '../api/trips.js'
import AddTripModal from '../components/AddTripModal.jsx'
import './Dashboard.css'

function Dashboard() {
  const [trips, setTrips] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)

  function loadTrips() {
    setLoading(true)
    getTrips()
      .then((data) => setTrips(data))
      .catch((err) => console.error('Не загрузились поездки:', err))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadTrips()
  }, [])

  function handleCreateTrip(tripData) {
    createTrip(tripData).then((newTrip) => {
      setTrips((prev) => [newTrip, ...prev])
      setShowModal(false)
    })
  }

  function handleDeleteTrip(id) {
    if (!window.confirm('Точно удалить эту поездку?')) return
    deleteTrip(id).then(() => {
      setTrips((prev) => prev.filter((t) => t.id !== id))
    })
  }

  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    })
  }

  const statusLabels = { planning: 'Планирование', upcoming: 'Скоро', completed: 'Завершено', cancelled: 'Отменено' }

  if (loading) {
    return <div className="page-wrapper"><div className="loading-screen">Загрузка...</div></div>
  }

  const tripWord = trips.length === 1 ? 'поездка' : (trips.length >= 2 && trips.length <= 4) ? 'поездки' : 'поездок'

  return (
    <div className="page-wrapper">
      <div className="dashboard container">
        <div className="dashboard-header">
          <div>
            <h1>Мои поездки</h1>
            <p className="dashboard-subtitle">
              {trips.length > 0 ? `У вас ${trips.length} ${tripWord}` : 'Пока нет ни одной поездки'}
            </p>
          </div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            + Создать поездку
          </button>
        </div>

        {trips.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🗺</div>
            <h2>Пока пусто</h2>
            <p>Создайте свою первую поездку и начните планировать!</p>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
              Создать поездку
            </button>
          </div>
        ) : (
          <div className="trips-grid">
            {trips.map((trip) => (
              <div key={trip.id} className="trip-card">
                <div className="trip-card-header">
                  <span className={`trip-status status-${trip.status}`}>
                    {statusLabels[trip.status] || trip.status}
                  </span>
                  <button className="trip-delete-btn" onClick={() => handleDeleteTrip(trip.id)} title="Удалить">
                    ×
                  </button>
                </div>
                <h3 className="trip-card-title">{trip.title}</h3>
                <div className="trip-card-location">
                  📍 {trip.city}, {trip.country}
                </div>
                <div className="trip-card-dates">
                  🗓 {formatDate(trip.start_date)} — {formatDate(trip.end_date)}
                </div>
                {trip.description && <p className="trip-card-desc">{trip.description}</p>}
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && <AddTripModal onCreate={handleCreateTrip} onClose={() => setShowModal(false)} />}
    </div>
  )
}

export default Dashboard
