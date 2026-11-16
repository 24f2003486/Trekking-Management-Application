<template>
  <div class="d-flex">
    <TrekkerSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="mb-4">
        <h2 class="fw-bold mb-1">My Trekker Profile</h2>
        <p class="text-muted mb-0">Manage your personal information, emergency contact details, and account credentials.</p>
      </div>

      <!-- Feedback Alerts -->
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
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2 text-muted small">Loading your profile details...</p>
      </div>

      <div v-else class="row g-4">
        <!-- Profile Summary Card -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm text-center p-4">
            <div class="mx-auto mb-3 d-flex align-items-center justify-content-center bg-primary-subtle text-primary rounded-circle" style="width: 80px; height: 80px; font-size: 2rem;">
              👤
            </div>
            <h5 class="fw-bold mb-1">{{ form.full_name || 'Trekker' }}</h5>
            <p class="text-muted small mb-3">{{ form.email }}</p>

            <div class="d-flex justify-content-center gap-2 mb-3">
              <span class="badge bg-success-subtle text-success border border-success-subtle">
                Role: {{ form.role }}
              </span>
              <span class="badge" :class="form.status === 'Active' ? 'bg-primary-subtle text-primary border border-primary-subtle' : 'bg-secondary'">
                Status: {{ form.status }}
              </span>
            </div>

            <div class="text-start border-top pt-3 small text-muted">
              <div class="mb-2">
                <strong>Member Since:</strong> {{ formatDate(form.created_at) }}
              </div>
              <div>
                <strong>Account Type:</strong> Verified Registered Trekker
              </div>
            </div>
          </div>
        </div>

        <!-- Profile Edit Form -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white py-3">
              <h5 class="card-title mb-0 fw-semibold">Personal Information & Contact</h5>
            </div>
            <div class="card-body p-4">
              <form @submit.prevent="saveProfile">
                <!-- Full Name -->
                <div class="mb-3">
                  <label for="fullName" class="form-label fw-semibold">
                    Full Name <span class="text-danger">*</span>
                  </label>
                  <input
                    id="fullName"
                    v-model="form.full_name"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': errors.full_name }"
                    placeholder="Enter your complete legal name"
                    required
                  />
                  <div v-if="errors.full_name" class="invalid-feedback">
                    {{ errors.full_name }}
                  </div>
                  <small class="text-muted">Used for expedition rosters and safety manifests.</small>
                </div>

                <!-- Email (Read-Only) -->
                <div class="mb-3">
                  <label for="email" class="form-label fw-semibold">Email Address</label>
                  <input
                    id="email"
                    :value="form.email"
                    type="email"
                    class="form-control bg-light"
                    readonly
                    disabled
                  />
                  <small class="text-muted">Primary account email used for authentication and booking notifications.</small>
                </div>

                <!-- Contact Number -->
                <div class="mb-3">
                  <label for="contactNumber" class="form-label fw-semibold">Contact / Mobile Number</label>
                  <input
                    id="contactNumber"
                    v-model="form.contact_number"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': errors.contact_number }"
                    placeholder="e.g. +91 9876543210"
                  />
                  <div v-if="errors.contact_number" class="invalid-feedback">
                    {{ errors.contact_number }}
                  </div>
                  <small class="text-muted">Essential for trek leaders and emergency communications during mountain expeditions.</small>
                </div>

                <!-- Protected Account Attributes (Informational) -->
                <div class="row g-3 mb-4">
                  <div class="col-sm-6">
                    <label class="form-label fw-semibold text-muted small">Assigned Role</label>
                    <input type="text" :value="form.role" class="form-control bg-light" readonly disabled />
                  </div>
                  <div class="col-sm-6">
                    <label class="form-label fw-semibold text-muted small">Account Status</label>
                    <input type="text" :value="form.status" class="form-control bg-light" readonly disabled />
                  </div>
                </div>

                <!-- Action Buttons -->
                <div class="d-flex justify-content-end gap-2 pt-3 border-top">
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="resetForm"
                    :disabled="saving"
                  >
                    Reset
                  </button>
                  <button
                    type="submit"
                    class="btn btn-primary px-4 fw-semibold"
                    :disabled="saving"
                  >
                    <span v-if="saving" class="spinner-border spinner-border-sm me-1" role="status"></span>
                    {{ saving ? 'Saving Profile...' : 'Save Changes' }}
                  </button>
                </div>
              </form>
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
import { authService } from '../services/auth'
import TrekkerSidebar from '../components/TrekkerSidebar.vue'

const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const originalData = ref({})
const form = reactive({
  full_name: '',
  email: '',
  contact_number: '',
  role: 'Trekker',
  status: 'Active',
  created_at: null
})

const errors = reactive({
  full_name: '',
  contact_number: ''
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
  } catch {
    return dateStr
  }
}

const fetchProfile = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/api/trekker/profile')
    const user = res.data?.data || {}
    originalData.value = { ...user }

    form.full_name = user.full_name || ''
    form.email = user.email || ''
    form.contact_number = user.contact_number || ''
    form.role = user.role || 'Trekker'
    form.status = user.status || 'Active'
    form.created_at = user.created_at || null
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to load profile.'
  } finally {
    loading.value = false
  }
}

const validate = () => {
  let valid = true
  errors.full_name = ''
  errors.contact_number = ''

  if (!form.full_name || form.full_name.trim().length < 2) {
    errors.full_name = 'Full name must be at least 2 characters.'
    valid = false
  } else if (form.full_name.trim().length > 100) {
    errors.full_name = 'Full name must not exceed 100 characters.'
    valid = false
  }

  if (form.contact_number && form.contact_number.trim()) {
    const regex = /^\+?[0-9\s\-]{7,20}$/
    if (!regex.test(form.contact_number.trim())) {
      errors.contact_number = 'Invalid contact number format. Use standard telephone format (e.g., +91 9876543210).'
      valid = false
    }
  }

  return valid
}

const saveProfile = async () => {
  if (!validate()) return

  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const payload = {
      full_name: form.full_name.trim(),
      contact_number: form.contact_number ? form.contact_number.trim() : null
    }

    const res = await api.put('/api/trekker/profile', payload)
    successMessage.value = res.data?.message || 'Profile updated successfully!'

    // Refresh auth state so navbar and sidebar reflect updated name
    await authService.fetchCurrentUser()
    await fetchProfile()
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to update profile.'
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  form.full_name = originalData.value.full_name || ''
  form.contact_number = originalData.value.contact_number || ''
  errors.full_name = ''
  errors.contact_number = ''
}

onMounted(() => {
  fetchProfile()
})
</script>
