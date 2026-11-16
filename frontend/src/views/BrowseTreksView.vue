<template>
  <div class="d-flex">
    <TrekkerSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">Browse Available Treks</h2>
          <p class="text-muted mb-0">Discover verified trails open for booking and reserve your expedition spot.</p>
        </div>
        <div>
          <button class="btn btn-outline-secondary" @click="fetchTreks" :disabled="loading">
            🔄 Refresh Catalog
          </button>
        </div>
      </div>

      <!-- Feedback Alerts -->
      <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
        {{ successMessage }}
        <button type="button" class="btn-close" @click="successMessage = ''"></button>
      </div>
      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ errorMessage }}
        <button type="button" class="btn-close" @click="errorMessage = ''"></button>
      </div>

      <!-- Search & Filters Toolbar -->
      <TrekSearchFilters
        v-model="filters"
        @search="handleSearch"
        @clear="handleClearFilters"
      />

      <!-- Catalog Grid -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-success" role="status"></div>
        <p class="mt-2 text-muted small">Loading available expeditions...</p>
      </div>

      <div v-else-if="treks.length === 0" class="text-center py-5 bg-white rounded-3 shadow-sm p-4">
        <span class="fs-1 d-block mb-2">🏔️</span>
        <h5 class="fw-bold">No expeditions match your criteria.</h5>
        <p class="text-muted small mb-3">Try adjusting your search terms or difficulty/duration filters.</p>
        <button class="btn btn-primary btn-sm" @click="handleClearFilters">
          Reset Filters
        </button>
      </div>

      <div v-else>
        <div class="row g-4 mb-4">
          <div v-for="trek in treks" :key="trek.id" class="col-md-6 col-lg-4">
            <TrekCard :trek="trek" @book="openBookingModal" />
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.pages > 1" class="d-flex justify-content-center mt-4">
          <Pagination :pagination="pagination" @change-page="handlePageChange" />
        </div>
      </div>

      <!-- Booking Confirmation Modal -->
      <BookingConfirmationModal
        :show="showModal"
        :trek="selectedTrek"
        :loading="bookingInProgress"
        @confirm="confirmBooking"
        @cancel="closeBookingModal"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../services/api'
import TrekkerSidebar from '../components/TrekkerSidebar.vue'
import TrekCard from '../components/TrekCard.vue'
import TrekSearchFilters from '../components/TrekSearchFilters.vue'
import BookingConfirmationModal from '../components/BookingConfirmationModal.vue'
import Pagination from '../components/Pagination.vue'

const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const treks = ref([])
const pagination = ref({ page: 1, pages: 1, total: 0, has_prev: false, has_next: false })

const filters = reactive({
  search: '',
  difficulty: '',
  duration: ''
})

// Booking Modal State
const showModal = ref(false)
const selectedTrek = ref(null)
const bookingInProgress = ref(false)

const fetchTreks = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {
      page: pagination.value.page,
      per_page: 9
    }
    if (filters.search) params.search = filters.search
    if (filters.difficulty) params.difficulty = filters.difficulty

    if (filters.duration === 'short') {
      params.min_duration = 1
      params.max_duration = 3
    } else if (filters.duration === 'medium') {
      params.min_duration = 4
      params.max_duration = 7
    } else if (filters.duration === 'long') {
      params.min_duration = 8
    }

    const res = await api.get('/api/trekker/treks', { params })
    treks.value = res.data?.data?.treks || []
    pagination.value = res.data?.data?.pagination || { page: 1, pages: 1, total: 0 }
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to load available treks.'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.value.page = 1
  fetchTreks()
}

const handleClearFilters = () => {
  filters.search = ''
  filters.difficulty = ''
  filters.duration = ''
  pagination.value.page = 1
  fetchTreks()
}

const handlePageChange = (newPage) => {
  pagination.value.page = newPage
  fetchTreks()
}

const openBookingModal = (trek) => {
  selectedTrek.value = trek
  showModal.value = true
}

const closeBookingModal = () => {
  showModal.value = false
  selectedTrek.value = null
}

const confirmBooking = async () => {
  if (!selectedTrek.value) return
  bookingInProgress.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const res = await api.post('/api/trekker/bookings', {
      trek_id: selectedTrek.value.id
    })
    successMessage.value = res.data?.message || `Successfully booked ${selectedTrek.value.trek_name}!`
    closeBookingModal()
    // Refresh catalog to update slot capacity & active indicators
    await fetchTreks()
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'Failed to book trek.'
    closeBookingModal()
  } finally {
    bookingInProgress.value = false
  }
}

onMounted(() => {
  fetchTreks()
})
</script>
