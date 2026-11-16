<template>
  <div class="d-flex">
    <StaffSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Breadcrumbs & Back -->
      <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><router-link to="/staff/dashboard">Dashboard</router-link></li>
          <li class="breadcrumb-item"><router-link to="/staff/treks">My Treks</router-link></li>
          <li class="breadcrumb-item active" aria-current="page">{{ trek?.trek_name || 'Trek Details' }}</li>
        </ol>
      </nav>

      <!-- Alert Banners -->
      <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
        {{ successMessage }}
        <button type="button" class="btn-close" @click="successMessage = ''"></button>
      </div>
      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ errorMessage }}
        <button type="button" class="btn-close" @click="errorMessage = ''"></button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-success" role="status"></div>
        <p class="mt-2 text-muted small">Loading expedition details & controls...</p>
      </div>

      <div v-else-if="trek">
        <!-- Header Section -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
              <div>
                <div class="d-flex align-items-center gap-2 mb-1">
                  <h2 class="fw-bold mb-0">{{ trek.trek_name }}</h2>
                  <span class="badge" :class="getDifficultyBadge(trek.difficulty)">
                    {{ trek.difficulty }}
                  </span>
                </div>
                <p class="text-muted mb-0">
                  📍 {{ trek.location }} &bull; 🗓️ {{ trek.start_date }} to {{ trek.end_date }} ({{ trek.duration_days }} days)
                </p>
              </div>
              <div class="d-flex gap-2">
                <router-link :to="`/staff/treks/${trek.id}/participants`" class="btn btn-outline-success">
                  👥 View Participants ({{ trek.booked_slots || 0 }})
                </router-link>
                <button class="btn btn-outline-secondary" @click="fetchTrekDetails" :disabled="loading">
                  🔄 Refresh
                </button>
              </div>
            </div>

            <div v-if="trek.description" class="mt-3 text-secondary small">
              {{ trek.description }}
            </div>
          </div>
        </div>

        <div class="row g-4 mb-4">
          <!-- 1. Operational Progress Lifecycle -->
          <div class="col-lg-7">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h5 class="card-title mb-0 fw-bold">🧭 Operational Progress Lifecycle</h5>
                <small class="text-muted">Track on-ground execution stage (unidirectional progression)</small>
              </div>
              <div class="card-body">
                <!-- Stepper Progress UI -->
                <div class="stepper-wrapper mb-4">
                  <div
                    v-for="(stage, idx) in stages"
                    :key="stage"
                    class="stepper-item"
                    :class="{
                      'completed': isStagePassed(stage),
                      'active': trek.operational_progress === stage
                    }"
                  >
                    <div class="step-counter">{{ idx + 1 }}</div>
                    <div class="step-name">{{ stage }}</div>
                  </div>
                </div>

                <div class="p-3 bg-light rounded-3 mb-3">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <small class="text-muted d-block">Current Stage</small>
                      <span class="fw-bold fs-5" :class="getProgressTextColor(trek.operational_progress)">
                        {{ trek.operational_progress }}
                      </span>
                    </div>
                    <span class="badge fs-6" :class="getProgressBadge(trek.operational_progress)">
                      {{ trek.operational_progress }}
                    </span>
                  </div>
                </div>

                <!-- Transition Controls -->
                <div v-if="trek.operational_progress !== 'Completed'">
                  <label class="form-label fw-semibold small text-uppercase text-muted">Advance to Next Stage:</label>
                  <div class="d-flex flex-wrap gap-2">
                    <button
                      v-for="nextStage in allowedNextTransitions"
                      :key="nextStage"
                      class="btn"
                      :class="nextStage === 'Completed' ? 'btn-danger' : 'btn-primary'"
                      @click="updateProgress(nextStage)"
                      :disabled="savingProgress"
                    >
                      {{ savingProgress ? 'Updating...' : `Advance to: ${nextStage}` }}
                    </button>
                  </div>
                  <small v-if="allowedNextTransitions.includes('Completed')" class="text-muted d-block mt-2">
                    ⚠️ Note: Advancing to <strong>Completed</strong> will automatically close booking availability.
                  </small>
                </div>
                <div v-else class="alert alert-success d-flex align-items-center mb-0">
                  <span class="fs-4 me-2">🏁</span>
                  <div>
                    <strong>Expedition Completed:</strong> This trek has reached its terminal lifecycle stage.
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 2. Booking Availability Status -->
          <div class="col-lg-5">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h5 class="card-title mb-0 fw-bold">🟢 Booking Availability Status</h5>
                <small class="text-muted">Toggle trek availability for prospective trekkers</small>
              </div>
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center p-3 bg-light rounded-3 mb-3">
                  <div>
                    <small class="text-muted d-block">Booking Status</small>
                    <span class="fw-bold fs-5" :class="trek.status === 'Open' ? 'text-success' : 'text-secondary'">
                      {{ trek.status }}
                    </span>
                  </div>
                  <span class="badge fs-6" :class="trek.status === 'Open' ? 'bg-success' : 'bg-secondary'">
                    {{ trek.status }}
                  </span>
                </div>

                <div v-if="trek.status === 'Completed' || trek.operational_progress === 'Completed'" class="alert alert-secondary small mb-0">
                  🔒 Booking status cannot be changed for completed expeditions.
                </div>
                <div v-else class="d-grid gap-2">
                  <button
                    v-if="trek.status === 'Open'"
                    class="btn btn-warning"
                    @click="updateStatus('Closed')"
                    :disabled="savingStatus"
                  >
                    {{ savingStatus ? 'Updating...' : '🔒 Close Bookings' }}
                  </button>
                  <button
                    v-else
                    class="btn btn-success"
                    @click="updateStatus('Open')"
                    :disabled="savingStatus"
                  >
                    {{ savingStatus ? 'Updating...' : '🔓 Open for Bookings' }}
                  </button>
                  <small class="text-muted">
                    Administrative statuses (Pending/Approved) are managed by administrators.
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Capacity & Available Slots Management -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3 border-bottom">
            <h5 class="card-title mb-0 fw-bold">🎟️ Capacity & Slots Management</h5>
            <small class="text-muted">Adjust total available expedition slots with active reservation protection</small>
          </div>
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-6 mb-3 mb-md-0">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <span class="text-muted">Active Confirmed Bookings:</span>
                  <strong class="fs-5 text-primary">{{ trek.booked_slots || 0 }}</strong>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <span class="text-muted">Current Slot Capacity:</span>
                  <strong class="fs-5">{{ trek.available_slots }}</strong>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <span class="text-muted">Remaining Open Slots:</span>
                  <strong class="fs-5 text-success">{{ trek.remaining_slots }}</strong>
                </div>

                <div class="progress" style="height: 10px;">
                  <div
                    class="progress-bar bg-success"
                    role="progressbar"
                    :style="{ width: `${Math.min(100, Math.round(((trek.booked_slots || 0) / (trek.available_slots || 1)) * 100))}%` }"
                  ></div>
                </div>
              </div>

              <div class="col-md-6 border-start-md ps-md-4">
                <form @submit.prevent="saveSlots">
                  <div class="mb-3">
                    <label for="slotsInput" class="form-label fw-semibold">
                      Update Total Available Slots
                    </label>
                    <div class="input-group">
                      <input
                        id="slotsInput"
                        v-model.number="slotFormValue"
                        type="number"
                        min="0"
                        class="form-control"
                        :class="{ 'is-invalid': slotError }"
                        required
                      />
                      <button class="btn btn-primary" type="submit" :disabled="savingSlots">
                        {{ savingSlots ? 'Saving...' : 'Save Capacity' }}
                      </button>
                    </div>
                    <div v-if="slotError" class="invalid-feedback d-block">
                      {{ slotError }}
                    </div>
                    <div class="form-text small">
                      Minimum allowable slots: <strong>{{ trek.booked_slots || 0 }}</strong> (cannot reduce below confirmed reservations).
                    </div>
                  </div>
                </form>
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
import { useRoute } from 'vue-router'
import api from '../services/api'
import StaffSidebar from '../components/StaffSidebar.vue'

