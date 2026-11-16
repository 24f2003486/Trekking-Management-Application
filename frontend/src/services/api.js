import axios from 'axios'

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('tma_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle unauthenticated responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token if token is invalid or expired
      localStorage.removeItem('tma_access_token')
      localStorage.removeItem('tma_user')
    }
    return Promise.reject(error)
  }
)

export default api

