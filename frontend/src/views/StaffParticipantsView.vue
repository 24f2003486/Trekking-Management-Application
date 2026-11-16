<template>
  <div class="d-flex">
    <StaffSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Breadcrumbs -->
      <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><router-link to="/staff/dashboard">Dashboard</router-link></li>
          <li class="breadcrumb-item"><router-link to="/staff/treks">My Treks</router-link></li>
          <li class="breadcrumb-item">
            <router-link :to="`/staff/treks/${trekId}`">{{ trek?.trek_name || 'Trek Details' }}</router-link>
          </li>
          <li class="breadcrumb-item active" aria-current="page">Participant Roster</li>
        </ol>
      </nav>

      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">Participant Roster</h2>
          <p class="text-muted mb-0">
            Registered trekkers for <strong>{{ trek?.trek_name || 'Expedition' }}</strong>
            <span v-if="trek?.location" class="ms-2 badge bg-light text-dark border">📍 {{ trek.location }}</span>
          </p>
        </div>
        <div>
          <button class="btn btn-outline-secondary me-2" @click="fetchParticipants" :disabled="loading">
            🔄 Refresh
          </button>
          <router-link :to="`/staff/treks/${trekId}`" class="btn btn-outline-primary">
            ⚙️ Trek Operations
          </router-link>
        </div>
      </div>

      <!-- Alert -->
      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ errorMessage }}
        <button type="button" class="btn-close" @click="errorMessage = ''"></button>
      </div>

      <!-- Summary Stat Cards -->
      <div class="row g-3 mb-4">
        <div class="col-sm-4">
          <div class="card border-0 shadow-sm p-3 bg-white rounded-3">
            <div class="text-muted small text-uppercase fw-semibold">Total Registrations</div>
            <div class="fs-3 fw-bold text-dark">{{ summary.total }}</div>
            <small class="text-muted">All booking records</small>
          </div>
        </div>
        <div class="col-sm-4">
          <div class="card border-0 shadow-sm p-3 bg-white rounded-3">
            <div class="text-muted small text-uppercase fw-semibold">Active Confirmed</div>
            <div class="fs-3 fw-bold text-success">{{ summary.active }}</div>
            <small class="text-muted">Trekkers confirmed on roster</small>
          </div>
        </div>
        <div class="col-sm-4">
          <div class="card border-0 shadow-sm p-3 bg-white rounded-3">
            <div class="text-muted small text-uppercase fw-semibold">Cancelled</div>
            <div class="fs-3 fw-bold text-secondary">{{ summary.cancelled }}</div>
            <small class="text-muted">Cancelled reservations</small>
          </div>
        </div>
      </div>

      <!-- Filters & Privacy Banner -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <div class="row g-3 align-items-center">
            <div class="col-md-6">
              <div class="input-group">
                <span class="input-group-text bg-white border-end-0">🔍</span>
                <input
                  v-model="filters.search"
                  type="text"
                  class="form-control border-start-0"
                  placeholder="Search participant name, email, or phone..."
                  @keyup.enter="handleSearch"
                />
              </div>
            </div>
            <div class="col-md-4">
              <select v-model="filters.status" class="form-select" @change="handleSearch">
                <option value="">All Participant Records</option>
                <option value="Booked">Confirmed / Active Only</option>
                <option value="Cancelled">Cancelled Only</option>
              </select>
            </div>
            <div class="col-md-2">
              <button class="btn btn-secondary w-100" @click="resetFilters">
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Participants Table Card -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center border-bottom">
          <h5 class="card-title mb-0 fw-semibold">Registered Participants ({{ pagination.total }})</h5>
          <span class="badge bg-light text-muted border">🔒 Privacy Protected: Credentials Encrypted</span>
        </div>
        <div class="card-body p-0">
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-success" role="status"></div>
            <p class="mt-2 text-muted small">Loading participant roster...</p>
          </div>

          <div v-else-if="participants.length === 0" class="text-center py-5 text-muted">
            <span class="fs-1 d-block mb-2">👥</span>
            <h5 class="fw-semibold">No participants found.</h5>
            <p class="small text-muted">No participant records match the current filter criteria for this expedition.</p>
          </div>

          <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Participant Roster Table">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Booking ID</th>
                  <th>Participant Details</th>
                  <th>Contact Info</th>
                  <th>Booking Status</th>
                  <th>Payment</th>
                  <th>Reservation Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in participants" :key="item.booking_id || item.id">
                  <td>
                    <span class="badge bg-light text-dark border">#{{ item.booking_id || item.id }}</span>
                  </td>
                  <td>
                    <div class="fw-bold">{{ item.participant?.full_name || 'Participant' }}</div>
                    <small class="text-muted">User ID: {{ item.participant?.id || item.user_id }}</small>
                  </td>
                  <td>
                    <div>{{ item.participant?.email }}</div>
                    <small class="text-muted">{{ item.participant?.contact_number || 'No phone provided' }}</small>
                  </td>
                  <td>
                    <span
                      class="badge"
                      :class="item.booking_status === 'Booked' ? 'bg-success' : 'bg-secondary'"
                    >
                      {{ item.booking_status === 'Booked' ? 'Confirmed Active' : 'Cancelled' }}
                    </span>
                  </td>
                  <td>
                    <span
                      class="badge"
                      :class="item.payment_status === 'Paid' ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-warning-subtle text-warning border border-warning-subtle'"
                    >
                      {{ item.payment_status || 'Pending' }}
                    </span>
                  </td>
                  <td>
                    <div class="small">{{ formatDate(item.booking_date) }}</div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="pagination.pages > 1" class="card-footer bg-white border-top-0 px-3 py-2">
          <Pagination :pagination="pagination" @change-page="handlePageChange" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import StaffSidebar from '../components/StaffSidebar.vue'
import Pagination from '../components/Pagination.vue'

const route = useRoute()
const trekId = route.params.id

const loading = ref(true)
const errorMessage = ref('')
const trek = ref(null)
const participants = ref([])
const summary = ref({ total: 0, active: 0, cancelled: 0 })
const pagination = ref({ page: 1, pages: 1, total: 0, has_prev: false, has_next: false })

const filters = reactive({
  search: '',
  status: '',
  page: 1
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return dateStr
  }
}

const fetchParticipants = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {
      page: filters.page,
      per_page: 20
    }
    if (filters.search) params.search = filters.search
    if (filters.status) params.status = filters.status

    const res = await api.get(`/api/staff/treks/${trekId}/participants`, { params })
    const data = res.data?.data || {}
    trek.value = data.trek || null
    participants.value = data.participants || []
    summary.value = data.summary || {
      total: data.total_participants || 0,
      active: data.active_count || 0,
      cancelled: data.cancelled_count || 0
    }
    pagination.value = data.pagination || { page: 1, pages: 1, total: 0 }
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to load participant roster.'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  filters.page = 1
  fetchParticipants()
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.page = 1
  fetchParticipants()
}

const handlePageChange = (newPage) => {
  filters.page = newPage
  fetchParticipants()
}

onMounted(() => {
  fetchParticipants()
})
</script>
