<template>
  <div class="d-flex">
    <AdminSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <div class="mb-4">
        <router-link to="/admin/treks" class="text-decoration-none small text-muted">
          ← Back to Treks List
        </router-link>
        <h2 class="fw-bold mb-1 mt-1">Create New Trek Route</h2>
        <p class="text-muted mb-0">Define itinerary details, seasonal dates, capacity, and assign staff leaders.</p>
      </div>

      <div v-if="serverError" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ serverError }}
        <button type="button" class="btn-close" @click="serverError = ''"></button>
      </div>

      <div class="card border-0 shadow-sm" style="max-width: 850px;">
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
                  placeholder="e.g. Roopkund Mystery Lake Expedition"
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
                  placeholder="e.g. Garhwal Himalayas, Uttarakhand"
                  required
                />
                <div v-if="errors.location" class="invalid-feedback">{{ errors.location }}</div>
              </div>

              <!-- Status -->
              <div class="col-md-6">
                <label class="form-label fw-semibold small">Initial Status *</label>
                <select v-model="form.status" class="form-select">
                  <option value="Pending">Pending (Default)</option>
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
                <label class="form-label fw-semibold small">Available Slots (Capacity) *</label>
                <input
                  v-model.number="form.available_slots"
                  type="number"
                  min="1"
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
                  <option :value="null">-- Select Active Staff (Optional) --</option>
                  <option v-for="s in availableStaff" :key="s.id" :value="s.id">
                    {{ s.full_name }} ({{ s.email }}) {{ s.staff_profile?.specialization ? `- ${s.staff_profile.specialization}` : '' }}
                  </option>
                </select>
                <small class="text-muted">Only active Trek Staff users are available for assignment.</small>
              </div>

              <!-- Description -->
              <div class="col-12">
                <label class="form-label fw-semibold small">Description</label>
                <textarea
                  v-model="form.description"
                  class="form-control"
                  rows="3"
                  placeholder="Detailed overview of trail route, terrain, acclimatization itinerary, etc."
                ></textarea>
              </div>
            </div>

            <div class="mt-4 pt-3 border-top d-flex gap-2">
              <button type="submit" class="btn btn-primary px-4" :disabled="submitting">
                {{ submitting ? 'Creating...' : 'Create Trek' }}
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
import { useRouter } from 'vue-router'
import api from '../services/api'
import AdminSidebar from '../components/AdminSidebar.vue'

const router = useRouter()
const submitting = ref(false)
const serverError = ref('')
const availableStaff = ref([])
const errors = reactive({})

const form = reactive({
  name: '',
  location: '',
  description: '',
  difficulty: 'Moderate',
  duration_days: 5,
  available_slots: 15,
  start_date: '',
  end_date: '',
  status: 'Pending',
  assigned_staff_id: null
})

const fetchAvailableStaff = async () => {
  try {
    const res = await api.get('/api/admin/staff/available')
    availableStaff.value = res.data?.data?.staff || []
  } catch (err) {
    console.error('Failed to load available staff', err)
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
    await api.post('/api/admin/treks', payload)
    router.push('/admin/treks')
  } catch (err) {
    serverError.value = err.response?.data?.message || 'Failed to create trek.'
    if (err.response?.data?.errors) {
      Object.assign(errors, err.response.data.errors)
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchAvailableStaff()
})
</script>
