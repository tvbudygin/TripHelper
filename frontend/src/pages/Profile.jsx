import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchCurrentUser } from '../api/authApi.js'
import { fetchStats, fetchVisitedCountries, updateNotificationSettings } from '../api/profileApi.js'
import { fetchTrips, updateTrip } from '../api/tripsApi.js'
import { useAuth } from '../context/AuthContext.jsx'
import WorldMap from '../components/WorldMap.jsx'
import { formatTripPlaces, getTripCountries } from '../utils/tripCountries.js'
import './Profile.css'

const STAT_LABELS = {
  total_trips: 'Поездок',
  countries_visited: 'Стран',
  cities_visited: 'Городов',
  total_activities: 'Активностей',
  total_transports: 'Перемещений',
  total_accommodations: 'Мест проживания',
}

const ALL_FILTER = 'Все'

/** Год из даты 2026-05-01 */
function getYear(isoDate) {
  return isoDate.slice(0, 4)
}

/** Страница профиля */
function Profile() {
  const [profile, setProfile] = useState(null)
  const [stats, setStats] = useState(null)
  const [trips, setTrips] = useState([])
  const [visitedCountries, setVisitedCountries] = useState([])
  const [yearFilter, setYearFilter] = useState(ALL_FILTER)
  const [countryFilter, setCountryFilter] = useState(ALL_FILTER)
  const [isCompletedOpen, setIsCompletedOpen] = useState(false)

  const { clearSession } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    clearSession()
    navigate('/')
  }

  useEffect(() => {
    fetchCurrentUser().then(setProfile)
    fetchStats().then(setStats)
    fetchTrips().then(setTrips)
    fetchVisitedCountries().then(setVisitedCountries)
  }, [])

  const years = useMemo(
    () => [...new Set(trips.map((trip) => getYear(trip.start_date)))].sort(),
    [trips],
  )
  const countries = useMemo(
    () => [...new Set(trips.flatMap(getTripCountries))].sort(),
    [trips],
  )
  const activeTrips = trips.filter((trip) => !trip.is_completed)
  const completedTrips = trips.filter((trip) => trip.is_completed)

  // поездки после фильтров
  const filteredTrips = activeTrips.filter((trip) => {
    const matchesYear = yearFilter === ALL_FILTER || getYear(trip.start_date) === yearFilter
    const matchesCountry = countryFilter === ALL_FILTER || getTripCountries(trip).includes(countryFilter)
    return matchesYear && matchesCountry
  })

  /** Включает и выключает уведомления */
  async function handleNotificationsToggle(event) {
    const updatedProfile = await updateNotificationSettings(event.target.checked)
    setProfile(updatedProfile)
  }

  /** Возвращает поездку из завершённых */
  async function handleRestore(tripId) {
    const restored = await updateTrip(tripId, { is_completed: false })
    setTrips((current) => current.map((trip) => (trip.id === tripId ? restored : trip)))
  }

  if (!profile || !stats) {
    return <div className="page-wrapper container">Загрузка...</div>
  }

  return (
    <div className="page-wrapper container">
      <div className="profile-header">
        <div className="profile-avatar">{profile.full_name.charAt(0).toUpperCase()}</div>
        <div className="profile-header-info">
          <h2>{profile.full_name}</h2>
          <p>{profile.email}</p>
        </div>
        <button type="button" className="btn btn-secondary btn-sm profile-logout" onClick={handleLogout}>
          Выйти
        </button>
      </div>

      <div className="profile-settings">
        <label className="settings-toggle">
          <input
            type="checkbox"
            checked={profile.notifications_enabled}
            onChange={handleNotificationsToggle}
          />
          Получать уведомления о поездках
        </label>
        {!profile.is_verified && (
          <p>Подтвердите почту по ссылке из письма, чтобы получать уведомления на email. Уведомления на сайте доступны без подтверждения.</p>
        )}
      </div>

      <h3 className="profile-stats-title">Статистика путешествий</h3>
      <div className="stats-grid">
        {Object.entries(STAT_LABELS).map(([key, label]) => (
          <div className="stat-card" key={key}>
            <span className="stat-value">{stats[key]}</span>
            <span className="stat-label">{label}</span>
          </div>
        ))}
      </div>

      <h3 className="profile-stats-title">Карта путешествий</h3>
      <div className="profile-map">
        <WorldMap visitedCountryNames={visitedCountries} />
      </div>

      <div className="profile-trips-header">
        <h3>Мои поездки</h3>
        <div className="profile-filters">
          <select value={yearFilter} onChange={(e) => setYearFilter(e.target.value)}>
            <option value={ALL_FILTER}>Все годы</option>
            {years.map((year) => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
          <select value={countryFilter} onChange={(e) => setCountryFilter(e.target.value)}>
            <option value={ALL_FILTER}>Все страны</option>
            {countries.map((country) => (
              <option key={country} value={country}>{country}</option>
            ))}
          </select>
        </div>
      </div>

      {filteredTrips.length === 0 && <p className="dashboard-empty">Поездок не найдено</p>}

      <ul className="profile-trip-list">
        {filteredTrips.map((trip) => (
          <li key={trip.id}>
            <Link to={`/trips/${trip.id}`}>
              {trip.title} - {formatTripPlaces(trip)} ({getYear(trip.start_date)})
            </Link>
          </li>
        ))}
      </ul>

      <div className="profile-completed">
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => setIsCompletedOpen((v) => !v)}>
          {isCompletedOpen ? 'Скрыть завершённые' : `Завершённые поездки (${completedTrips.length})`}
        </button>

        {isCompletedOpen && (
          completedTrips.length === 0 ? (
            <p className="dashboard-empty">Завершённых поездок пока нет</p>
          ) : (
            <ul className="profile-trip-list">
              {completedTrips.map((trip) => (
                <li key={trip.id} className="profile-completed-item">
                  <Link to={`/trips/${trip.id}`}>
                    {trip.title} - {formatTripPlaces(trip)} ({getYear(trip.start_date)})
                  </Link>
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => handleRestore(trip.id)}>
                    Вернуть
                  </button>
                </li>
              ))}
            </ul>
          )
        )}
      </div>
    </div>
  )
}

export default Profile
