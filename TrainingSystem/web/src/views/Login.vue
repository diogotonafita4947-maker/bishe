<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="header-box">
          <img src="../assets/vue.svg" alt="logo" class="logo" />
          <h2>实训教学管理系统</h2>
        </div>
      </template>

      <el-form :model="loginForm" label-width="0px" size="large">
        <el-form-item>
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入账号" 
            prefix-icon="User" 
          />
        </el-form-item>

        <el-form-item>
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码" 
            prefix-icon="Lock" 
            show-password 
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            style="width: 100%; font-weight: bold;" 
            @click="handleLogin" 
            :loading="loading"
          >
            🚀 立即登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="tips">
        <p>学生测试账号: 请自行注册</p>
        <p>管理员账号: admin / 123456</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import http from '../http'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)

const loginForm = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }

  loading.value = true
  try {
    // 1. 获取 Token
    const res = await axios.post('http://127.0.0.1:8000/api/token/', loginForm.value)
    const token = res.data.access
    const refresh = res.data.refresh

    // 2. 存 Token
    localStorage.setItem('access_token', token)
    localStorage.setItem('refresh_token', refresh)
    localStorage.setItem('username', loginForm.value.username)

    ElMessage.success('登录成功，正在获取用户信息...')

    // 3. ★★★ 关键步骤：获取用户角色，决定跳去哪里 ★★★
    const userRes = await http.get('users/me/')
    const role = userRes.data.role
    
    // 4. 根据角色跳转不同页面
    if (role === 'teacher' || role === 'admin') {
      // 老师 -> 教师仪表盘
      router.push('/teacher/dashboard')
    } else {
      // 学生 -> 学生仪表盘
      router.push('/student/dashboard')
    }

  } catch (error) {
    console.error(error)
    ElMessage.error('登录失败：账号或密码错误')
    localStorage.clear()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #74ebd5 0%, #ACB6E5 100%);
}
.login-card {
  width: 420px;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}
.header-box {
  text-align: center;
  margin-bottom: 10px;
}
.logo {
  width: 50px;
  margin-bottom: 10px;
}
h2 {
  margin: 0;
  color: #333;
  font-size: 22px;
}
.tips {
  margin-top: 20px;
  text-align: center;
  color: #909399;
  font-size: 12px;
  background: #f4f4f5;
  padding: 10px;
  border-radius: 4px;
}
</style>