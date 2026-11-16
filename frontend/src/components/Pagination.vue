<template>
  <nav v-if="pagination && (pagination.pages > 1 || pagination.total_pages > 1)" aria-label="Page navigation" class="d-flex justify-content-between align-items-center mt-3">
    <div class="text-muted small">
      Showing page {{ currentPage }} of {{ totalPages }} ({{ totalItems }} items total)
    </div>
    <ul class="pagination pagination-sm mb-0">
      <li class="page-item" :class="{ disabled: !hasPrev }">
        <button class="page-link" @click="$emit('change-page', currentPage - 1)" :disabled="!hasPrev">
          Previous
        </button>
      </li>
      <li
        v-for="p in visiblePages"
        :key="p"
        class="page-item"
        :class="{ active: p === currentPage }"
      >
        <button class="page-link" @click="$emit('change-page', p)">
          {{ p }}
        </button>
      </li>
      <li class="page-item" :class="{ disabled: !hasNext }">
        <button class="page-link" @click="$emit('change-page', currentPage + 1)" :disabled="!hasNext">
          Next
        </button>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  pagination: {
    type: Object,
    default: () => ({ page: 1, pages: 1, total: 0, has_prev: false, has_next: false })
  }
})

defineEmits(['change-page'])

const currentPage = computed(() => props.pagination?.page || 1)
const totalPages = computed(() => props.pagination?.pages || props.pagination?.total_pages || 1)
const totalItems = computed(() => props.pagination?.total !== undefined ? props.pagination.total : (props.pagination?.total_items || 0))
const hasPrev = computed(() => props.pagination?.has_prev ?? (currentPage.value > 1))
const hasNext = computed(() => props.pagination?.has_next ?? (currentPage.value < totalPages.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})
</script>
