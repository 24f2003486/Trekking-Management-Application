import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '../services/auth'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'
import ManageTreksView from '../views/ManageTreksView.vue'
import CreateTrekView from '../views/CreateTrekView.vue'
import EditTrekView from '../views/EditTrekView.vue'
import ManageStaffView from '../views/ManageStaffView.vue'
import CreateStaffView from '../views/CreateStaffView.vue'
import EditStaffView from '../views/EditStaffView.vue'
import ManageUsersView from '../views/ManageUsersView.vue'
import ManageBookingsView from '../views/ManageBookingsView.vue'
import ReportsView from '../views/ReportsView.vue'
import StaffDashboardView from '../views/StaffDashboardView.vue'
import StaffTreksView from '../views/StaffTreksView.vue'
import StaffTrekDetailsView from '../views/StaffTrekDetailsView.vue'
import StaffParticipantsView from '../views/StaffParticipantsView.vue'
import TrekkerDashboardView from '../views/TrekkerDashboardView.vue'
import UnauthorizedView from '../views/UnauthorizedView.vue'

const routes = [
  {
    path: '/',
    redirect: () => {
      const user = authService.state.user
      if (user && authService.state.isAuthenticated) {
        return authService.getRoleDashboardPath(user.role)
      }
      return '/login'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { guestOnly: true }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboardView,
    meta: { requiresAuth: true, allowedRoles: ['Admin'] }
  },
  {
    path: '/admin/treks',
    name: 'ManageTreks',
    component: ManageTreksView,
    meta: { requiresAuth: true, allowedRoles: ['Admin'] }
  },
  {
    path: '/admin/treks/create',
    name: 'CreateTrek',
    component: CreateTrekView,
    meta: { requiresAuth: true, allowedRoles: ['Admin'] }
  },
  {
    path: '/admin/treks/:id/edit',
    name: 'EditTrek',
    component: EditTrekView,
    meta: { requiresAuth: true, allowedRoles: ['Admin'] }
  },
  {
    path: '/admin/staff',
    name: 'ManageStaff',
    component: ManageStaffView,
    meta: { requiresAuth: true, allowedRoles: ['Admin'] }
  },
  {
    path: '/admin/staff/create',
    name: 'CreateStaff',
    component: CreateStaffView,
    meta: { requiresAuth: true, allowedRoles: ['Admin'] }
  },
  {
    path: '/admin/staff/:id/edit',
    name: 'EditStaff',
    component: EditStaffView,
    meta: { requiresAuth: true, allowedRoles: ['Admin'] }
  },
  {
    path: '/admin/users',
    name: 'ManageUsers',
    component: ManageUsersView,
    meta: { requiresAuth: true, allowedRoles: ['Admin'] }
  },
  {
    path: '/admin/bookings',
    name: 'ManageBookings',
    component: ManageBookingsView,
    meta: { requiresAuth: true, allowedRoles: ['Admin'] }
  },
  {
    path: '/admin/reports',
    name: 'Reports',
    component: ReportsView,
    meta: { requiresAuth: true, allowedRoles: ['Admin'] }
  },
  {
    path: '/staff/dashboard',
    name: 'StaffDashboard',
    component: StaffDashboardView,
    meta: { requiresAuth: true, allowedRoles: ['Trek Staff'] }
  },
  {
    path: '/staff/treks',
    name: 'StaffTreks',
    component: StaffTreksView,
    meta: { requiresAuth: true, allowedRoles: ['Trek Staff'] }
  },
  {
    path: '/staff/treks/:id',
    name: 'StaffTrekDetails',
    component: StaffTrekDetailsView,
    meta: { requiresAuth: true, allowedRoles: ['Trek Staff'] }
  },
  {
    path: '/staff/treks/:id/participants',
    name: 'StaffParticipants',
    component: StaffParticipantsView,
    meta: { requiresAuth: true, allowedRoles: ['Trek Staff'] }
  },
  {
    path: '/trekker/dashboard',
    name: 'TrekkerDashboard',
    component: TrekkerDashboardView,
    meta: { requiresAuth: true, allowedRoles: ['Trekker'] }
  },
  {
    path: '/unauthorized',
    name: 'Unauthorized',
    component: UnauthorizedView
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = authService.state.isAuthenticated
  const user = authService.state.user

  // 1. Guest-only routes (login, register)
  if (to.meta.guestOnly && isAuthenticated && user) {
    return next(authService.getRoleDashboardPath(user.role))
  }

  // 2. Protected routes requiring authentication
  if (to.meta.requiresAuth) {
    if (!isAuthenticated || !user) {
      return next({ path: '/login', query: { redirect: to.fullPath } })
    }

    // Role-based authorization
    if (to.meta.allowedRoles && !to.meta.allowedRoles.includes(user.role)) {
      return next('/unauthorized')
    }
  }

  next()
})

export default router

