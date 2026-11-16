<template>
  <div class="d-flex">
    <AdminSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">Bookings & History</h2>
          <p class="text-muted mb-0">Read-only audit log of participant reservations and expedition bookings.</p>
        </div>
      </div>

      <!-- Filter & Search Toolbar -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-3">
          <form class="row g-2 align-items-center" @submit.prevent="handleSearch">
            <div class="col-md-5">
              <input
                v-model="filters.search"
                type="text"
                class="form-control form-control-sm"
                placeholder="Search by booking ID, trekker name or trek..."
              />
            </div>
            <div class="col-md-4">
              <select v-model="filters.status" class="form-select form-select-sm" @change="handleSearch">
                <option value="">All Booking Statuses</option>
                <option value="Booked">Booked</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>
            <div class="col-md-3 d-flex gap-1">
              <button type="submit" class="btn btn-sm btn-primary flex-grow-1">Search</button>
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="resetFilters">Reset</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Bookings Data Table -->
      <div class="card border-0 shadow-sm">
        <div class="card-body p-0">
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted small">Loading booking records...</p>
          </div>

          <div v-else-if="bookings.length === 0" class="text-center py-5 text-muted">
            <span class="fs-1 d-block mb-2">🎟️</span>
            No bookings found matching current search/filter criteria.
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light text-muted small text-uppercase">
                <tr>
                  <th scope="col" class="ps-3">Booking ID</th>
                  <th scope="col">Trekker</th>
                  <th scope="col">Trek Expedition</th>
                  <th scope="col">Booking Date</th>
                  <th scope="col">Booking Status</th>
                  <th scope="col">Payment Status</th>
                  <th scope="col" class="text-end pe-3">Details</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="b in bookings" :key="b.id">
                  <td class="ps-3 fw-bold text-secondary">#{{ b.id }}</td>
                  <td>
                    <div class="fw-semibold">{{ b.user_name || b.user?.full_name || 'N/A' }}</div>
                    <small class="text-muted">{{ b.user_email || b.user?.email || '-' }}</small>
                  </td>
                  <td>
                    <div class="fw-semibold">{{ b.trek_name || b.trek?.trek_name || b.trek?.name || 'N/A' }}</div>
                    <small class="text-muted">{{ b.trek_location || b.trek?.location || '-' }}</small>
                  </td>
                  <td>{{ formatDate(b.booking_date) }}</td>
                  <td>
                    <span class="badge" :class="getBookingStatusBadge(b.booking_status || b.status)">
                      {{ b.booking_status || b.status }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="getPaymentStatusBadge(b.payment_status)">
                      {{ b.payment_status || 'Pending' }}
                    </span>
                  </td>
                  <td class="text-end pe-3">
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-primary"
                      @click="viewBookingDetails(b)"
                    >
                      👁️ View
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="pagination.pages > 1" class="card-footer bg-white border-0 py-2">
          <Pagination :pagination="pagination" @change-page="goToPage" />
        </div>
      </div>

      <!-- Booking Detail Modal -->
      <div v-if="selectedBooking" class="modal-backdrop fade show" style="z-index: 1050;"></div>
      <div
        v-if="selectedBooking"
        class="modal fade show d-block"
        tabindex="-1"
        style="z-index: 1055;"
        role="dialog"
      >
        <div class="modal-dialog modal-dialog-centered" role="document">
          <div class="modal-content shadow border-0">
            <div class="modal-header border-bottom-0 pb-0">
              <h5 class="modal-title fw-bold">Booking Details #{{ selectedBooking.id }}</h5>
              <button type="button" class="btn-close" @click="selectedBooking = null"></button>
            </div>
            <div class="modal-body py-3">
              <div class="card bg-light border-0 mb-3">
                <div class="card-body p-3">
                  <h6 class="fw-bold mb-2 text-primary">Trek Expedition</h6>
                  <div><strong>Trek:</strong> {{ selectedBooking.trek_name || selectedBooking.trek?.trek_name || selectedBooking.trek?.name }}</div>
                  <div><strong>Location:</strong> {{ selectedBooking.trek_location || selectedBooking.trek?.location }}</div>
                </div>
              </div>

              <div class="card bg-light border-0 mb-3">
                <div class="card-body p-3">
                  <h6 class="fw-bold mb-2 text-primary">Participant Details</h6>
                  <div><strong>Full Name:</strong> {{ selectedBooking.user_name || selectedBooking.user?.full_name }}</div>
                  <div><strong>Email:</strong> {{ selectedBooking.user_email || selectedBooking.user?.email }}</div>
                  <div><strong>Contact:</strong> {{ selectedBooking.user?.contact_number || selectedBooking.user?.phone_number || '-' }}</div>
                </div>
              </div>

              <div class="d-flex justify-content-between">
                <div>
                  <small class="text-muted d-block">Reservation Status</small>
                  <span class="badge" :class="getBookingStatusBadge(selectedBooking.booking_status || selectedBooking.status)">
                    {{ selectedBooking.booking_status || selectedBooking.status }}
                  </span>
                </div>
                <div>
                  <small class="text-muted d-block">Payment Status</small>
                  <span class="badge" :class="getPaymentStatusBadge(selectedBooking.payment_status)">
                    {{ selectedBooking.payment_status || 'Pending' }}
                  </span>
                </div>
                <div>
                  <small class="text-muted d-block">Booked At</small>
                  <span class="small fw-semibold">{{ formatDate(selectedBooking.booking_date) }}</span>
                </div>
              </div>
            </div>
            <div class="modal-footer border-top-0 pt-0">
              <button type="button" class="btn btn-secondary btn-sm" @click="selectedBooking = null">
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../services/api'
import AdminSidebar from '../components/AdminSidebar.vue'
import Pagination from '../components/Pagination.vue'

const loading = ref(false)
const bookings = ref([])
const selectedBooking = ref(null)
const pagination = ref({ page: 1, pages: 1, total: 0 })

const filters = reactive({
  search: '',
  status: '',
  page: 1,
  per_page: 10
})

const fetchBookings = async () => {
  loading.value = true
  try {
    const params = {
      page: filters.page,
      per_page: filters.per_page,
      search: filters.search || undefined,
      status: filters.status || undefined
    }
    const res = await api.get('/api/admin/bookings', { params })
    bookings.value = res.data?.data?.bookings || []
    pagination.value = res.data?.data?.pagination || { page: 1, pages: 1, total: bookings.value.length }
  } catch (err) {
    console.error('Failed to load bookings', err)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  filters.page = 1
  fetchBookings()
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.page = 1
  fetchBookings()
}

const goToPage = (p) => {
  filters.page = p
  fetchBookings()
}

const viewBookingDetails = (b) => {
  selectedBooking.value = b
}

const formatDate = (d) => {
  if (!d) return '-'
  return new Date(d).toLocaleString()
}

const getBookingStatusBadge = (status) => {
  switch (status) {
    case 'Booked': return 'bg-success'
    case 'Completed': return 'bg-primary'
    case 'Cancelled': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

const getPaymentStatusBadge = (status) => {
  switch (status) {
    case 'Paid': return 'bg-success'
    case 'Pending': return 'bg-warning text-dark'
    case 'Refunded': return 'bg-info text-dark'
    case 'Failed': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

onMounted(() => {
  fetchBookings()
})
</script>
