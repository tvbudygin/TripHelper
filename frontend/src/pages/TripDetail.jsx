import { useEffect, useState } from 'react'
import { formatTripPlaces } from '../utils/tripCountries.js'
import { useParams } from 'react-router-dom'
import { fetchTripDetails } from '../api/tripsApi.js'
import { deleteItem, refreshTransportStatus } from '../api/tripItemsApi.js'
import AddTripModal from '../components/AddTripModal.jsx'
import Modal from '../components/Modal.jsx'
import BudgetSection from '../components/BudgetSection.jsx'
import {
  TransportForm,
  AccommodationForm,
  ActivityForm,
  TripSection,
  renderTransportItem,
  renderAccommodationItem,
  renderActivityItem,
} from '../components/TripItemForms.jsx'
import './TripDetail.css'

/** Страница поездки */
function TripDetail() {
  const { tripId } = useParams()
  const [trip, setTrip] = useState(null)
  const [isEditingTrip, setIsEditingTrip] = useState(false)
  // itemModal: какая форма открыта и какой элемент редактируется (null - новый)
  const [itemModal, setItemModal] = useState(null)

  useEffect(() => {
    fetchTripDetails(tripId).then(setTrip)
  }, [tripId])

  if (!trip) {
    return <div className="page-wrapper container">Загрузка...</div>
  }

  /** Обновляет данные поездки после редактирования */
  function handleTripUpdated(updatedTrip) {
    setTrip((current) => ({ ...current, ...updatedTrip }))
    setIsEditingTrip(false)
  }

  /** Добавляет или обновляет элемент поездки */
  function handleItemSaved(resourceKey, savedItem) {
    setTrip((current) => {
      const items = current[resourceKey]
      const alreadyExists = items.some((item) => item.id === savedItem.id)
      const nextItems = alreadyExists
        ? items.map((item) => (item.id === savedItem.id ? savedItem : item))
        : [...items, savedItem]
      return { ...current, [resourceKey]: nextItems }
    })
    setItemModal(null)
  }

  /** Обновляет статус рейса */
  async function handleRefreshStatus(transportId) {
    const updated = await refreshTransportStatus(tripId, transportId)
    handleItemSaved('transports', updated)
  }

  function handleExpenseAdded(expense) {
    setTrip((current) => ({ ...current, expenses: [...current.expenses, expense] }))
  }

  function handleExpenseDeleted(expenseId) {
    setTrip((current) => ({
      ...current,
      expenses: current.expenses.filter((expense) => expense.id !== expenseId),
    }))
  }

  /** Удаляет элемент поездки */
  async function handleItemDelete(resource, resourceKey, itemId) {
    await deleteItem(tripId, resource, itemId)
    setTrip((current) => ({
      ...current,
      [resourceKey]: current[resourceKey].filter((item) => item.id !== itemId),
    }))
  }

  return (
    <div className="page-wrapper container">
      <div className="trip-header">
        <div>
          <h2>{trip.title}</h2>
          <p>{formatTripPlaces(trip)}</p>
          {trip.origin_country && <p className="trip-item-meta">Выезд из: {trip.origin_country}</p>}
          <p className="trip-item-meta">{trip.start_date} – {trip.end_date}</p>
          {trip.description && <p className="trip-description">{trip.description}</p>}
        </div>
        <div className="trip-header-actions">
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => setIsEditingTrip(true)}>
            Изменить поездку
          </button>
        </div>
      </div>

      <TripSection
        title="Перемещения"
        items={trip.transports}
        onAddClick={() => setItemModal({ resource: 'transports', item: null })}
        onEditClick={(item) => setItemModal({ resource: 'transports', item })}
        onDeleteClick={(id) => handleItemDelete('transports', 'transports', id)}
        renderItem={(item) => renderTransportItem(item, handleRefreshStatus)}
      />

      <TripSection
        title="Жильё"
        items={trip.accommodations}
        onAddClick={() => setItemModal({ resource: 'accommodations', item: null })}
        onEditClick={(item) => setItemModal({ resource: 'accommodations', item })}
        onDeleteClick={(id) => handleItemDelete('accommodations', 'accommodations', id)}
        renderItem={renderAccommodationItem}
      />

      <TripSection
        title="Активности"
        items={trip.activities}
        onAddClick={() => setItemModal({ resource: 'activities', item: null })}
        onEditClick={(item) => setItemModal({ resource: 'activities', item })}
        onDeleteClick={(id) => handleItemDelete('activities', 'activities', id)}
        renderItem={renderActivityItem}
      />

      <BudgetSection
        trip={trip}
        onExpenseAdded={handleExpenseAdded}
        onExpenseDeleted={handleExpenseDeleted}
      />

      {isEditingTrip && (
        <AddTripModal trip={trip} onClose={() => setIsEditingTrip(false)} onSaved={handleTripUpdated} />
      )}

      {itemModal?.resource === 'transports' && (
        <Modal title={itemModal.item ? 'Изменить перемещение' : 'Новое перемещение'} onClose={() => setItemModal(null)}>
          <TransportForm
            tripId={tripId}
            initialItem={itemModal.item}
            onSaved={(saved) => handleItemSaved('transports', saved)}
          />
        </Modal>
      )}
      {itemModal?.resource === 'accommodations' && (
        <Modal title={itemModal.item ? 'Изменить жильё' : 'Новое жильё'} onClose={() => setItemModal(null)}>
          <AccommodationForm
            tripId={tripId}
            trip={trip}
            initialItem={itemModal.item}
            onSaved={(saved) => handleItemSaved('accommodations', saved)}
          />
        </Modal>
      )}
      {itemModal?.resource === 'activities' && (
        <Modal title={itemModal.item ? 'Изменить активность' : 'Новая активность'} onClose={() => setItemModal(null)}>
          <ActivityForm
            tripId={tripId}
            initialItem={itemModal.item}
            onSaved={(saved) => handleItemSaved('activities', saved)}
          />
        </Modal>
      )}
    </div>
  )
}

export default TripDetail