const route = useRoute()
const trekId = route.params.id

const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const trek = ref(null)

// Capacity
const slotFormValue = ref(0)
const slotError = ref('')
const savingSlots = ref(false)

// Status
const savingStatus = ref(false)

// Progress
const savingProgress = ref(false)

const stages = ['Not Started', 'Started', 'Ongoing', 'Completed']

const allowedTransitionsMap = {
  'Not Started': ['Started', 'Ongoing'],
  'Started': ['Ongoing', 'Completed'],
  'Ongoing': ['Completed'],
  'Completed': []
}

const allowedNextTransitions = computed(() => {
  if (!trek.value) return []
  return allowedTransitionsMap[trek.value.operational_progress] || []
})

const isStagePassed = (stage) => {
  if (!trek.value) return false
  const currentIdx = stages.indexOf(trek.value.operational_progress)
  const targetIdx = stages.indexOf(stage)
  return targetIdx < currentIdx
}

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

const getProgressTextColor = (progress) => {
  switch (progress) {
    case 'Not Started': return 'text-secondary'
    case 'Started': return 'text-info'
    case 'Ongoing': return 'text-primary'
    case 'Completed': return 'text-success'
    default: return 'text-secondary'
  }
}

const fetchTrekDetails = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get(`/api/staff/treks/${trekId}`)
    trek.value = res.data?.data?.trek || res.data?.data || {}
    slotFormValue.value = trek.value.available_slots
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to load trek details.'
  } finally {
    loading.value = false
  }
}

