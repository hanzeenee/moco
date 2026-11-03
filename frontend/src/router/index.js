import { createRouter, createWebHistory, createMemoryHistory } from 'vue-router'
import HomeView from '../components/HomeView.vue'

const routes = [
  { path: '/utilities', name: 'utilities', component: () => import(/* webpackChunkName: "utility-library" */ '../components/UtilityLibrary.vue') },
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/lecture',
    name: 'lecture',
    component: () => import(/* webpackChunkName: "lecture" */ '../components/LectureView.vue'),
  },
  {
    path: '/event',
    name: 'event',
    component: () => import(/* webpackChunkName: "event" */ '../components/EventView.vue'),
  },
  {
    path: '/classroom',
    name: 'classroom',
    component: () => import(/* webpackChunkName: "classroom" */ '../components/ClassroomView.vue'),
  },
]

// Preserve existing shared hash links while switching to clean history URLs.
if (typeof window !== 'undefined' && window.location.pathname === '/' && window.location.hash.startsWith('#/')) {
  try {
    const legacyUrl = new URL(window.location.hash.slice(1), window.location.origin)
    if (legacyUrl.origin === window.location.origin) {
      if (!legacyUrl.search) legacyUrl.search = window.location.search
      window.history.replaceState(
        window.history.state,
        '',
        legacyUrl.pathname + legacyUrl.search + legacyUrl.hash
      )
    }
  } catch {
    // Leave malformed legacy links for the router to handle normally.
  }
}

export function createAppRouter({ memory = typeof window === 'undefined' } = {}) {
  return createRouter({
    history: memory ? createMemoryHistory() : createWebHistory(),
    routes,
  })
}

const router = createAppRouter()

export default router