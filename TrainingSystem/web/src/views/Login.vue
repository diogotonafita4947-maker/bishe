<template>
    <div class="login-container">
      <el-card class="login-card">
        <template #header>
          <h2 style="text-align: center;">实训系统登录</h2>
        </template>
        
        <el-form :model="loginForm" label-width="0px">
          <el-form-item>
            <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" />
          </el-form-item>
          
          <el-form-item>
            <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password />
          </el-form-item>
  
          <el-form-item>
            <el-button type="primary" style="width: 100%;" @click="handleLogin" :loading="loading">
              立即登录
            </el-button>
          </el-form-item>
        </el-form>
        
        <div style="text-align: center; color: #999; font-size: 12px;">
          测试账号: admin / 密码: 123456
        </div>
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from 'axios'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { User, Lock } from '@element-plus/icons-vue' // 需确保引入了图标
  
  const router = useRouter()
  const loading = ref(false)
  
  const loginForm = ref({
    username: '',
    password: ''
  })
  
  const handleLogin = async () => {
    if(!loginForm.value.username || !loginForm.value.password) {
      ElMessage.warning('请输入账号和密码')
      return
    }
  
    loading.value = true
    try {
      // 1. 发送账号密码给后端
      const res = await axios.post('http://127.0.0.1:8000/api/token/', loginForm.value)
      
      // 2. 登录成功，拿到 token (访问令牌)
      const token = res.data.access
      const refresh = res.data.refresh
      
      console.log('登录成功，Token:', token)
      
      // 3. 把令牌存到浏览器里 (localStorage)，这样刷新页面也不会掉线
      localStorage.setItem('access_token', token)
      localStorage.setItem('username', loginForm.value.username)
      
      ElMessage.success('登录成功！')
      
      // 4. 跳转到任务列表页
      router.push('/tasks')
  
    } catch (error) {
      console.error(error)
      ElMessage.error('登录失败，请检查账号密码')
    } finally {
      loading.value = false
    }
  }
  </script>
  
  <style scoped>
  .login-container {
    display: flex; justify-content: center; align-items: center;
    height: 100vh; background-color: #f0f2f5;
  }
  .login-card { width: 400px; }
  </style>