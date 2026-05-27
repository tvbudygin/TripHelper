import api from './axios.js'

export async function register(data) {
  const res = await api.post('/auth/register', data)
  return res.data
}

export async function login(email, password) {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)
  const res = await api.post('/auth/login', formData)
  return res.data
}

export async function getMe() {
  const res = await api.get('/auth/me')
  return res.data
}
