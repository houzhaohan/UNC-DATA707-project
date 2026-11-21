import { createRouter, createWebHistory } from 'vue-router'
import PeakDashboard from '../views/PeakDashboard.vue'
import StationDashboard from '../views/StationDashboard.vue'
import RouteDashboard from '../views/RouteDashboard.vue'

const routes = [
  { path: '/', redirect: '/peak' },
  { path: '/peak', name: 'peak', component: PeakDashboard, meta: { title: 'Peak vs Off-Peak Analysis' } },
  { path: '/station', name: 'station', component: StationDashboard, meta: { title: 'Station Efficiency Analysis' } },
  { path: '/route', name: 'route', component: RouteDashboard, meta: { title: 'Route Performance Analysis' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
