<template>
  <span class="badge" :class="badgeClass">
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  }
})

const badgeClass = computed(() => {
  switch (props.status) {
    case 'Booked':
      return 'bg-success'
    case 'Cancelled':
      return 'bg-secondary'
    case 'Completed':
      return 'bg-primary'
    case 'Pending':
      return 'bg-warning text-dark'
    default:
      return 'bg-light text-dark border'
  }
})

const label = computed(() => {
  switch (props.status) {
    case 'Booked':
      return 'Confirmed (Booked)'
    case 'Cancelled':
      return 'Cancelled'
    case 'Completed':
      return 'Completed'
    default:
      return props.status
  }
})
</script>
