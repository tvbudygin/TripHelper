import { useState } from 'react'
import { createExpense, deleteExpense } from '../api/expensesApi.js'
import { getErrorMessage } from '../api/errors.js'
import './BudgetSection.css'

/** Сумма цен */
function sumPrices(items) {
  return items.reduce((total, item) => total + Number(item.price || 0), 0)
}

/** Форматирует сумму: 12 500,50 */
function formatMoney(value) {
  return value.toLocaleString('ru-RU', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

/** Бюджет поездки: цены перемещений, жилья и активностей плюс свои расходы */
function BudgetSection({ trip, onExpenseAdded, onExpenseDeleted }) {
  const [title, setTitle] = useState('')
  const [amount, setAmount] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const transportsTotal = sumPrices(trip.transports)
  const accommodationsTotal = sumPrices(trip.accommodations)
  const activitiesTotal = sumPrices(trip.activities)
  const expensesTotal = sumPrices(trip.expenses.map((expense) => ({ price: expense.amount })))
  const grandTotal = transportsTotal + accommodationsTotal + activitiesTotal + expensesTotal

  async function handleAdd(event) {
    event.preventDefault()
    setErrorMessage('')
    try {
      const created = await createExpense(trip.id, { title, amount: Number(amount) })
      onExpenseAdded(created)
      setTitle('')
      setAmount('')
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Не удалось добавить расход'))
    }
  }

  async function handleDelete(expenseId) {
    await deleteExpense(trip.id, expenseId)
    onExpenseDeleted(expenseId)
  }

  return (
    <section className="trip-section budget-section">
      <div className="trip-section-header">
        <h3>Бюджет</h3>
        <span className="budget-total">Потрачено: {formatMoney(grandTotal)}</span>
      </div>

      <ul className="budget-breakdown">
        <li><span>Перемещения</span><span>{formatMoney(transportsTotal)}</span></li>
        <li><span>Жильё</span><span>{formatMoney(accommodationsTotal)}</span></li>
        <li><span>Активности</span><span>{formatMoney(activitiesTotal)}</span></li>
        <li><span>Прочие расходы</span><span>{formatMoney(expensesTotal)}</span></li>
      </ul>

      {trip.expenses.length > 0 && (
        <ul className="trip-item-list budget-expense-list">
          {trip.expenses.map((expense) => (
            <li key={expense.id} className="trip-item">
              <div>
                <strong>{expense.title}</strong>
                <br />
                <span className="trip-item-meta">{formatMoney(expense.amount)}</span>
              </div>
              <button type="button" className="btn btn-danger btn-sm" onClick={() => handleDelete(expense.id)}>
                Удалить
              </button>
            </li>
          ))}
        </ul>
      )}

      {errorMessage && <div className="alert-error">{errorMessage}</div>}
      <form className="budget-form" onSubmit={handleAdd}>
        <input
          placeholder="На что потратили (например, такси) *"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <input
          type="number"
          min="0"
          step="any"
          placeholder="Сумма *"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
        <button type="submit" className="btn btn-secondary btn-sm">Добавить расход</button>
      </form>
    </section>
  )
}

export default BudgetSection
