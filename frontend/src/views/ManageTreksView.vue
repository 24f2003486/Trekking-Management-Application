<template>
  <div class="d-flex">
    <AdminSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">Trek Management</h2>
          <p class="text-muted mb-0">Browse, filter, configure routes, and allocate staff leaders.</p>
        </div>
        <router-link to="/admin/treks/create" class="btn btn-primary">
          ➕ Create New Trek
        </router-link>
      </div>

      <!-- Success & Error Alerts -->
      <div v-if="successMsg" class="alert alert-success alert-dismissible fade show" role="alert">
        {{ successMsg }}
        <button type="button" class="btn-close" @click="successMsg = ''"></button>
      </div>
      <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ errorMsg }}
        <button type="button" class="btn-close" @click="errorMsg = ''"></button>
      </div>

      <!-- Filters & Search Toolbar -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-3">
          <form class="row g-2 align-items-center" @submit.prevent="handleSearch">
            <div class="col-md-4">
              <input
                v-model="filters.search"
                type="text"
                class="form-control form-control-sm"
                placeholder="Search by trek name or ID..."
              />
            </div>
            <div class="col-md-3">
              <select v-model="filters.difficulty" class="form-select form-select-sm" @change="handleSearch">
                <option value="">All Difficulties</option>
                <option value="Easy">Easy</option>
                <option value="Moderate">Moderate</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
            <div class="col-md-3">
              <select v-model="filters.status" class="form-select form-select-sm" @change="handleSearch">
                <option value="">All Statuses</option>
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Open">Open</option>
                <option value="Closed">Closed</option>
                <option value="Completed">Completed</option>
              </select>
            </div>
            <div class="col-md-2 d-flex gap-1">
              <button type="submit" class="btn btn-sm btn-primary flex-grow-1">Search</button>
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="resetFilters">Reset</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Treks Data Table -->
      <div class="card border-0 shadow-sm">
        <div class="card-body p-0">
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted small">Loading treks catalog...</p>
          </div>

          <div v-else-if="treks.length === 0" class="text-center py-5 text-muted">
            <span class="fs-1 d-block mb-2">🏔️</span>
            No treks found matching current search/filter criteria.
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light text-muted small text-uppercase">
                <tr>
                  <th scope="col" class="ps-3">ID</th>
                  <th scope="col">Trek Name</th>
                  <th scope="col">Location</th>
                  <th scope="col">Difficulty</th>
                  <th scope="col">Duration</th>
                  <th scope="col">Slots</th>
                  <th scope="col">Assigned Staff</th>
                  <th scope="col">Status</th>
                  <th scope="col">Bookings</th>
                  <th scope="col" class="text-end pe-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in treks" :key="t.id">
                  <td class="ps-3 fw-bold text-secondary">#{{ t.id }}</td>
                  <td>
                    <div class="fw-semibold">{{ t.name || t.trek_name }}</div>
                    <small class="text-muted">{{ formatDate(t.start_date) }} - {{ formatDate(t.end_date) }}</small>
                  </td>
                  <td>{{ t.location }}</td>
                  <td>
                    <span class="badge" :class="getDifficultyBadge(t.difficulty)">{{ t.difficulty }}</span>
                  </td>
                  <td>{{ t.duration_days }} days</td>
                  <td>{{ t.available_slots }}</td>
                  <td>
                    <span v-if="t.assigned_staff_name" class="badge bg-light text-dark border">
                      👤 {{ t.assigned_staff_name }}
                    </span>
                    <span v-else class="text-muted small">Unassigned</span>
                  </td>
                  <td>
                    <span class="badge" :class="getStatusBadge(t.status)">{{ t.status }}</span>
                  </td>
                  <td>
                    <span class="badge bg-secondary rounded-pill">{{ t.bookings_count || 0 }}</span>
                  </td>
                  <td class="text-end pe-3">
                    <div class="btn-group btn-group-sm">
                      <router-link :to="`/admin/treks/${t.id}/edit`" class="btn btn-outline-secondary" title="Edit Trek">
                        ✏️
                      </router-link>
                      <button
                        type="button"
                        class="btn btn-outline-danger"
                        title="Delete Trek"
                        @click="promptDelete(t)"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="pagination.pages > 1" class="card-footer bg-white border-0 py-2">
          <Pagination :pagination="pagination" @change-page="goToPage" />
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <ConfirmationModal
        :show="showDeleteModal"
        title="Safe Trek Deletion"
        :message="deleteMessage"
        confirm-text="Delete Trek"
        variant="danger"
        @confirm="confirmDelete"
        @cancel="showDeleteModal = false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../services/api'
import AdminSidebar from '../components/AdminSidebar.vue'
import Pagination from '../components/Pagination.vue'
import ConfirmationModal from '../components/ConfirmationModal.vue'

const loading = ref(false)
const successMsg = ref('')
const errorMsg = ref('')
const treks = ref([])
const pagination = ref({ page: 1, pages: 1, total: 0 })

const filters = reactive({
  search: '',
  difficulty: '',
  status: '',
  page: 1,
  per_page: 10
})

const showDeleteModal = ref(false)
const trekToDelete = ref(null)
const deleteMessage = ref('')

const fetchTreks = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const params = {
      page: filters.page,
      per_page: filters.per_page,
      search: filters.search || undefined,
      difficulty: filters.difficulty || undefined,
      status: filters.status || undefined
    }
    const res = await api.get('/api/admin/treks', { params })
    treks.value = res.data?.data?.treks || []
    pagination.value = res.data?.data?.pagination || { page: 1, pages: 1, total: treks.value.length }
  } catch (err) {
    errorMsg.value = err.response?.data?.message || 'Failed to retrieve treks.'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  filters.page = 1
  fetchTreks()
}

const resetFilters = () => {
  filters.search = ''
  filters.difficulty = ''
  filters.status = ''
  filters.page = 1
  fetchTreks()
}

const goToPage = (p) => {
  filters.page = p
  fetchTreks()
}

const promptDelete = (trek) => {
  trekToDelete.value = trek
  if ((trek.bookings_count || 0) > 0) {
    deleteMessage.value = `Trek "${trek.name || trek.trek_name}" has ${trek.bookings_count} existing booking(s). Safe deletion policy prevents deleting treks with booking history.`
  } else {
    deleteMessage.value = `Are you sure you want to permanently delete trek "${trek.name || trek.trek_name}"? This action cannot be undone.`
  }
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  if (!trekToDelete.value) return
  showDeleteModal.value = false
  errorMsg.value = ''
  successMsg.value = ''
  try {
    await api.delete(`/api/admin/treks/${trekToDelete.value.id}`)
    successMsg.value = `Trek "${trekToDelete.value.name || trekToDelete.value.trek_name}" deleted successfully.`
    fetchTreks()
  } catch (err) {
    errorMsg.value = err.response?.data?.message || 'Failed to delete trek.'
  } finally {
    trekToDelete.value = null
  }
}

const formatDate = (d) => {
  if (!d) return ''
  return new Date(d).toLocaleDateString()
}

const getDifficultyBadge = (diff) => {
  switch (diff) {
    case 'Easy': return 'bg-success'
    case 'Moderate': return 'bg-warning text-dark'
    case 'Hard': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

const getStatusBadge = (status) => {
  switch (status) {
    case 'Open': return 'bg-success'
    case 'Pending': return 'bg-warning text-dark'
    case 'Approved': return 'bg-info text-dark'
    case 'Closed': return 'bg-secondary'
    case 'Completed': return 'bg-primary'
    default: return 'bg-light text-dark'
  }
}

onMounted(() => {
  fetchTreks()
})
</script>
