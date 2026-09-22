import { apiClient } from './ApiClient.js'

/** Регистрация */
export function registerUser(fullName, email, password) {
  return apiClient.post('/auth/register', { full_name: fullName, email, password })
}

/** Вход (backend ждёт форму, а не JSON) */
export function loginUser(email, password) {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  return apiClient.postForm('/auth/login', form)
}

/** Данные текущего пользователя */
export function fetchCurrentUser() {
  return apiClient.get('/auth/me')
}
