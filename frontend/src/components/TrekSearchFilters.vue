<template>
  <div class="card border-0 shadow-sm mb-4">
    <div class="card-body">
      <div class="row g-3">
        <!-- Search bar -->
        <div class="col-md-4">
          <label class="form-label small text-muted fw-semibold mb-1">Search Expedition</label>
          <div class="input-group">
            <span class="input-group-text bg-white border-end-0">🔍</span>
            <input
              :value="modelValue.search"
              @input="updateField('search', $event.target.value)"
              type="text"
              class="form-control border-start-0"
              placeholder="Search by trek name or location..."
              @keyup.enter="$emit('search')"
            />
          </div>
        </div>

        <!-- Difficulty Filter -->
        <div class="col-md-3">
          <label class="form-label small text-muted fw-semibold mb-1">Difficulty</label>
          <select
            :value="modelValue.difficulty"
            @change="updateField('difficulty', $event.target.value)"
            class="form-select"
          >
            <option value="">All Difficulties</option>
            <option value="Easy">Easy</option>
            <option value="Moderate">Moderate</option>
            <option value="Hard">Hard</option>
          </select>
        </div>

        <!-- Duration Filter -->
        <div class="col-md-3">
          <label class="form-label small text-muted fw-semibold mb-1">Duration</label>
          <select
            :value="modelValue.duration"
            @change="updateField('duration', $event.target.value)"
            class="form-select"
          >
            <option value="">All Durations</option>
            <option value="short">1 - 3 Days (Weekend)</option>
            <option value="medium">4 - 7 Days (Standard)</option>
            <option value="long">8+ Days (Extended Expedition)</option>
          </select>
        </div>

        <!-- Clear / Action Buttons -->
        <div class="col-md-2 d-flex align-items-end gap-2">
          <button class="btn btn-outline-secondary w-100" @click="$emit('clear')" title="Clear all filters">
            Clear
          </button>
          <button class="btn btn-success w-100" @click="$emit('search')" title="Apply filters">
            Search
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'search', 'clear'])

const updateField = (field, value) => {
  emit('update:modelValue', {
    ...props.modelValue,
    [field]: value
  })
}
</script>
