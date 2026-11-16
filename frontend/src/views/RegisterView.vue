<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 col-md-9 col-lg-6">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4 p-md-5">
            <div class="text-center mb-4">
              <div class="fs-1 mb-2">🏔️</div>
              <h2 class="h4 fw-bold">Create Trekker Account</h2>
              <p class="text-muted small">
                Join our trekking community to discover and book expeditions
              </p>
            </div>

            <!-- Success Alert -->
            <div
              v-if="successMessage"
              class="alert alert-success d-flex align-items-center small py-2"
              role="alert"
            >
              <div>{{ successMessage }} Redirecting to sign in...</div>
            </div>

            <!-- Error Alert -->
            <div
              v-if="errorMessage"
              class="alert alert-danger d-flex align-items-center small py-2"
              role="alert"
            >
              <div>{{ errorMessage }}</div>
            </div>

            <!-- Registration Form -->
            <form @submit.prevent="handleRegister" novalidate>
              <!-- Full Name -->
              <div class="mb-3">
                <label for="fullName" class="form-label small fw-semibold">
                  Full Name <span class="text-danger">*</span>
                </label>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  class="form-control"
                  :class="{ 'is-invalid': fieldErrors.full_name }"
                  v-model.trim="form.full_name"
                  autocomplete="name"
                  required
                  placeholder="e.g. John Doe"
                  :disabled="loading"
                />
                <div v-if="fieldErrors.full_name" class="invalid-feedback">
                  {{ fieldErrors.full_name }}
                </div>
              </div>

              <!-- Email -->
              <div class="mb-3">
                <label for="email" class="form-label small fw-semibold">
                  Email address <span class="text-danger">*</span>
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  class="form-control"
                  :class="{ 'is-invalid': fieldErrors.email }"
                  v-model.trim="form.email"
                  autocomplete="username"
                  spellcheck="false"
                  required
                  placeholder="name@example.com"
                  :disabled="loading"
                />
                <div v-if="fieldErrors.email" class="invalid-feedback">
                  {{ fieldErrors.email }}
                </div>
              </div>

              <!-- Contact Number -->
              <div class="mb-3">
                <label for="contactNumber" class="form-label small fw-semibold">
                  Contact Number <span class="text-muted fw-normal">(Optional)</span>
                </label>
                <input
                  id="contactNumber"
                  name="contactNumber"
                  type="tel"
                  class="form-control"
                  :class="{ 'is-invalid': fieldErrors.contact_number }"
                  v-model.trim="form.contact_number"
                  autocomplete="tel"
                  placeholder="+91-9876543210"
                  :disabled="loading"
                />
                <div v-if="fieldErrors.contact_number" class="invalid-feedback">
                  {{ fieldErrors.contact_number }}
                </div>
              </div>

              <!-- Password -->
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center">
                  <label for="password" class="form-label small fw-semibold mb-1">
                    Password <span class="text-danger">*</span>
                  </label>
                  <button
                    type="button"
                    class="btn btn-link btn-sm text-decoration-none p-0 mb-1"
                    @click="showPassword = !showPassword"
                    tabindex="-1"
                  >
                    {{ showPassword ? 'Hide' : 'Show' }}
                  </button>
                </div>
                <input
                  id="password"
                  name="password"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-control"
                  :class="{ 'is-invalid': fieldErrors.password }"
                  v-model="form.password"
                  autocomplete="new-password"
                  required
                  placeholder="Minimum 8 characters"
                  :disabled="loading"
                />
                <div v-if="fieldErrors.password" class="invalid-feedback">
                  {{ fieldErrors.password }}
                </div>
              </div>

              <!-- Confirm Password -->
              <div class="mb-3">
                <label for="confirmPassword" class="form-label small fw-semibold">
                  Confirm Password <span class="text-danger">*</span>
                </label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-control"
                  :class="{ 'is-invalid': fieldErrors.confirm_password }"
                  v-model="form.confirm_password"
                  autocomplete="new-password"
                  required
                  placeholder="Re-enter your password"
                  :disabled="loading"
                />
                <div v-if="fieldErrors.confirm_password" class="invalid-feedback">
                  {{ fieldErrors.confirm_password }}
                </div>
              </div>

              <!-- Submit Button -->
              <div class="d-grid mt-4">
                <button
                  type="submit"
                  class="btn btn-success py-2 fw-semibold"
                  :disabled="loading"
                >
                  <span
                    v-if="loading"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  {{ loading ? 'Creating Account...' : 'Create Trekker Account' }}
                </button>
              </div>
            </form>

            <hr class="my-4 text-muted" />

            <!-- Link back to login -->
            <div class="text-center small">
              <span class="text-muted">Already registered? </span>
              <router-link to="/login" class="fw-semibold text-decoration-none">
                Sign In here
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/auth'

const router = useRouter()

const form = reactive({
  full_name: '',
  email: '',
  contact_number: '',
  password: '',
  confirm_password: ''
})

const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const fieldErrors = ref({})

const handleRegister = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  fieldErrors.value = {}

  // Client-side quick checks
  if (!form.full_name) {
    fieldErrors.value.full_name = 'Full name is required.'
  }
  if (!form.email) {
    fieldErrors.value.email = 'Email address is required.'
  }
  if (!form.password) {
    fieldErrors.value.password = 'Password is required.'
  } else if (form.password.length < 8) {
    fieldErrors.value.password = 'Password must be at least 8 characters.'
  }
  if (!form.confirm_password) {
    fieldErrors.value.confirm_password = 'Password confirmation is required.'
  } else if (form.password !== form.confirm_password) {
    fieldErrors.value.confirm_password = 'Passwords do not match.'
  }

  if (Object.keys(fieldErrors.value).length > 0) {
    return
  }

  loading.value = true
  try {
    const res = await authService.register({
      full_name: form.full_name,
      email: form.email,
      contact_number: form.contact_number || null,
      password: form.password,
      confirm_password: form.confirm_password
    })

    successMessage.value = res.message || 'Registration successful!'
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    if (err.response && err.response.data) {
      errorMessage.value = err.response.data.message || 'Registration failed.'
      if (err.response.data.errors) {
        fieldErrors.value = err.response.data.errors
      }
    } else {
      errorMessage.value = 'Network error or server unreachable. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

