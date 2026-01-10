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
        :default-active="activeMenu" 
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
      </el-menu>
    </div>

    <div class="main-layout">
      <div class="top-bar">
        <div class="welcome">你好，{{ realName }} 老师</div>
        <el-button type="danger" link @click="logout">退出</el-button>
      </div>
      
      <div class="content-view">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Monitor, DataBoard, User, Document } from '@element-plus/icons-vue'
import http from '../http'

const router = useRouter()
const route = useRoute()
const realName = ref('教师')

// 计算当前高亮的菜单项
const activeMenu = computed(() => {
  // 如果当前在 /teacher 根路径，默认高亮 dashboard
  if (route.path === '/teacher') return '/teacher/dashboard'
  return route.path
})

onMounted(async () => {
  try {
    const res = await http.get('users/me/')
    realName.value = res.data.real_name || res.data.username
  } catch(e) {}
})

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.teacher-container { display: flex; height: 100vh; }
.sidebar { width: 220px; background-color: #545c64; display: flex; flex-direction: column; flex-shrink: 0; }
.logo { height: 60px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: bold; border-bottom: 1px solid #666; }
.el-menu-vertical { border-right: none; flex: 1; }
.main-layout { flex: 1; display: flex; flex-direction: column; background: #f0f2f5; overflow: hidden; }
.top-bar { height: 60px; background: #fff; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); flex-shrink: 0; }
.welcome { font-weight: bold; font-size: 16px; }
.content-view { padding: 20px; flex: 1; overflow-y: auto; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>