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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/auth'

const router = useRouter()
const loading = ref(false)

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

