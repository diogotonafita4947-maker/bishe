<template>
  <div class="list-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span style="font-weight: bold; font-size: 18px;">📋 学生实训报告管理</span>
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../http'
import { useRouter } from 'vue-router'

const router = useRouter()
const tableData = ref([])
const loading = ref(false)

const fetchReports = async () => {
  loading.value = true
  try {
    const res = await http.get('reports/')
    tableData.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const goGrade = (id) => {
  router.push(`/grade/${id}`)
}

const getStatusType = (s) => ({ 'draft': 'info', 'submitted': 'primary', 'graded': 'success', 'returned': 'danger' }[s] || 'info')
const getStatusText = (s) => ({ 'draft': '草稿', 'submitted': '待批改', 'graded': '已评分', 'returned': '需重做' }[s] || s)
const formatTime = (t) => t ? t.substring(0, 16).replace('T', ' ') : '-'

onMounted(() => fetchReports())
</script>

<style scoped>
.list-container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>