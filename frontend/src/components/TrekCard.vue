<template>
  <div class="card h-100 border-0 shadow-sm trek-card">
    <div class="card-body p-4 d-flex flex-column">
      <!-- Top badges -->
      <div class="d-flex justify-content-between align-items-center mb-2">
        <span class="badge" :class="getDifficultyBadge(trek.difficulty)">
          {{ trek.difficulty }}
        </span>
        <span class="badge bg-secondary">
          ⏱️ {{ trek.duration_days }} Days
        </span>
      </div>

      <!-- Title & Location -->
      <h5 class="card-title fw-bold text-dark mb-1">{{ trek.trek_name }}</h5>
      <p class="text-muted small mb-3">📍 {{ trek.location }}</p>

      <!-- Description Snippet -->
      <p v-if="trek.description" class="text-secondary small flex-grow-1 trek-desc mb-3">
        {{ trek.description }}
      </p>
      <div v-else class="flex-grow-1"></div>

      <!-- Dates & Itinerary info -->
      <div class="bg-light p-2 rounded-3 mb-3 small">
        <div class="d-flex justify-content-between text-muted mb-1">
          <span>Start: <strong>{{ trek.start_date }}</strong></span>
          <span>End: <strong>{{ trek.end_date }}</strong></span>
        </div>
      </div>

      <!-- Slots & Occupancy bar -->
      <div class="mb-3">
        <div class="d-flex justify-content-between align-items-center small mb-1">
          <span class="text-muted">Capacity:</span>
          <strong :class="trek.remaining_slots > 0 ? 'text-success' : 'text-danger'">
            {{ trek.remaining_slots }} / {{ trek.available_slots }} slots available
          </strong>
        </div>
        <div class="progress" style="height: 6px;">
          <div
            class="progress-bar"
            :class="trek.remaining_slots > 0 ? 'bg-success' : 'bg-danger'"
            role="progressbar"
            :style="{ width: `${Math.min(100, Math.round(((trek.booked_slots || 0) / (trek.available_slots || 1)) * 100))}%` }"
          ></div>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="d-flex gap-2 pt-2 border-top">
        <router-link :to="`/trekker/treks/${trek.id}`" class="btn btn-outline-primary btn-sm flex-grow-1">
          View Details
        </router-link>

        <span v-if="trek.has_active_booking" class="badge bg-info text-dark d-flex align-items-center px-2">
          ✅ Active Booking
        </span>
        <span v-else-if="trek.remaining_slots <= 0" class="badge bg-secondary d-flex align-items-center px-2">
          🔒 Full
        </span>
        <button
          v-else
          class="btn btn-success btn-sm flex-grow-1 fw-semibold"
          @click="$emit('book', trek)"
        >
          Book Now
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  trek: {
    type: Object,
    required: true
  }
})

defineEmits(['book'])

const getDifficultyBadge = (difficulty) => {
  switch (difficulty) {
    case 'Easy': return 'bg-success-subtle text-success border border-success-subtle'
    case 'Moderate': return 'bg-warning-subtle text-warning border border-warning-subtle'
    case 'Hard': return 'bg-danger-subtle text-danger border border-danger-subtle'
    default: return 'bg-secondary'
  }
}
</script>

<style scoped>
.trek-card {
  border-radius: 12px;
  transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}
.trek-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.1) !important;
}
.trek-desc {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
