<template>
  <div class="d-flex">
    <AdminSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">Trek Staff Management</h2>
          <p class="text-muted mb-0">Provision guides, manage specializations, experience, and access status.</p>
        </div>
        <router-link to="/admin/staff/create" class="btn btn-primary">
          ➕ Add New Staff
        </router-link>
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

      <!-- Search & Status Filter -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-3">
          <form class="row g-2 align-items-center" @submit.prevent="handleSearch">
            <div class="col-md-5">
              <input
                v-model="filters.search"
                type="text"
                class="form-control form-control-sm"
                placeholder="Search staff by name, email or ID..."
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

      <!-- Staff Data Table -->
      <div class="card border-0 shadow-sm">
        <div class="card-body p-0">
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted small">Loading staff records...</p>
          </div>

          <div v-else-if="staffList.length === 0" class="text-center py-5 text-muted">
            <span class="fs-1 d-block mb-2">🧗</span>
            No trek staff found matching current criteria.
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light text-muted small text-uppercase">
                <tr>
                  <th scope="col" class="ps-3">ID</th>
                  <th scope="col">Staff Member</th>
                  <th scope="col">Contact</th>
                  <th scope="col">Specialization</th>
                  <th scope="col">Experience</th>
                  <th scope="col">Assigned Treks</th>
                  <th scope="col">Status</th>
                  <th scope="col" class="text-end pe-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in staffList" :key="s.id">
                  <td class="ps-3 fw-bold text-secondary">#{{ s.id }}</td>
                  <td>
                    <div class="fw-semibold">{{ s.full_name }}</div>
                    <small class="text-muted">{{ s.email }}</small>
                  </td>
                  <td>{{ s.contact_number || s.phone_number || '-' }}</td>
                  <td>
                    <span v-if="s.staff_profile?.specialization || s.specialization" class="badge bg-light text-dark border">
                      {{ s.staff_profile?.specialization || s.specialization }}
                    </span>
                    <span v-else class="text-muted small">-</span>
                  </td>
                  <td>
                    {{ s.staff_profile?.experience_years !== undefined ? s.staff_profile.experience_years : (s.experience_years || 0) }} yrs
                  </td>
                  <td>
                    <span class="badge bg-secondary rounded-pill">
                      {{ s.assigned_treks_count || 0 }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="getStatusBadge(s.status)">{{ s.status }}</span>
                  </td>
                  <td class="text-end pe-3">
                    <div class="btn-group btn-group-sm">
                      <router-link :to="`/admin/staff/${s.id}/edit`" class="btn btn-outline-secondary" title="Edit Staff">
                        ✏️
                      </router-link>
                      <button
                        v-if="s.status === 'Active'"
                        type="button"
                        class="btn btn-outline-warning"
                        title="Deactivate Account"
                        @click="changeStatus(s, 'Inactive')"
                      >
                        ⏸️
                      </button>
                      <button
                        v-else-if="s.status === 'Inactive'"
                        type="button"
                        class="btn btn-outline-success"
                        title="Activate Account"
                        @click="changeStatus(s, 'Active')"
                      >
                        ▶️
                      </button>
                      <button
                        v-if="s.status !== 'Blacklisted'"
                        type="button"
                        class="btn btn-outline-danger"
                        title="Blacklist Account"
                        @click="changeStatus(s, 'Blacklisted')"
                      >
                        🚫
                      </button>
                      <button
                        v-else
                        type="button"
                        class="btn btn-outline-success"
                        title="Reactivate Account"
                        @click="changeStatus(s, 'Active')"
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
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../services/api'
import AdminSidebar from '../components/AdminSidebar.vue'
import Pagination from '../components/Pagination.vue'

const loading = ref(false)
const successMsg = ref('')
const errorMsg = ref('')
const staffList = ref([])
const pagination = ref({ page: 1, pages: 1, total: 0 })

const filters = reactive({
  search: '',
  status: '',
  page: 1,
  per_page: 10
})

const fetchStaff = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const params = {
      page: filters.page,
      per_page: filters.per_page,
      search: filters.search || undefined,
      status: filters.status || undefined
    }
    const res = await api.get('/api/admin/staff', { params })
    staffList.value = res.data?.data?.staff || []
    pagination.value = res.data?.data?.pagination || { page: 1, pages: 1, total: staffList.value.length }
  } catch (err) {
    errorMsg.value = err.response?.data?.message || 'Failed to retrieve staff accounts.'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  filters.page = 1
  fetchStaff()
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.page = 1
  fetchStaff()
}

const goToPage = (p) => {
  filters.page = p
  fetchStaff()
}

const changeStatus = async (staff, newStatus) => {
  errorMsg.value = ''
  successMsg.value = ''
  try {
    await api.patch(`/api/admin/staff/${staff.id}/status`, { status: newStatus })
    successMsg.value = `Staff account status for "${staff.full_name}" updated to "${newStatus}".`
    fetchStaff()
  } catch (err) {
    errorMsg.value = err.response?.data?.message || 'Failed to update staff status.'
  }
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
  fetchStaff()
})
</script>
