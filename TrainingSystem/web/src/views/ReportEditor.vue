<template>
  <div class="editor-container" v-loading="loading">

    <div class="status-bar" v-if="reportStatus">

      <el-alert v-if="reportStatus === 'graded'" type="success" :closable="false" show-icon>
        <template #title>
          <span style="font-size: 16px; font-weight: bold;">🎉 恭喜！作业已评阅归档</span>
        </template>
        <div class="grade-result">
          <span class="score-badge">{{ reportScore }} 分</span>
          <p class="teacher-comment">🧑‍🏫 老师评语：{{ teacherComment || '（老师没有留下文字评语）' }}</p>
        </div>
      </el-alert>

      <el-alert v-if="reportStatus === 'returned'" type="error" :closable="false" show-icon>
        <template #title>
          <span style="font-size: 16px; font-weight: bold;">⚠️ 作业被退回，请修改后重新提交</span>
        </template>
        <p class="teacher-comment">🧑‍🏫 退回原因：{{ teacherComment }}</p>
      </el-alert>

      <el-alert v-if="reportStatus === 'submitted'" type="warning" :closable="false" show-icon>
        <template #title>
          <span style="font-weight: bold;">⏳ 作业已提交，等待老师批阅中...</span>
        </template>
        <p>在此期间无法修改内容。</p>
      </el-alert>
    </div>

    <div class="page-header">
      <h2>{{ taskTitle }}</h2>
      <el-button @click="router.back()">返回列表</el-button>
    </div>

    <el-card shadow="never" class="editor-card">
      <div v-for="(item, index) in contentStructure" :key="index" class="form-item">

        <h3 v-if="item.type === 'header'" class="section-title">{{ item.value }}</h3>

        <div v-if="item.type === 'input'" class="qa-box">
          <label>{{ item.label }}</label>
          <el-input v-model="formData[item.label]" :placeholder="item.placeholder" :disabled="isReadOnly" />
        </div>

        <div v-if="item.type === 'textarea'" class="qa-box">
          <label>{{ item.label }}</label>
          <el-input v-model="formData[item.label]" type="textarea" :rows="5" :placeholder="item.placeholder"
            :disabled="isReadOnly" />
        </div>
      </div>
    </el-card>

    <div class="footer-actions" v-if="!isReadOnly">
      <el-button @click="saveDraft">保存草稿</el-button>
      <el-button type="primary" size="large" @click="submitReport">
        {{ reportStatus === 'returned' ? '修改完成，重新提交' : '提交作业' }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '../http'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const taskId = route.params.taskId

const loading = ref(true)
const taskTitle = ref('')
const contentStructure = ref([]) // 模板结构
const formData = ref({})         // 学生填写的数据
const reportId = ref(null)       // 报告ID
const reportStatus = ref('draft') // 状态：draft, submitted, graded, returned
const reportScore = ref(0)
const teacherComment = ref('')

// 计算属性：是否只读
// 只有 'draft' (草稿) 和 'returned' (被退回) 状态下可以编辑
const isReadOnly = computed(() => {
  return ['submitted', 'graded'].includes(reportStatus.value)
})

// 1. 初始化数据
const initData = async () => {
  try {
    // A. 先获取任务详情，拿到模板结构
    const taskRes = await http.get(`tasks/${taskId}/`)
    taskTitle.value = taskRes.data.title
    const templateId = taskRes.data.template

    const tempRes = await http.get(`templates/${templateId}/`)
    contentStructure.value = tempRes.data.content_structure

    // B. 检查该学生是否已经在这个任务下创建过报告
    // (注意：这里假设你的后端 ViewSet 已经过滤了 request.user)
    const reportRes = await http.get(`reports/?task=${taskId}`)

    if (reportRes.data.length > 0) {
      // 如果有旧数据，就回显
      const existReport = reportRes.data[0]
      reportId.value = existReport.id
      formData.value = existReport.content_data || {}
      reportStatus.value = existReport.status
      reportScore.value = existReport.score
      teacherComment.value = existReport.teacher_comment
    } else {
      // 第一次做，初始化为空对象
      reportStatus.value = 'draft'
      formData.value = {}
    }

  } catch (error) {
    console.error(error)
    ElMessage.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

// 2. 保存草稿
const saveDraft = async () => {
  try {
    const payload = {
      task: taskId,
      content_data: formData.value,
      status: 'draft' // 强制设为草稿
    }

    if (reportId.value) {
      await http.patch(`reports/${reportId.value}/`, payload)
    } else {
      const res = await http.post('reports/', payload)
      reportId.value = res.data.id
    }
    ElMessage.success('草稿保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 3. 提交作业
const submitReport = async () => {
  try {
    await ElMessageBox.confirm(
      '提交后将无法修改，直到老师批阅或退回。确定提交吗？',
      '提交确认',
      { type: 'warning' }
    )

    const payload = {
      task: taskId,
      content_data: formData.value,
      status: 'submitted' // ★ 变为已提交状态
    }

    if (reportId.value) {
      await http.patch(`reports/${reportId.value}/`, payload)
    } else {
      const res = await http.post('reports/', payload)
      reportId.value = res.data.id
    }

    ElMessage.success('作业提交成功！')
    reportStatus.value = 'submitted' // 前端立刻更新状态，锁定界面
    router.back() // 返回列表

  } catch (error) {
    if (error !== 'cancel') ElMessage.error('提交失败')
  }
}

onMounted(() => {
  initData()
})
</script>

<style scoped>
.editor-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.status-bar {
  margin-bottom: 20px;
}

.grade-result {
  margin-top: 10px;
}

.score-badge {
  font-size: 24px;
  color: #67C23A;
  font-weight: bold;
  margin-right: 15px;
}

.teacher-comment {
  color: #606266;
  margin-top: 5px;
  font-style: italic;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  margin-top: 30px;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
  background: #f0f9eb;
  padding: 10px;
}

.qa-box {
  margin-bottom: 20px;
}

.qa-box label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

.footer-actions {
  margin-top: 40px;
  text-align: center;
  border-top: 1px solid #eee;
  padding-top: 20px;
}
</style>