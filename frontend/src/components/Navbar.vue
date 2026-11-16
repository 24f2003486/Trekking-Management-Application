<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
    <div class="container">
      <router-link class="navbar-brand d-flex align-items-center" to="/">
        <span class="me-2">🏔️</span>
        <span class="fw-bold">TMA V2</span>
        <span class="badge bg-secondary ms-2 small">MAD-II</span>
      </router-link>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarContent"
        aria-controls="navbarContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav ms-auto align-items-center">
          <!-- Unauthenticated Links -->
          <template v-if="!authService.state.isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Sign In</router-link>
            </li>
            <li class="nav-item">
              <router-link class="btn btn-outline-light btn-sm ms-2" to="/register">
                Register
              </router-link>
            </li>
          </template>

          <!-- Authenticated Links -->
          <template v-else>
            <li class="nav-item me-3">
              <span class="text-light small">
                Signed in as:
                <strong class="ms-1">{{ authService.state.user?.full_name }}</strong>
                <span class="badge bg-primary ms-2">{{ authService.state.user?.role }}</span>
              </span>
            </li>
            <!-- Notifications Dropdown -->
            <li class="nav-item dropdown me-2 position-relative">
              <button
                class="btn btn-sm btn-outline-light position-relative dropdown-toggle"
                type="button"
                id="notificationsDropdown"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                @click="fetchNotifications"
              >
                🔔
                <span
                  v-if="unreadCount > 0"
                  class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
                  style="font-size: 0.65rem;"
                >
                  {{ unreadCount }}
                </span>
              </button>
              <ul
                class="dropdown-menu dropdown-menu-end shadow p-2"
                style="width: 320px; max-height: 400px; overflow-y: auto;"
                aria-labelledby="notificationsDropdown"
              >
                <li class="d-flex justify-content-between align-items-center px-2 py-1 border-bottom mb-2">
                  <span class="fw-bold small">Notifications</span>
                  <button
                    v-if="unreadCount > 0"
                    class="btn btn-link btn-sm p-0 text-decoration-none small text-primary"
                    @click.stop="markAllRead"
                  >
                    Mark all read
                  </button>
                </li>
                <li v-if="notifications.length === 0" class="text-center text-muted py-3 small">
                  No notifications yet.
                </li>
                <li
                  v-for="item in notifications"
                  :key="item.id"
                  class="p-2 mb-1 rounded small border-bottom"
                  :class="item.is_read ? 'bg-light text-muted' : 'bg-white border-start border-3 border-primary'"
                >
                  <div class="d-flex justify-content-between align-items-start">
                    <strong class="text-dark">{{ item.title }}</strong>
                    <button
                      v-if="!item.is_read"
                      class="btn btn-sm btn-link p-0 text-muted ms-1"
                      title="Mark as read"
                      @click.stop="markRead(item.id)"
                    >
                      ✓
                    </button>
                  </div>
                  <div class="small mt-1 text-secondary" style="line-height: 1.3;">{{ item.message }}</div>
                  <div class="text-muted text-end mt-1" style="font-size: 0.7rem;">{{ formatDate(item.created_at) }}</div>
                </li>
              </ul>
            </li>
            <li class="nav-item">
              <router-link
                class="btn btn-sm btn-outline-info me-2"
                :to="authService.getRoleDashboardPath(authService.state.user?.role)"
              >
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <button
                class="btn btn-sm btn-danger"
                @click="handleLogout"
                :disabled="loading"
              >
                {{ loading ? 'Signing out...' : 'Logout' }}
              </button>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/auth'
import api from '../services/api'

const router = useRouter()
const loading = ref(false)
const notifications = ref([])
const unreadCount = ref(0)

const fetchNotifications = async () => {
  if (!authService.state.isAuthenticated) return
  try {
    const res = await api.get('/api/notifications')
    notifications.value = res.data?.data?.notifications || []
    unreadCount.value = res.data?.data?.unread_count || 0
  } catch (err) {
    // Ignore fetch error
  }
}

const markRead = async (id) => {
  try {
    await api.patch(`/api/notifications/${id}/read`)
    const target = notifications.value.find(n => n.id === id)
    if (target && !target.is_read) {
      target.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  } catch (err) {
    console.error(err)
  }
}

const markAllRead = async () => {
  try {
    await api.post('/api/notifications/read-all')
    notifications.value.forEach(n => { n.is_read = true })
    unreadCount.value = 0
  } catch (err) {
    console.error(err)
  }
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  if (authService.state.isAuthenticated) {
    fetchNotifications()
  }
})

const handleLogout = async () => {
  loading.value = true
  try {
    await authService.logout()
    router.push('/login')
  } finally {
    loading.value = false
  }
}
</script>

