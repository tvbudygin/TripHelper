import { useState } from 'react'
import RequiredMark from './RequiredMark.jsx'
import { createTrip, updateTrip } from '../api/tripsApi.js'
import { getErrorMessage } from '../api/errors.js'
import { COUNTRY_SUGGESTIONS, CITY_SUGGESTIONS } from '../data/geoSuggestions.js'
import './TripForm.css'

/** Форма поездки: создаёт новую или редактирует существующую (если передан trip) */
function TripForm({ trip, onSaved, onCancel }) {
  const isEditMode = Boolean(trip)

  const [title, setTitle] = useState(trip?.title || '')
  const [country, setCountry] = useState(trip?.country || '')
  const [city, setCity] = useState(trip?.city || '')
  const [originCountry, setOriginCountry] = useState(trip?.origin_country || '')
  const [extraStops, setExtraStops] = useState(trip?.extra_stops || [])
  const [newStopCountry, setNewStopCountry] = useState('')
  const [newStopCity, setNewStopCity] = useState('')
  const [startDate, setStartDate] = useState(trip?.start_date || '')
  const [endDate, setEndDate] = useState(trip?.end_date || '')
  const [description, setDescription] = useState(trip?.description || '')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  /** Список дополнительных стран, включая ту, что уже вписана в поля */
  function stopsWithPending() {
    const pendingCountry = newStopCountry.trim()
    if (!pendingCountry) return extraStops
    return [...extraStops, { country: pendingCountry, city: newStopCity.trim() || null }]
  }

  /** Добавляет страну и город в список */
  function handleAddStop() {
    setExtraStops(stopsWithPending())
    setNewStopCountry('')
    setNewStopCity('')
  }

  function handleRemoveStop(index) {
    setExtraStops(extraStops.filter((_, itemIndex) => itemIndex !== index))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')
    setIsSubmitting(true)

    const payload = {
      title,
      country,
      extra_stops: stopsWithPending(),
      origin_country: originCountry || null,
      city,
      start_date: startDate,
      end_date: endDate,
      description: description || null,
    }

    try {
      const savedTrip = isEditMode ? await updateTrip(trip.id, payload) : await createTrip(payload)
      onSaved(savedTrip)
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Не удалось сохранить поездку'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div>
      {errorMessage && <div className="alert-error">{errorMessage}</div>}

      <form className="trip-form" onSubmit={handleSubmit}>
        <div className="form-group form-group-wide">
          <label htmlFor="title">Название поездки<RequiredMark /></label>
          <input id="title" value={title} onChange={(e) => setTitle(e.target.value)} required />
        </div>

        <div className="form-group form-group-wide">
          <label htmlFor="originCountry">Откуда выезжаете: страна</label>
          <input id="originCountry" value={originCountry} onChange={(e) => setOriginCountry(e.target.value)} list="country-suggestions" />
        </div>

        <div className="form-pair">
        <div className="form-group">
          <label htmlFor="country">Куда едете: страна<RequiredMark /></label>
          <input id="country" value={country} onChange={(e) => setCountry(e.target.value)} list="country-suggestions" required />
          <datalist id="country-suggestions">
            {COUNTRY_SUGGESTIONS.map((option) => (
              <option key={option} value={option} />
            ))}
          </datalist>
        </div>

        <div className="form-group">
          <label htmlFor="city">Куда едете: город<RequiredMark /></label>
          <input id="city" value={city} onChange={(e) => setCity(e.target.value)} list="city-suggestions" required />
          <datalist id="city-suggestions">
            {CITY_SUGGESTIONS.map((option) => (
              <option key={option} value={option} />
            ))}
          </datalist>
        </div>

        </div>

        <div className="form-group form-group-wide">
          <label htmlFor="stop-country">Куда ещё едете: страна и город</label>
          <div className="stop-add-column">
            <input
              id="stop-country"
              value={newStopCountry}
              onChange={(e) => setNewStopCountry(e.target.value)}
              list="country-suggestions"
              placeholder="Страна, например Франция"
            />
            <input
              value={newStopCity}
              onChange={(e) => setNewStopCity(e.target.value)}
              list="city-suggestions"
              placeholder="Город, например Париж"
              aria-label="Город дополнительной страны"
            />
            <button type="button" className="btn btn-secondary btn-sm" onClick={handleAddStop}>
              Добавить
            </button>
          </div>
          {extraStops.length > 0 && (
            <div className="country-chips">
              {extraStops.map((stop, index) => (
                <span key={`${stop.country}-${index}`} className="country-chip">
                  {stop.city ? `${stop.country} — ${stop.city}` : stop.country}
                  <button type="button" aria-label={`Убрать ${stop.country}`} onClick={() => handleRemoveStop(index)}>×</button>
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="startDate">Дата начала<RequiredMark /></label>
          <input
            id="startDate"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="endDate">Дата окончания<RequiredMark /></label>
          <input
            id="endDate"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            required
          />
        </div>

        <div className="form-group form-group-wide">
          <label htmlFor="description">Заметки</label>
          <textarea
            id="description"
            rows="3"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div className="trip-form-actions">
          <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
            {isSubmitting ? 'Сохраняем...' : isEditMode ? 'Сохранить изменения' : 'Создать поездку'}
          </button>
          {onCancel && (
            <button type="button" className="btn btn-secondary" onClick={onCancel}>
              Отмена
            </button>
          )}
        </div>
      </form>
    </div>
  )
}

export default TripForm
