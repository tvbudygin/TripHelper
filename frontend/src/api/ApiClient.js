import axios from 'axios'

const TOKEN_STORAGE_KEY = 'th_access_token'

/** Клиент для запросов к backend, сам добавляет токен авторизации */
class ApiClient {
  constructor(baseURL) {
    this.instance = axios.create({ baseURL })
    this.instance.interceptors.request.use((config) => {
      const token = localStorage.getItem(TOKEN_STORAGE_KEY)
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })
  }

  get(url, params) {
    return this.instance.get(url, { params }).then((response) => response.data)
  }

  post(url, body) {
    return this.instance.post(url, body).then((response) => response.data)
  }

  /** Скачивает файл (для .ics) */
  getBlob(url) {
    return this.instance.get(url, { responseType: 'blob' }).then((response) => response.data)
  }

  patch(url, body) {
    return this.instance.patch(url, body).then((response) => response.data)
  }

  postForm(url, urlEncodedBody) {
    const headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    return this.instance.post(url, urlEncodedBody, { headers }).then((response) => response.data)
  }

  uploadFile(url, file) {
    const formData = new FormData()
    formData.append('file', file)
    const headers = { 'Content-Type': 'multipart/form-data' }
    return this.instance.post(url, formData, { headers }).then((response) => response.data)
  }

  delete(url) {
    return this.instance.delete(url).then((response) => response.data)
  }
}

export const apiClient = new ApiClient('/api')
export { TOKEN_STORAGE_KEY }
