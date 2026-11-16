import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '../services/auth'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'
import StaffDashboardView from '../views/StaffDashboardView.vue'
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
    path: '/staff/dashboard',
    name: 'StaffDashboard',
    component: StaffDashboardView,
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

