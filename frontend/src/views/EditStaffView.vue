<template>
  <div class="d-flex">
    <AdminSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <div class="mb-4">
        <router-link to="/admin/staff" class="text-decoration-none small text-muted">
          ← Back to Staff List
        </router-link>
        <h2 class="fw-bold mb-1 mt-1">Edit Staff Profile #{{ staffId }}</h2>
        <p class="text-muted mb-0">Update credentials, specialization, and field qualifications.</p>
      </div>

      <div v-if="serverError" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ serverError }}
        <button type="button" class="btn-close" @click="serverError = ''"></button>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2 text-muted small">Loading staff record...</p>
      </div>

      <div v-else class="row g-4" style="max-width: 1000px;">
        <div class="col-md-7">
          <div class="card border-0 shadow-sm">
            <div class="card-body p-4">
              <form @submit.prevent="handleSubmit">
                <div class="row g-3">
                  <!-- Full Name -->
                  <div class="col-12">
                    <label class="form-label fw-semibold small">Full Name *</label>
                    <input
                      v-model="form.full_name"
                      type="text"
                      class="form-control"
                      :class="{ 'is-invalid': errors.full_name }"
                      required
                    />
                    <div v-if="errors.full_name" class="invalid-feedback">{{ errors.full_name }}</div>
                  </div>

                  <!-- Email (Read-Only) -->
                  <div class="col-12">
                    <label class="form-label fw-semibold small">Email Address</label>
                    <input
                      :value="staffEmail"
                      type="email"
                      class="form-control bg-light"
                      disabled
                      readonly
                    />
                    <small class="text-muted">Account email serves as primary identity.</small>
                  </div>

                  <!-- Contact Number -->
                  <div class="col-md-6">
                    <label class="form-label fw-semibold small">Contact Number</label>
                    <input
                      v-model="form.contact_number"
                      type="text"
                      class="form-control"
                    />
                  </div>

                  <!-- Specialization -->
                  <div class="col-md-6">
                    <label class="form-label fw-semibold small">Specialization</label>
                    <input
                      v-model="form.specialization"
                      type="text"
                      class="form-control"
                    />
                  </div>

                  <!-- Experience Years -->
                  <div class="col-md-6">
                    <label class="form-label fw-semibold small">Experience (Years) *</label>
                    <input
                      v-model.number="form.experience_years"
                      type="number"
                      min="0"
                      class="form-control"
                      :class="{ 'is-invalid': errors.experience_years }"
                      required
                    />
                    <div v-if="errors.experience_years" class="invalid-feedback">{{ errors.experience_years }}</div>
                  </div>

                  <!-- Emergency Contact -->
                  <div class="col-md-6">
                    <label class="form-label fw-semibold small">Emergency Contact</label>
                    <input
                      v-model="form.emergency_contact"
                      type="text"
                      class="form-control"
                    />
                  </div>
                </div>

                <div class="mt-4 pt-3 border-top d-flex gap-2">
                  <button type="submit" class="btn btn-primary px-4" :disabled="submitting">
                    {{ submitting ? 'Saving...' : 'Update Staff Profile' }}
                  </button>
                  <router-link to="/admin/staff" class="btn btn-outline-secondary">
                    Cancel
                  </router-link>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Assigned Treks Sidebar -->
        <div class="col-md-5">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white py-3 border-bottom">
              <h6 class="card-title fw-bold mb-0">Assigned Treks ({{ assignedTreks.length }})</h6>
            </div>
            <div class="card-body p-0">
              <div v-if="assignedTreks.length === 0" class="text-center py-4 text-muted small">
                No active treks currently assigned to this staff member.
              </div>
              <ul v-else class="list-group list-group-flush">
                <li v-for="t in assignedTreks" :key="t.id" class="list-group-item p-3">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <div class="fw-semibold">{{ t.name || t.trek_name }}</div>
                      <small class="text-muted">{{ t.location }} ({{ t.duration_days }} days)</small>
                    </div>
                    <span class="badge bg-secondary">{{ t.status }}</span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
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
const staffId = route.params.id

const loading = ref(true)
const submitting = ref(false)
const serverError = ref('')
const staffEmail = ref('')
const assignedTreks = ref([])
const errors = reactive({})

const form = reactive({
  full_name: '',
  contact_number: '',
  specialization: '',
  experience_years: 0,
  emergency_contact: ''
})

const fetchStaffDetails = async () => {
  loading.value = true
  serverError.value = ''
  try {
    const res = await api.get(`/api/admin/staff/${staffId}`)
    const s = res.data?.data?.staff || res.data?.data
    if (s) {
      form.full_name = s.full_name || ''
      staffEmail.value = s.email || ''
      form.contact_number = s.contact_number || s.phone_number || ''
      form.specialization = s.staff_profile?.specialization || s.specialization || ''
      form.experience_years = s.staff_profile?.experience_years !== undefined ? s.staff_profile.experience_years : (s.experience_years || 0)
      form.emergency_contact = s.staff_profile?.emergency_contact || s.emergency_contact || ''
      assignedTreks.value = s.assigned_treks || []
    }
  } catch (err) {
    serverError.value = err.response?.data?.message || 'Failed to retrieve staff details.'
  } finally {
    loading.value = false
  }
}

const validate = () => {
  Object.keys(errors).forEach(k => delete errors[k])
  let isValid = true

  if (!form.full_name.trim()) {
    errors.full_name = 'Full name is required.'
    isValid = false
  }
  if (form.experience_years < 0) {
    errors.experience_years = 'Experience cannot be negative.'
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
      full_name: form.full_name.trim(),
      contact_number: form.contact_number ? form.contact_number.trim() : null,
      phone_number: form.contact_number ? form.contact_number.trim() : null,
      specialization: form.specialization ? form.specialization.trim() : null,
      experience_years: form.experience_years,
      emergency_contact: form.emergency_contact ? form.emergency_contact.trim() : null
    }
    await api.put(`/api/admin/staff/${staffId}`, payload)
    router.push('/admin/staff')
  } catch (err) {
    serverError.value = err.response?.data?.message || 'Failed to update staff profile.'
    if (err.response?.data?.errors) {
      Object.assign(errors, err.response.data.errors)
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchStaffDetails()
})
</script>
