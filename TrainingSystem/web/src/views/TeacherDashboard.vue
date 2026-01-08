<template>
  <div class="teacher-container">
    <div class="sidebar">
      <div class="logo">
        <el-icon><Monitor /></el-icon> 教师工作台
      </div>
      <el-menu
        active-text-color="#ffd04b"
        background-color="#545c64"
        class="el-menu-vertical"
        default-active="1"
        text-color="#fff"
        router
      >
        <el-menu-item index="/teacher/dashboard">
          <el-icon><DataBoard /></el-icon><span>概览</span>
        </el-menu-item>
        <el-menu-item index="/teacher/classes">
          <el-icon><User /></el-icon><span>班级管理</span>
        </el-menu-item>
        <el-menu-item index="/teacher/tasks">
          <el-icon><Document /></el-icon><span>实训任务</span>
        </el-menu-item>
        <el-menu-item index="/teacher/list">
          <el-icon><Edit /></el-icon><span>批阅报告</span>
        </el-menu-item>
      </el-menu>
    </div>

    <div class="main-layout">
      <div class="top-bar">
        <div class="welcome">你好，{{ realName }} 老师</div>
        <el-button type="danger" link @click="logout">退出</el-button>
      </div>
      
      <div class="content-view">
        <el-row :gutter="20" class="overview-row">
          <el-col :span="8">
            <el-card shadow="hover" class="overview-card">
              <div class="num">{{ stats.class_count || 0 }}</div>
              <div class="txt">我的班级</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="overview-card">
              <div class="num">{{ stats.task_count || 0 }}</div>
              <div class="txt">已发布任务</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="overview-card">
              <div class="num">{{ stats.report_count || 0 }}</div>
              <div class="txt">待批阅报告</div>
            </el-card>
          </el-col>
        </el-row>

        <div class="quick-actions">
          <h3>快捷操作</h3>
          <el-button type="primary" size="large" icon="Plus" @click="router.push('/teacher/tasks')">发布新任务</el-button>
          <el-button type="success" size="large" icon="User" @click="router.push('/teacher/classes')">管理班级</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Monitor, DataBoard, User, Document, Edit, Plus } from '@element-plus/icons-vue'
import http from '../http'

const router = useRouter()
const realName = ref('')
const stats = ref({})

onMounted(async () => {
  try {
    const res = await http.get('users/me/')
    realName.value = res.data.real_name || res.data.username
    
    // 获取统计数据(假设后端有这个接口，没有的话可以先忽略或自己实现)
    // const statRes = await http.get('teacher/stats/') 
    // stats.value = statRes.data
  } catch(e) {}
})

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.teacher-container { display: flex; height: 100vh; }
.sidebar { width: 220px; background-color: #545c64; display: flex; flex-direction: column; }
.logo { height: 60px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: bold; border-bottom: 1px solid #666; }
.el-menu-vertical { border-right: none; flex: 1; }
.main-layout { flex: 1; display: flex; flex-direction: column; background: #f0f2f5; }
.top-bar { height: 60px; background: #fff; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.welcome { font-weight: bold; font-size: 16px; }
.content-view { padding: 20px; flex: 1; overflow-y: auto; }
.overview-row { margin-bottom: 30px; }
.overview-card { text-align: center; }
.num { font-size: 32px; font-weight: bold; color: #409EFF; }
.txt { color: #666; margin-top: 5px; }
.quick-actions h3 { margin-bottom: 20px; }
</style>