<template>
  <div class="admin-sidebar bg-white border-end h-100 p-3 shadow-sm">
    <div class="d-flex align-items-center pb-3 mb-3 border-bottom">
      <span class="fs-4 me-2">🛡️</span>
      <div>
        <h6 class="mb-0 fw-bold">Admin Console</h6>
        <small class="text-muted">TMA Operations</small>
      </div>
    </div>

    <nav class="nav nav-pills flex-column gap-1">
      <router-link
        to="/admin/dashboard"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath === '/admin/dashboard' }"
      >
        <span class="me-2">📊</span>
        <span>Dashboard</span>
      </router-link>

      <router-link
        to="/admin/treks"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath.startsWith('/admin/treks') }"
      >
        <span class="me-2">🏔️</span>
        <span>Trek Management</span>
      </router-link>

      <router-link
        to="/admin/staff"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath.startsWith('/admin/staff') }"
      >
        <span class="me-2">🧗</span>
        <span>Staff Management</span>
      </router-link>

      <router-link
        to="/admin/users"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath.startsWith('/admin/users') }"
      >
        <span class="me-2">👥</span>
        <span>Trekker Users</span>
      </router-link>

      <router-link
        to="/admin/bookings"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath.startsWith('/admin/bookings') }"
      >
        <span class="me-2">🎟️</span>
        <span>Bookings & History</span>
      </router-link>

      <router-link
        to="/admin/reports"
        class="nav-link d-flex align-items-center"
        :class="{ active: currentPath.startsWith('/admin/reports') }"
      >
        <span class="me-2">📈</span>
        <span>Reports & Analytics</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentPath = computed(() => route.path)
</script>

<style scoped>
.admin-sidebar {
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
