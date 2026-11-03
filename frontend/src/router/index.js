import { createRouter, createWebHistory, createMemoryHistory } from 'vue-router'
import HomeView from '../components/HomeView.vue'
import UtilityLibrary from '../components/UtilityLibrary.vue'
import LectureView from '../components/LectureView.vue'
import EventView from '../components/EventView.vue'
import ClassroomView from '../components/ClassroomView.vue'

const routes = [
  { path: '/utilities', name: 'utilities', component: UtilityLibrary },
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/lecture',
    name: 'lecture',
    component: LectureView,
  },
  {
    path: '/event',
    name: 'event',
    component: EventView,
  },
  {
    path: '/classroom',
    name: 'classroom',
    component: ClassroomView,
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