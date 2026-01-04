import { createRouter, createWebHistory } from 'vue-router'
import TaskList from '../views/TaskList.vue'
import ReportEditor from '../views/ReportEditor.vue'
import Login from '../views/Login.vue'
import ReportGrade from '../views/ReportGrade.vue' // <--- 1. 确保这里引入了

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/',
    redirect: '/tasks'
  },
  {
    path: '/tasks',
    name: 'TaskList',
    component: TaskList
  },
  {
    path: '/editor/:id',
    name: 'ReportEditor',
    component: ReportEditor
  }, // <--- 2. 这里的逗号千万不能少！
  {
    path: '/grade/:id',
    name: 'ReportGrade',
    component: ReportGrade
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// --- 路由守卫 ---
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.name !== 'Login' && !token) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router