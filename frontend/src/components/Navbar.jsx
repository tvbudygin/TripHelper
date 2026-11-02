import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import NotificationBell from './NotificationBell.jsx'
import ThemeToggle from './ThemeToggle.jsx'
import './Navbar.css'

/** Верхнее меню */
function Navbar() {
  const { user } = useAuth()

  return (
    <header className="navbar">
      <div className="navbar-inner container">
        <Link to="/" className="navbar-logo">
          Trip<span>Helper</span>
        </Link>

        <nav className="navbar-links">
          <Link to="/help" className="nav-link">Помощь</Link>
          {user ? (
            <>
              <Link to="/dashboard" className="nav-link">Мои поездки</Link>
              <Link to="/profile" className="nav-link">Профиль</Link>
              <NotificationBell />
              <ThemeToggle />
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Войти</Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                Регистрация
              </Link>
              <ThemeToggle />
            </>
          )}
        </nav>
      </div>
    </header>
  )
}

export default Navbar
