<template>
  <div v-if="show" class="modal-backdrop fade show" style="z-index: 1050;"></div>
  <div
    v-if="show"
    class="modal fade show d-block"
    tabindex="-1"
    style="z-index: 1055;"
    role="dialog"
  >
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content shadow border-0">
        <div class="modal-header border-bottom-0 pb-0">
          <h5 class="modal-title fw-bold">{{ title }}</h5>
          <button type="button" class="btn-close" aria-label="Close" @click="$emit('cancel')"></button>
        </div>
        <div class="modal-body py-3 text-secondary">
          <p class="mb-0">{{ message }}</p>
        </div>
        <div class="modal-footer border-top-0 pt-0">
          <button type="button" class="btn btn-outline-secondary btn-sm" @click="$emit('cancel')">
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-sm"
            :class="`btn-${variant}`"
            @click="$emit('confirm')"
          >
            {{ confirmText }}
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
  title: {
    type: String,
    default: 'Confirm Action'
  },
  message: {
    type: String,
    default: 'Are you sure you want to proceed with this action?'
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  variant: {
    type: String,
    default: 'danger'
  }
})

defineEmits(['confirm', 'cancel'])
</script>
