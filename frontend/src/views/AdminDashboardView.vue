<template>
  <div class="d-flex">
    <AdminSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">Administrative Dashboard</h2>
          <p class="text-muted mb-0">Overview of operational metrics, users, expeditions, and bookings.</p>
        </div>
        <div>
          <router-link to="/admin/treks/create" class="btn btn-primary me-2">
            ➕ New Trek
          </router-link>
          <router-link to="/admin/staff/create" class="btn btn-outline-primary">
            ➕ Add Staff
          </router-link>
        </div>
      </div>

      <!-- Alert / Error Banner -->
      <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ error }}
        <button type="button" class="btn-close" @click="error = ''"></button>
      </div>

      <!-- Loading Spinner -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2 text-muted small">Loading real-time database metrics...</p>
      </div>

      <div v-else>
        <!-- Primary Metric Row -->
        <div class="row g-3 mb-4">
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Total Treks"
              :value="stats.total_treks"
              icon="🏔️"
              color="primary"
              subtitle="All registered expeditions"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Total Users"
              :value="stats.total_registered_users"
              icon="👥"
              color="success"
              subtitle="Registered Trekkers"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Trek Staff"
              :value="stats.total_trek_staff"
              icon="🧗"
              color="info"
              subtitle="Field guides & leaders"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Total Bookings"
              :value="stats.total_bookings"
              icon="🎟️"
              color="warning"
              subtitle="All-time reservations"
            />
          </div>
        </div>

        <!-- Secondary Operational Breakdown -->
        <div class="row g-3 mb-4">
          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Trek Status Distribution</h6>
              </div>
              <div class="card-body">
                <ul class="list-group list-group-flush">
                  <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                    <span><span class="badge bg-success me-2">●</span> Open Treks</span>
                    <span class="fw-bold">{{ stats.open_treks || 0 }}</span>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                    <span><span class="badge bg-warning me-2">●</span> Pending Treks</span>
                    <span class="fw-bold">{{ stats.pending_treks || 0 }}</span>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                    <span><span class="badge bg-secondary me-2">●</span> Completed Treks</span>
                    <span class="fw-bold">{{ stats.completed_treks || 0 }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">User Account Health</h6>
              </div>
              <div class="card-body">
                <ul class="list-group list-group-flush">
                  <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                    <span><span class="badge bg-success me-2">●</span> Active Accounts</span>
                    <span class="fw-bold">{{ stats.active_users || 0 }}</span>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                    <span><span class="badge bg-danger me-2">●</span> Blacklisted Accounts</span>
                    <span class="fw-bold">{{ stats.blacklisted_users || 0 }}</span>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                    <span><span class="badge bg-info me-2">●</span> System Admins</span>
                    <span class="fw-bold">{{ stats.total_admins || 1 }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Administrative Quick Access</h6>
              </div>
              <div class="card-body d-flex flex-column gap-2 justify-content-center">
                <router-link to="/admin/treks" class="btn btn-outline-secondary btn-sm text-start">
                  🏔️ Manage Trek Catalog & Routes
                </router-link>
                <router-link to="/admin/staff" class="btn btn-outline-secondary btn-sm text-start">
                  🧗 Manage Field Staff & Guides
                </router-link>
                <router-link to="/admin/users" class="btn btn-outline-secondary btn-sm text-start">
                  👥 Manage Trekker Accounts & Status
                </router-link>
                <router-link to="/admin/bookings" class="btn btn-outline-secondary btn-sm text-start">
                  🎟️ View Historical Bookings
                </router-link>
                <router-link to="/admin/reports" class="btn btn-outline-primary btn-sm text-start">
                  📈 Analytics & Activity Reports
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import AdminSidebar from '../components/AdminSidebar.vue'
import StatCard from '../components/StatCard.vue'

const loading = ref(true)
const error = ref('')
const stats = ref({})

const fetchStats = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('/api/admin/dashboard')
    stats.value = res.data?.data?.stats || res.data?.data || {}
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load admin dashboard statistics.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>
