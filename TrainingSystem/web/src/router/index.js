import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import TeacherDashboard from '../views/TeacherDashboard.vue'
import TeacherOverview from '../views/TeacherOverview.vue' 
import TeacherTask from '../views/TeacherTask.vue'
import TeacherClass from '../views/ClassManager.vue' 
import TeacherGrading from '../views/TeacherGrading.vue' // 批改页

import StudentDashboard from '../views/StudentDashboard.vue' // 班级列表 (首页)
import StudentClassTasks from '../views/StudentClassTasks.vue' // ★ 新增：班级内的任务列表
import StudentDoTask from '../views/StudentDoTask.vue' // 做题页

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  
  // 管理员
  { path: '/admin/dashboard', component: AdminDashboard },
  
  // 教师端
  { 
    path: '/teacher', 
    component: TeacherDashboard,
    children: [
      { path: '', redirect: '/teacher/dashboard' }, 
      { path: 'dashboard', component: TeacherOverview }, 
      { path: 'tasks', component: TeacherTask },
      { path: 'classes', component: TeacherClass },
      { path: 'grading/:reportId', component: TeacherGrading },
    ]
  },
  
  // ★★★ 学生端路由重构 ★★★
  // 1. 首页：班级列表
  { path: '/student/dashboard', component: StudentDashboard },
  
  // 2. 二级页：某个班级内的任务列表
  { path: '/student/class/:classId', component: StudentClassTasks },
  
  // 3. 三级页：具体某个任务的做题页
  { path: '/tasks/:id/do', component: StudentDoTask },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router