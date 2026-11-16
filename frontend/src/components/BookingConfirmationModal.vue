<template>
  <div v-if="show" class="modal-backdrop fade show"></div>
  <div
    v-if="show"
    class="modal fade show d-block"
    tabindex="-1"
    role="dialog"
    aria-modal="true"
    aria-labelledby="bookingModalTitle"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-success text-white">
          <h5 id="bookingModalTitle" class="modal-title fw-bold">
            🏔️ Confirm Expedition Reservation
          </h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('cancel')"></button>
        </div>

        <div class="modal-body p-4" v-if="trek">
          <h5 class="fw-bold mb-1 text-dark">{{ trek.trek_name }}</h5>
          <p class="text-muted small mb-3">📍 {{ trek.location }}</p>

          <div class="bg-light p-3 rounded-3 mb-3 border">
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted small">Dates:</span>
              <strong class="small">{{ trek.start_date }} to {{ trek.end_date }}</strong>
            </div>
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted small">Duration:</span>
              <span class="badge bg-secondary">{{ trek.duration_days }} Days</span>
            </div>
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted small">Difficulty:</span>
              <span class="badge" :class="getDifficultyBadge(trek.difficulty)">{{ trek.difficulty }}</span>
            </div>
            <div class="d-flex justify-content-between">
              <span class="text-muted small">Available Capacity:</span>
              <span class="fw-bold text-success">{{ trek.remaining_slots }} slots remaining</span>
            </div>
          </div>

          <div class="alert alert-info py-2 small mb-0">
            ℹ️ Your reservation will be confirmed immediately. Please ensure you are prepared for this expedition.
          </div>
        </div>

        <div class="modal-footer bg-light">
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="$emit('cancel')"
            :disabled="loading"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-success fw-semibold"
            @click="$emit('confirm')"
            :disabled="loading || (trek && trek.remaining_slots <= 0)"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-1" role="status"></span>
            {{ loading ? 'Reserving Slot...' : 'Confirm Reservation' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  show: {
    type: Boolean,
    default: false
  },
  trek: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['confirm', 'cancel'])

const getDifficultyBadge = (difficulty) => {
  switch (difficulty) {
    case 'Easy': return 'bg-success-subtle text-success border border-success-subtle'
    case 'Moderate': return 'bg-warning-subtle text-warning border border-warning-subtle'
    case 'Hard': return 'bg-danger-subtle text-danger border border-danger-subtle'
    default: return 'bg-secondary'
  }
}
</script>
