<template>
  <div class="dashboard-container">
    <el-header class="header">
      <div class="left">
        <h2>👋 欢迎回来，{{ studentName }}</h2>
        <p class="subtitle" v-if="myClass">当前班级：<el-tag>{{ myClass }}</el-tag></p>
        <p class="subtitle" v-else>🔴 您尚未加入任何教学班</p>
      </div>
      <el-button type="danger" plain @click="logout">退出登录</el-button>
    </el-header>

    <div class="main-content">
      
      <div v-if="!myClass" class="join-box">
        <el-card shadow="hover" class="join-card">
          <template #header>
            <div class="card-header">
              <span>🚀 加入教学班级</span>
            </div>
          </template>
          <div class="card-body">
            <el-input 
              v-model="inviteCode" 
              placeholder="请输入老师提供的 6 位邀请码" 
              size="large" 
              class="code-input"
              maxlength="6"
            >
              <template #prefix>
                <el-icon><Key /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" size="large" class="join-btn" @click="handleJoin" :loading="joining">
              立即加入
            </el-button>
            <p class="tip">请向您的任课老师获取邀请码</p>
          </div>
        </el-card>
      </div>

      <div v-else>
        <el-row :gutter="20" class="stat-row">
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card" style="border-left: 4px solid #409EFF">
              <div class="stat-value">{{ pendingCount }}</div>
              <div class="stat-label">待完成任务</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card" style="border-left: 4px solid #67C23A">
              <div class="stat-value">{{ finishedCount }}</div>
              <div class="stat-label">已提交报告</div>
            </el-card>
          </el-col>
        </el-row>
        
        <div class="task-section">
          <h3>📅 我的实训任务</h3>
          <el-empty v-if="tasks.length === 0" description="老师暂未发布任务" />
          <el-row :gutter="20" v-else>
            <el-col :span="12" v-for="task in tasks" :key="task.id" style="margin-bottom: 20px;">
              <el-card shadow="hover" class="task-card">
                <template #header>
                  <div class="task-header">
                    <span class="task-title">{{ task.title }}</span>
                    <el-tag :type="getStatusType(task.status)">{{ getStatusText(task.status) }}</el-tag>
                  </div>
                </template>
                <div class="task-desc">
                  <p>截止时间：{{ formatDate(task.end_time) }}</p>
                  <p>指导老师：{{ task.teacher_name }}</p>
                </div>
                <div class="task-footer">
                   <el-button type="primary" plain @click="router.push('/tasks')">去完成</el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Key } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../http'

const router = useRouter()
const studentName = ref('')
const myClass = ref('')
const inviteCode = ref('')
const joining = ref(false)

const tasks = ref([])
const pendingCount = ref(0)
const finishedCount = ref(0)

onMounted(async () => {
  await fetchUserInfo()
  if (myClass.value) {
    fetchTasks()
  }
})

const fetchUserInfo = async () => {
  try {
    const res = await http.get('users/me/')
    studentName.value = res.data.real_name || res.data.username
    myClass.value = res.data.class_group_name // 如果没加班，这里是 null
  } catch (e) {
    ElMessage.error('获取用户信息失败')
  }
}

const handleJoin = async () => {
  if (!inviteCode.value || inviteCode.value.length < 6) return ElMessage.warning('请输入完整的6位邀请码')
  
  joining.value = true
  try {
    const res = await http.post('classes/join_class/', { invite_code: inviteCode.value })
    ElMessage.success(res.data.message)
    // 刷新数据
    await fetchUserInfo()
    fetchTasks()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '加入失败，请检查验证码')
  } finally {
    joining.value = false
  }
}

const fetchTasks = async () => {
  try {
    const res = await http.get('tasks/')
    tasks.value = res.data
    // 简单统计
    // 注意：这里需要根据实际情况统计，这里仅做演示
    pendingCount.value = tasks.value.length
  } catch (e) {}
}

const getStatusType = (status) => status === 'finished' ? 'info' : 'success'
const getStatusText = (status) => status === 'finished' ? '已结束' : '进行中'
const formatDate = (str) => str ? new Date(str).toLocaleString() : '-'

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.dashboard-container { min-height: 100vh; background: #f5f7fa; }
.header { background: #fff; display: flex; justify-content: space-between; align-items: center; padding: 0 40px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.subtitle { color: #999; font-size: 14px; margin-top: 5px; }
.main-content { max-width: 1200px; margin: 30px auto; padding: 0 20px; }

/* 加入班级卡片样式 */
.join-box { display: flex; justify-content: center; margin-top: 80px; }
.join-card { width: 500px; text-align: center; border-radius: 12px; }
.card-header { font-size: 18px; font-weight: bold; }
.card-body { padding: 30px 10px; }
.code-input { margin-bottom: 20px; font-size: 18px; letter-spacing: 2px; text-align: center; }
.join-btn { width: 100%; letter-spacing: 4px; font-weight: bold; }
.tip { margin-top: 15px; color: #909399; font-size: 13px; }

.stat-row { margin-bottom: 30px; }
.stat-card { text-align: center; border-radius: 8px; }
.stat-value { font-size: 32px; font-weight: bold; color: #303133; margin-bottom: 5px; }
.stat-label { color: #909399; }
.task-header { display: flex; justify-content: space-between; align-items: center; }
.task-title { font-weight: bold; font-size: 16px; }
.task-desc { color: #666; font-size: 14px; margin: 15px 0; line-height: 1.6; }
.task-footer { text-align: right; }
</style>