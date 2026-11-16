<template>
  <div class="d-flex">
    <StaffSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">My Assigned Treks</h2>
          <p class="text-muted mb-0">View and manage expeditions assigned to your leadership.</p>
        </div>
        <div>
          <button class="btn btn-outline-secondary" @click="fetchTreks" :disabled="loading">
            🔄 Refresh List
          </button>
        </div>
      </div>

      <!-- Alerts -->
      <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
        {{ successMessage }}
        <button type="button" class="btn-close" @click="successMessage = ''"></button>
      </div>
      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ errorMessage }}
        <button type="button" class="btn-close" @click="errorMessage = ''"></button>
      </div>

      <!-- Search and Filter Bar -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-5">
              <div class="input-group">
                <span class="input-group-text bg-white border-end-0">🔍</span>
                <input
                  v-model="filters.search"
                  type="text"
                  class="form-control border-start-0"
                  placeholder="Search by trek name or location..."
                  @keyup.enter="handleSearch"
                />
              </div>
            </div>
            <div class="col-md-3">
              <select v-model="filters.status" class="form-select" @change="handleSearch">
                <option value="">All Booking Statuses</option>
                <option value="Open">Open</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
            <div class="col-md-3">
              <select v-model="filters.progress" class="form-select" @change="handleSearch">
                <option value="">All Progress Stages</option>
                <option value="Not Started">Not Started</option>
                <option value="Started">Started</option>
                <option value="Ongoing">Ongoing</option>
                <option value="Completed">Completed</option>
              </select>
            </div>
            <div class="col-md-1 d-flex">
              <button class="btn btn-secondary w-100" @click="resetFilters" title="Reset filters">
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Treks List Card -->
      <div class="card border-0 shadow-sm">
        <div class="card-body p-0">
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-success" role="status"></div>
            <p class="mt-2 text-muted small">Loading assigned treks...</p>
          </div>

          <div v-else-if="treks.length === 0" class="text-center py-5 text-muted">
            <span class="fs-1 d-block mb-2">🏔️</span>
            <h5 class="fw-semibold">No assigned treks match your criteria.</h5>
            <p class="small text-muted">Try clearing your filters or check with administrators for assigned treks.</p>
          </div>

          <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Assigned Expeditions List">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Trek & Location</th>
                  <th>Dates & Duration</th>
                  <th>Difficulty</th>
                  <th>Booking Status</th>
                  <th>Progress</th>
                  <th>Capacity & Bookings</th>
                  <th class="text-end pe-3">Operations</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="trek in treks" :key="trek.id">
                  <td>
                    <div class="fw-bold fs-6">{{ trek.trek_name }}</div>
                    <small class="text-muted">📍 {{ trek.location }}</small>
                  </td>
                  <td>
                    <div class="small fw-semibold">{{ trek.start_date }}</div>
                    <small class="text-muted">to {{ trek.end_date }} ({{ trek.duration_days }} days)</small>
                  </td>
                  <td>
                    <span class="badge" :class="getDifficultyBadge(trek.difficulty)">
                      {{ trek.difficulty }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="trek.status === 'Open' ? 'bg-success' : 'bg-secondary'">
                      {{ trek.status }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="getProgressBadge(trek.operational_progress)">
                      {{ trek.operational_progress }}
                    </span>
                  </td>
                  <td>
                    <div class="d-flex align-items-center gap-2 mb-1">
                      <div class="progress flex-grow-1" style="height: 6px; width: 60px;">
                        <div
                          class="progress-bar bg-success"
                          role="progressbar"
                          :style="{ width: `${Math.min(100, Math.round(((trek.booked_slots || 0) / (trek.available_slots || 1)) * 100))}%` }"
                        ></div>
                      </div>
                      <span class="small fw-bold">{{ trek.booked_slots || 0 }} / {{ trek.available_slots }}</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                      <small class="text-muted">{{ trek.remaining_slots }} remaining</small>
                      <button
                        class="btn btn-link btn-sm p-0 text-decoration-none"
                        @click="openSlotModal(trek)"
                        title="Quick update slots"
                      >
                        ✏️ Edit Slots
                      </button>
                    </div>
                  </td>
                  <td class="text-end pe-3">
                    <div class="btn-group btn-group-sm">
                      <router-link
                        :to="`/staff/treks/${trek.id}`"
                        class="btn btn-outline-primary"
                        title="Trek details, status & progress operations"
                      >
                        ⚙️ Manage
                      </router-link>
                      <router-link
                        :to="`/staff/treks/${trek.id}/participants`"
                        class="btn btn-outline-success"
                        title="Participant list"
                      >
                        👥 ({{ trek.booked_slots || 0 }})
                      </router-link>
                    </div>
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

      <!-- Quick Slot Capacity Modal -->
      <div v-if="slotModalTrek" class="modal-backdrop fade show"></div>
      <div
        v-if="slotModalTrek"
        class="modal fade show d-block"
        tabindex="-1"
        role="dialog"
        aria-modal="true"
        aria-labelledby="slotModalTitle"
      >
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow">
            <div class="modal-header bg-light">
              <h5 id="slotModalTitle" class="modal-title fw-bold">Update Available Slots</h5>
              <button type="button" class="btn-close" @click="closeSlotModal"></button>
            </div>
            <div class="modal-body">
              <p class="mb-2">
                Trek: <strong>{{ slotModalTrek.trek_name }}</strong>
              </p>
              <div class="alert alert-info py-2 small mb-3">
                Current active bookings: <strong>{{ slotModalTrek.booked_slots || 0 }}</strong>.
                Slots cannot be set lower than this count.
              </div>

              <div class="mb-3">
                <label for="newSlotsInput" class="form-label fw-semibold">New Available Slot Capacity</label>
                <input
                  id="newSlotsInput"
                  v-model.number="newSlotsValue"
                  type="number"
                  min="0"
                  class="form-control"
                  :class="{ 'is-invalid': slotInputError }"
                />
                <div v-if="slotInputError" class="invalid-feedback">
                  {{ slotInputError }}
                </div>
              </div>
            </div>
            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary" @click="closeSlotModal" :disabled="savingSlots">
                Cancel
              </button>
              <button type="button" class="btn btn-primary" @click="saveSlots" :disabled="savingSlots">
                {{ savingSlots ? 'Saving...' : 'Update Slots' }}
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
import StaffSidebar from '../components/StaffSidebar.vue'
import Pagination from '../components/Pagination.vue'

const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const treks = ref([])
const pagination = ref({ page: 1, pages: 1, total: 0, has_prev: false, has_next: false })

const filters = reactive({
  search: '',
  status: '',
  progress: '',
  page: 1
})

// Slot Modal State
const slotModalTrek = ref(null)
const newSlotsValue = ref(0)
const slotInputError = ref('')
const savingSlots = ref(false)

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

const fetchTreks = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {
      page: filters.page,
      per_page: 10
    }
    if (filters.search) params.search = filters.search
    if (filters.status) params.status = filters.status
    if (filters.progress) params.progress = filters.progress

    const res = await api.get('/api/staff/treks', { params })
    treks.value = res.data?.data?.treks || []
    pagination.value = res.data?.data?.pagination || { page: 1, pages: 1, total: 0 }
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to load assigned treks.'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  filters.page = 1
  fetchTreks()
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.progress = ''
  filters.page = 1
  fetchTreks()
}

const handlePageChange = (newPage) => {
  filters.page = newPage
  fetchTreks()
}

// Quick Slot Modal
const openSlotModal = (trek) => {
  slotModalTrek.value = trek
  newSlotsValue.value = trek.available_slots
  slotInputError.value = ''
}

const closeSlotModal = () => {
  slotModalTrek.value = null
  slotInputError.value = ''
}

const saveSlots = async () => {
  if (!slotModalTrek.value) return
  const activeCount = slotModalTrek.value.booked_slots || 0
  if (newSlotsValue.value < 0) {
    slotInputError.value = 'Available slots cannot be negative.'
    return
  }
  if (newSlotsValue.value < activeCount) {
    slotInputError.value = `Cannot reduce slots below ${activeCount} active bookings.`
    return
  }

  savingSlots.value = true
  slotInputError.value = ''
  try {
    await api.patch(`/api/staff/treks/${slotModalTrek.value.id}/slots`, {
      available_slots: newSlotsValue.value
    })
    successMessage.value = `Available slots for '${slotModalTrek.value.trek_name}' updated successfully.`
    closeSlotModal()
    fetchTreks()
  } catch (err) {
    slotInputError.value = err.response?.data?.message || 'Failed to update slots.'
  } finally {
    savingSlots.value = false
  }
}

onMounted(() => {
  fetchTreks()
})
</script>
