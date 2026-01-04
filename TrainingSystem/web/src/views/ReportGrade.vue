<template>
  <div class="grade-container" v-loading="loading">
    <el-page-header @back="goBack" content="实训作业阅卷" style="margin-bottom: 20px;">
      <template #extra>
        <el-tag :type="statusTagType" size="large" effect="dark">{{ statusText }}</el-tag>
      </template>
    </el-page-header>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span style="font-weight: bold; font-size: 16px;">
                <el-icon>
                  <Document />
                </el-icon> {{ studentName }} 的提交内容
              </span>
            </div>
          </template>

          <div class="paper-content">
            <div v-if="templateStructure.length === 0" class="empty-tip">
              暂无内容或加载中...
            </div>

            <div v-for="(item, index) in templateStructure" :key="index" class="form-item">
              <h3 v-if="item.type === 'header'" class="section-title">{{ item.value }}</h3>

              <div v-if="['input', 'textarea'].includes(item.type)" class="qa-box">
                <div class="question-label">
                  <span class="index-num">{{ index + 1 }}.</span> {{ item.label }}
                </div>
                <div class="answer-box">
                  {{ studentData[item.label] || '（该生未填写此项）' }}
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="grade-panel">
          <template #header>
            <span style="font-weight: bold;">📝 批阅操作</span>
          </template>

          <el-form label-position="top">
            <el-form-item label="给予分数 (0-100)">
              <el-input-number v-model="gradeForm.score" :min="0" :max="100" style="width: 100%"
                :disabled="isReadOnly" />
            </el-form-item>

            <el-form-item label="教师评语">
              <el-input v-model="gradeForm.teacher_comment" type="textarea" :rows="6" placeholder="请输入评语，指出不足之处..."
                :disabled="isReadOnly" />
            </el-form-item>

            <div class="action-buttons" v-if="!isReadOnly">
              <el-button type="success" style="flex: 1" @click="submitGrade('graded')">
                <el-icon><Select /></el-icon> 通过并归档
              </el-button>

              <el-button type="danger" style="flex: 1" @click="submitGrade('returned')">
                <el-icon>
                  <CloseBold />
                </el-icon> 退回重写
              </el-button>
            </div>

            <div v-else class="read-only-tip">
              <el-alert title="该报告已归档，不可修改" type="info" show-icon :closable="false" />
            </div>

            <p class="tip-text" v-if="!isReadOnly">
              <span style="color: #67C23A;">● 通过</span>：学生不可再改，成绩生效。<br>
              <span style="color: #F56C6C;">● 退回</span>：状态变回草稿，学生需重交。
            </p>

          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '../http'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Select, CloseBold } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const reportId = route.params.id

const loading = ref(true)
const studentName = ref('')
const reportStatus = ref('')
const templateStructure = ref([])
const studentData = ref({})

const gradeForm = ref({
  score: 80,
  teacher_comment: ''
})

// 1. 初始化：拉取报告详情
const initGrade = async () => {
  try {
    // 获取学生报告内容
    const reportRes = await http.get(`reports/${reportId}/`)
    const report = reportRes.data

    studentName.value = report.student_name
    reportStatus.value = report.status
    studentData.value = report.content_data || {} // 防止为空报错

    // 回显已有分数和评语
    if (report.score) gradeForm.value.score = report.score
    if (report.teacher_comment) gradeForm.value.teacher_comment = report.teacher_comment

    // 获取题目结构（为了渲染出漂亮的题目列表）
    // 注意：这里需要你后端 serializer 包含 task 字段，或者我们在报告里存了 structure
    // 如果你后端没返回 template 结构，这里可能只会显示答案。
    // 为了稳妥，我们先尝试拉取 task 信息
    if (report.task) {
      const taskRes = await http.get(`tasks/${report.task}/`)
      const templateRes = await http.get(`templates/${taskRes.data.template}/`)
      templateStructure.value = templateRes.data.content_structure
    }

  } catch (error) {
    console.error(error)
    ElMessage.error('加载作业失败，请检查网络')
  } finally {
    loading.value = false
  }
}

// 2. 提交评分 (核心功能)
const submitGrade = async (targetStatus) => {
  // 二次确认，防止手滑
  const actionText = targetStatus === 'graded' ? '通过并归档' : '退回给学生'

  try {
    await ElMessageBox.confirm(
      `确定要将这份作业 ${actionText} 吗？`,
      '操作确认',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )

    // 发送请求
    const payload = {
      score: gradeForm.value.score,
      teacher_comment: gradeForm.value.teacher_comment,
      status: targetStatus // ★ 核心：改变状态
    }

    await http.patch(`reports/${reportId}/`, payload)

    ElMessage.success(`操作成功！作业已${actionText}`)
    router.back() // 成功后返回列表页

  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('提交失败，请检查后端接口')
    }
  }
}

const goBack = () => router.back()

// 辅助逻辑
const isReadOnly = computed(() => reportStatus.value === 'graded') // 已评分则锁定
const statusText = computed(() => {
  const map = { 'submitted': '待批改', 'graded': '已归档', 'returned': '已退回', 'draft': '草稿中' }
  return map[reportStatus.value] || '未知状态'
})
const statusTagType = computed(() => {
  return reportStatus.value === 'graded' ? 'success' : (reportStatus.value === 'returned' ? 'danger' : 'primary')
})

onMounted(() => {
  initGrade()
})
</script>

<style scoped>
.grade-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  margin-top: 25px;
  margin-bottom: 15px;
  padding-left: 10px;
  border-left: 4px solid #409EFF;
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 0 4px 4px 0;
}

.qa-box {
  margin-bottom: 20px;
}

.question-label {
  font-weight: bold;
  margin-bottom: 8px;
  color: #303133;
}

.index-num {
  color: #909399;
  margin-right: 5px;
}

.answer-box {
  background: #fafafa;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  min-height: 40px;
  white-space: pre-wrap;
  color: #606266;
  line-height: 1.6;
}

.grade-panel {
  position: sticky;
  top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.tip-text {
  font-size: 12px;
  color: #909399;
  margin-top: 15px;
  line-height: 1.8;
  background: #f4f4f5;
  padding: 10px;
  border-radius: 4px;
}

.empty-tip {
  text-align: center;
  color: #999;
  padding: 50px;
}
</style>