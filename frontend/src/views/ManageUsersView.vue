<template>
  <div class="d-flex">
    <AdminSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">Trekker User Management</h2>
          <p class="text-muted mb-0">Monitor registered trekker profiles, bookings count, and manage account statuses.</p>
        </div>
      </div>

      <!-- Alerts -->
      <div v-if="successMsg" class="alert alert-success alert-dismissible fade show" role="alert">
        {{ successMsg }}
        <button type="button" class="btn-close" @click="successMsg = ''"></button>
      </div>
      <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ errorMsg }}
        <button type="button" class="btn-close" @click="errorMsg = ''"></button>
      </div>

      <!-- Search & Status Filter Toolbar -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-3">
          <form class="row g-2 align-items-center" @submit.prevent="handleSearch">
            <div class="col-md-5">
              <input
                v-model="filters.search"
                type="text"
                class="form-control form-control-sm"
                placeholder="Search trekker by name, email or ID..."
              />
            </div>
            <div class="col-md-4">
              <select v-model="filters.status" class="form-select form-select-sm" @change="handleSearch">
                <option value="">All Account Statuses</option>
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
                <option value="Blacklisted">Blacklisted</option>
              </select>
            </div>
            <div class="col-md-3 d-flex gap-1">
              <button type="submit" class="btn btn-sm btn-primary flex-grow-1">Search</button>
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="resetFilters">Reset</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Trekker Data Table -->
      <div class="card border-0 shadow-sm">
        <div class="card-body p-0">
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted small">Loading trekker accounts...</p>
          </div>

          <div v-else-if="users.length === 0" class="text-center py-5 text-muted">
            <span class="fs-1 d-block mb-2">👥</span>
            No trekker accounts found matching search/filter criteria.
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light text-muted small text-uppercase">
                <tr>
                  <th scope="col" class="ps-3">ID</th>
                  <th scope="col">Trekker Name</th>
                  <th scope="col">Contact</th>
                  <th scope="col">Joined</th>
                  <th scope="col">Bookings</th>
                  <th scope="col">Status</th>
                  <th scope="col" class="text-end pe-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in users" :key="u.id">
                  <td class="ps-3 fw-bold text-secondary">#{{ u.id }}</td>
                  <td>
                    <div class="fw-semibold">{{ u.full_name }}</div>
                    <small class="text-muted">{{ u.email }}</small>
                  </td>
                  <td>{{ u.contact_number || u.phone_number || '-' }}</td>
                  <td>{{ formatDate(u.created_at) }}</td>
                  <td>
                    <span class="badge bg-secondary rounded-pill">
                      {{ u.bookings_count || 0 }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="getStatusBadge(u.status)">{{ u.status }}</span>
                  </td>
                  <td class="text-end pe-3">
                    <div class="btn-group btn-group-sm">
                      <button
                        type="button"
                        class="btn btn-outline-secondary"
                        title="Edit Profile"
                        @click="openEditModal(u)"
                      >
                        ✏️
                      </button>
                      <button
                        v-if="u.status === 'Active'"
                        type="button"
                        class="btn btn-outline-warning"
                        title="Deactivate Account"
                        @click="changeStatus(u, 'Inactive')"
                      >
                        ⏸️
                      </button>
                      <button
                        v-else-if="u.status === 'Inactive'"
                        type="button"
                        class="btn btn-outline-success"
                        title="Activate Account"
                        @click="changeStatus(u, 'Active')"
                      >
                        ▶️
                      </button>
                      <button
                        v-if="u.status !== 'Blacklisted'"
                        type="button"
                        class="btn btn-outline-danger"
                        title="Blacklist Account"
                        @click="changeStatus(u, 'Blacklisted')"
                      >
                        🚫
                      </button>
                      <button
                        v-else
                        type="button"
                        class="btn btn-outline-success"
                        title="Reactivate Account"
                        @click="changeStatus(u, 'Active')"
                      >
                        ✅
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

      <!-- Quick Edit Modal -->
      <div v-if="editingUser" class="modal-backdrop fade show" style="z-index: 1050;"></div>
      <div
        v-if="editingUser"
        class="modal fade show d-block"
        tabindex="-1"
        style="z-index: 1055;"
        role="dialog"
      >
        <div class="modal-dialog modal-dialog-centered" role="document">
          <div class="modal-content shadow border-0">
            <div class="modal-header border-bottom-0 pb-0">
              <h5 class="modal-title fw-bold">Edit Trekker #{{ editingUser.id }}</h5>
              <button type="button" class="btn-close" @click="editingUser = null"></button>
            </div>
            <div class="modal-body py-3">
              <div class="mb-3">
                <label class="form-label small fw-semibold">Email (Immutable)</label>
                <input :value="editingUser.email" type="text" class="form-control form-control-sm bg-light" disabled />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-semibold">Full Name *</label>
                <input v-model="editForm.full_name" type="text" class="form-control form-control-sm" required />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-semibold">Phone / Contact Number</label>
                <input v-model="editForm.contact_number" type="text" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="modal-footer border-top-0 pt-0">
              <button type="button" class="btn btn-outline-secondary btn-sm" @click="editingUser = null">
                Cancel
              </button>
              <button type="button" class="btn btn-primary btn-sm" :disabled="saving" @click="saveUser">
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../services/api'
import AdminSidebar from '../components/AdminSidebar.vue'
import Pagination from '../components/Pagination.vue'

const loading = ref(false)
const saving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')
const users = ref([])
const pagination = ref({ page: 1, pages: 1, total: 0 })

const filters = reactive({
  search: '',
  status: '',
  page: 1,
  per_page: 10
})

const editingUser = ref(null)
const editForm = reactive({
  full_name: '',
  contact_number: ''
})

const fetchUsers = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const params = {
      page: filters.page,
      per_page: filters.per_page,
      search: filters.search || undefined,
      status: filters.status || undefined
    }
    const res = await api.get('/api/admin/users', { params })
    users.value = res.data?.data?.users || []
    pagination.value = res.data?.data?.pagination || { page: 1, pages: 1, total: users.value.length }
  } catch (err) {
    errorMsg.value = err.response?.data?.message || 'Failed to retrieve trekker accounts.'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  filters.page = 1
  fetchUsers()
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.page = 1
  fetchUsers()
}

