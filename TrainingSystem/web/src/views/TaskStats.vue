<template>
    <div class="stats-container" v-loading="loading">
      <div class="header">
        <el-button @click="router.back()">返回列表</el-button>
        <h2>{{ taskInfo.title }} - 提交统计</h2>
      </div>
  
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="8">
          <el-statistic title="应提交人数" :value="statsList.length" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="已提交" :value="submittedCount" value-style="color: green" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="未提交" :value="statsList.length - submittedCount" value-style="color: red" />
        </el-col>
      </el-row>
  
      <el-card shadow="never">
        <el-table :data="statsList" border height="500">
          <el-table-column prop="student_name" label="姓名" width="120" />
          <el-table-column prop="student_number" label="学号" width="150" />
          
          <el-table-column label="提交状态" width="120">
            <template #default="scope">
              <el-tag v-if="scope.row.status === 'unsubmitted'" type="danger">未提交</el-tag>
              <el-tag v-else-if="scope.row.status === 'graded'" type="success">已评分</el-tag>
              <el-tag v-else type="primary">已提交</el-tag>
            </template>
          </el-table-column>
  
          <el-table-column label="提交时间" width="180">
            <template #default="scope">
              {{ formatTime(scope.row.submitted_at) }}
            </template>
          </el-table-column>
  
          <el-table-column prop="score" label="成绩" width="100">
             <template #default="scope">
               <span v-if="scope.row.score" style="font-weight: bold; color: #409EFF;">{{ scope.row.score }}</span>
               <span v-else>-</span>
             </template>
          </el-table-column>
  
          <el-table-column label="操作" min-width="150">
            <template #default="scope">
              <el-button 
                v-if="scope.row.status !== 'unsubmitted'" 
                size="small" 
                type="primary" 
                @click="goGrade(scope.row.report_id)"
              >
                {{ scope.row.status === 'graded' ? '修改评分' : '去批改' }}
              </el-button>
              <span v-else style="color: #999; font-size: 12px;">待学生提交</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import http from '../http'
  
  const route = useRoute()
  const router = useRouter()
  const taskId = route.params.taskId
  
  const loading = ref(true)
  const taskInfo = ref({})
  const statsList = ref([])
  
  const submittedCount = computed(() => {
    return statsList.value.filter(s => s.status !== 'unsubmitted').length
  })
  
  const initData = async () => {
    try {
      // 1. 获取任务详情
      const tRes = await http.get(`tasks/${taskId}/`)
      taskInfo.value = tRes.data
  
      // 2. 获取统计名单
      const sRes = await http.get(`tasks/${taskId}/statistics/`)
      statsList.value = sRes.data
    } catch (error) {
      console.error(error)
    } finally {
      loading.value = false
    }
  }
  
  const goGrade = (reportId) => {
    router.push(`/grade/${reportId}`)
  }
  
  const formatTime = (t) => t ? t.substring(5, 16).replace('T', ' ') : '-'
  
  onMounted(() => initData())
  </script>
  
  <style scoped>
  .stats-container { padding: 20px; max-width: 1000px; margin: 0 auto; }
  .header { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
  </style>