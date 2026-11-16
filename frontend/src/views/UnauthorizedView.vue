<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 col-md-8 col-lg-6 text-center">
        <div class="card shadow-sm border-0 p-4 p-md-5">
          <div class="fs-1 text-danger mb-3">⛔</div>
          <h1 class="h3 fw-bold text-danger">Access Denied</h1>
          <p class="text-muted mt-2">
            You do not have the required role or permissions to view this resource (HTTP 403 Forbidden).
          </p>

          <div v-if="authService.state.isAuthenticated" class="alert alert-secondary small text-start my-3">
            <div><strong>Your Account:</strong> {{ authService.state.user?.email }}</div>
            <div><strong>Your Current Role:</strong> <span class="badge bg-secondary">{{ authService.state.user?.role }}</span></div>
          </div>

          <div class="d-flex justify-content-center gap-2 mt-3">
            <router-link
              v-if="authService.state.isAuthenticated"
              :to="authService.getRoleDashboardPath(authService.state.user?.role)"
              class="btn btn-primary"
            >
              Return to Your Dashboard
            </router-link>
            <router-link
              v-else
              to="/login"
              class="btn btn-primary"
            >
              Go to Sign In
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { authService } from '../services/auth'
</script>

