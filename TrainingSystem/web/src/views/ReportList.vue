<template>
  <div class="list-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button 
              v-if="currentClassName" 
              icon="ArrowLeft" 
              @click="goBack" 
              style="margin-right: 15px"
            >
              返回班级面板
            </el-button>
            
            <span style="font-weight: bold; font-size: 18px;">
              {{ currentClassName ? `📂 ${currentClassName} - 学生报告` : '📋 所有实训报告' }}
            </span>
          </div>
          <el-button type="primary" @click="fetchReports">刷新列表</el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="student_name" label="提交学生" width="120" />
        <el-table-column prop="task_title" label="任务名称" min-width="150" />
        <el-table-column prop="submitted_at" label="提交时间" width="180">
          <template #default="scope">{{ formatTime(scope.row.submitted_at) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="goGrade(scope.row.id)">
              {{ scope.row.status === 'graded' ? '修改评分' : '去批改' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="!loading && tableData.length === 0" description="暂无提交记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../http'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue' // 引入图标

const router = useRouter()
const route = useRoute()  // ★ 获取路由参数 (classId)

const tableData = ref([])
const loading = ref(false)
// 从 URL 参数里拿班级名字，用来显示标题
const currentClassName = ref(route.query.className || '')

// 1. 获取报告列表 (支持按班级筛选)
const fetchReports = async () => {
  loading.value = true
  try {
    let url = 'reports/'
    // ★ 如果是从班级卡片点进来的，URL里会有 classId
    if (route.query.classId) {
      url += `?class_id=${route.query.classId}`
    }
    
    const res = await http.get(url)
    tableData.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 2. 跳转去批改
const goGrade = (id) => {
  router.push(`/grade/${id}`)
}

// 3. 返回按钮逻辑
const goBack = () => {
  router.push('/dashboard')
}

// 辅助函数
const getStatusType = (s) => ({ 'draft': 'info', 'submitted': 'primary', 'graded': 'success', 'returned': 'danger' }[s] || 'info')
const getStatusText = (s) => ({ 'draft': '草稿', 'submitted': '待批改', 'graded': '已评分', 'returned': '需重做' }[s] || s)
const formatTime = (t) => t ? t.substring(0, 16).replace('T', ' ') : '-'

onMounted(() => fetchReports())
</script>

<style scoped>
.list-container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; }
</style>