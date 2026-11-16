<template>
  <div class="staff-sidebar bg-white border-end h-100 p-3 shadow-sm">
    <div class="d-flex align-items-center pb-3 mb-3 border-bottom">
      <span class="fs-4 me-2">🧭</span>
      <div>
        <h6 class="mb-0 fw-bold">Staff Console</h6>
        <small class="text-muted">Field Operations</small>
      </div>
    </div>

    <!-- Staff Profile Card -->
    <div class="card bg-light border-0 mb-3 p-2 rounded-3">
      <div class="small fw-semibold text-truncate">{{ authService.state.user?.full_name }}</div>
      <div class="text-muted small">Trek Staff Member</div>
    </div>

    <nav class="nav nav-pills flex-column gap-1">
      <router-link
        to="/staff/dashboard"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath === '/staff/dashboard' }"
      >
        <span class="me-2">📊</span>
        <span>Dashboard</span>
      </router-link>

      <router-link
        to="/staff/treks"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath.startsWith('/staff/treks') }"
      >
        <span class="me-2">🏔️</span>
        <span>My Assigned Treks</span>
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
.staff-sidebar {
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
  color: #198754;
}

.nav-link.active {
  background-color: #198754;
  color: #ffffff !important;
}
</style>
