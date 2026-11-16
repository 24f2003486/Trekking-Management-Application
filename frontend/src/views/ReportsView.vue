<template>
  <div class="d-flex">
    <AdminSidebar />

    <div class="flex-grow-1 p-4 bg-light" style="min-height: calc(100vh - 56px);">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="fw-bold mb-1">Reports & Analytics</h2>
          <p class="text-muted mb-0">Live database-derived operational statistics, distributions, and demand analysis.</p>
        </div>
        <button class="btn btn-outline-secondary btn-sm" @click="fetchReports" :disabled="loading">
          🔄 Refresh Data
        </button>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ error }}
        <button type="button" class="btn-close" @click="error = ''"></button>
      </div>

      <!-- Loading Spinner -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2 text-muted small">Aggregating database statistics...</p>
      </div>

      <div v-else>
        <!-- Primary Metrics Overview -->
        <div class="row g-3 mb-4">
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Total Treks"
              :value="reports.total_treks"
              icon="🏔️"
              color="primary"
              subtitle="Registered routes"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Completed Treks"
              :value="reports.completed_treks"
              icon="✅"
              color="success"
              subtitle="Concluded expeditions"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Total Bookings"
              :value="reports.total_bookings"
              icon="🎟️"
              color="warning"
              subtitle="All reservations"
            />
          </div>
          <div class="col-sm-6 col-xl-3">
            <StatCard
              title="Distinct Participants"
              :value="reports.total_participants"
              icon="👥"
              color="info"
              subtitle="Unique trekkers booked"
            />
          </div>
        </div>

        <!-- Distributions Row -->
        <div class="row g-4 mb-4">
          <!-- Difficulty Distribution -->
          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Trek Difficulty Breakdown</h6>
              </div>
              <div class="card-body">
                <table class="table table-sm align-middle mb-0">
                  <thead>
                    <tr class="text-muted small text-uppercase">
                      <th>Difficulty</th>
                      <th class="text-end">Treks</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(count, diff) in reports.treks_by_difficulty" :key="diff">
                      <td>
                        <span class="badge" :class="getDifficultyBadge(diff)">{{ diff }}</span>
                      </td>
                      <td class="text-end fw-bold">{{ count }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Trek Status Distribution -->
          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Trek Status Distribution</h6>
              </div>
              <div class="card-body">
                <table class="table table-sm align-middle mb-0">
                  <thead>
                    <tr class="text-muted small text-uppercase">
                      <th>Status</th>
                      <th class="text-end">Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(count, status) in reports.treks_by_status" :key="status">
                      <td>
                        <span class="badge" :class="getStatusBadge(status)">{{ status }}</span>
                      </td>
                      <td class="text-end fw-bold">{{ count }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Booking Status Distribution -->
          <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Booking Status Breakdown</h6>
              </div>
              <div class="card-body">
                <table class="table table-sm align-middle mb-0">
                  <thead>
                    <tr class="text-muted small text-uppercase">
                      <th>Status</th>
                      <th class="text-end">Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(count, status) in reports.bookings_by_status" :key="status">
                      <td>
                        <span class="badge" :class="getBookingStatusBadge(status)">{{ status }}</span>
                      </td>
                      <td class="text-end fw-bold">{{ count }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Popular Treks Table -->
        <div class="row g-4 mb-4">
          <div class="col-lg-7">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Most Popular Treks (by Booking Demand)</h6>
              </div>
              <div class="card-body p-0">
                <div v-if="!reports.popular_treks || reports.popular_treks.length === 0" class="text-center py-4 text-muted small">
                  No booking demand data available yet.
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light text-muted small text-uppercase">
                      <tr>
                        <th scope="col" class="ps-3">Rank</th>
                        <th scope="col">Trek Name</th>
                        <th scope="col">Location</th>
                        <th scope="col">Difficulty</th>
                        <th scope="col" class="text-end pe-3">Bookings</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(trek, idx) in reports.popular_treks" :key="trek.id">
                        <td class="ps-3 fw-bold text-secondary">#{{ idx + 1 }}</td>
                        <td class="fw-semibold">{{ trek.name || trek.trek_name }}</td>
                        <td>{{ trek.location }}</td>
                        <td>
                          <span class="badge" :class="getDifficultyBadge(trek.difficulty)">{{ trek.difficulty }}</span>
                        </td>
                        <td class="text-end pe-3">
                          <span class="badge bg-primary rounded-pill">{{ trek.booking_count }}</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- Monthly Activity -->
          <div class="col-lg-5">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="card-title fw-bold mb-0">Monthly Booking Activity</h6>
              </div>
              <div class="card-body p-0">
                <div v-if="!reports.monthly_activity || reports.monthly_activity.length === 0" class="text-center py-4 text-muted small">
                  No monthly booking activity recorded.
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light text-muted small text-uppercase">
                      <tr>
                        <th scope="col" class="ps-3">Month</th>
                        <th scope="col">Activity Level</th>
                        <th scope="col" class="text-end pe-3">Bookings</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="m in reports.monthly_activity" :key="m.month">
                        <td class="ps-3 fw-bold">{{ m.month }}</td>
                        <td>
                          <div class="progress" style="height: 6px;">
                            <div
                              class="progress-bar bg-info"
                              role="progressbar"
                              :style="{ width: `${Math.min(100, (m.count / (maxMonthlyCount || 1)) * 100)}%` }"
                            ></div>
                          </div>
                        </td>
                        <td class="text-end pe-3 fw-bold">{{ m.count }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Milestone 7: Monthly Activity Reports Section -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center flex-wrap gap-2">
            <div>
              <h5 class="card-title fw-bold mb-0">📑 Executive Monthly Activity Reports</h5>
              <p class="text-muted small mb-0">System-generated monthly audit summaries of completed treks, distinct participants, and popular routes.</p>
            </div>
            <div class="d-flex gap-2 align-items-center">
              <input
                type="month"
                v-model="selectedMonth"
                class="form-control form-control-sm"
                style="max-width: 160px;"
                title="Select Month (YYYY-MM)"
              />
              <button
                class="btn btn-primary btn-sm"
                @click="generateReport"
                :disabled="generatingReport"
              >
                <span v-if="generatingReport" class="spinner-border spinner-border-sm me-1"></span>
                {{ generatingReport ? 'Generating...' : '⚡ Generate Report' }}
              </button>
              <button
                class="btn btn-outline-secondary btn-sm"
                @click="fetchMonthlyReports"
                :disabled="loadingMonthlyReports"
              >
                🔄 Refresh
              </button>
            </div>
          </div>
          <div class="card-body p-0">
            <div v-if="reportSuccessMsg" class="alert alert-success m-3 py-2 small">
              {{ reportSuccessMsg }}
            </div>
            <div v-if="loadingMonthlyReports" class="text-center py-4">
              <div class="spinner-border spinner-border-sm text-primary"></div>
              <p class="text-muted small mt-1">Loading report history...</p>
            </div>
            <div v-else-if="monthlyReports.length === 0" class="text-center text-muted py-4 small">
              No monthly audit reports generated yet. Select a month and click "Generate Report".
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light small">
                  <tr>
                    <th class="ps-3">Report Month</th>
                    <th>Status</th>
                    <th>Treks Conducted</th>
                    <th>Participants</th>
                    <th>Total Bookings</th>
                    <th>Generated Date</th>
                    <th class="text-end pe-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in monthlyReports" :key="r.id">
                    <td class="ps-3 fw-bold">{{ r.report_month }}</td>
                    <td>
                      <span v-if="r.status === 'Generated'" class="badge bg-success">Generated</span>
                      <span v-else class="badge bg-danger">{{ r.status }}</span>
                    </td>
                    <td>{{ r.total_treks }}</td>
                    <td>{{ r.total_participants }}</td>
                    <td>{{ r.total_bookings }}</td>
                    <td class="small text-muted">{{ formatReportDate(r.generated_at) }}</td>
                    <td class="text-end pe-3">
                      <button
                        v-if="r.status === 'Generated'"
                        class="btn btn-outline-primary btn-sm me-2"
                        @click="viewReport(r.id)"
                      >
                        👁️ View Report
                      </button>
                      <button
                        v-if="r.status === 'Generated'"
                        class="btn btn-sm btn-success"
                        @click="downloadReport(r.id, r.filename)"
                      >
                        ⬇️ Download
                      </button>
                      <span v-else class="text-muted small">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import AdminSidebar from '../components/AdminSidebar.vue'
import StatCard from '../components/StatCard.vue'

const loading = ref(true)
const error = ref('')
const reports = ref({})

// Milestone 7: Monthly Audit Reports
const monthlyReports = ref([])
const loadingMonthlyReports = ref(false)
const generatingReport = ref(false)
const reportSuccessMsg = ref('')
const selectedMonth = ref('')

const fetchReports = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('/api/admin/reports')
    reports.value = res.data?.data || {}
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to retrieve reports.'
  } finally {
    loading.value = false
  }
}

const fetchMonthlyReports = async () => {
  loadingMonthlyReports.value = true
  try {
    const res = await api.get('/api/admin/reports/monthly')
    monthlyReports.value = res.data?.data?.reports || []
  } catch (err) {
    //
  } finally {
    loadingMonthlyReports.value = false
  }
}

const generateReport = async () => {
  generatingReport.value = true
  reportSuccessMsg.value = ''
  try {
    const payload = {}
    if (selectedMonth.value) {
      payload.month = selectedMonth.value
    }
    const res = await api.post('/api/admin/reports/monthly/generate', payload)
    reportSuccessMsg.value = res.data?.message || 'Report generation initiated successfully!'
    setTimeout(fetchMonthlyReports, 1000)
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to trigger report generation.'
  } finally {
    generatingReport.value = false
  }
}

const viewReport = (reportId) => {
  window.open(`/api/admin/reports/monthly/${reportId}/download?download=false`, '_blank')
}

const downloadReport = async (reportId, filename) => {
  try {
    const res = await api.get(`/api/admin/reports/monthly/${reportId}/download?download=true`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([res.data], { type: 'text/html' }))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename || `monthly_report_${reportId}.html`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    alert('Failed to download report.')
  }
}

const formatReportDate = (isoStr) => {
  if (!isoStr) return '-'
  try {
    const d = new Date(isoStr)
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return isoStr
  }
}

const maxMonthlyCount = computed(() => {
  if (!reports.value.monthly_activity || reports.value.monthly_activity.length === 0) return 1
  return Math.max(...reports.value.monthly_activity.map(m => m.count), 1)
})

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

const getBookingStatusBadge = (status) => {
  switch (status) {
    case 'Booked': return 'bg-success'
    case 'Completed': return 'bg-primary'
    case 'Cancelled': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

onMounted(() => {
  fetchReports()
  fetchMonthlyReports()
})
</script>
