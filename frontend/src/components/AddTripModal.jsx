import Modal from './Modal.jsx'
import TripForm from './TripForm.jsx'

/** Модальное окно с формой поездки - используется только для редактирования из свёрнутого вида */
function AddTripModal({ trip, onClose, onSaved }) {
  return (
    <Modal title={trip ? 'Изменить поездку' : 'Новая поездка'} onClose={onClose}>
      <TripForm trip={trip} onSaved={onSaved} />
    </Modal>
  )
}

export default AddTripModal
