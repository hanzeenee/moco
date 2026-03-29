import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LectureView from '../views/LectureView.vue'
import EventView from '../views/EventView.vue'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import ClassroomView from '../views/ClassroomView.vue'

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
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/signup',
    name: 'signup',
    component: SignupView,
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