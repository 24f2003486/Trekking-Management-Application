<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 col-md-8 col-lg-5">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4 p-md-5">
            <div class="text-center mb-4">
              <div class="fs-1 mb-2">🏔️</div>
              <h2 class="h4 fw-bold">Sign In</h2>
              <p class="text-muted small">
                Trekking Management Application V2
              </p>
            </div>

            <!-- Error Alert -->
            <div
              v-if="errorMessage"
              class="alert alert-danger d-flex align-items-center small py-2"
              role="alert"
            >
              <div>{{ errorMessage }}</div>
            </div>

            <!-- Sign-in Form -->
            <form @submit.prevent="handleLogin" novalidate>
              <!-- Email Input -->
              <div class="mb-3">
                <label for="email" class="form-label small fw-semibold">
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  class="form-control"
                  :class="{ 'is-invalid': fieldErrors.email }"
                  v-model.trim="email"
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

              <!-- Password Input -->
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center">
                  <label for="password" class="form-label small fw-semibold mb-1">
                    Password
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
                  v-model="password"
                  autocomplete="current-password"
                  required
                  placeholder="Enter your password"
                  :disabled="loading"
                />
                <div v-if="fieldErrors.password" class="invalid-feedback">
                  {{ fieldErrors.password }}
                </div>
              </div>

              <!-- Submit Button -->
              <div class="d-grid mt-4">
                <button
                  type="submit"
                  class="btn btn-primary py-2 fw-semibold"
                  :disabled="loading"
                >
                  <span
                    v-if="loading"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  {{ loading ? 'Signing in...' : 'Sign In' }}
                </button>
              </div>
            </form>

            <hr class="my-4 text-muted" />

            <!-- Link to Registration -->
            <div class="text-center small">
              <span class="text-muted">Don't have an account? </span>
              <router-link to="/register" class="fw-semibold text-decoration-none">
                Register as a Trekker
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authService } from '../services/auth'

const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const fieldErrors = ref({})

const handleLogin = async () => {
  errorMessage.value = ''
  fieldErrors.value = {}

  // Client-side quick check
  if (!email.value) {
    fieldErrors.value.email = 'Please enter your email.'
  }
  if (!password.value) {
    fieldErrors.value.password = 'Please enter your password.'
  }
  if (Object.keys(fieldErrors.value).length > 0) {
    return
  }

  loading.value = true
  try {
    const res = await authService.login(email.value, password.value)
    const userRole = res.data.user.role

    // Redirect to redirect query param or default role dashboard
    const redirectPath = route.query.redirect || authService.getRoleDashboardPath(userRole)
    router.push(redirectPath)
  } catch (err) {
    if (err.response && err.response.data) {
      errorMessage.value = err.response.data.message || 'Login failed.'
      if (err.response.data.errors) {
        fieldErrors.value = err.response.data.errors
      }
    } else {
      errorMessage.value = 'Network error or server unreachable. Please check backend status.'
    }
  } finally {
    loading.value = false
  }
}
</script>

