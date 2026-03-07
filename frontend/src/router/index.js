import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LectureView from '../views/LectureView.vue'
import EventView from '../views/EventView.vue'

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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router