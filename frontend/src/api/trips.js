import api from './axios.js'

export async function getTrips() {
  const res = await api.get('/trips/')
  return res.data
}

export async function createTrip(data) {
  const res = await api.post('/trips/', data)
  return res.data
}

export async function deleteTrip(id) {
  await api.delete(`/trips/${id}`)
}
