<template>
    <div class="task-page">
      <div class="page-header">
        <el-button link @click="router.back()" class="back-btn"><el-icon><ArrowLeft /></el-icon> 返回班级列表</el-button>
        <h2>{{ className }} - 实训任务</h2>
      </div>
  
      <div class="task-list-container" v-loading="loading">
        <el-empty v-if="tasks.length === 0" description="该班级暂无发布的任务" />
        
        <el-card 
          v-for="task in tasks" 
          :key="task.id" 
          class="task-card" 
          shadow="hover"
          :class="getCardClass(task.my_status)"
        >
          <div class="card-content">
            <div class="task-main">
              <div class="icon-wrapper" :class="task.my_status">
                <el-icon v-if="task.my_status === 'graded'" :size="24"><Trophy /></el-icon>
                <el-icon v-else-if="task.my_status === 'returned'" :size="24"><Warning /></el-icon>
                <el-icon v-else-if="task.my_status === 'submitted'" :size="24"><Checked /></el-icon>
                <el-icon v-else :size="24"><List /></el-icon>
              </div>
              
              <div class="info-text">
                <div class="task-title">
                  {{ task.title }}
                  <el-tag v-if="task.my_status === 'graded'" type="success" size="small" effect="dark">已结束</el-tag>
                  <el-tag v-else-if="task.my_status === 'returned'" type="danger" size="small" effect="dark">已打回</el-tag>
                  <el-tag v-else-if="task.my_status === 'submitted'" type="primary" size="small">已提交</el-tag>
                  <el-tag v-else type="warning" size="small">进行中</el-tag>
                </div>
                <div class="task-meta">
                  <span class="meta-item"><el-icon><User /></el-icon> 指导：{{ task.teacher_name }}</span>
                  <span class="divider">|</span>
                  <span class="meta-item" :class="{ expired: isExpired(task.end_time) }">
                    <el-icon><Timer /></el-icon> 截止：{{ formatDate(task.end_time) }}
                  </span>
                </div>
              </div>
            </div>
  
            <div class="task-action">
              <div v-if="task.my_status === 'graded'" class="score-wrapper">
                <div class="score-label">最终得分</div>
                <div class="score-num">{{ task.my_score }} <span class="unit">分</span></div>
              </div>
  
              <div class="btn-wrapper">
                <el-button v-if="task.my_status === 'graded'" round @click="goTask(task.id)">查看试卷</el-button>
                <el-button v-else-if="task.my_status === 'returned'" type="danger" round @click="goTask(task.id)">重新提交</el-button>
                <el-button v-else-if="task.my_status === 'submitted'" type="primary" plain round @click="goTask(task.id)">查看提交</el-button>
                <el-button v-else type="primary" round @click="goTask(task.id)" :disabled="isExpired(task.end_time)">去完成</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ArrowLeft, List, Trophy, Warning, Checked, User, Timer } from '@element-plus/icons-vue'
  import http from '../http'
  
  const route = useRoute()
  const router = useRouter()
  const classId = route.params.classId
  const loading = ref(false)
  const tasks = ref([])
  const className = ref('班级任务')
  
  onMounted(async () => {
    loading.value = true
    try {
      const res = await http.get('tasks/')
      tasks.value = res.data.filter(t => t.target_class === Number(classId))
      if(tasks.value.length > 0) {
        className.value = tasks.value[0].target_class_name
      }
    } catch (e) {} 
    finally { loading.value = false }
  })
  
  const getCardClass = (status) => {
    if (status === 'graded') return 'card-graded'
    if (status === 'returned') return 'card-returned'
    return ''
  }
  const goTask = (id) => router.push(`/tasks/${id}/do`)
  const formatDate = (str) => new Date(str).toLocaleDateString()
  const isExpired = (t) => new Date(t) < new Date()
  </script>
  
  <style scoped>
  .task-page { min-height: 100vh; background: #f5f7fa; padding: 20px; }
  .page-header { max-width: 1000px; margin: 0 auto 20px; display: flex; align-items: center; gap: 20px; }
  .page-header h2 { font-size: 20px; color: #333; margin: 0; }
  .back-btn { font-size: 14px; }
  .task-list-container { max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 15px; }
  .task-card { border-radius: 8px; border: none; transition: all 0.3s; }
  .task-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
  .card-graded { border-left: 5px solid #67c23a; background: #f0f9eb; }
  .card-returned { border-left: 5px solid #f56c6c; background: #fef0f0; }
  .card-content { display: flex; justify-content: space-between; align-items: center; padding: 5px; }
  .task-main { display: flex; align-items: center; gap: 15px; flex: 1; }
  .icon-wrapper { width: 48px; height: 48px; border-radius: 8px; background: #ecf5ff; color: #409EFF; display: flex; align-items: center; justify-content: center; }
  .icon-wrapper.graded { background: #e1f3d8; color: #67c23a; }
  .icon-wrapper.returned { background: #fde2e2; color: #f56c6c; }
  .icon-wrapper.submitted { background: #e9e9eb; color: #909399; }
  .info-text { flex: 1; }
  .task-title { font-size: 16px; font-weight: bold; color: #303133; display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
  .task-meta { font-size: 13px; color: #909399; display: flex; align-items: center; gap: 5px; }
  .meta-item { display: flex; align-items: center; gap: 4px; }
  .divider { margin: 0 10px; color: #dcdfe6; }
  .expired { color: #f56c6c; }
  .task-action { display: flex; align-items: center; gap: 20px; }
  .score-wrapper { text-align: center; margin-right: 10px; }
  .score-label { font-size: 12px; color: #67c23a; margin-bottom: 2px; }
  .score-num { font-size: 24px; font-weight: bold; color: #67c23a; line-height: 1; font-family: Impact, sans-serif; }
  .score-num .unit { font-size: 12px; font-weight: normal; }
  .btn-wrapper { min-width: 100px; text-align: right; }
  </style>