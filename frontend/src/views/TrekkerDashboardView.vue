<template>
  <div class="d-flex">
    <TrekkerSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">Trekker Portal</h2>
          <p class="text-muted mb-0">
            Welcome back, <strong>{{ profile.trekker_name || authService.state.user?.full_name }}</strong>! Ready for your next mountain adventure?
          </p>
        </div>
        <div>
          <router-link to="/trekker/treks" class="btn btn-success me-2">
            🏔️ Browse Available Treks
          </router-link>
          <router-link to="/trekker/bookings" class="btn btn-outline-primary">
            🎟️ My Bookings
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
        <p class="mt-2 text-muted small">Loading your dashboard and booking metrics...</p>
      </div>

      <div v-else>
        <!-- Primary Metric Row -->
        <div class="row g-3 mb-4">
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Total Bookings"
              :value="metrics.total_bookings"
              icon="🎟️"
              color="primary"
              subtitle="All expedition reservations"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Active Confirmed"
              :value="metrics.active_bookings"
              icon="✅"
              color="success"
              subtitle="Confirmed upcoming spots"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Cancelled"
              :value="metrics.cancelled_bookings"
              icon="❌"
              color="secondary"
              subtitle="Cancelled reservations"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Completed"
              :value="metrics.completed_bookings"
              icon="🏁"
              color="info"
              subtitle="Finished expeditions"
            />
          </div>
        </div>

        <!-- Upcoming Expeditions Section -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0 fw-semibold">Upcoming Confirmed Expeditions</h5>
            <router-link to="/trekker/bookings" class="btn btn-sm btn-outline-primary">
              View All History
            </router-link>
          </div>
          <div class="card-body p-0">
            <div v-if="upcomingTreks.length === 0" class="text-center py-5 text-muted">
              <span class="fs-1 d-block mb-2">🏔️</span>
              <h5 class="fw-semibold">No upcoming expeditions booked.</h5>
              <p class="small text-muted mb-3">Discover and reserve exciting mountain trails from our catalog.</p>
              <router-link to="/trekker/treks" class="btn btn-primary btn-sm">
                Explore Available Treks
              </router-link>
            </div>
            <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Upcoming Bookings Table">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Trek & Location</th>
                    <th>Dates & Duration</th>
                    <th>Difficulty</th>
                    <th>Status</th>
                    <th>Progress</th>
                    <th class="text-end pe-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="b in upcomingTreks" :key="b.id">
                    <td>
                      <div class="fw-bold fs-6">{{ b.trek_name || b.trek?.name }}</div>
                      <small class="text-muted">📍 {{ b.trek_location || b.trek?.location }}</small>
                    </td>
                    <td>
                      <div class="small fw-semibold">{{ b.trek_start_date }}</div>
                      <small class="text-muted">to {{ b.trek_end_date }} ({{ b.trek_duration_days }}d)</small>
                    </td>
                    <td>
                      <span class="badge" :class="getDifficultyBadge(b.trek_difficulty)">
                        {{ b.trek_difficulty }}
                      </span>
                    </td>
                    <td>
                      <BookingStatusBadge :status="b.booking_status" />
                    </td>
                    <td>
                      <span class="badge" :class="getProgressBadge(b.trek_operational_progress)">
                        {{ b.trek_operational_progress || 'Not Started' }}
                      </span>
                    </td>
                    <td class="text-end pe-3">
                      <router-link :to="`/trekker/treks/${b.trek_id}`" class="btn btn-sm btn-outline-primary">
                        View Trek
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Recent Booking Activity -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="card-title mb-0 fw-semibold">Recent Booking Activity</h5>
          </div>
          <div class="card-body p-0">
            <div v-if="recentBookings.length === 0" class="text-center py-4 text-muted small">
              No recent booking activity recorded.
            </div>
            <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Recent Activity Table">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Booking ID</th>
                    <th>Trek Name</th>
                    <th>Booking Date</th>
                    <th>Status</th>
                    <th>Payment</th>
                    <th class="text-end pe-3">Details</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in recentBookings" :key="item.id">
                    <td>
                      <span class="badge bg-light text-dark border">#{{ item.id }}</span>
                    </td>
                    <td>
                      <div class="fw-semibold">{{ item.trek_name }}</div>
                      <small class="text-muted">{{ item.trek_location }}</small>
                    </td>
                    <td>
                      <span class="small">{{ formatDate(item.booking_date) }}</span>
                    </td>
                    <td>
                      <BookingStatusBadge :status="item.booking_status" />
                    </td>
                    <td>
                      <span
                        class="badge"
                        :class="item.payment_status === 'Paid' ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-warning-subtle text-warning border border-warning-subtle'"
                      >
                        {{ item.payment_status || 'Pending' }}
                      </span>
                    </td>
                    <td class="text-end pe-3">
                      <router-link :to="`/trekker/treks/${item.trek_id}`" class="btn btn-sm btn-outline-secondary">
                        View
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authService } from '../services/auth'
import api from '../services/api'
import TrekkerSidebar from '../components/TrekkerSidebar.vue'
import StatCard from '../components/StatCard.vue'
import BookingStatusBadge from '../components/BookingStatusBadge.vue'

const loading = ref(true)
const error = ref('')
const profile = ref({})
const metrics = ref({
  total_bookings: 0,
  active_bookings: 0,
  cancelled_bookings: 0,
  completed_bookings: 0
})
const upcomingTreks = ref([])
const recentBookings = ref([])

const getDifficultyBadge = (difficulty) => {
  switch (difficulty) {
    case 'Easy': return 'bg-success-subtle text-success border border-success-subtle'
    case 'Moderate': return 'bg-warning-subtle text-warning border border-warning-subtle'
    case 'Hard': return 'bg-danger-subtle text-danger border border-danger-subtle'
    default: return 'bg-secondary'
  }
}

const getProgressBadge = (progress) => {
  switch (progress) {
    case 'Not Started': return 'bg-secondary'
    case 'Started': return 'bg-info text-dark'
    case 'Ongoing': return 'bg-primary'
    case 'Completed': return 'bg-success'
    default: return 'bg-secondary'
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

const fetchDashboardData = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('/api/trekker/dashboard')
    const data = res.data?.data || {}
    profile.value = {
      trekker_name: data.trekker_name,
      email: data.email,
      contact_number: data.contact_number,
      status: data.status
    }
    metrics.value = {
      total_bookings: data.total_bookings || 0,
      active_bookings: data.active_bookings || 0,
      cancelled_bookings: data.cancelled_bookings || 0,
      completed_bookings: data.completed_bookings || 0
    }
    upcomingTreks.value = data.upcoming_treks || []
    recentBookings.value = data.recent_bookings || []
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load dashboard data.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>
