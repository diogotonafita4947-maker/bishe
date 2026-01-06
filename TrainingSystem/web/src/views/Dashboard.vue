<template>
  <div class="dashboard-container">
    <div class="nav-header">
      <div class="header-left">
        <h2>🏫 教学管理控制台</h2>
      </div>
      <div class="header-right">
        <span class="user-info">老师：{{ currentUsername }}</span>
        <el-button type="danger" plain @click="handleLogout">退出</el-button>
      </div>
    </div>

    <div class="section-title">
      <h3>📂 我的班级管理</h3>
      <div class="actions">
        <el-button type="success" icon="Position" @click="$router.push('/teacher/create-task')">发布任务</el-button>
        <el-button type="primary" icon="Plus" @click="showCreateDialog = true">新建班级</el-button>
      </div>
    </div>

    <div class="class-grid" v-loading="loading">
      <el-card v-for="cls in classList" :key="cls.id" shadow="hover" class="class-card" @click="enterClass(cls)">
        <template #header>
          <div class="card-header">
            <span class="class-name">{{ cls.name }}</span>
            <el-tag type="success" size="small">{{ cls.code }}</el-tag>
          </div>
        </template>
        <div class="card-content">
          <div class="stat-item">
            <div class="number">{{ cls.student_count }}</div>
            <div class="label">学生人数</div>
          </div>
          <div class="enter-btn">点击进入管理 ></div>
        </div>
      </el-card>

      <el-empty v-if="classList.length === 0" description="暂无班级，请先创建" />
    </div>

    <div class="section-title" style="margin-top: 40px;">
      <h3>📊 全校数据概览</h3>
    </div>
    <div class="charts-row">
      <el-card shadow="hover" class="chart-card">
        <div ref="pieChartRef" class="chart-box"></div>
      </el-card>
      <el-card shadow="hover" class="chart-card">
        <div ref="barChartRef" class="chart-box"></div>
      </el-card>
    </div>

    <el-dialog v-model="showCreateDialog" title="创建新班级" width="400px">
      <el-input v-model="newClassName" placeholder="请输入班级名称（如：24级软件1班）" />
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createClass">确定创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '../http'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const classList = ref([])
const currentUsername = localStorage.getItem('username')

// 弹窗控制
const showCreateDialog = ref(false)
const newClassName = ref('')

// 图表Refs
const pieChartRef = ref(null)
const barChartRef = ref(null)

const handleLogout = () => {
  localStorage.removeItem('access_token')
  router.push('/login')
}

// 1. 获取班级列表
const fetchClasses = async () => {
  loading.value = true
  try {
    const res = await http.get('classes/')
    classList.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 2. 创建班级
const createClass = async () => {
  if (!newClassName.value) return ElMessage.warning('请输入班级名称')
  try {
    await http.post('classes/', { name: newClassName.value })
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    newClassName.value = ''
    fetchClasses() // 刷新列表
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

// 3. 进入班级 (带参数跳转到列表页)
const enterClass = (cls) => {
  // 跳转到 ReportList，并带上 classId 和 className
  router.push({
    path: '/teacher/list',
    query: { classId: cls.id, className: cls.name }
  })
}

// 4. 获取统计图表 (简化版)
const initCharts = async () => {
  try {
    const res = await http.get('dashboard/stats/')
    const data = res.data
    // 简单渲染饼图
    const pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      title: { text: '全校作业状态', left: 'center' },
      tooltip: { trigger: 'item' },
      series: [{ type: 'pie', radius: '50%', data: data.pie_data }]
    })
    // 简单渲染柱状图
    const barChart = echarts.init(barChartRef.value)
    barChart.setOption({
      title: { text: '成绩分布', left: 'center' },
      xAxis: { type: 'category', data: data.bar_data.categories },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: data.bar_data.values }]
    })
  } catch (e) { }
}

onMounted(() => {
  fetchClasses()
  initCharts()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

/* 班级卡片网格 */
.class-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.class-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
}

.class-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.class-name {
  font-weight: bold;
  font-size: 16px;
}

.card-content {
  text-align: center;
  padding: 10px 0;
}

.number {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}

.label {
  color: #909399;
  font-size: 12px;
  margin-bottom: 15px;
}

.enter-btn {
  color: #409EFF;
  font-size: 14px;
  border-top: 1px dashed #eee;
  padding-top: 10px;
}

/* 图表 */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-box {
  height: 300px;
}
</style>