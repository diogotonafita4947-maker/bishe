import { createRouter, createWebHistory } from 'vue-router'

import Login from '../views/Login.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import TaskList from '../views/TaskList.vue'
import TeacherDashboard from '../views/TeacherDashboard.vue'
import TeacherTask from '../views/TeacherTask.vue'
import TaskStats from '../views/TaskStats.vue'
import ClassManager from '../views/ClassManager.vue'
import ReportList from '../views/ReportList.vue'
import ReportGrade from '../views/ReportGrade.vue'
import UserProfile from '../views/UserProfile.vue'
// ★ 引入管理员页面
import AdminDashboard from '../views/AdminDashboard.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  
  // 管理员
  { path: '/admin/dashboard', name: 'AdminDashboard', component: AdminDashboard },

  // 学生
  { path: '/student/dashboard', name: 'StudentDashboard', component: StudentDashboard },
  { path: '/tasks', name: 'TaskList', component: TaskList },
  
  // 教师
  { path: '/teacher/dashboard', name: 'TeacherDashboard', component: TeacherDashboard },
  { path: '/teacher/classes', name: 'ClassManager', component: ClassManager },
  { path: '/teacher/tasks', name: 'TeacherTask', component: TeacherTask },
  { path: '/teacher/task/:taskId/stats', name: 'TaskStats', component: TaskStats },
  { path: '/teacher/list', name: 'ReportList', component: ReportList },
  
  // 通用
  { path: '/grade/:id', name: 'ReportGrade', component: ReportGrade },
  { path: '/profile', name: 'UserProfile', component: UserProfile }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router