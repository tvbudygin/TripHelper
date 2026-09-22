import { useState } from 'react'
import RequiredMark from '../components/RequiredMark.jsx'
import { Link, useNavigate } from 'react-router-dom'
import { registerUser, loginUser, fetchCurrentUser } from '../api/authApi.js'
import { getErrorMessage } from '../api/errors.js'
import { useAuth } from '../context/AuthContext.jsx'
import './Auth.css'

const MIN_PASSWORD_LENGTH = 6

/** Страница регистрации */
function Register() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { saveSession } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')

    if (password.length < MIN_PASSWORD_LENGTH) {
      setErrorMessage(`Пароль должен быть не короче ${MIN_PASSWORD_LENGTH} символов`)
      return
    }

    setIsSubmitting(true)
    try {
      await registerUser(fullName, email, password)
      const { access_token: token } = await loginUser(email, password)
      localStorage.setItem('th_access_token', token)
      const currentUser = await fetchCurrentUser()
      saveSession(token, currentUser)
      navigate('/dashboard')
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Не удалось зарегистрироваться.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="page-wrapper auth-page">
      <div className="auth-card">
        <h2>Создать аккаунт</h2>
        <p className="auth-card-subtitle">Это займёт меньше минуты</p>

        {errorMessage && <div className="alert-error">{errorMessage}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="fullName">Имя<RequiredMark /></label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Электронная почта<RequiredMark /></label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль<RequiredMark /></label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
            {isSubmitting ? 'Создаём аккаунт...' : 'Зарегистрироваться'}
          </button>
        </form>

        <p className="auth-switch">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  )
}

export default Register
