<template>
  <div class="dashboard-container">
    <div class="nav-header">
      <div class="left-info">
        <span class="logo-text">📚 实训云课堂</span>
        <span class="divider">|</span>
        <span class="user-name">你好，{{ studentName }}</span>
      </div>
      <el-button type="danger" link @click="logout">退出登录</el-button>
    </div>

    <div class="main-body">
      
      <div v-if="!currentClass" class="class-list-view">
        <div class="view-header">
          <h3>我的课程班级</h3>
        </div>

        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="cls in myClasses" :key="cls.id">
            <el-card class="course-card" shadow="hover" @click="enterClass(cls)">
              <div class="card-cover">
                <div class="cover-content">
                  <el-icon :size="40"><Reading /></el-icon>
                </div>
                <div class="class-tag">教学班</div>
              </div>
              <div class="card-info">
                <h4 class="cls-name">{{ cls.name }}</h4>
                <p class="cls-teacher">👨‍🏫 {{ cls.teacher_name || '讲师' }}</p>
                <div class="enter-btn">点击进入 ></div>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <div class="add-card" @click="joinDialogVisible = true">
              <el-icon class="add-icon"><Plus /></el-icon>
              <p>加入新班级</p>
            </div>
          </el-col>
        </el-row>
      </div>

      <div v-else class="class-detail-view">
        <div class="breadcrumb-bar">
          <el-button link icon="ArrowLeft" @click="currentClass = null">返回课程列表</el-button>
          <span class="separator">/</span>
          <span class="current-crumb">{{ currentClass.name }}</span>
        </div>

        <div class="task-list-area">
          <h3>📅 实训任务</h3>
          <el-empty v-if="filteredTasks.length === 0" description="该班级暂无任务" />
          
          <div v-for="task in filteredTasks" :key="task.id" class="task-item" @click="goToTask(task)">
            <div class="task-icon">
              <el-icon v-if="task.status === 'finished'" color="#67C23A"><CircleCheckFilled /></el-icon>
              <el-icon v-else color="#409EFF"><Document /></el-icon>
            </div>
            <div class="task-main">
              <div class="task-title">
                {{ task.title }}
                <el-tag size="small" :type="task.status === 'finished' ? 'success' : 'warning'" effect="plain">
                  {{ task.status === 'finished' ? '已完成' : '进行中' }}
                </el-tag>
              </div>
              <div class="task-meta">
                <span>截止：{{ formatDate(task.end_time) }}</span>
                <span style="margin-left:15px">指导：{{ task.teacher_name }}</span>
              </div>
            </div>
            <div class="task-action">
              <el-button round size="small" :type="task.status === 'finished' ? 'default' : 'primary'">
                {{ task.status === 'finished' ? '查看' : '去完成' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>

    </div>

    <el-dialog v-model="joinDialogVisible" title="加入教学班级" width="400px">
      <div style="text-align: center; margin: 20px 0;">
        <el-input 
          v-model="inviteCode" 
          placeholder="请输入6位邀请码" 
          size="large" 
          maxlength="6"
          style="font-size: 20px; text-align: center; letter-spacing: 2px;"
        >
           <template #prefix><el-icon><Key /></el-icon></template>
        </el-input>
        <p style="color:#999; font-size:12px; margin-top:10px">邀请码请向任课老师获取</p>
      </div>
      <template #footer>
        <el-button @click="joinDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleJoin" :loading="joining">立即加入</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Reading, Plus, ArrowLeft, Document, CircleCheckFilled, Key } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import http from '../http'

const router = useRouter()
const studentName = ref('')
const myClasses = ref([]) // ★★★ 变成数组 ★★★
const currentClass = ref(null) 
const allTasks = ref([]) // 所有班级的任务
const joinDialogVisible = ref(false)
const inviteCode = ref('')
const joining = ref(false)

onMounted(async () => {
  await fetchUserInfo()
})

const fetchUserInfo = async () => {
  try {
    const res = await http.get('users/me/')
    studentName.value = res.data.real_name || res.data.username
    // ★★★ 获取班级列表 ★★★
    myClasses.value = res.data.joined_classes || [] 
  } catch (e) {
    ElMessage.error('获取信息失败')
  }
}

const handleJoin = async () => {
  if (!inviteCode.value || inviteCode.value.length < 6) return ElMessage.warning('请输入完整邀请码')
  joining.value = true
  try {
    const res = await http.post('classes/join_class/', { invite_code: inviteCode.value })
    ElMessage.success(res.data.message)
    joinDialogVisible.value = false
    inviteCode.value = ''
    await fetchUserInfo() // 刷新班级列表
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '加入失败')
  } finally {
    joining.value = false
  }
}

