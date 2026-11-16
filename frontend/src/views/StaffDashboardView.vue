<template>
  <div class="container py-5">
    <div class="row">
      <div class="col-12">
        <!-- Header banner -->
        <div class="p-4 p-md-5 mb-4 bg-light rounded-3 shadow-sm border">
          <div class="container-fluid py-2">
            <div class="d-flex align-items-center mb-3">
              <span class="fs-1 me-3">🧭</span>
              <div>
                <h1 class="display-6 fw-bold mb-0">Trek Staff Portal</h1>
                <span class="badge bg-warning text-dark mt-1">Role: Trek Staff</span>
              </div>
            </div>
            <p class="col-md-9 fs-5 text-muted">
              Welcome, <strong>{{ authService.state.user?.full_name }}</strong>. You are authenticated as an authorized expedition staff member.
            </p>
          </div>
        </div>

        <!-- API Verification Status Card -->
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-header bg-white py-3 border-bottom">
            <h5 class="card-title mb-0 fw-semibold text-warning text-dark">Backend Verification Status</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-warning" role="status"></div>
              <p class="mt-2 text-muted small">Validating Trek Staff authorization with Flask backend...</p>
            </div>
            <div v-else-if="apiMessage" class="alert alert-success d-flex align-items-center mb-0">
              <span class="me-2">✅</span>
              <div>
                <strong>Backend Authorization Successful:</strong> {{ apiMessage }}
              </div>
            </div>
            <div v-else-if="apiError" class="alert alert-danger mb-0">
              <strong>Backend Verification Error:</strong> {{ apiError }}
            </div>
          </div>
        </div>

        <!-- Roadmap Cards -->
        <div class="row g-4">
          <div class="col-md-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body">
                <h6 class="card-title text-muted fw-bold">ASSIGNED EXPEDITIONS</h6>
                <p class="card-text text-muted small">
                  View scheduled batches assigned to you, along with detailed route itineraries and participant caps.
                </p>
                <span class="badge bg-secondary">Planned: Milestone 3</span>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body">
                <h6 class="card-title text-muted fw-bold">FIELD ATTENDANCE & CHECKPOINTS</h6>
                <p class="card-text text-muted small">
                  Track participant lists, record checkpoint status, and log weather or trail conditions in real time.
                </p>
                <span class="badge bg-secondary">Planned: Milestone 3</span>
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
import { authService } from '../services/auth'
import api from '../services/api'

const loading = ref(true)
const apiMessage = ref('')
const apiError = ref('')

onMounted(async () => {
  try {
    const res = await api.get('/api/staff/dashboard')
    apiMessage.value = res.data.message || 'Access granted.'
  } catch (err) {
    apiError.value = err.response?.data?.message || 'Failed to verify backend authorization.'
  } finally {
    loading.value = false
  }
})
</script>

