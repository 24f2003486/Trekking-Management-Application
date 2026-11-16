<template>
  <div class="d-flex">
    <StaffSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">Trek Staff Portal</h2>
          <p class="text-muted mb-0">
            Welcome, <strong>{{ profile.staff_name || authService.state.user?.full_name }}</strong>
            <span v-if="profile.specialization" class="ms-2 badge bg-success-subtle text-success border border-success-subtle">
              {{ profile.specialization }} ({{ profile.experience_years }} yrs exp)
            </span>
          </p>
        </div>
        <div>
          <button class="btn btn-outline-secondary me-2" @click="fetchDashboardData" :disabled="loading">
            🔄 Refresh
          </button>
          <router-link to="/staff/treks" class="btn btn-success">
            🏔️ View All Assigned Treks
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
        <div class="spinner-border text-success" role="status"></div>
        <p class="mt-2 text-muted small">Loading your assigned expeditions and participant data...</p>
      </div>

      <div v-else>
        <!-- Primary Metric Row -->
        <div class="row g-3 mb-4">
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Assigned Treks"
              :value="metrics.total_assigned_treks"
              icon="🏔️"
              color="primary"
              subtitle="Expeditions in your roster"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Open for Booking"
              :value="metrics.open_treks"
              icon="🟢"
              color="success"
              subtitle="Currently accepting trekkers"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Active Participants"
              :value="metrics.total_participants"
              icon="👥"
              color="warning"
              subtitle="Confirmed trekker bookings"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Completed Treks"
              :value="metrics.completed_treks"
              icon="🏁"
              color="secondary"
              subtitle="Finished expeditions"
            />
          </div>
        </div>

        <!-- Assigned Treks Section -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0 fw-semibold">Upcoming & Active Assigned Expeditions</h5>
            <router-link to="/staff/treks" class="btn btn-sm btn-outline-success">
              View All ({{ metrics.total_assigned_treks }})
            </router-link>
          </div>
          <div class="card-body p-0">
            <div v-if="assignedTreks.length === 0" class="text-center py-5 text-muted">
              <span class="fs-1 d-block mb-2">🏔️</span>
              <p class="mb-0">You currently have no expeditions assigned to you.</p>
              <small class="text-muted">Expeditions assigned to you by administrators will appear here.</small>
            </div>
            <div v-else class="table-responsive" tabindex="0" role="region" aria-label="Assigned Expeditions Table">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Trek Name & Location</th>
                    <th>Dates</th>
                    <th>Difficulty</th>
                    <th>Booking Status</th>
                    <th>Progress</th>
                    <th>Capacity / Booked</th>
                    <th class="text-end pe-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="trek in assignedTreks" :key="trek.id">
                    <td>
                      <div class="fw-bold">{{ trek.trek_name }}</div>
                      <small class="text-muted">📍 {{ trek.location }}</small>
                    </td>
                    <td>
                      <div class="small fw-semibold">{{ trek.start_date }}</div>
                      <small class="text-muted">to {{ trek.end_date }} ({{ trek.duration_days }}d)</small>
                    </td>
                    <td>
                      <span class="badge" :class="getDifficultyBadge(trek.difficulty)">
                        {{ trek.difficulty }}
                      </span>
                    </td>
                    <td>
                      <span class="badge" :class="trek.status === 'Open' ? 'bg-success' : (trek.status === 'Closed' ? 'bg-secondary' : 'bg-info')">
                        {{ trek.status }}
                      </span>
                    </td>
                    <td>
                      <span class="badge" :class="getProgressBadge(trek.operational_progress)">
                        {{ trek.operational_progress }}
                      </span>
                    </td>
                    <td>
                      <div class="d-flex align-items-center gap-2">
                        <div class="progress flex-grow-1" style="height: 6px; width: 60px;">
                          <div
                            class="progress-bar bg-success"
                            role="progressbar"
                            :style="{ width: `${Math.min(100, Math.round(((trek.booked_slots || 0) / (trek.available_slots || 1)) * 100))}%` }"
                          ></div>
                        </div>
                        <span class="small fw-semibold">{{ trek.booked_slots || 0 }} / {{ trek.available_slots }}</span>
                      </div>
                      <small class="text-muted">{{ trek.remaining_slots }} remaining</small>
                    </td>
                    <td class="text-end pe-3">
                      <div class="btn-group btn-group-sm">
                        <router-link :to="`/staff/treks/${trek.id}`" class="btn btn-outline-primary" title="Manage slots, status, progress">
                          ⚙️ Manage
                        </router-link>
                        <router-link :to="`/staff/treks/${trek.id}/participants`" class="btn btn-outline-success" title="View participant roster">
                          👥 ({{ trek.booked_slots || 0 }})
                        </router-link>
                      </div>
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
import StaffSidebar from '../components/StaffSidebar.vue'
import StatCard from '../components/StatCard.vue'

const loading = ref(true)
const error = ref('')
const profile = ref({})
const metrics = ref({
  total_assigned_treks: 0,
  open_treks: 0,
  closed_treks: 0,
  ongoing_treks: 0,
  completed_treks: 0,
  total_participants: 0
})
const assignedTreks = ref([])

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

const fetchDashboardData = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('/api/staff/dashboard')
    const data = res.data?.data || {}
    profile.value = {
      staff_name: data.staff_name,
      email: data.email,
      specialization: data.specialization,
      experience_years: data.experience_years
    }
    metrics.value = {
      total_assigned_treks: data.total_assigned_treks || 0,
      open_treks: data.open_treks || 0,
      closed_treks: data.closed_treks || 0,
      ongoing_treks: data.ongoing_treks || 0,
      completed_treks: data.completed_treks || 0,
      total_participants: data.total_participants || 0
    }
    assignedTreks.value = data.assigned_treks || data.treks || []
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load staff dashboard metrics.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>
