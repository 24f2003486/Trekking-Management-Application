<template>
  <div class="d-flex">
    <TrekkerSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Breadcrumbs -->
      <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><router-link to="/trekker/dashboard">Dashboard</router-link></li>
          <li class="breadcrumb-item"><router-link to="/trekker/treks">Browse Treks</router-link></li>
          <li class="breadcrumb-item active" aria-current="page">{{ trek?.trek_name || 'Trek Details' }}</li>
        </ol>
      </nav>

      <!-- Feedback Alerts -->
      <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
        {{ successMessage }}
        <button type="button" class="btn-close" @click="successMessage = ''"></button>
      </div>
      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ errorMessage }}
        <button type="button" class="btn-close" @click="errorMessage = ''"></button>
      </div>

      <!-- Loading Spinner -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-success" role="status"></div>
        <p class="mt-2 text-muted small">Loading expedition details...</p>
      </div>

      <div v-else-if="trek">
        <!-- Trek Hero Banner -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
              <div>
                <div class="d-flex align-items-center gap-2 mb-2">
                  <h2 class="fw-bold mb-0">{{ trek.trek_name }}</h2>
                  <span class="badge" :class="getDifficultyBadge(trek.difficulty)">
                    {{ trek.difficulty }}
                  </span>
                  <span class="badge bg-secondary">
                    ⏱️ {{ trek.duration_days }} Days
                  </span>
                </div>
                <p class="text-muted mb-0">
                  📍 {{ trek.location }} &bull; 🗓️ <strong>{{ trek.start_date }}</strong> to <strong>{{ trek.end_date }}</strong>
                </p>
              </div>

              <!-- Booking CTA Card Header -->
              <div>
                <div v-if="trek.has_active_booking" class="badge bg-success-subtle text-success border border-success-subtle p-2 fs-6">
                  ✅ Active Reservation Confirmed
                </div>
                <div v-else-if="trek.remaining_slots <= 0" class="badge bg-secondary p-2 fs-6">
                  🔒 Expedition Fully Booked
                </div>
                <button
                  v-else-if="trek.is_open && trek.operational_progress !== 'Completed'"
                  class="btn btn-success btn-lg fw-bold shadow-sm"
                  @click="showModal = true"
                >
                  🎟️ Book This Trek
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="row g-4 mb-4">
          <!-- Left Column: Description & Details -->
          <div class="col-lg-8">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h5 class="card-title mb-0 fw-bold">Expedition Overview & Route Details</h5>
              </div>
              <div class="card-body p-4">
                <div class="mb-4">
                  <h6 class="fw-semibold text-dark">Trail Description</h6>
                  <p class="text-secondary leading-relaxed">
                    {{ trek.description || 'No detailed route description provided for this expedition.' }}
                  </p>
                </div>

                <div class="row g-3 pt-3 border-top">
                  <div class="col-sm-6">
                    <div class="p-3 bg-light rounded-3">
                      <small class="text-muted d-block">Geographic Region</small>
                      <strong class="text-dark">{{ trek.location }}</strong>
                    </div>
                  </div>
                  <div class="col-sm-6">
                    <div class="p-3 bg-light rounded-3">
                      <small class="text-muted d-block">Trek Leader / Staff</small>
                      <strong class="text-dark">{{ trek.assigned_staff_name || 'Assigned Expedition Guide' }}</strong>
                    </div>
                  </div>
                  <div class="col-sm-6">
                    <div class="p-3 bg-light rounded-3">
                      <small class="text-muted d-block">Operational Progress</small>
                      <span class="badge" :class="getProgressBadge(trek.operational_progress)">
                        {{ trek.operational_progress }}
                      </span>
                    </div>
                  </div>
                  <div class="col-sm-6">
                    <div class="p-3 bg-light rounded-3">
                      <small class="text-muted d-block">Booking Availability</small>
                      <span class="badge" :class="trek.status === 'Open' ? 'bg-success' : 'bg-secondary'">
                        {{ trek.status }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column: Capacity & Reservation Status -->
          <div class="col-lg-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h5 class="card-title mb-0 fw-bold">Capacity & Availability</h5>
              </div>
              <div class="card-body p-4">
                <div class="text-center py-3 mb-3 bg-light rounded-3">
                  <div class="fs-1 fw-bold" :class="trek.remaining_slots > 0 ? 'text-success' : 'text-danger'">
                    {{ trek.remaining_slots }}
                  </div>
                  <small class="text-muted text-uppercase fw-semibold">Slots Remaining</small>
                </div>

                <div class="mb-3">
                  <div class="d-flex justify-content-between text-muted small mb-1">
                    <span>Occupancy ({{ trek.booked_slots || 0 }} booked):</span>
                    <span>{{ trek.total_slots }} Total Slots</span>
                  </div>
                  <div class="progress" style="height: 8px;">
                    <div
                      class="progress-bar"
                      :class="trek.remaining_slots > 0 ? 'bg-success' : 'bg-danger'"
                      role="progressbar"
                      :style="{ width: `${Math.min(100, Math.round(((trek.booked_slots || 0) / (trek.total_slots || 1)) * 100))}%` }"
                    ></div>
                  </div>
                </div>

                <!-- Eligibility Card -->
                <div class="pt-3 border-top">
                  <div v-if="trek.has_active_booking" class="alert alert-info py-2 small mb-0">
                    ℹ️ You currently hold an active confirmed booking for this trek. You can view your reservation in <router-link to="/trekker/bookings">My Bookings</router-link>.
                  </div>
                  <div v-else-if="trek.remaining_slots <= 0" class="alert alert-secondary py-2 small mb-0">
                    🔒 All available slots have been filled. Check back later in case cancellations occur.
                  </div>
                  <div v-else-if="!trek.is_open" class="alert alert-warning py-2 small mb-0">
                    ⚠️ This trek is currently closed to new reservations.
                  </div>
                  <div v-else class="d-grid gap-2">
                    <button
                      class="btn btn-success fw-bold py-2 shadow-sm"
                      @click="showModal = true"
                      :disabled="bookingInProgress"
                    >
                      Reserve Your Spot
                    </button>
                    <small class="text-muted text-center">Instant confirmation upon reservation</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Booking Confirmation Modal -->
      <BookingConfirmationModal
        :show="showModal"
        :trek="trek"
        :loading="bookingInProgress"
        @confirm="confirmBooking"
        @cancel="showModal = false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import TrekkerSidebar from '../components/TrekkerSidebar.vue'
import BookingConfirmationModal from '../components/BookingConfirmationModal.vue'

const route = useRoute()
const trekId = route.params.id

const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const trek = ref(null)

const showModal = ref(false)
const bookingInProgress = ref(false)

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

const fetchTrekDetails = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get(`/api/trekker/treks/${trekId}`)
    trek.value = res.data?.data?.trek || res.data?.data || {}
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to load trek details.'
  } finally {
    loading.value = false
  }
}

const confirmBooking = async () => {
  if (!trek.value) return
  bookingInProgress.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const res = await api.post('/api/trekker/bookings', {
      trek_id: trek.value.id
    })
    successMessage.value = res.data?.message || `Successfully booked ${trek.value.trek_name}!`
    showModal.value = false
    await fetchTrekDetails()
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to book trek.'
    showModal.value = false
  } finally {
    bookingInProgress.value = false
  }
}

onMounted(() => {
  fetchTrekDetails()
})
</script>
