import { useState } from 'react'
import RequiredMark from '../components/RequiredMark.jsx'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { loginUser, fetchCurrentUser } from '../api/authApi.js'
import { getErrorMessage } from '../api/errors.js'
import { useAuth } from '../context/AuthContext.jsx'
import './Auth.css'

/** Страница входа */
function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { saveSession } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const isJustVerified = searchParams.get('verified') === '1'

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')
    setIsSubmitting(true)

    try {
      const { access_token: token } = await loginUser(email, password)
      localStorage.setItem('th_access_token', token)
      const currentUser = await fetchCurrentUser()
      saveSession(token, currentUser)
      navigate('/dashboard')
    } catch (error) {
      setErrorMessage(getErrorMessage(error, 'Не удалось войти. Проверьте почту и пароль.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="page-wrapper auth-page">
      <div className="auth-card">
        <h2>Вход в аккаунт</h2>
        <p className="auth-card-subtitle">Рады видеть вас снова</p>

        {isJustVerified && <div className="alert-success">Почта подтверждена, можно входить</div>}
        {errorMessage && <div className="alert-error">{errorMessage}</div>}

        <form onSubmit={handleSubmit}>
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
            {isSubmitting ? 'Входим...' : 'Войти'}
          </button>
        </form>

        <p className="auth-switch">
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </p>
      </div>
    </div>
  )
}

export default Login
