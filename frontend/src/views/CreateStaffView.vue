<template>
  <div class="d-flex">
    <AdminSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <div class="mb-4">
        <router-link to="/admin/staff" class="text-decoration-none small text-muted">
          ← Back to Staff List
        </router-link>
        <h2 class="fw-bold mb-1 mt-1">Provision New Trek Staff</h2>
        <p class="text-muted mb-0">Create a field guide/leader account with associated operational profile.</p>
      </div>

      <div v-if="serverError" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ serverError }}
        <button type="button" class="btn-close" @click="serverError = ''"></button>
      </div>

      <div class="card border-0 shadow-sm" style="max-width: 800px;">
        <div class="card-body p-4">
          <form @submit.prevent="handleSubmit">
            <div class="row g-3">
              <!-- Full Name -->
              <div class="col-md-6">
                <label class="form-label fw-semibold small">Full Name *</label>
                <input
                  v-model="form.full_name"
                  type="text"
                  class="form-control"
                  :class="{ 'is-invalid': errors.full_name }"
                  placeholder="e.g. Tenzing Norgay"
                  required
                />
                <div v-if="errors.full_name" class="invalid-feedback">{{ errors.full_name }}</div>
              </div>

              <!-- Email -->
              <div class="col-md-6">
                <label class="form-label fw-semibold small">Email Address *</label>
                <input
                  v-model="form.email"
                  type="email"
                  class="form-control"
                  :class="{ 'is-invalid': errors.email }"
                  placeholder="e.g. tenzing@trekkingapp.local"
                  required
                />
                <div v-if="errors.email" class="invalid-feedback">{{ errors.email }}</div>
              </div>

              <!-- Password -->
              <div class="col-md-6">
                <label class="form-label fw-semibold small">Initial Password *</label>
                <input
                  v-model="form.password"
                  type="password"
                  class="form-control"
                  :class="{ 'is-invalid': errors.password }"
                  placeholder="Minimum 8 characters"
                  required
                />
                <div v-if="errors.password" class="invalid-feedback">{{ errors.password }}</div>
              </div>

              <!-- Contact Number -->
              <div class="col-md-6">
                <label class="form-label fw-semibold small">Contact Number</label>
                <input
                  v-model="form.contact_number"
                  type="text"
                  class="form-control"
                  placeholder="e.g. +91 9876543210"
                />
              </div>

              <!-- Specialization -->
              <div class="col-md-6">
                <label class="form-label fw-semibold small">Specialization</label>
                <input
                  v-model="form.specialization"
                  type="text"
                  class="form-control"
                  placeholder="e.g. High Altitude Navigation, Glacier Rescue"
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
              <div class="col-12">
                <label class="form-label fw-semibold small">Emergency Contact Number</label>
                <input
                  v-model="form.emergency_contact"
                  type="text"
                  class="form-control"
                  placeholder="e.g. +91 9811223344 (Base camp / kin contact)"
                />
              </div>
            </div>

            <div class="mt-4 pt-3 border-top d-flex gap-2">
              <button type="submit" class="btn btn-primary px-4" :disabled="submitting">
                {{ submitting ? 'Provisioning...' : 'Provision Staff Account' }}
              </button>
              <router-link to="/admin/staff" class="btn btn-outline-secondary">
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
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import AdminSidebar from '../components/AdminSidebar.vue'

const router = useRouter()
const submitting = ref(false)
const serverError = ref('')
const errors = reactive({})

const form = reactive({
  full_name: '',
  email: '',
  password: '',
  contact_number: '',
  specialization: '',
  experience_years: 0,
  emergency_contact: ''
})

const validate = () => {
  Object.keys(errors).forEach(k => delete errors[k])
  let isValid = true

  if (!form.full_name.trim()) {
    errors.full_name = 'Full name is required.'
    isValid = false
  }
  if (!form.email.trim()) {
    errors.email = 'Email address is required.'
    isValid = false
  }
  if (!form.password || form.password.length < 8) {
    errors.password = 'Initial password must be at least 8 characters.'
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
      email: form.email.trim(),
      password: form.password,
      contact_number: form.contact_number ? form.contact_number.trim() : null,
      specialization: form.specialization ? form.specialization.trim() : null,
      experience_years: form.experience_years,
      emergency_contact: form.emergency_contact ? form.emergency_contact.trim() : null
    }
    await api.post('/api/admin/staff', payload)
    router.push('/admin/staff')
  } catch (err) {
    serverError.value = err.response?.data?.message || 'Failed to provision staff account.'
    if (err.response?.data?.errors) {
      Object.assign(errors, err.response.data.errors)
    }
  } finally {
    submitting.value = false
  }
}
</script>
