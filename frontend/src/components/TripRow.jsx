import { useState } from 'react'
import { formatTripPlaces } from '../utils/tripCountries.js'
import { Link } from 'react-router-dom'
import { fetchTripDetails, deleteTrip, updateTrip } from '../api/tripsApi.js'
import { deleteItem, refreshTransportStatus } from '../api/tripItemsApi.js'
import { getErrorMessage } from '../api/errors.js'
import AddTripModal from './AddTripModal.jsx'
import Modal from './Modal.jsx'
import {
  TransportForm,
  AccommodationForm,
  ActivityForm,
  TripSection,
  renderTransportItem,
  renderAccommodationItem,
  renderActivityItem,
} from './TripItemForms.jsx'
import './TripRow.css'

const STATUS_LABELS = {
  planning: 'Планируется',
  active: 'Идёт сейчас',
  done: 'Завершена',
}

/** Форматирует дату: 01.05.2026 */
function formatDate(isoDate) {
  const [year, month, day] = isoDate.split('-')
  return `${day}.${month}.${year}`
}

/** Одна поездка в списке: по клику разворачивается и показывает перемещения, жильё и активности */
function TripRow({ trip, onDeleted, onUpdated }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [details, setDetails] = useState(null)
  const [isLoadingDetails, setIsLoadingDetails] = useState(false)
  const [isEditingTrip, setIsEditingTrip] = useState(false)
  // itemModal: какая форма открыта и какой элемент редактируется (null — новый)
  const [itemModal, setItemModal] = useState(null)

  /** Разворачивает и сворачивает поездку (при первом открытии загружает детали) */
  async function toggleExpanded() {
    const willExpand = !isExpanded
    setIsExpanded(willExpand)
    if (willExpand && !details) {
      setIsLoadingDetails(true)
      const loaded = await fetchTripDetails(trip.id)
      setDetails(loaded)
      setIsLoadingDetails(false)
    }
  }

  async function handleDelete() {
    if (!window.confirm('Удалить эту поездку вместе со всеми данными?')) return
    await deleteTrip(trip.id)
    onDeleted(trip.id)
  }

  /** Отмечает поездку завершённой */
  async function handleComplete() {
    const completed = await updateTrip(trip.id, { is_completed: true })
    onUpdated(completed)
  }

  function handleTripSaved(updatedTrip) {
    onUpdated(updatedTrip)
    setDetails((current) => (current ? { ...current, ...updatedTrip } : current))
    setIsEditingTrip(false)
  }

  /** Добавляет или обновляет элемент поездки */
  function handleItemSaved(resourceKey, savedItem) {
    setDetails((current) => {
      const items = current[resourceKey]
      const alreadyExists = items.some((item) => item.id === savedItem.id)
      const nextItems = alreadyExists
        ? items.map((item) => (item.id === savedItem.id ? savedItem : item))
        : [...items, savedItem]
      return { ...current, [resourceKey]: nextItems }
    })
    setItemModal(null)
  }

  async function handleRefreshStatus(transportId) {
    try {
      const updated = await refreshTransportStatus(trip.id, transportId)
      handleItemSaved('transports', updated)
    } catch (error) {
      window.alert(getErrorMessage(error, 'Не удалось получить статус рейса'))
    }
  }

  async function handleItemDelete(resource, resourceKey, itemId) {
    await deleteItem(trip.id, resource, itemId)
    setDetails((current) => ({
      ...current,
      [resourceKey]: current[resourceKey].filter((item) => item.id !== itemId),
    }))
  }

  return (
    <div className="trip-row">
      <div className="trip-row-summary" onClick={toggleExpanded}>
        <span className="trip-row-toggle">{isExpanded ? '▾' : '▸'}</span>

        <div className="trip-row-main">
          <div className="trip-row-title-line">
            <span className="trip-row-title">{trip.title}</span>
            <span className="trip-row-status">{STATUS_LABELS[trip.status] || trip.status}</span>
          </div>
          <span className="trip-row-place">{formatTripPlaces(trip)}</span>
          <span className="trip-row-dates">{formatDate(trip.start_date)} — {formatDate(trip.end_date)}</span>
        </div>

        <div className="trip-row-actions" onClick={(event) => event.stopPropagation()}>
          <Link to={`/trips/${trip.id}`} className="btn btn-primary btn-sm">Открыть</Link>
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => setIsEditingTrip(true)}>
            Изменить
          </button>
          <button type="button" className="btn btn-secondary btn-sm" onClick={handleComplete}>
            Завершилась
          </button>
          <button type="button" className="btn btn-danger btn-sm" onClick={handleDelete}>
            Удалить
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="trip-row-details">
          {isLoadingDetails && <p>Загрузка...</p>}
          {details && (
            <>
              {details.description && <p className="trip-description">{details.description}</p>}

              <TripSection
                title="Перемещения"
                items={details.transports}
                onAddClick={() => setItemModal({ resource: 'transports', item: null })}
                onEditClick={(item) => setItemModal({ resource: 'transports', item })}
                onDeleteClick={(id) => handleItemDelete('transports', 'transports', id)}
                renderItem={(item) => renderTransportItem(item, handleRefreshStatus)}
              />
              <TripSection
                title="Жильё"
                items={details.accommodations}
                onAddClick={() => setItemModal({ resource: 'accommodations', item: null })}
                onEditClick={(item) => setItemModal({ resource: 'accommodations', item })}
                onDeleteClick={(id) => handleItemDelete('accommodations', 'accommodations', id)}
                renderItem={renderAccommodationItem}
              />
              <TripSection
                title="Активности"
                items={details.activities}
                onAddClick={() => setItemModal({ resource: 'activities', item: null })}
                onEditClick={(item) => setItemModal({ resource: 'activities', item })}
                onDeleteClick={(id) => handleItemDelete('activities', 'activities', id)}
                renderItem={renderActivityItem}
              />
            </>
          )}
        </div>
      )}

      {isEditingTrip && (
        <AddTripModal trip={trip} onClose={() => setIsEditingTrip(false)} onSaved={handleTripSaved} />
      )}

      {itemModal?.resource === 'transports' && (
        <Modal title={itemModal.item ? 'Изменить перемещение' : 'Новое перемещение'} onClose={() => setItemModal(null)}>
          <TransportForm
            tripId={trip.id}
            initialItem={itemModal.item}
            onSaved={(saved) => handleItemSaved('transports', saved)}
          />
        </Modal>
      )}
      {itemModal?.resource === 'accommodations' && (
        <Modal title={itemModal.item ? 'Изменить жильё' : 'Новое жильё'} onClose={() => setItemModal(null)}>
          <AccommodationForm
            tripId={trip.id}
            trip={trip}
            initialItem={itemModal.item}
            onSaved={(saved) => handleItemSaved('accommodations', saved)}
          />
        </Modal>
      )}
      {itemModal?.resource === 'activities' && (
        <Modal title={itemModal.item ? 'Изменить активность' : 'Новая активность'} onClose={() => setItemModal(null)}>
          <ActivityForm
            tripId={trip.id}
            initialItem={itemModal.item}
            onSaved={(saved) => handleItemSaved('activities', saved)}
          />
        </Modal>
      )}
    </div>
  )
}

export default TripRow
