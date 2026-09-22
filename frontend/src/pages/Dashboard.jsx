import { useEffect, useState } from 'react'
import { fetchTrips } from '../api/tripsApi.js'
import TripRow from '../components/TripRow.jsx'
import TripForm from '../components/TripForm.jsx'
import './Dashboard.css'

/** Страница со списком поездок */
function Dashboard() {
  const [trips, setTrips] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
    loadTrips()
  }, [])

  /** Загружает поездки */
  function loadTrips() {
    setIsLoading(true)
    fetchTrips()
      .then(setTrips)
      .finally(() => setIsLoading(false))
  }

  /** Добавляет новую поездку в список */
  function handleCreated(newTrip) {
    setTrips((current) => [newTrip, ...current])
    setIsCreating(false)
  }

  /** Обновляет поездку в списке */
  function handleUpdated(updatedTrip) {
    setTrips((current) => current.map((trip) => (trip.id === updatedTrip.id ? updatedTrip : trip)))
  }

  /** Убирает удалённую поездку из списка */
  function handleDeleted(tripId) {
    setTrips((current) => current.filter((trip) => trip.id !== tripId))
  }

  // завершённые поездки видны только в профиле
  const visibleTrips = trips.filter((trip) => !trip.is_completed)

  return (
    <div className="page-wrapper container">
      <div className="dashboard-header">
        <h2>Мои поездки</h2>
        {!isCreating && (
          <button type="button" className="btn btn-primary" onClick={() => setIsCreating(true)}>
            Создать поездку
          </button>
        )}
      </div>

      {isCreating && (
        <div className="dashboard-create-panel">
          <h3>Новая поездка</h3>
          <TripForm onSaved={handleCreated} onCancel={() => setIsCreating(false)} />
        </div>
      )}

      {isLoading && <p>Загрузка...</p>}

      {!isLoading && visibleTrips.length === 0 && !isCreating && (
        <p className="dashboard-empty">Пока нет ни одной поездки — самое время создать первую.</p>
      )}

      <div className="trip-list">
        {visibleTrips.map((trip) => (
          <TripRow key={trip.id} trip={trip} onDeleted={handleDeleted} onUpdated={handleUpdated} />
        ))}
      </div>
    </div>
  )
}

export default Dashboard
