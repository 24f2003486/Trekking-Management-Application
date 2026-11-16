<template>
  <div class="d-flex">
    <AdminSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">Reports & Analytics</h2>
          <p class="text-muted mb-0">Live database-derived operational statistics, distributions, and demand analysis.</p>
        </div>
        <button class="btn btn-outline-secondary btn-sm" @click="fetchReports" :disabled="loading">
          🔄 Refresh Data
        </button>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ error }}
        <button type="button" class="btn-close" @click="error = ''"></button>
      </div>

      <!-- Loading Spinner -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2 text-muted small">Aggregating database statistics...</p>
      </div>

      <div v-else>
        <!-- Primary Metrics Overview -->
        <div class="row g-3 mb-4">
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Total Treks"
              :value="reports.total_treks"
              icon="🏔️"
              color="primary"
              subtitle="Registered routes"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Completed Treks"
              :value="reports.completed_treks"
              icon="✅"
              color="success"
              subtitle="Concluded expeditions"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Total Bookings"
              :value="reports.total_bookings"
              icon="🎟️"
              color="warning"
              subtitle="All reservations"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Distinct Participants"
              :value="reports.total_participants"
              icon="👥"
              color="info"
              subtitle="Unique trekkers booked"
            />
          </div>
        </div>

        <!-- Distributions Row -->
        <div class="row g-4 mb-4">
          <!-- Difficulty Distribution -->
          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Trek Difficulty Breakdown</h6>
              </div>
              <div class="card-body">
                <table class="table table-sm align-middle mb-0">
                  <thead>
                    <tr class="text-muted small text-uppercase">
                      <th>Difficulty</th>
                      <th class="text-end">Treks</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(count, diff) in reports.treks_by_difficulty" :key="diff">
                      <td>
                        <span class="badge" :class="getDifficultyBadge(diff)">{{ diff }}</span>
                      </td>
                      <td class="text-end fw-bold">{{ count }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Trek Status Distribution -->
          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Trek Status Distribution</h6>
              </div>
              <div class="card-body">
                <table class="table table-sm align-middle mb-0">
                  <thead>
                    <tr class="text-muted small text-uppercase">
                      <th>Status</th>
                      <th class="text-end">Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(count, status) in reports.treks_by_status" :key="status">
                      <td>
                        <span class="badge" :class="getStatusBadge(status)">{{ status }}</span>
                      </td>
                      <td class="text-end fw-bold">{{ count }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Booking Status Distribution -->
          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Booking Status Breakdown</h6>
              </div>
              <div class="card-body">
                <table class="table table-sm align-middle mb-0">
                  <thead>
                    <tr class="text-muted small text-uppercase">
                      <th>Status</th>
                      <th class="text-end">Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(count, status) in reports.bookings_by_status" :key="status">
                      <td>
                        <span class="badge" :class="getBookingStatusBadge(status)">{{ status }}</span>
                      </td>
                      <td class="text-end fw-bold">{{ count }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Popular Treks Table -->
        <div class="row g-4 mb-4">
          <div class="col-lg-7">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Most Popular Treks (by Booking Demand)</h6>
              </div>
              <div class="card-body p-0">
                <div v-if="!reports.popular_treks || reports.popular_treks.length === 0" class="text-center py-4 text-muted small">
                  No booking demand data available yet.
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light text-muted small text-uppercase">
                      <tr>
                        <th scope="col" class="ps-3">Rank</th>
                        <th scope="col">Trek Name</th>
                        <th scope="col">Location</th>
                        <th scope="col">Difficulty</th>
                        <th scope="col" class="text-end pe-3">Bookings</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(trek, idx) in reports.popular_treks" :key="trek.id">
                        <td class="ps-3 fw-bold text-secondary">#{{ idx + 1 }}</td>
                        <td class="fw-semibold">{{ trek.name || trek.trek_name }}</td>
                        <td>{{ trek.location }}</td>
                        <td>
                          <span class="badge" :class="getDifficultyBadge(trek.difficulty)">{{ trek.difficulty }}</span>
                        </td>
                        <td class="text-end pe-3">
                          <span class="badge bg-primary rounded-pill">{{ trek.booking_count }}</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- Monthly Activity -->
          <div class="col-lg-5">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Monthly Booking Activity</h6>
              </div>
              <div class="card-body p-0">
                <div v-if="!reports.monthly_activity || reports.monthly_activity.length === 0" class="text-center py-4 text-muted small">
                  No monthly booking activity recorded.
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light text-muted small text-uppercase">
                      <tr>
                        <th scope="col" class="ps-3">Month</th>
                        <th scope="col">Activity Level</th>
                        <th scope="col" class="text-end pe-3">Bookings</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="m in reports.monthly_activity" :key="m.month">
                        <td class="ps-3 fw-bold">{{ m.month }}</td>
                        <td>
                          <div class="progress" style="height: 6px;">
                            <div
                              class="progress-bar bg-info"
                              role="progressbar"
                              :style="{ width: `${Math.min(100, (m.count / (maxMonthlyCount || 1)) * 100)}%` }"
                            ></div>
                          </div>
                        </td>
                        <td class="text-end pe-3 fw-bold">{{ m.count }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import AdminSidebar from '../components/AdminSidebar.vue'
import StatCard from '../components/StatCard.vue'

const loading = ref(true)
const error = ref('')
const reports = ref({})

const fetchReports = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('/api/admin/reports')
    reports.value = res.data?.data || {}
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to retrieve reports.'
  } finally {
    loading.value = false
  }
}

const maxMonthlyCount = computed(() => {
  if (!reports.value.monthly_activity || reports.value.monthly_activity.length === 0) return 1
  return Math.max(...reports.value.monthly_activity.map(m => m.count), 1)
})

const getDifficultyBadge = (diff) => {
  switch (diff) {
    case 'Easy': return 'bg-success'
    case 'Moderate': return 'bg-warning text-dark'
    case 'Hard': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

const getStatusBadge = (status) => {
  switch (status) {
    case 'Open': return 'bg-success'
    case 'Pending': return 'bg-warning text-dark'
    case 'Approved': return 'bg-info text-dark'
    case 'Closed': return 'bg-secondary'
    case 'Completed': return 'bg-primary'
    default: return 'bg-light text-dark'
  }
}

const getBookingStatusBadge = (status) => {
  switch (status) {
    case 'Booked': return 'bg-success'
    case 'Completed': return 'bg-primary'
    case 'Cancelled': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

onMounted(() => {
  fetchReports()
})
</script>
