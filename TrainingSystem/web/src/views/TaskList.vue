<template>
  <div class="task-container">
    <div class="page-header">
      <h2>我的实训任务列表</h2>
      <el-button type="danger" size="small" @click="logout">退出登录</el-button>
    </div>
    
    <div v-if="loading" class="loading-box">
      <el-icon class="is-loading"><Loading /></el-icon> 数据正在加载中...
    </div>

    <el-empty v-if="!loading && tasks.length === 0" description="暂无发布的实训任务" />

    <el-row :gutter="20" v-else>
      <el-col :span="8" v-for="task in tasks" :key="task.id" style="margin-bottom: 20px;">
        <el-card shadow="hover" class="task-card">
          <template #header>
            <div class="card-header">
              <span class="task-title">{{ task.title }}</span>
              <el-tag v-if="task.status === 'published'" type="success" size="small">进行中</el-tag>
              <el-tag v-else type="info" size="small">已结束</el-tag>
            </div>
          </template>
          
          <div class="card-content">
            <p><strong>发布教师：</strong> {{ task.teacher_name }}</p>
            <p><strong>截止时间：</strong> {{ formatDate(task.end_time) }}</p>
            <p class="task-desc">{{ task.description || '暂无详细描述' }}</p>
          </div>
          
          <div class="card-footer">
            <el-button type="primary" plain style="width: 100%" @click="goToEditor(task.id)">
              进入实训并填写报告
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../http' // <--- 重点：改用了我们封装的 http
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const tasks = ref([])
const loading = ref(true)
const router = useRouter()

const goToEditor = (taskId) => {
  router.push(`/editor/${taskId}`)
}

// --- 退出登录功能 ---
const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('username')
  router.push('/login')
  ElMessage.success('已退出登录')
}

const fetchTasks = async () => {
  loading.value = true
  try {
    // <--- 重点：这里不需要写完整网址了，http.js 会自动补全
    const response = await http.get('tasks/') 
    tasks.value = response.data
  } catch (error) {
    console.error('获取失败:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '无'
  return dateStr.replace('T', ' ').substring(0, 16)
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
/* 样式保持不变 */
.task-container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.task-title { font-weight: bold; font-size: 16px; }
.card-content p { color: #606266; font-size: 14px; margin: 8px 0; }
.task-desc { color: #909399; font-size: 12px; }
.card-footer { margin-top: 15px; border-top: 1px dashed #eee; padding-top: 15px; }
</style>