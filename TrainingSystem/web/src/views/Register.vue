<template>
    <div class="login-container">
      <el-card class="login-card">
        <template #header>
          <h2 style="text-align: center;">用户注册</h2>
        </template>
        
        <el-form :model="form" label-width="0px">
          <el-form-item>
            <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="User" />
          </el-form-item>
          
          <el-form-item>
            <el-input v-model="form.password" type="password" placeholder="设置密码" prefix-icon="Lock" show-password />
          </el-form-item>
          
          <el-form-item>
            <el-select v-model="form.role" placeholder="选择身份" style="width: 100%">
              <el-option label="我是学生" value="student" />
              <el-option label="我是老师" value="teacher" />
            </el-select>
          </el-form-item>
  
          <el-form-item>
            <el-button type="success" style="width: 100%;" @click="handleRegister" :loading="loading">
              立即注册
            </el-button>
          </el-form-item>
          
          <div class="link-area">
            <el-button link type="primary" @click="$router.push('/login')">已有账号？去登录</el-button>
          </div>
        </el-form>
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from 'axios'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { User, Lock } from '@element-plus/icons-vue'
  
  const router = useRouter()
  const loading = ref(false)
  const form = ref({
    username: '',
    password: '',
    role: 'student'
  })
  
  const handleRegister = async () => {
    if(!form.value.username || !form.value.password) return ElMessage.warning('请填写完整')
    
    loading.value = true
    try {
      // 这里的地址要对应后端
      await axios.post('http://127.0.0.1:8000/api/register/', form.value)
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } catch (error) {
      const msg = error.response?.data?.error || '注册失败'
      ElMessage.error(msg)
    } finally {
      loading.value = false
    }
  }
  </script>
  
  <style scoped>
  .login-container { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5; }
  .login-card { width: 400px; }
  .link-area { text-align: center; margin-top: 10px; }
  </style>