const saveSlots = async () => {
  slotError.value = ''
  errorMessage.value = ''
  successMessage.value = ''

  const activeCount = trek.value.booked_slots || 0
  if (slotFormValue.value < 0) {
    slotError.value = 'Available slots cannot be negative.'
    return
  }
  if (slotFormValue.value < activeCount) {
    slotError.value = `Cannot reduce slots below ${activeCount} active bookings.`
    return
  }

  savingSlots.value = true
  try {
    const res = await api.patch(`/api/staff/treks/${trekId}/slots`, {
      available_slots: slotFormValue.value
    })
    successMessage.value = res.data?.message || 'Slots updated successfully.'
    await fetchTrekDetails()
  } catch (err) {
    slotError.value = err.response?.data?.message || 'Failed to update slots.'
  } finally {
    savingSlots.value = false
  }
}

const updateStatus = async (newStatus) => {
  errorMessage.value = ''
  successMessage.value = ''
  savingStatus.value = true
  try {
    const res = await api.patch(`/api/staff/treks/${trekId}/status`, {
      status: newStatus
    })
    successMessage.value = res.data?.message || `Status updated to ${newStatus}.`
    await fetchTrekDetails()
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to update status.'
  } finally {
    savingStatus.value = false
  }
}

const updateProgress = async (newProgress) => {
  errorMessage.value = ''
  successMessage.value = ''
  savingProgress.value = true
  try {
    const res = await api.patch(`/api/staff/treks/${trekId}/progress`, {
      operational_progress: newProgress
    })
    successMessage.value = res.data?.message || `Progress updated to ${newProgress}.`
    await fetchTrekDetails()
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to update operational progress.'
  } finally {
    savingProgress.value = false
  }
}

onMounted(() => {
  fetchTrekDetails()
})
</script>

<style scoped>
.stepper-wrapper {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}
.stepper-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}
.stepper-item::before {
  position: absolute;
  content: "";
  border-bottom: 2px solid #ccc;
  width: 100%;
  top: 18px;
  left: -50%;
  z-index: 1;
}
.stepper-item:first-child::before {
  content: none;
}
.step-counter {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e9ecef;
  margin-bottom: 6px;
  font-weight: 600;
  color: #495057;
}
.stepper-item.active .step-counter {
  background: #0d6efd;
  color: #fff;
}
.stepper-item.completed .step-counter {
  background: #198754;
  color: #fff;
}
.step-name {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
  text-align: center;
}
.stepper-item.active .step-name {
  font-weight: 700;
  color: #0d6efd;
}
.stepper-item.completed .step-name {
  color: #198754;
}
</style>
