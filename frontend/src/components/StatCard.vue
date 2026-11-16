<template>
  <div class="card h-100 border-0 shadow-sm stat-card">
    <div class="card-body d-flex align-items-center justify-content-between p-3">
      <div>
        <div class="text-uppercase text-muted fw-semibold small mb-1">{{ title }}</div>
        <div class="fs-3 fw-bold" :class="`text-${color}`">{{ value !== undefined && value !== null ? value : '-' }}</div>
        <div v-if="subtitle" class="text-muted small mt-1">{{ subtitle }}</div>
      </div>
      <div v-if="icon" class="stat-icon-wrapper rounded-3 p-3" :class="`bg-${color}-subtle text-${color}`">
        <span class="fs-3">{{ icon }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    default: 0
  },
  icon: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: 'primary'
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.stat-card {
  border-radius: 10px;
  transition: transform 0.15s ease-in-out;
}
.stat-card:hover {
  transform: translateY(-2px);
}
.stat-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
}
.bg-primary-subtle { background-color: #e7f1ff; }
.bg-success-subtle { background-color: #e6f7ec; }
.bg-warning-subtle { background-color: #fff8e6; }
.bg-danger-subtle { background-color: #fde8e8; }
.bg-info-subtle { background-color: #e1f6fa; }
.bg-dark-subtle { background-color: #e9ecef; }
</style>
