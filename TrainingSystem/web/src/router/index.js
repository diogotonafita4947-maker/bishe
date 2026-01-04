import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import TaskList from '../views/TaskList.vue'
import ReportEditor from '../views/ReportEditor.vue'
import ReportGrade from '../views/ReportGrade.vue'
import ReportList from '../views/ReportList.vue' // ★ 这一行必须有，且 ReportList.vue 文件必须存在！

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/tasks', name: 'TaskList', component: TaskList },
  
  // ★ 重点修复：这里必须叫 :taskId，才能和 ReportEditor.vue 里的代码对应上
  { path: '/task/:taskId', name: 'ReportEditor', component: ReportEditor },
  
  { path: '/teacher/list', name: 'ReportList', component: ReportList },
  { path: '/grade/:id', name: 'ReportGrade', component: ReportGrade }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router