<template>
  <div class="d-flex">
    <AdminSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <div class="mb-4">
        <router-link to="/admin/treks" class="text-decoration-none small text-muted">
          ← Back to Treks List
        </router-link>
        <h2 class="fw-bold mb-1 mt-1">Edit Trek Route #{{ trekId }}</h2>
        <p class="text-muted mb-0">Update expedition details, schedule, capacity, and leader assignments.</p>
      </div>

      <div v-if="serverError" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ serverError }}
        <button type="button" class="btn-close" @click="serverError = ''"></button>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2 text-muted small">Loading trek details...</p>
      </div>

      <div v-else class="card border-0 shadow-sm" style="max-width: 850px;">
        <div class="card-body p-4">
          <form @submit.prevent="handleSubmit">
            <div class="row g-3">
              <!-- Trek Name -->
              <div class="col-md-8">
                <label class="form-label fw-semibold small">Trek Name *</label>
                <input
                  v-model="form.name"
                  type="text"
                  class="form-control"
                  :class="{ 'is-invalid': errors.name }"
                  required
                />
                <div v-if="errors.name" class="invalid-feedback">{{ errors.name }}</div>
              </div>

              <!-- Difficulty -->
              <div class="col-md-4">
                <label class="form-label fw-semibold small">Difficulty Level *</label>
                <select
                  v-model="form.difficulty"
                  class="form-select"
                  :class="{ 'is-invalid': errors.difficulty }"
                  required
                >
                  <option value="Easy">Easy</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Hard">Hard</option>
                </select>
                <div v-if="errors.difficulty" class="invalid-feedback">{{ errors.difficulty }}</div>
              </div>

              <!-- Location -->
              <div class="col-md-6">
                <label class="form-label fw-semibold small">Location / Region *</label>
                <input
                  v-model="form.location"
                  type="text"
                  class="form-control"
                  :class="{ 'is-invalid': errors.location }"
                  required
                />
                <div v-if="errors.location" class="invalid-feedback">{{ errors.location }}</div>
              </div>

              <!-- Status -->
              <div class="col-md-6">
                <label class="form-label fw-semibold small">Status *</label>
                <select v-model="form.status" class="form-select">
                  <option value="Pending">Pending</option>
                  <option value="Approved">Approved</option>
                  <option value="Open">Open</option>
                  <option value="Closed">Closed</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>

              <!-- Duration & Slots -->
              <div class="col-md-6">
                <label class="form-label fw-semibold small">Duration (Days) *</label>
                <input
                  v-model.number="form.duration_days"
                  type="number"
                  min="1"
                  class="form-control"
                  :class="{ 'is-invalid': errors.duration_days }"
                  required
                />
                <div v-if="errors.duration_days" class="invalid-feedback">{{ errors.duration_days }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label fw-semibold small">Available Slots *</label>
                <input
                  v-model.number="form.available_slots"
                  type="number"
                  min="0"
                  class="form-control"
                  :class="{ 'is-invalid': errors.available_slots }"
                  required
                />
                <div v-if="errors.available_slots" class="invalid-feedback">{{ errors.available_slots }}</div>
              </div>

              <!-- Start & End Date -->
              <div class="col-md-6">
                <label class="form-label fw-semibold small">Start Date *</label>
                <input
                  v-model="form.start_date"
                  type="date"
                  class="form-control"
                  :class="{ 'is-invalid': errors.start_date }"
                  required
                />
                <div v-if="errors.start_date" class="invalid-feedback">{{ errors.start_date }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label fw-semibold small">End Date *</label>
                <input
                  v-model="form.end_date"
                  type="date"
                  class="form-control"
                  :class="{ 'is-invalid': errors.end_date }"
                  required
                />
                <div v-if="errors.end_date" class="invalid-feedback">{{ errors.end_date }}</div>
              </div>

              <!-- Assigned Staff Selector -->
              <div class="col-12">
                <label class="form-label fw-semibold small">Assigned Trek Staff (Guide/Leader)</label>
                <select v-model="form.assigned_staff_id" class="form-select">
                  <option :value="null">-- Unassigned --</option>
                  <option v-for="s in availableStaff" :key="s.id" :value="s.id">
                    {{ s.full_name }} ({{ s.email }}) {{ s.staff_profile?.specialization ? `- ${s.staff_profile.specialization}` : '' }}
                  </option>
                </select>
              </div>

              <!-- Description -->
              <div class="col-12">
                <label class="form-label fw-semibold small">Description</label>
                <textarea
                  v-model="form.description"
                  class="form-control"
                  rows="3"
                ></textarea>
              </div>
            </div>

            <div class="mt-4 pt-3 border-top d-flex gap-2">
              <button type="submit" class="btn btn-primary px-4" :disabled="submitting">
                {{ submitting ? 'Saving...' : 'Update Trek' }}
              </button>
              <router-link to="/admin/treks" class="btn btn-outline-secondary">
                Cancel
              </router-link>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import AdminSidebar from '../components/AdminSidebar.vue'

const route = useRoute()
const router = useRouter()
const trekId = route.params.id

const loading = ref(true)
const submitting = ref(false)
const serverError = ref('')
const availableStaff = ref([])
const errors = reactive({})

const form = reactive({
  name: '',
  location: '',
  description: '',
  difficulty: 'Moderate',
  duration_days: 1,
  available_slots: 0,
  start_date: '',
  end_date: '',
  status: 'Pending',
  assigned_staff_id: null
})

const fetchTrekAndStaff = async () => {
  loading.value = true
  serverError.value = ''
  try {
    const [trekRes, staffRes] = await Promise.all([
      api.get(`/api/admin/treks/${trekId}`),
      api.get('/api/admin/staff/available')
    ])

    const t = trekRes.data?.data?.trek || trekRes.data?.data
    if (t) {
      form.name = t.name || t.trek_name || ''
      form.location = t.location || ''
      form.description = t.description || ''
      form.difficulty = t.difficulty || 'Moderate'
      form.duration_days = t.duration_days || 1
      form.available_slots = t.available_slots || 0
      form.start_date = t.start_date || ''
      form.end_date = t.end_date || ''
      form.status = t.status || 'Pending'
      form.assigned_staff_id = t.assigned_staff_id || null
    }

    availableStaff.value = staffRes.data?.data?.staff || []
  } catch (err) {
    serverError.value = err.response?.data?.message || 'Failed to retrieve trek details.'
  } finally {
    loading.value = false
  }
}

const validate = () => {
  Object.keys(errors).forEach(k => delete errors[k])
  let isValid = true

  if (!form.name.trim()) {
    errors.name = 'Trek name is required.'
    isValid = false
  }
  if (!form.location.trim()) {
    errors.location = 'Location is required.'
    isValid = false
  }
  if (!form.start_date) {
    errors.start_date = 'Start date is required.'
    isValid = false
  }
  if (!form.end_date) {
    errors.end_date = 'End date is required.'
    isValid = false
  }
  if (form.start_date && form.end_date && form.end_date < form.start_date) {
    errors.end_date = 'End date cannot precede start date.'
    isValid = false
  }
  if (form.duration_days <= 0) {
    errors.duration_days = 'Duration must be positive.'
    isValid = false
  }
  if (form.available_slots < 0) {
    errors.available_slots = 'Slots cannot be negative.'
    isValid = false
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validate()) return

  submitting.value = true
  serverError.value = ''

  try {
    const payload = {
      trek_name: form.name.trim(),
      name: form.name.trim(),
      location: form.location.trim(),
      description: form.description ? form.description.trim() : null,
      difficulty: form.difficulty,
      duration_days: form.duration_days,
      available_slots: form.available_slots,
      start_date: form.start_date,
      end_date: form.end_date,
      status: form.status,
      assigned_staff_id: form.assigned_staff_id || null
    }
    await api.put(`/api/admin/treks/${trekId}`, payload)
    router.push('/admin/treks')
  } catch (err) {
    serverError.value = err.response?.data?.message || 'Failed to update trek.'
    if (err.response?.data?.errors) {
      Object.assign(errors, err.response.data.errors)
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchTrekAndStaff()
})
</script>
