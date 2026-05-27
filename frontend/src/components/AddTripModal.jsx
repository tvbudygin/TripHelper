import { useState } from 'react'

function AddTripModal({ onCreate, onClose }) {
  const [title, setTitle] = useState('')
  const [country, setCountry] = useState('')
  const [city, setCity] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (new Date(endDate) < new Date(startDate)) {
      setError('Дата окончания не может быть раньше начала')
      return
    }

    setLoading(true)

    try {
      await onCreate({
        title,
        description: description || null,
        country,
        city,
        start_date: startDate,
        end_date: endDate,
      })
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка создания поездки')
    } finally {
      setLoading(false)
    }
  }

  function handleOverlayClick(e) {
    if (e.target === e.currentTarget) onClose()
  }

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-card">
        <div className="modal-header">
          <h2>Новая поездка</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        {error && <div className="alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Название поездки</label>
            <input
              id="title"
              type="text"
              placeholder="Например: Отпуск в Турции"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
              <label htmlFor="country">Страна</label>
              <input
                id="country"
                type="text"
                placeholder="Турция"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                required
              />
          </div>

          <div className="form-group">
              <label htmlFor="city">Город</label>
              <input
                id="city"
                type="text"
                placeholder="Стамбул"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                required
              />
            </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="startDate">Дата начала</label>
              <input
                id="startDate"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="endDate">Дата окончания</label>
              <input
                id="endDate"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Описание (необязательно)</label>
            <textarea
              id="description"
              placeholder="Заметки о поездке..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Отмена
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Создание...' : 'Создать поездку'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AddTripModal
