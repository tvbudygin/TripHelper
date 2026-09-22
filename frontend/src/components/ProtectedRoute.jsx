import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

/** Пускает на страницу только авторизованных */
function ProtectedRoute({ children }) {
  const { user, isCheckingSession } = useAuth()

  if (isCheckingSession) {
    return <div className="loading-screen">Загрузка...</div>
  }
  if (!user) {
    return <Navigate to="/login" replace />
  }
  return children
}

export default ProtectedRoute
