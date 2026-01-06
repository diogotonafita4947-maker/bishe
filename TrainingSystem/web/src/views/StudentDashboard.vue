<template>
    <div class="dashboard-container">
      <div class="nav-bar">
        <div class="brand">🎓 实训教学平台</div>
        <div class="user-profile">
          <span style="margin-right: 15px;">你好，{{ user.username }}</span>
          <el-dropdown @command="handleCommand">
            <el-avatar :size="32" style="cursor: pointer; background: #409EFF;">学</el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
  
      <div class="content-area">
        <h2 style="font-weight: 500; color: #333; margin-bottom: 25px;">我的课程</h2>
  
        <div v-if="user.class_group" class="course-card" @click="goTasks">
          <div class="cover-img">
            <span>{{ user.class_group_name ? user.class_group_name.substring(0,1) : '班' }}</span>
          </div>
          <div class="card-info">
            <h3 class="class-name">{{ user.class_group_name }}</h3>
            <p class="teacher-name">
              <el-icon><User /></el-icon> 班级 ID: {{ user.class_group }}
            </p>
            <div class="action-row">
              <span class="enter-btn">点击进入学习 ></span>
            </div>
          </div>
        </div>
  
        <div v-else class="empty-state">
          <div class="empty-card" @click="router.push('/profile')">
            <el-icon :size="40" color="#909399"><Plus /></el-icon>
            <p>您还未加入任何班级</p>
            <el-button type="primary" round>点击去加入</el-button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import http from '../http'
  import { useRouter } from 'vue-router'
  import { User, Plus } from '@element-plus/icons-vue'
  
  const router = useRouter()
  const user = ref({})
  
  const fetchUser = async () => {
    try {
      const res = await http.get('users/me/')
      user.value = res.data
    } catch (error) {
      console.error(error)
    }
  }
  
  const goTasks = () => {
    // 点击卡片进入任务列表
    router.push('/tasks')
  }
  
  const handleCommand = (cmd) => {
    if (cmd === 'profile') router.push('/profile')
    if (cmd === 'logout') {
      localStorage.clear()
      router.push('/login')
    }
  }
  
  onMounted(() => fetchUser())
  </script>
  
  <style scoped>
  .dashboard-container { min-height: 100vh; background: #f5f7fa; }
  .nav-bar { height: 60px; background: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05); }
  .brand { font-size: 20px; font-weight: bold; color: #409EFF; }
  .content-area { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
  .course-card { width: 280px; background: #fff; border-radius: 12px; overflow: hidden; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #ebeef5; }
  .course-card:hover { transform: translateY(-5px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
  .cover-img { height: 140px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; }
  .cover-img span { font-size: 60px; color: rgba(255,255,255,0.3); font-weight: bold; }
  .card-info { padding: 15px 20px; }
  .class-name { margin: 0 0 10px 0; font-size: 16px; color: #333; font-weight: bold; }
  .teacher-name { color: #909399; font-size: 13px; margin: 0 0 15px 0; }
  .enter-btn { color: #409EFF; font-size: 13px; font-weight: 500; }
  .empty-card { width: 280px; height: 260px; background: #fff; border-radius: 12px; border: 2px dashed #dcdfe6; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; color: #909399; gap: 15px; }
  .empty-card:hover { border-color: #409EFF; color: #409EFF; }
  </style>