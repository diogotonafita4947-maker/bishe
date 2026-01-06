import { createRouter, createWebHistory } from 'vue-router'

// 1. 引入所有页面组件
import Login from '../views/Login.vue'

// 学生端页面
import StudentDashboard from '../views/StudentDashboard.vue'
import TaskList from '../views/TaskList.vue'  // 现在的 TaskList 已经是包含编辑器的完整工作台了

// 教师端页面
import TeacherDashboard from '../views/TeacherDashboard.vue'
import TeacherTask from '../views/TeacherTask.vue'
import TaskStats from '../views/TaskStats.vue'
import ClassManager from '../views/ClassManager.vue'
import ReportList from '../views/ReportList.vue'

// 通用/其他页面
import ReportGrade from '../views/ReportGrade.vue'   // 老师评分页
import UserProfile from '../views/UserProfile.vue'   // 个人中心

const routes = [
  // 根路径重定向
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  
  // ============================
  // 仪表盘 (Dashboard)
  // ============================
  { path: '/student/dashboard', name: 'StudentDashboard', component: StudentDashboard },
  { path: '/teacher/dashboard', name: 'TeacherDashboard', component: TeacherDashboard },

  // ============================
  // 学生功能
  // ============================
  // ★ 核心工作台 (集成了任务列表 + 在线编辑器)
  { path: '/tasks', name: 'TaskList', component: TaskList },
  
  // 注意：旧的 '/task/:taskId' 路由已被删除，因为现在直接在 /tasks 页面里点击左侧切换
  
  // ============================
  // 教师功能
  // ============================
  // 班级管理
  { path: '/teacher/classes', name: 'ClassManager', component: ClassManager },
  // 任务发布与管理
  { path: '/teacher/tasks', name: 'TeacherTask', component: TeacherTask },
  // 作业统计与批阅入口
  { path: '/teacher/task/:taskId/stats', name: 'TaskStats', component: TaskStats },
  // 列表视图 (备用)
  { path: '/teacher/list', name: 'ReportList', component: ReportList },
  
  // ============================
  // 通用功能
  // ============================
  // 评分页面 (老师点进去给学生打分)
  { path: '/grade/:id', name: 'ReportGrade', component: ReportGrade },
  // 个人中心
  { path: '/profile', name: 'UserProfile', component: UserProfile }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router