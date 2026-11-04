import { useState } from 'react'
import RequiredMark from './RequiredMark.jsx'
import { createItem, updateItem } from '../api/tripItemsApi.js'
import { openDocument, uploadAndParseDocument } from '../api/uploadsApi.js'
import { getErrorMessage } from '../api/errors.js'
import { CITY_SUGGESTIONS, getAirportSuggestions } from '../data/geoSuggestions.js'

/** Формы перемещений, жилья и активностей (используются на странице поездки и в списке поездок) */

const TRANSPORT_TYPES = ['Самолёт', 'Поезд', 'Автобус', 'Автомобиль', 'Паром', 'Другое']
const ACCOMMODATION_TYPES = ['Отель', 'Апартаменты', 'Хостел', 'Другое']
const ACTIVITY_TYPES = ['Музей', 'Экскурсия', 'Концерт', 'Ресторан', 'Парк', 'Выставка', 'Другое']

const TRANSPORT_STATUS_LABELS = {
  scheduled: 'В расписании',
  delayed: 'Задержан',
  cancelled: 'Отменён',
  changed: 'Изменён',
  en_route: 'В полёте',
  landed: 'Приземлился',
}

/** Загрузка документа (билет, бронь) с распознаванием полей; kind: transport, accommodation или activity */
function DocumentField({ kind, documentUrl, onUploaded, onRecognized }) {
  const [isUploading, setIsUploading] = useState(false)
  const [recognizeMessage, setRecognizeMessage] = useState('')

  async function handleFileChange(event) {
    const file = event.target.files[0]
    if (!file) return

    setIsUploading(true)
    setRecognizeMessage('')
    try {
      const { url, suggested } = await uploadAndParseDocument(file, kind)
      onUploaded(url)
      if (suggested) {
        onRecognized(suggested)
        setRecognizeMessage('Данные распознаны, проверьте поля выше')
      } else {
        setRecognizeMessage('Не удалось распознать документ, заполните поля вручную')
      }
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="form-group">
      <label>Документ (PDF/фото): попробуем распознать поля автоматически</label>
      <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={handleFileChange} />
      {isUploading && <span className="document-status">Распознаём документ...</span>}
      {!isUploading && documentUrl && <span className="document-status">Файл прикреплён</span>}
      {!isUploading && recognizeMessage && <span className="document-status">{recognizeMessage}</span>}
    </div>
  )
}

/** Подставляет распознанные значения в форму */
function applyFields(fields, setters) {
  Object.entries(setters).forEach(([name, setter]) => {
    if (fields[name] !== undefined && fields[name] !== null) setter(fields[name])
  })
}

/** Форма перемещения (новое или редактирование) */
export function TransportForm({ tripId, initialItem, onSaved }) {
  const isEditMode = Boolean(initialItem)

  const [type, setType] = useState(initialItem?.type || TRANSPORT_TYPES[0])
  const [departureLocation, setDepartureLocation] = useState(initialItem?.departure_location || '')
  const [arrivalLocation, setArrivalLocation] = useState(initialItem?.arrival_location || '')
  const [departureAirport, setDepartureAirport] = useState(initialItem?.departure_airport || '')
  const [arrivalAirport, setArrivalAirport] = useState(initialItem?.arrival_airport || '')
  const [departureDatetime, setDepartureDatetime] = useState(
    initialItem?.departure_datetime ? initialItem.departure_datetime.slice(0, 16) : '',
  )
  const [arrivalDatetime, setArrivalDatetime] = useState(
    initialItem?.arrival_datetime ? initialItem.arrival_datetime.slice(0, 16) : '',
  )
  const [statusValue, setStatusValue] = useState(initialItem?.status || 'scheduled')
  const [ticketNumber, setTicketNumber] = useState(initialItem?.ticket_number || '')
  const [airline, setAirline] = useState(initialItem?.airline || '')
  const [gateOrPlatform, setGateOrPlatform] = useState(initialItem?.gate_or_platform || '')
  const [price, setPrice] = useState(initialItem?.price ?? '')
  const [carriage, setCarriage] = useState(initialItem?.carriage || '')
  const [seat, setSeat] = useState(initialItem?.seat || '')
  const [documentUrl, setDocumentUrl] = useState(initialItem?.document_url || null)
  const [errorMessage, setErrorMessage] = useState('')
  const isPlane = type === 'Самолёт'
  const isTrain = type === 'Поезд'

  /** Заполняет форму распознанными данными */
  function applyRecognizedFields(fields) {
    applyFields(fields, {
      type: setType,
      departure_location: setDepartureLocation,
      arrival_location: setArrivalLocation,
      price: (value) => setPrice(String(value)),
      departure_airport: setDepartureAirport,
      arrival_airport: setArrivalAirport,
      departure_datetime: (value) => setDepartureDatetime(value.slice(0, 16)),
      arrival_datetime: (value) => setArrivalDatetime(value.slice(0, 16)),
      ticket_number: setTicketNumber,
      airline: setAirline,
      gate_or_platform: setGateOrPlatform,
      carriage: setCarriage,
      seat: setSeat,
    })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')
    const payload = {
      type,
      departure_location: departureLocation || null,
      arrival_location: arrivalLocation || null,
      price: price === '' ? null : Number(price),
      departure_airport: departureAirport || null,
      arrival_airport: arrivalAirport || null,
      departure_datetime: departureDatetime || null,
      arrival_datetime: arrivalDatetime || null,
      ticket_number: ticketNumber || null,
      airline: airline || null,
      gate_or_platform: gateOrPlatform || null,
      carriage: isTrain ? carriage || null : null,
      seat: seat || null,
      document_url: documentUrl,
    }

    try {
      const saved = isEditMode
        ? await updateItem(tripId, 'transports', initialItem.id, { ...payload, status: statusValue })
        : await createItem(tripId, 'transports', payload)
      onSaved(saved)
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Не удалось сохранить перемещение'))
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {errorMessage && <div className="alert-error">{errorMessage}</div>}
      <div className="form-group">
        <label>Тип транспорта<RequiredMark /></label>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          {TRANSPORT_TYPES.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label>Откуда: город</label>
        <input
          value={departureLocation}
          onChange={(e) => setDepartureLocation(e.target.value)}
          list="transport-city-suggestions"
        />
      </div>
      {isPlane && (
        <div className="form-group">
          <label>Аэропорт вылета (в городе их может быть несколько)</label>
          <input
            value={departureAirport}
            onChange={(e) => setDepartureAirport(e.target.value)}
            list="departure-airport-suggestions"
            placeholder="например, Шереметьево (SVO)"
          />
        </div>
      )}
      <div className="form-group">
        <label>Куда: город</label>
        <input
          value={arrivalLocation}
          onChange={(e) => setArrivalLocation(e.target.value)}
          list="transport-city-suggestions"
        />
      </div>
      {isPlane && (
        <div className="form-group">
          <label>Аэропорт прилёта</label>
          <input
            value={arrivalAirport}
            onChange={(e) => setArrivalAirport(e.target.value)}
            list="arrival-airport-suggestions"
            placeholder="например, Фьюмичино (FCO)"
          />
        </div>
      )}
      <datalist id="transport-city-suggestions">
        {CITY_SUGGESTIONS.map((option) => <option key={option} value={option} />)}
      </datalist>
      <datalist id="departure-airport-suggestions">
        {getAirportSuggestions(departureLocation).map((option) => <option key={option} value={option} />)}
      </datalist>
      <datalist id="arrival-airport-suggestions">
        {getAirportSuggestions(arrivalLocation).map((option) => <option key={option} value={option} />)}
      </datalist>
      <div className="form-group">
        <label>Дата и время отправления</label>
        <input
          type="datetime-local"
          value={departureDatetime}
          onChange={(e) => setDepartureDatetime(e.target.value)}
        />
      </div>
      <div className="form-group">
        <label>Дата и время прибытия</label>
        <input
          type="datetime-local"
          value={arrivalDatetime}
          onChange={(e) => setArrivalDatetime(e.target.value)}
        />
      </div>
      <div className="form-group">
        <label>{isTrain ? 'Номер поезда' : isPlane ? 'Номер рейса' : 'Номер билета'}</label>
        <input
          value={ticketNumber}
          onChange={(e) => setTicketNumber(e.target.value)}
          placeholder={isTrain ? 'например, 016А' : 'например, EK162'}
        />
      </div>
      <div className="form-group">
        <label>{isPlane ? 'Авиакомпания' : 'Перевозчик'}</label>
        <input value={airline} onChange={(e) => setAirline(e.target.value)} placeholder="например, Emirates" />
      </div>
      <div className="form-group">
        <label>Гейт / платформа / перрон</label>
        <input
          value={gateOrPlatform}
          onChange={(e) => setGateOrPlatform(e.target.value)}
          placeholder="например, гейт 14 или платформа 3"
        />
      </div>
      {isTrain && (
        <div className="form-group">
          <label>Вагон</label>
          <input value={carriage} onChange={(e) => setCarriage(e.target.value)} placeholder="например, 7" />
        </div>
      )}
      <div className="form-group">
        <label>Место</label>
        <input value={seat} onChange={(e) => setSeat(e.target.value)} placeholder="например, 14C" />
      </div>
      <div className="form-group">
        <label>Стоимость</label>
        <input type="number" min="0" step="any" value={price} onChange={(e) => setPrice(e.target.value)} />
      </div>
      {isEditMode && (
        <div className="form-group">
          <label>Статус</label>
          <select value={statusValue} onChange={(e) => setStatusValue(e.target.value)}>
            {Object.entries(TRANSPORT_STATUS_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
      )}
      <DocumentField
        kind="transport"
        documentUrl={documentUrl}
        onUploaded={setDocumentUrl}
        onRecognized={applyRecognizedFields}
      />
      <button type="submit" className="btn btn-primary">{isEditMode ? 'Сохранить' : 'Добавить'}</button>
    </form>
  )
}

/** Форма жилья */
export function AccommodationForm({ tripId, trip, initialItem, onSaved }) {
  const isEditMode = Boolean(initialItem)

  const [name, setName] = useState(initialItem?.name || '')
  const [type, setType] = useState(initialItem?.type || ACCOMMODATION_TYPES[0])
  const [checkInDate, setCheckInDate] = useState(initialItem?.check_in_date || '')
  const [checkOutDate, setCheckOutDate] = useState(initialItem?.check_out_date || '')
  const [checkInTime, setCheckInTime] = useState(initialItem?.check_in_time || '')
  const [checkOutTime, setCheckOutTime] = useState(initialItem?.check_out_time || '')
  const [address, setAddress] = useState(initialItem?.address || '')
  const [price, setPrice] = useState(initialItem?.price ?? '')
  const [documentUrl, setDocumentUrl] = useState(initialItem?.document_url || null)
  const [errorMessage, setErrorMessage] = useState('')

  /** Заполняет форму распознанными данными */
  function applyRecognizedFields(fields) {
    applyFields(fields, {
      name: setName,
      type: setType,
      address: setAddress,
      check_in_date: setCheckInDate,
      check_out_date: setCheckOutDate,
      check_in_time: setCheckInTime,
      check_out_time: setCheckOutTime,
      price: (value) => setPrice(String(value)),
    })
  }

  const isOutsideTrip =
    (checkInDate && checkInDate < trip.start_date) || (checkOutDate && checkOutDate > trip.end_date)

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')
    const payload = {
      name: name || null,
      type,
      check_in_date: checkInDate || null,
      check_out_date: checkOutDate || null,
      address: address || null,
      check_in_time: checkInTime || null,
      check_out_time: checkOutTime || null,
      price: price === '' ? null : Number(price),
      document_url: documentUrl,
    }

    try {
      const saved = isEditMode
        ? await updateItem(tripId, 'accommodations', initialItem.id, payload)
        : await createItem(tripId, 'accommodations', payload)
      onSaved(saved)
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Не удалось сохранить жильё'))
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {errorMessage && <div className="alert-error">{errorMessage}</div>}
      <div className="form-group">
        <label>Название жилья</label>
        <input value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Тип<RequiredMark /></label>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          {ACCOMMODATION_TYPES.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label>Адрес</label>
        <input value={address} onChange={(e) => setAddress(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Дата заселения</label>
        <input type="date" value={checkInDate} onChange={(e) => setCheckInDate(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Дата выезда</label>
        <input type="date" value={checkOutDate} onChange={(e) => setCheckOutDate(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Время заселения</label>
        <input type="time" value={checkInTime} onChange={(e) => setCheckInTime(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Время выселения</label>
        <input type="time" value={checkOutTime} onChange={(e) => setCheckOutTime(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Стоимость</label>
        <input type="number" min="0" step="any" value={price} onChange={(e) => setPrice(e.target.value)} />
      </div>
      {isOutsideTrip && (
        <p className="form-warning">
          Даты проживания выходят за пределы поездки ({trip.start_date} – {trip.end_date}).
        </p>
      )}
      <DocumentField
        kind="accommodation"
        documentUrl={documentUrl}
        onUploaded={setDocumentUrl}
        onRecognized={applyRecognizedFields}
      />
      <button type="submit" className="btn btn-primary">{isEditMode ? 'Сохранить' : 'Добавить'}</button>
    </form>
  )
}

/** Форма активности */
export function ActivityForm({ tripId, initialItem, onSaved }) {
  const isEditMode = Boolean(initialItem)

  const [title, setTitle] = useState(initialItem?.title || '')
  const [type, setType] = useState(initialItem?.type || ACTIVITY_TYPES[0])
  const [visitDate, setVisitDate] = useState(initialItem?.visit_date || '')
  const [visitTime, setVisitTime] = useState(initialItem?.visit_time || '')
  const [address, setAddress] = useState(initialItem?.address || '')
  const [openingTime, setOpeningTime] = useState(initialItem?.opening_time || '')
  const [closingTime, setClosingTime] = useState(initialItem?.closing_time || '')
  const [price, setPrice] = useState(initialItem?.price ?? '')
  const [documentUrl, setDocumentUrl] = useState(initialItem?.document_url || null)
  const [errorMessage, setErrorMessage] = useState('')

  /** Заполняет форму распознанными данными */
  function applyRecognizedFields(fields) {
    applyFields(fields, {
      title: setTitle,
      type: setType,
      visit_date: setVisitDate,
      visit_time: setVisitTime,
      opening_time: setOpeningTime,
      closing_time: setClosingTime,
      address: setAddress,
      price: (value) => setPrice(String(value)),
    })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')
    const payload = {
      title: title || null,
      type,
      visit_date: visitDate || null,
      visit_time: visitTime || null,
      address: address || null,
      opening_time: openingTime || null,
      closing_time: closingTime || null,
      price: price === '' ? null : Number(price),
      document_url: documentUrl,
    }

    try {
      const saved = isEditMode
        ? await updateItem(tripId, 'activities', initialItem.id, payload)
        : await createItem(tripId, 'activities', payload)
      onSaved(saved)
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Не удалось сохранить активность'))
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {errorMessage && <div className="alert-error">{errorMessage}</div>}
      <div className="form-group">
        <label>Название места или события</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Тип<RequiredMark /></label>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          {ACTIVITY_TYPES.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label>Дата посещения</label>
        <input type="date" value={visitDate} onChange={(e) => setVisitDate(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Время посещения</label>
        <input type="time" value={visitTime} onChange={(e) => setVisitTime(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Время открытия</label>
        <input type="time" value={openingTime} onChange={(e) => setOpeningTime(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Время закрытия</label>
        <input type="time" value={closingTime} onChange={(e) => setClosingTime(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Адрес</label>
        <input value={address} onChange={(e) => setAddress(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Стоимость</label>
        <input type="number" min="0" step="any" value={price} onChange={(e) => setPrice(e.target.value)} />
      </div>
      <DocumentField
        kind="activity"
        documentUrl={documentUrl}
        onUploaded={setDocumentUrl}
        onRecognized={applyRecognizedFields}
      />
      <button type="submit" className="btn btn-primary">{isEditMode ? 'Сохранить' : 'Добавить'}</button>
    </form>
  )
}

/** Раздел поездки со списком и кнопками */
export function TripSection({ title, items, renderItem, onAddClick, onEditClick, onDeleteClick }) {
  return (
    <section className="trip-section">
      <div className="trip-section-header">
        <h3>{title}</h3>
        <button type="button" className="btn btn-secondary btn-sm" onClick={onAddClick}>
          Добавить
        </button>
      </div>

      {items.length === 0 && <p className="trip-section-empty">Пока ничего не добавлено</p>}

      <ul className="trip-item-list">
        {items.map((item) => (
          <li key={item.id} className="trip-item">
            <div className="trip-item-content">{renderItem(item)}</div>
            <div className="trip-item-actions">
              <button type="button" className="btn btn-secondary btn-sm" onClick={() => onEditClick(item)}>
                Изменить
              </button>
              <button type="button" className="btn btn-danger btn-sm" onClick={() => onDeleteClick(item.id)}>
                Удалить
              </button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}

/** Кнопка открытия прикреплённого файла */
function OpenDocumentButton({ documentUrl }) {
  const [errorMessage, setErrorMessage] = useState('')

  async function handleOpen() {
    setErrorMessage('')
    try {
      await openDocument(documentUrl)
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Не удалось открыть документ'))
    }
  }

  return (
    <div className="document-open">
      <button type="button" className="btn btn-secondary btn-sm" onClick={handleOpen}>
        Открыть документ
      </button>
      {errorMessage && <div className="flight-status-error">{errorMessage}</div>}
    </div>
  )
}

/** Кнопка проверки рейса и результат строкой под временем */
function FlightStatusCheck({ item, onRefreshStatus }) {
  const [isChecking, setIsChecking] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  async function handleCheck() {
    setIsChecking(true)
    setErrorMessage('')
    try {
      await onRefreshStatus(item.id)
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Не удалось получить статус рейса'))
    } finally {
      setIsChecking(false)
    }
  }

  return (
    <>
      <button
        type="button"
        className="btn btn-secondary btn-sm refresh-status-button"
        onClick={handleCheck}
        disabled={isChecking}
      >
        {isChecking ? 'Проверяем...' : 'Обновить статус'}
      </button>
      {item.flight_summary && (
        <div className="flight-status-info">
          Рейс {item.flight_summary}
        </div>
      )}
      {errorMessage && <div className="flight-status-error">{errorMessage}</div>}
    </>
  )
}

/** Как показать перемещение в списке */
export function renderTransportItem(item, onRefreshStatus) {
  return (
    <>
      <strong>{item.type}</strong>
      {item.airline && ` (${item.airline})`}: {item.departure_location || 'откуда не указано'} →{' '}
      {item.arrival_location || 'куда не указано'}
      {(item.departure_airport || item.arrival_airport) && (
        <span className="trip-item-meta">
          {' '}({item.departure_airport || '?'} → {item.arrival_airport || '?'})
        </span>
      )}
      <br />
      <span className="trip-item-meta">
        {item.departure_datetime ? item.departure_datetime.replace('T', ' ').slice(0, 16) : 'дата не указана'}
        {' | '}{TRANSPORT_STATUS_LABELS[item.status] || 'Статус неизвестен'}
      </span>
      {item.arrival_datetime && (
        <span className="trip-item-meta"> → прибытие {item.arrival_datetime.replace('T', ' ').slice(0, 16)}</span>
      )}
      {item.actual_departure_datetime && (
        <span className="trip-item-meta trip-item-meta-alert">
          {' '}- новое время: {item.actual_departure_datetime.replace('T', ' ')}
        </span>
      )}
      {item.gate_or_platform && (
        <span className="trip-item-meta"> · {item.gate_or_platform}</span>
      )}
      {item.price != null && <span className="trip-item-meta"> · {item.price}</span>}
      {item.carriage && <span className="trip-item-meta"> · вагон {item.carriage}</span>}
      {item.seat && <span className="trip-item-meta"> · место {item.seat}</span>}
      {item.type === 'Самолёт' && item.ticket_number && (
        <FlightStatusCheck item={item} onRefreshStatus={onRefreshStatus} />
      )}
      {item.document_url && <OpenDocumentButton documentUrl={item.document_url} />}
    </>
  )
}

/** Как показать жильё в списке */
export function renderAccommodationItem(item) {
  return (
    <>
      <strong>{item.name || 'Без названия'}</strong> ({item.type})
      <br />
      <span className="trip-item-meta">
        {item.check_in_date || '-'}{item.check_in_time && ` ${item.check_in_time}`} –{' '}
        {item.check_out_date || '-'}{item.check_out_time && ` ${item.check_out_time}`}
        {item.price != null && ` · ${item.price}`}
      </span>
      {item.document_url && <OpenDocumentButton documentUrl={item.document_url} />}
    </>
  )
}

/** Как показать активность в списке */
export function renderActivityItem(item) {
  return (
    <>
      <strong>{item.title || 'Без названия'}</strong> ({item.type})
      <br />
      <span className="trip-item-meta">
        {item.visit_date || 'дата не указана'}{item.visit_time && ` ${item.visit_time}`}
        {(item.opening_time || item.closing_time) && ` · ${item.opening_time || '?'}–${item.closing_time || '?'}`}
        {item.price != null && ` · ${item.price}`}
      </span>
      {item.document_url && <OpenDocumentButton documentUrl={item.document_url} />}
    </>
  )
}
