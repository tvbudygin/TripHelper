import api from './axios.js'

export async function getProfile() {
  const res = await api.get('/profile/')
  return res.data
}

export async function getStats() {
  const res = await api.get('/profile/stats')
  return res.data
}
