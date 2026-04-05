import { createRouter, createWebHashHistory } from 'vue-router'
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

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router