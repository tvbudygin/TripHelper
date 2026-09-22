import { createContext, useContext, useState, useEffect } from 'react'
import { fetchCurrentUser } from '../api/authApi.js'
import { TOKEN_STORAGE_KEY } from '../api/ApiClient.js'

const AuthContext = createContext(null)

/** Хранит текущего пользователя; при загрузке страницы восстанавливает вход по токену */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isCheckingSession, setIsCheckingSession] = useState(true)

  useEffect(() => {
    const savedToken = localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!savedToken) {
      setIsCheckingSession(false)
      return
    }

    fetchCurrentUser()
      .then(setUser)
      .catch(() => localStorage.removeItem(TOKEN_STORAGE_KEY))
      .finally(() => setIsCheckingSession(false))
  }, [])

  function saveSession(token, userData) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token)
    setUser(userData)
  }

  function clearSession() {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    setUser(null)
  }

  const value = { user, isCheckingSession, saveSession, clearSession }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/** Доступ к пользователю и функциям входа/выхода */
export function useAuth() {
  return useContext(AuthContext)
}