const enterClass = async (cls) => {
  currentClass.value = cls
  try {
    const res = await http.get('tasks/')
    allTasks.value = res.data
  } catch(e) {
    ElMessage.error('获取任务失败')
  }
}

// 过滤当前选中班级的任务
const filteredTasks = computed(() => {
  if (!currentClass.value) return []
  // 后端返回的任务里有 target_class 字段（班级ID）
  return allTasks.value.filter(t => t.target_class === currentClass.value.id)
})

const goToTask = (task) => {
  router.push(`/tasks`) 
}

const formatDate = (str) => str ? new Date(str).toLocaleDateString() : '无期限'
const logout = () => { localStorage.removeItem('token'); router.push('/login') }
</script>

<style scoped>
.dashboard-container { min-height: 100vh; background: #f5f7fa; display: flex; flex-direction: column; }
.nav-header { height: 60px; background: #fff; padding: 0 30px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.left-info { display: flex; align-items: center; }
.logo-text { font-size: 18px; font-weight: bold; color: #409EFF; }
.divider { margin: 0 15px; color: #ddd; }
.user-name { font-size: 14px; color: #666; }
.main-body { flex: 1; max-width: 1200px; margin: 0 auto; width: 100%; padding: 30px 20px; }
.course-card { cursor: pointer; transition: transform 0.2s; border: none; border-radius: 12px; overflow: hidden; height: 260px; display: flex; flex-direction: column; }
.course-card:hover { transform: translateY(-5px); box-shadow: 0 12px 32px rgba(0,0,0,0.1); }
.course-card :deep(.el-card__body) { padding: 0; height: 100%; display: flex; flex-direction: column; }
.card-cover { height: 140px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; position: relative; }
.cover-content { color: #fff; opacity: 0.8; }
.class-tag { position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.2); color: #fff; font-size: 12px; padding: 2px 8px; border-radius: 4px; }
.card-info { padding: 15px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; background: #fff; }
.cls-name { font-size: 16px; margin: 0 0 5px 0; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cls-teacher { font-size: 13px; color: #999; margin: 0; }
.enter-btn { font-size: 13px; color: #409EFF; margin-top: 10px; opacity: 0; transition: opacity 0.2s; }
.course-card:hover .enter-btn { opacity: 1; }
.add-card { height: 260px; border: 2px dashed #dcdfe6; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; color: #909399; transition: all 0.3s; background: #fff; }
.add-card:hover { border-color: #409EFF; color: #409EFF; background: #f0f9eb; }
.add-icon { font-size: 40px; margin-bottom: 10px; }
.breadcrumb-bar { display: flex; align-items: center; margin-bottom: 20px; font-size: 14px; }
.separator { margin: 0 10px; color: #999; }
.current-crumb { font-weight: bold; color: #333; }
.task-list-area { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.task-item { display: flex; align-items: center; padding: 20px; border-bottom: 1px solid #f0f0f0; cursor: pointer; transition: background 0.2s; }
.task-item:last-child { border-bottom: none; }
.task-item:hover { background: #f9f9f9; }
.task-icon { margin-right: 20px; font-size: 24px; display: flex; align-items: center; }
.task-main { flex: 1; }
.task-title { font-size: 16px; font-weight: bold; color: #333; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
.task-meta { font-size: 13px; color: #999; }
</style>