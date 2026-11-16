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
        <div class="d-flex gap-2 flex-wrap">
          <button class="btn btn-outline-success" @click="showExportModal = true; fetchExports()">
            📥 Export CSV History
          </button>
          <router-link to="/trekker/treks" class="btn btn-primary">
            🏔️ Explore Treks
          </router-link>
          <button class="btn btn-outline-secondary" @click="fetchBookings" :disabled="loading">
            🔄 Refresh
          </button>
        </div>
      </div>

      <!-- Feedback Alerts -->
      <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
        {{ successMessage }}
        <button type="button" class="btn-close" @click="successMessage = ''"></button>
      </div>

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
                    <button
                      v-if="b.booking_status === 'Booked' && (b.trek_operational_progress !== 'Completed' && b.trek?.operational_progress !== 'Completed')"
                      type="button"
                      class="btn btn-outline-danger"
                      @click="confirmCancel(b)"
                      :disabled="cancellingId === b.id"
                      title="Cancel Reservation"
                    >
                      <span v-if="cancellingId === b.id" class="spinner-border spinner-border-sm" role="status"></span>
                      <span v-else>Cancel</span>
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
                  <div class="col-6 mt-2">
                    <span class="text-muted d-block">Guide / Assigned Staff:</span>
                    <span class="fw-semibold">{{ selectedBooking.trek?.assigned_staff_name || 'Unassigned' }}</span>
                  </div>
                  <div class="col-6 mt-2">
                    <span class="text-muted d-block">Trek Status:</span>
                    <span class="badge bg-secondary">{{ selectedBooking.trek_status || selectedBooking.trek?.status || 'Unknown' }}</span>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <button
                    v-if="selectedBooking.booking_status === 'Booked' && (selectedBooking.trek_operational_progress !== 'Completed' && selectedBooking.trek?.operational_progress !== 'Completed')"
                    type="button"
                    class="btn btn-outline-danger btn-sm"
                    @click="confirmCancel(selectedBooking); selectedBooking = null;"
                  >
                    Cancel This Booking
                  </button>
                </div>
                <div class="d-flex gap-2">
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

      <!-- Export History Modal -->
      <div v-if="showExportModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content shadow">
            <div class="modal-header">
              <h5 class="modal-title fw-bold">📥 Export Trekking History (CSV)</h5>
              <button type="button" class="btn-close" @click="showExportModal = false"></button>
            </div>
            <div class="modal-body p-4">
              <p class="text-muted small mb-3">
                Download a complete spreadsheet record of all your expedition registrations, dates, locations, difficulty levels, and booking statuses. Exports are generated securely in the background.
              </p>

              <div class="d-flex justify-content-between align-items-center mb-3">
                <button
                  class="btn btn-primary btn-sm"
                  @click="triggerExport"
                  :disabled="exportTriggering"
                >
                  <span v-if="exportTriggering" class="spinner-border spinner-border-sm me-1"></span>
                  {{ exportTriggering ? 'Queueing Export Job...' : '⚡ Generate New CSV Export' }}
                </button>
                <button class="btn btn-outline-secondary btn-sm" @click="fetchExports" :disabled="loadingExports">
                  🔄 Refresh Status
                </button>
              </div>

              <div v-if="exportMessage" class="alert alert-info py-2 small mb-3">
                {{ exportMessage }}
              </div>

              <!-- Export Jobs List -->
              <h6 class="fw-bold mt-3 mb-2 small text-uppercase text-muted">Recent Export Requests</h6>
              <div v-if="loadingExports" class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary"></div>
              </div>
              <div v-else-if="exportJobs.length === 0" class="text-center text-muted py-3 small bg-light rounded">
                No CSV exports requested yet. Click "Generate New CSV Export" above.
              </div>
              <div v-else class="table-responsive">
                <table class="table table-sm align-middle mb-0">
                  <thead class="table-light small">
                    <tr>
                      <th>Job ID</th>
                      <th>Requested At</th>
                      <th>Status</th>
                      <th class="text-end">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="job in exportJobs" :key="job.id">
                      <td>#{{ job.id }}</td>
                      <td class="small">{{ formatDate(job.created_at) }}</td>
                      <td>
                        <span v-if="job.status === 'Completed'" class="badge bg-success">Completed</span>
                        <span v-else-if="job.status === 'Processing'" class="badge bg-warning text-dark">
                          <span class="spinner-border spinner-border-sm me-1" style="width: 0.7rem; height: 0.7rem;"></span>Processing...
                        </span>
                        <span v-else-if="job.status === 'Pending'" class="badge bg-secondary">Queued</span>
                        <span v-else class="badge bg-danger">Failed</span>
                        <small v-if="job.error_message" class="text-danger d-block mt-1">{{ job.error_message }}</small>
                      </td>
                      <td class="text-end">
                        <button
                          v-if="job.status === 'Completed'"
                          class="btn btn-sm btn-outline-success"
                          @click="downloadExport(job)"
                        >
                          ⬇️ Download CSV
                        </button>
                        <span v-else-if="job.status === 'Processing' || job.status === 'Pending'" class="text-muted small">
                          Generating...
                        </span>
                        <span v-else class="text-muted small">-</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary btn-sm" @click="showExportModal = false">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import api from '../services/api'
