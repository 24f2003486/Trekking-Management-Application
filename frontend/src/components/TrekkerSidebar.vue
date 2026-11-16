<template>
  <div class="trekker-sidebar bg-white border-end h-100 p-3 shadow-sm">
    <div class="d-flex align-items-center pb-3 mb-3 border-bottom">
      <span class="fs-4 me-2">🧭</span>
      <div>
        <h6 class="mb-0 fw-bold">Trekker Portal</h6>
        <small class="text-muted">Expedition Explorer</small>
      </div>
    </div>

    <!-- Trekker Profile Card -->
    <div class="card bg-light border-0 mb-3 p-2 rounded-3">
      <div class="small fw-semibold text-truncate">{{ authService.state.user?.full_name }}</div>
      <div class="text-muted small">Registered Trekker</div>
    </div>

    <nav class="nav nav-pills flex-column gap-1">
      <router-link
        to="/trekker/dashboard"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath === '/trekker/dashboard' }"
      >
        <span class="me-2">📊</span>
        <span>Dashboard</span>
      </router-link>

      <router-link
        to="/trekker/treks"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath.startsWith('/trekker/treks') }"
      >
        <span class="me-2">🏔️</span>
        <span>Browse Treks</span>
      </router-link>

      <router-link
        to="/trekker/bookings"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath.startsWith('/trekker/bookings') }"
      >
        <span class="me-2">🎟️</span>
        <span>My Bookings</span>
      </router-link>

      <router-link
        to="/trekker/profile"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath === '/trekker/profile' }"
      >
        <span class="me-2">👤</span>
        <span>My Profile</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { authService } from '../services/auth'

const route = useRoute()
const currentPath = computed(() => route.path)
</script>

<style scoped>
.trekker-sidebar {
  min-height: calc(100vh - 56px);
  width: 250px;
}

.nav-link {
  color: #495057;
  font-weight: 500;
  border-radius: 8px;
  padding: 10px 14px;
  transition: all 0.15s ease-in-out;
}

.nav-link:hover {
  background-color: #f1f3f5;
  color: #0d6efd;
}

.nav-link.active {
  background-color: #0d6efd;
  color: #ffffff !important;
}
</style>
