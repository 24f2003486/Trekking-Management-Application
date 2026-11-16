import { reactive, readonly } from 'vue'
import api from './api'

// Centralized reactive authentication state
const state = reactive({
  user: JSON.parse(localStorage.getItem('tma_user') || 'null'),
  token: localStorage.getItem('tma_access_token') || null,
  isAuthenticated: !!localStorage.getItem('tma_access_token'),
  loading: false
})

export const authService = {
  // Read-only state export
  state: readonly(state),

  /**
   * Determine dashboard path based on role.
   */
  getRoleDashboardPath(role) {
    switch (role) {
      case 'Admin':
        return '/admin/dashboard'
      case 'Trek Staff':
        return '/staff/dashboard'
      case 'Trekker':
        return '/trekker/dashboard'
      default:
        return '/login'
    }
  },

  /**
   * User login.
   */
  async login(email, password) {
    state.loading = true
    try {
      const response = await api.post('/api/auth/login', { email, password })
      const data = response.data.data
      
      state.token = data.access_token
      state.user = data.user
      state.isAuthenticated = true
      
      localStorage.setItem('tma_access_token', data.access_token)
      localStorage.setItem('tma_user', JSON.stringify(data.user))
      
      return response.data
    } finally {
      state.loading = false
    }
  },

  /**
   * Trekker self-registration.
   */
  async register(registrationData) {
    state.loading = true
    try {
      const response = await api.post('/api/auth/register', registrationData)
      return response.data
    } finally {
      state.loading = false
    }
  },

  /**
   * User logout and token revocation.
   */
  async logout() {
    state.loading = true
    try {
      if (state.token) {
        await api.post('/api/auth/logout')
      }
    } catch (err) {
      console.warn('Logout API error or token already invalid:', err)
    } finally {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      state.loading = false
      localStorage.removeItem('tma_access_token')
      localStorage.removeItem('tma_user')
    }
  },

  /**
   * Refresh current user profile from /api/auth/me.
   */
  async fetchCurrentUser() {
    if (!state.token) return null
    try {
      const response = await api.get('/api/auth/me')
      state.user = response.data.data.user
      localStorage.setItem('tma_user', JSON.stringify(state.user))
      return state.user
    } catch (err) {
      this.logout()
      return null
    }
  }
}

