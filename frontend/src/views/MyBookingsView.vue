<template>
  <div class="d-flex">
    <TrekkerSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
        <div>
          <h2 class="fw-bold mb-1">My Expedition Bookings</h2>
          <p class="text-muted mb-0">Track all your registered mountain treks, reservation statuses, and expedition history.</p>
        </div>
        <div class="d-flex gap-2">
          <router-link to="/trekker/treks" class="btn btn-primary">
            🏔️ Explore Treks
          </router-link>
          <button class="btn btn-outline-secondary" @click="fetchBookings" :disabled="loading">
            🔄 Refresh
          </button>
        </div>
      </div>

      <!-- Feedback Alerts -->
      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ errorMessage }}
        <button type="button" class="btn-close" @click="errorMessage = ''"></button>
      </div>

      <!-- Filter Tabs / Toolbar -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-3">
          <div class="d-flex flex-wrap align-items-center justify-content-between gap-3">
            <!-- Status Filter Pills -->
            <ul class="nav nav-pills">
              <li class="nav-item">
                <button
                  type="button"
                  class="nav-link"
                  :class="{ active: currentStatus === '' }"
                  @click="setStatusFilter('')"
                >
                  All Bookings
                </button>
              </li>
              <li class="nav-item">
                <button
                  type="button"
                  class="nav-link"
                  :class="{ active: currentStatus === 'Booked' }"
                  @click="setStatusFilter('Booked')"
                >
                  Active Confirmed
                </button>
              </li>
              <li class="nav-item">
                <button
                  type="button"
                  class="nav-link"
                  :class="{ active: currentStatus === 'Completed' }"
                  @click="setStatusFilter('Completed')"
                >
                  Completed
                </button>
              </li>
              <li class="nav-item">
                <button
                  type="button"
                  class="nav-link"
                  :class="{ active: currentStatus === 'Cancelled' }"
                  @click="setStatusFilter('Cancelled')"
                >
                  Cancelled
                </button>
              </li>
            </ul>

            <!-- Item Count Badge -->
            <div class="text-muted small">
              Total Found: <strong class="text-dark">{{ pagination.total }}</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Content State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2 text-muted small">Loading your booking history...</p>
      </div>

      <div v-else-if="bookings.length === 0" class="card border-0 shadow-sm p-5 text-center bg-white">
        <span class="fs-1 d-block mb-3">🎟️</span>
        <h4 class="fw-bold mb-2">No bookings found</h4>
        <p class="text-muted small mb-4">
          <span v-if="currentStatus">No bookings currently match the "{{ currentStatus }}" filter.</span>
          <span v-else>You have not booked any expeditions yet. Browse our catalog to reserve your next adventure!</span>
        </p>
        <div>
          <button v-if="currentStatus" class="btn btn-outline-secondary btn-sm me-2" @click="setStatusFilter('')">
            Show All Bookings
          </button>
          <router-link to="/trekker/treks" class="btn btn-primary btn-sm">
            Browse Available Treks
          </router-link>
        </div>
      </div>

      <!-- Bookings Table -->
      <div v-else class="card border-0 shadow-sm mb-4">
        <div class="table-responsive" tabindex="0" role="region" aria-label="Bookings History Table">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th scope="col" style="width: 100px;">Booking #</th>
                <th scope="col">Trek & Route</th>
                <th scope="col">Expedition Dates</th>
                <th scope="col">Booking Date</th>
                <th scope="col">Status</th>
                <th scope="col">Progress</th>
                <th scope="col">Payment</th>
                <th scope="col" class="text-end pe-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in bookings" :key="b.id">
                <td>
                  <span class="badge bg-light text-dark border font-monospace">#{{ b.id }}</span>
                </td>
                <td>
                  <div class="fw-bold text-dark">{{ b.trek_name || b.trek?.trek_name || 'Trek Details' }}</div>
                  <small class="text-muted">📍 {{ b.trek_location || b.trek?.location || 'Mountain Trail' }}</small>
                </td>
                <td>
                  <div class="small fw-semibold">{{ b.trek_start_date || b.trek?.start_date }}</div>
                  <small class="text-muted">
                    to {{ b.trek_end_date || b.trek?.end_date }} ({{ b.trek_duration_days || b.trek?.duration_days }} days)
                  </small>
                </td>
                <td>
                  <span class="small">{{ formatDate(b.booking_date || b.created_at) }}</span>
                </td>
                <td>
                  <BookingStatusBadge :status="b.booking_status" />
                </td>
                <td>
                  <span class="badge" :class="getProgressBadge(b.trek_operational_progress || b.trek?.operational_progress)">
                    {{ b.trek_operational_progress || b.trek?.operational_progress || 'Not Started' }}
                  </span>
                </td>
                <td>
                  <span
                    class="badge"
                    :class="b.payment_status === 'Paid' ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-warning-subtle text-warning border border-warning-subtle'"
                  >
                    {{ b.payment_status || 'Pending' }}
                  </span>
                </td>
                <td class="text-end pe-3">
                  <div class="btn-group btn-group-sm">
                    <router-link
                      :to="`/trekker/treks/${b.trek_id}`"
                      class="btn btn-outline-primary"
                      title="View Trek Details"
                    >
                      View Trek
                    </router-link>
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      @click="openDetails(b)"
                      title="Booking Info"
                    >
                      Info
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Footer -->
        <div v-if="pagination.pages > 1" class="card-footer bg-white border-top py-3 d-flex justify-content-center">
          <Pagination :pagination="pagination" @change-page="handlePageChange" />
        </div>
      </div>

      <!-- Quick Details Modal -->
      <div v-if="selectedBooking" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);" role="dialog">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow">
            <div class="modal-header border-bottom">
              <h5 class="modal-title fw-bold">Booking Details #{{ selectedBooking.id }}</h5>
              <button type="button" class="btn-close" @click="selectedBooking = null"></button>
            </div>
            <div class="modal-body p-4">
              <div class="mb-3">
                <h6 class="fw-bold mb-1">{{ selectedBooking.trek_name || selectedBooking.trek?.trek_name }}</h6>
                <p class="text-muted small mb-0">📍 {{ selectedBooking.trek_location || selectedBooking.trek?.location }}</p>
              </div>

              <div class="p-3 bg-light rounded-3 mb-3">
                <div class="row g-2 small">
                  <div class="col-6">
                    <span class="text-muted d-block">Booking Status:</span>
                    <BookingStatusBadge :status="selectedBooking.booking_status" />
                  </div>
                  <div class="col-6">
                    <span class="text-muted d-block">Payment Status:</span>
                    <span class="fw-semibold">{{ selectedBooking.payment_status || 'Pending' }}</span>
                  </div>
                  <div class="col-6 mt-2">
                    <span class="text-muted d-block">Start Date:</span>
                    <span class="fw-semibold">{{ selectedBooking.trek_start_date || selectedBooking.trek?.start_date }}</span>
                  </div>
                  <div class="col-6 mt-2">
                    <span class="text-muted d-block">End Date:</span>
                    <span class="fw-semibold">{{ selectedBooking.trek_end_date || selectedBooking.trek?.end_date }}</span>
                  </div>
                  <div class="col-6 mt-2">
                    <span class="text-muted d-block">Booked On:</span>
                    <span class="fw-semibold">{{ formatDate(selectedBooking.booking_date || selectedBooking.created_at) }}</span>
                  </div>
                  <div class="col-6 mt-2">
                    <span class="text-muted d-block">Progress:</span>
                    <span class="badge" :class="getProgressBadge(selectedBooking.trek_operational_progress || selectedBooking.trek?.operational_progress)">
                      {{ selectedBooking.trek_operational_progress || selectedBooking.trek?.operational_progress || 'Not Started' }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-secondary btn-sm" @click="selectedBooking = null">Close</button>
                <router-link :to="`/trekker/treks/${selectedBooking.trek_id}`" class="btn btn-primary btn-sm">
                  Full Trek Page
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
import TrekkerSidebar from '../components/TrekkerSidebar.vue'
import BookingStatusBadge from '../components/BookingStatusBadge.vue'
import Pagination from '../components/Pagination.vue'

const loading = ref(true)
const errorMessage = ref('')
const bookings = ref([])
const currentStatus = ref('')
const pagination = ref({ page: 1, pages: 1, total: 0, has_prev: false, has_next: false })
const selectedBooking = ref(null)

const setStatusFilter = (status) => {
  currentStatus.value = status
  pagination.value.page = 1
  fetchBookings()
}

const handlePageChange = (newPage) => {
  pagination.value.page = newPage
  fetchBookings()
}

const openDetails = (booking) => {
  selectedBooking.value = booking
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

const fetchBookings = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {
      page: pagination.value.page,
      per_page: 10
    }
    if (currentStatus.value) {
      params.status = currentStatus.value
    }
    const res = await api.get('/api/trekker/bookings', { params })
    bookings.value = res.data?.data?.bookings || []
    pagination.value = res.data?.data?.pagination || { page: 1, pages: 1, total: 0 }
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to load booking history.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchBookings()
})
</script>