const goToPage = (p) => {
  filters.page = p
  fetchUsers()
}

const changeStatus = async (user, newStatus) => {
  errorMsg.value = ''
  successMsg.value = ''
  try {
    await api.patch(`/api/admin/users/${user.id}/status`, { status: newStatus })
    successMsg.value = `Status for user "${user.full_name}" updated to "${newStatus}".`
    fetchUsers()
  } catch (err) {
    errorMsg.value = err.response?.data?.message || 'Failed to update user status.'
  }
}

const openEditModal = (u) => {
  editingUser.value = u
  editForm.full_name = u.full_name
  editForm.contact_number = u.contact_number || u.phone_number || ''
}

const saveUser = async () => {
  if (!editingUser.value || !editForm.full_name.trim()) return
  saving.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    await api.put(`/api/admin/users/${editingUser.value.id}`, {
      full_name: editForm.full_name.trim(),
      contact_number: editForm.contact_number.trim(),
      phone_number: editForm.contact_number.trim()
    })
    successMsg.value = `Profile for "${editForm.full_name}" updated successfully.`
    editingUser.value = null
    fetchUsers()
  } catch (err) {
    errorMsg.value = err.response?.data?.message || 'Failed to update user.'
  } finally {
    saving.value = false
  }
}

const formatDate = (d) => {
  if (!d) return '-'
  return new Date(d).toLocaleDateString()
}

const getStatusBadge = (status) => {
  switch (status) {
    case 'Active': return 'bg-success'
    case 'Inactive': return 'bg-warning text-dark'
    case 'Blacklisted': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

onMounted(() => {
  fetchUsers()
})
</script>
