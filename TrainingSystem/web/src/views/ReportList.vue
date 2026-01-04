<template>
    <div class="list-container">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span style="font-weight: bold; font-size: 18px;">📋 学生实训报告管理</span>
            <el-button type="primary" @click="fetchReports">
              <el-icon style="margin-right: 5px"><Refresh /></el-icon> 刷新列表
            </el-button>
          </div>
        </template>
  
        <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
          
          <el-table-column prop="id" label="ID" width="80" />
          
          <el-table-column label="实训任务" min-width="150">
            <template #default="scope">
               {{ scope.row.task_title || ('任务ID: ' + scope.row.task) }}
            </template>
          </el-table-column>
  
          <el-table-column prop="student_name" label="提交学生" width="120">
            <template #default="scope">
              <el-tag effect="plain">{{ scope.row.student_name }}</el-tag>
            </template>
          </el-table-column>
  
          <el-table-column prop="submitted_at" label="提交时间" width="180">
            <template #default="scope">
              {{ formatTime(scope.row.submitted_at) }}
            </template>
          </el-table-column>
  
          <el-table-column label="当前状态" width="120">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
  
          <el-table-column prop="score" label="成绩" width="100">
             <template #default="scope">
               <span v-if="scope.row.score" style="font-weight: bold; color: #ff9900;">
                 {{ scope.row.score }} 分
               </span>
               <span v-else style="color: #ccc;">-</span>
             </template>
          </el-table-column>
  
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="goGrade(scope.row.id)"
              >
                <el-icon style="margin-right: 3px"><EditPen /></el-icon>
                {{ scope.row.status === 'graded' ? '修改评分' : '去批改' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import http from '../http' // 使用我们封装好的 http
  import { useRouter } from 'vue-router'
  import { Refresh, EditPen } from '@element-plus/icons-vue' // 确保引入图标
  
  const router = useRouter()
  const tableData = ref([])
  const loading = ref(false)
  
  // 1. 获取数据
  const fetchReports = async () => {
    loading.value = true
    try {
      // 之前你在 views.py 里写好了 StudentReportViewSet
      // 如果你是老师/管理员，这个接口会返回所有人的报告
      const res = await http.get('reports/')
      
      // 我们手动处理一下数据，方便前端显示（比如把 task ID 换成标题，如果后端没传标题，暂时显示ID）
      // 注意：这里最完美的做法是后端 Serializer 加上 task_title 字段
      // 咱们暂时先这样跑通
      tableData.value = res.data
    } catch (error) {
      console.error('获取列表失败', error)
    } finally {
      loading.value = false
    }
  }
  
  // 2. 跳转去评分
  const goGrade = (id) => {
    router.push(`/grade/${id}`)
  }
  
  // 辅助工具：状态颜色
  const getStatusType = (status) => {
    const map = {
      'draft': 'info',
      'submitted': 'primary', // 蓝色
      'graded': 'success',    // 绿色
      'returned': 'danger'    // 红色
    }
    return map[status] || 'info'
  }
  
  // 辅助工具：状态文字
  const getStatusText = (status) => {
    const map = {
      'draft': '草稿中',
      'submitted': '待批改',
      'graded': '已评分',
      'returned': '需重做'
    }
    return map[status] || status
  }
  
  // 辅助工具：时间格式化
  const formatTime = (str) => {
    if (!str) return '未提交'
    return str.replace('T', ' ').substring(0, 16)
  }
  
  onMounted(() => {
    fetchReports()
  })
  </script>
  
  <style scoped>
  .list-container {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  </style>