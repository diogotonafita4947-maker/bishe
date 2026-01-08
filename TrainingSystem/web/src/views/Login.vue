<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-left">
        <div class="logo-area">
          <el-icon :size="40" color="#fff"><Collection /></el-icon>
          <span class="app-name">实训云平台</span>
        </div>
        <div class="slogan">
          <h2>实名制教学管理</h2>
          <p>数据互通 · 自动归班 · 智能鉴权</p>
        </div>
        
        <div class="admin-entry">
          <input type="file" ref="fileInput" style="display:none" @change="uploadRoster" />
          <el-button type="primary" plain size="small" @click="$refs.fileInput.click()">
             🔧 [管理员] 导入名单
          </el-button>
        </div>
      </div>

      <div class="login-right">
        <el-tabs v-model="activeTab" class="custom-tabs" stretch>
          
          <el-tab-pane label="账号登录" name="login">
            <el-form :model="loginForm" size="large" @keyup.enter="handleLogin">
              <el-form-item style="margin-top: 20px;">
                <el-input 
                  v-model="loginForm.username" 
                  placeholder="请输入学号 / 工号 (仅限字母数字)" 
                  :prefix-icon="User"
                  @input="filterInput" 
                />
              </el-form-item>
              <el-form-item>
                <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" show-password />
              </el-form-item>
              <el-button type="primary" class="full-btn" @click="handleLogin" :loading="loading">立即登录</el-button>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="实名激活" name="register">
            <el-alert title="请确保您的信息已由管理员录入系统" type="info" :closable="false" style="margin-bottom:15px; background:#f0f9eb; color:#67c23a" />
            
            <el-form :model="regForm" size="large" ref="regRef" :rules="regRules">
              <el-form-item>
                <el-radio-group v-model="regForm.role" class="role-radio">
                  <el-radio-button label="student">我是学生</el-radio-button>
                  <el-radio-button label="teacher">我是老师</el-radio-button>
                </el-radio-group>
              </el-form-item>
              <el-form-item prop="username">
                <el-input 
                  v-model="regForm.username" 
                  :placeholder="regForm.role==='student'?'请输入学号':'请输入教师工号'" 
                  :prefix-icon="Postcard" 
                  @input="(val) => regForm.username = val.replace(/[^a-zA-Z0-9]/g, '')"
                />
              </el-form-item>
              <el-form-item prop="student_id"> 
                <el-input v-model="regForm.student_id" placeholder="请输入真实姓名 (用于核对)" :prefix-icon="User" />
              </el-form-item>
              <el-form-item prop="password">
                <el-input v-model="regForm.password" type="password" placeholder="设置登录密码" :prefix-icon="Lock" show-password />
              </el-form-item>
              <el-form-item prop="confirm_password">
                <el-input v-model="regForm.confirm_password" type="password" placeholder="确认登录密码" :prefix-icon="Lock" />
              </el-form-item>
              <el-button type="success" class="full-btn" @click="handleRegister" :loading="loading">验证并激活</el-button>
            </el-form>
          </el-tab-pane>

        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Collection, Postcard } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import http from '../http'

const router = useRouter()
const activeTab = ref('login')
const loading = ref(false)
const regRef = ref(null)
const fileInput = ref(null)

const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({
  role: 'student',
  username: '',   
  student_id: '', 
  password: '',
  confirm_password: ''
})

// ★★★ 核心函数：过滤非字母数字字符 ★★★
const filterInput = (val) => {
  loginForm.username = val.replace(/[^a-zA-Z0-9]/g, '')
}

const regRules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  student_id: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: (r, v, c) => v !== regForm.password ? c(new Error('密码不一致')) : c(), trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if(!loginForm.username || !loginForm.password) return ElMessage.warning('请输入账号密码')
  loading.value = true
  try {
    const res = await http.post('token/', loginForm)
    localStorage.setItem('token', res.data.access)
    const userRes = await http.get('users/me/')
    const role = userRes.data.role
    ElMessage.success('登录成功')
    
    if (role === 'admin' || loginForm.username === 'admin') router.push('/admin/dashboard')
    else if (role === 'teacher') router.push('/teacher/dashboard')
    else router.push('/student/dashboard')
    
  } catch (e) {
    ElMessage.error('登录失败：账号或密码错误')
  } finally { loading.value = false }
}

const handleRegister = async () => {
  if (!regRef.value) return
  await regRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await http.post('users/register/', regForm)
        ElMessage.success('激活成功！')
        loginForm.username = regForm.username
        loginForm.password = regForm.password
        await handleLogin()
      } catch (e) {
        const msg = e.response?.data?.error || (typeof e.response?.data === 'string' ? e.response.data : Object.values(e.response.data).flat().join(';'))
        ElMessage.error(msg || '注册失败')
      } finally { loading.value = false }
    }
  })
}

const uploadRoster = async (e) => {
  const file = e.target.files[0]
  if(!file) return
  if (!file.name.endsWith('.xlsx')) { ElMessage.error('仅支持 .xlsx 格式！'); return }
  const fd = new FormData()
  fd.append('file', file)
  try {
    const res = await http.post('users/upload_roster/', fd)
    ElMessage.success(res.data.message)
  } catch(e) { 
    ElMessage.error(e.response?.data?.error || '导入失败') 
  }
}
</script>

<style scoped>
.login-container { height: 100vh; width: 100vw; background: linear-gradient(135deg, #1c92d2 0%, #f2fcfe 100%); display: flex; align-items: center; justify-content: center; }
.login-box { width: 850px; height: 520px; background: #fff; border-radius: 12px; box-shadow: 0 12px 40px rgba(0,0,0,0.15); display: flex; overflow: hidden; }
.login-left { width: 45%; background: linear-gradient(135deg, #304352 0%, #d7d2cc 100%); color: #fff; padding: 40px; display: flex; flex-direction: column; justify-content: center; position: relative; }
.logo-area { display: flex; align-items: center; margin-bottom: 20px; z-index: 1; }
.app-name { font-size: 24px; font-weight: bold; margin-left: 10px; }
.slogan h2 { font-size: 28px; margin-bottom: 10px; z-index: 1; }
.slogan p { font-size: 14px; opacity: 0.8; z-index: 1; }
.admin-entry { position: absolute; bottom: 20px; left: 20px; z-index: 10; }
.login-right { flex: 1; padding: 45px; display: flex; flex-direction: column; justify-content: center; }
.custom-tabs :deep(.el-tabs__item) { font-size: 16px; font-weight: bold; }
.full-btn { width: 100%; margin-top: 10px; padding: 22px 0; font-size: 16px; letter-spacing: 2px; }
.role-radio { width: 100%; display: flex; margin-bottom: 10px; }
.role-radio :deep(.el-radio-button) { flex: 1; }
.role-radio :deep(.el-radio-button__inner) { width: 100%; padding: 12px 0; }
</style>