import TrekkerSidebar from '../components/TrekkerSidebar.vue'
import BookingStatusBadge from '../components/BookingStatusBadge.vue'
import Pagination from '../components/Pagination.vue'

const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const cancellingId = ref(null)
const bookings = ref([])
const currentStatus = ref('')
const pagination = ref({ page: 1, pages: 1, total: 0, has_prev: false, has_next: false })
const selectedBooking = ref(null)

// CSV Export state
const showExportModal = ref(false)
const exportJobs = ref([])
const loadingExports = ref(false)
const exportTriggering = ref(false)
const exportMessage = ref('')
let pollInterval = null

const fetchExports = async () => {
  loadingExports.value = true
  try {
    const res = await api.get('/api/trekker/exports')
    exportJobs.value = res.data?.data?.jobs || []
  } catch (err) {
    //
  } finally {
    loadingExports.value = false
  }
}

const triggerExport = async () => {
  exportTriggering.value = true
  exportMessage.value = ''
  try {
    const res = await api.post('/api/trekker/exports')
    exportMessage.value = 'CSV export job queued! It will be ready in a moment.'
    await fetchExports()
    startPolling()
  } catch (err) {
    exportMessage.value = err.response?.data?.message || 'Failed to queue export job.'
  } finally {
    exportTriggering.value = false
  }
}

const startPolling = () => {
  if (pollInterval) clearInterval(pollInterval)
  pollInterval = setInterval(async () => {
    try {
      const res = await api.get('/api/trekker/exports')
      exportJobs.value = res.data?.data?.jobs || []
      const hasPending = exportJobs.value.some(j => j.status === 'Pending' || j.status === 'Processing')
      if (!hasPending) {
        clearInterval(pollInterval)
        pollInterval = null
      }
    } catch {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }, 2000)
}

const downloadExport = async (job) => {
  try {
    const res = await api.get(`/api/trekker/exports/${job.id}/download`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', job.filename || `trekking_history_${job.id}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    alert('Failed to download export file.')
  }
}

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
})

const confirmCancel = async (booking) => {
  const trekTitle = booking.trek_name || booking.trek?.trek_name || 'this expedition'
  if (!window.confirm(`Are you sure you want to cancel your reservation for "${trekTitle}"? Your slot will be released for other trekkers.`)) {
    return
  }
  cancellingId.value = booking.id
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const res = await api.post(`/api/trekker/bookings/${booking.id}/cancel`)
    successMessage.value = res.data?.message || 'Booking reservation cancelled successfully.'
    await fetchBookings()
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to cancel reservation.'
  } finally {
    cancellingId.value = null
  }
}

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
