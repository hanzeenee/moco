import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../components/HomeView.vue'
import LectureView from '../components/LectureView.vue'
import EventView from '../components/EventView.vue'
import ClassroomView from '../components/ClassroomView.vue'

const routes = [
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
if (window.location.pathname === '/' && window.location.hash.startsWith('#/')) {
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

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router