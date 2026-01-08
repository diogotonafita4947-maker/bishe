<template>
  <div class="grade-container" v-loading="loading">
    
    <div class="header">
      <div class="left">
        <el-button @click="router.back()" link>
          <el-icon><ArrowLeft /></el-icon> 返回列表
        </el-button>
        <span class="title">批阅报告：{{ studentName }}</span>
      </div>
      <div class="right">
        <el-tag v-if="reportStatus === 'graded'" type="success">已评分</el-tag>
        <el-tag v-else type="warning">待批阅</el-tag>
      </div>
    </div>

    <div class="main-content">
      <div class="split-layout">
        
        <div class="paper-panel">
          <div class="paper-scroll">
            <div class="a4-paper">
              <div class="paper-header">
                <h1>实 训 (验) 报 告</h1>
              </div>

              <div class="report-table">
                <div class="rt-row">
                  <div class="rt-label">学生姓名</div>
                  <div class="rt-content">{{ studentName }}</div>
                  <div class="rt-label">学号</div>
                  <div class="rt-content">{{ studentId }}</div>
                </div>
                <div class="rt-row">
                  <div class="rt-label">实训名称</div>
                  <div class="rt-content span-3">{{ taskTitle }}</div>
                </div>

                <div v-for="(value, key) in studentContent" :key="key" class="rt-block input-block">
                  <div class="rt-block-label" :class="{ 'vertical-text': key.length > 4 }">
                    {{ key }}
                  </div>
                  <div class="rt-block-content">
                    {{ value || '（学生未填写）' }}
                  </div>
                </div>

                <div class="rt-block" style="min-height: 150px;">
                   <div class="rt-block-label">附件与截图</div>
                   <div class="rt-block-content attachment-container">
                      
                      <div v-if="attachmentList.length > 0">
                        <div v-for="(att, index) in attachmentList" :key="att.id" class="attachment-item">
                          
                          <div v-if="isImage(att.file)" class="full-width-image-box">
                            <div class="att-header">
                              <el-icon><Picture /></el-icon> 
                              <span class="att-name">截图 {{ index + 1 }}</span>
                            </div>
                            <el-image 
                              :src="att.file" 
                              fit="contain" 
                              class="full-image"
                              :preview-src-list="[att.file]" 
                              :initial-index="0"
                              lazy
                            />
                          </div>

                          <div v-else class="file-card-row" @click="handlePreview(att)">
                            <div class="file-icon">
                              <el-icon :size="24" v-if="isPdf(att.file)" color="#F56C6C"><Document /></el-icon>
                              <el-icon :size="24" v-else color="#409EFF"><Files /></el-icon>
                            </div>
                            <div class="file-info">
                              <div class="fname">{{ decodeName(att.file) }}</div>
                              <div class="ftip">{{ isPdf(att.file) ? 'PDF文档 - 点击预览' : '普通文件 - 点击下载' }}</div>
                            </div>
                            <el-button link type="primary">查看</el-button>
                          </div>

                        </div>
                      </div>

                      <div v-else class="empty-tip">无附件提交</div>
                   </div>
                </div>

                <div class="rt-block" v-if="reportStatus === 'graded'">
                  <div class="rt-block-label">教师评语</div>
                  <div class="rt-block-content" style="color: #E6A23C;">
                     <p><strong>得分：{{ form.score }}</strong></p>
                     <p>{{ form.teacher_comment }}</p>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>

        <div class="grade-panel">
          <el-card shadow="never" class="grade-card">
            <template #header>
              <div class="card-header"><span>📝 评分与反馈</span></div>
            </template>
            
            <el-form :model="form" label-position="top">
              <el-form-item label="最终得分 (0-100)">
                <el-input-number v-model="form.score" :min="0" :max="100" style="width: 100%;" size="large" />
              </el-form-item>
              
              <el-form-item label="评语与建议">
                <el-input 
                  v-model="form.teacher_comment" 
                  type="textarea" 
                  :rows="8" 
                  placeholder="请输入评语..."
                />
              </el-form-item>

              <el-form-item label="AI 辅助分析">
                <div class="ai-box">{{ aiSuggestion || '暂无 AI 分析数据' }}</div>
              </el-form-item>

              <div class="btn-area">
                <el-button type="primary" size="large" style="width: 100%;" @click="submitGrade" :loading="submitting">
                  提交评分
                </el-button>
              </div>
            </el-form>
          </el-card>
        </div>

      </div>
    </div>

    <el-dialog 
      v-model="previewVisible" 
      :title="previewTitle" 
      width="80%" 
      top="5vh"
      class="preview-dialog"
      destroy-on-close
    >
      <div class="preview-body">
        <iframe v-if="previewType === 'pdf'" :src="previewUrl" class="full-iframe"></iframe>
        <div v-else class="download-tip">
          <el-icon :size="60" color="#909399"><Warning /></el-icon>
          <p>该文件格式不支持在线预览</p>
          <a :href="previewUrl" target="_blank">
            <el-button type="primary">下载文件到本地查看</el-button>
          </a>
        </div>
      </div>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '../http'
import { ArrowLeft, Document, Files, Picture, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const reportId = route.params.id

const loading = ref(true)
const submitting = ref(false)

const studentName = ref('')
const studentId = ref('')
const taskTitle = ref('')
const reportStatus = ref('')
const studentContent = ref({})
const attachmentList = ref([])
const aiSuggestion = ref('')

const form = ref({ score: 80, teacher_comment: '' })

// 预览状态 (仅用于PDF或非图片文件)
const previewVisible = ref(false)
const previewUrl = ref('')
const previewTitle = ref('')
const previewType = ref('other')

const init = async () => {
  try {
    const res = await http.get(`reports/${reportId}/`)
    const data = res.data
    
    studentName.value = data.student_name
    studentId.value = data.student_number || '暂无学号'
    taskTitle.value = data.task_title
    reportStatus.value = data.status
    studentContent.value = data.content_data || {}
    aiSuggestion.value = data.ai_suggestion
    
    if (data.attachments_list && data.attachments_list.length > 0) {
      attachmentList.value = data.attachments_list
    } else if (data.attachment) {
      attachmentList.value = [{ id: 'old', file: data.attachment }]
    }

    if (data.status === 'graded') {
      form.value.score = data.score
      form.value.teacher_comment = data.teacher_comment
    }
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const submitGrade = async () => {
  submitting.value = true
  try {
    await http.patch(`reports/${reportId}/`, {
      score: form.value.score,
      teacher_comment: form.value.teacher_comment,
      status: 'graded'
    })
    ElMessage.success('评分提交成功')
    reportStatus.value = 'graded'
  } catch (e) { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}

const decodeName = (url) => {
  try { return decodeURIComponent(url.split('/').pop()) } catch (e) { return '未知文件' }
}

const isImage = (url) => /\.(jpg|jpeg|png|gif|webp)$/i.test(url)
const isPdf = (url) => /\.pdf$/i.test(url)

const handlePreview = (att) => {
  // 图片不需要进这里，直接页面展示
  previewUrl.value = att.file
  previewTitle.value = decodeName(att.file)
  
  if (isPdf(att.file)) {
    previewType.value = 'pdf'
    previewVisible.value = true
  } else {
    window.open(att.file, '_blank')
  }
}

onMounted(init)
</script>

<style scoped>
/* 保持整体布局一致 */
.grade-container { height: 100vh; display: flex; flex-direction: column; background: #eff1f3; }
.header { height: 56px; background: #fff; border-bottom: 1px solid #dcdfe6; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; }
.title { font-weight: bold; margin-left: 10px; font-size: 16px; }

.main-content { flex: 1; overflow: hidden; }
.split-layout { display: flex; height: 100%; }

.paper-panel { flex: 1; overflow-y: auto; background: #eff1f3; display: flex; justify-content: center; padding: 30px 0; }
.a4-paper { width: 210mm; min-height: 297mm; background: #fff; padding: 20mm; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 50px; }
.paper-header h1 { text-align: center; font-size: 26px; font-family: "SimSun", serif; margin-bottom: 30px; }

.grade-panel { width: 350px; background: #fff; border-left: 1px solid #dcdfe6; padding: 20px; overflow-y: auto; }
.grade-card { border: none; }
.ai-box { background: #f4f4f5; padding: 12px; border-radius: 4px; color: #606266; font-size: 13px; line-height: 1.5; min-height: 80px; }
.btn-area { margin-top: 30px; }

/* 表格样式 */
.report-table { border: 1px solid #333; display: flex; flex-direction: column; font-family: "SimSun", serif; font-size: 15px; color: #000; }
.rt-row, .rt-block { display: flex; border-bottom: 1px solid #333; }
.rt-row:last-child, .rt-block:last-child { border-bottom: none; }
.rt-label, .rt-block-label { background: #f7f7f7; font-weight: bold; border-right: 1px solid #333; display: flex; align-items: center; justify-content: center; text-align: center; }
.rt-label { width: 100px; padding: 10px; }
.rt-block-label { width: 60px; padding: 20px 5px; writing-mode: vertical-lr; letter-spacing: 4px; }
.rt-content, .rt-block-content { flex: 1; padding: 10px 15px; border-right: 1px solid #333; white-space: pre-wrap; line-height: 1.6; }
.rt-content:last-child { border-right: none; }
.rt-content.span-3 { flex: 3; }

/* ★★★ 附件大图样式 ★★★ */
.attachment-container { display: flex; flex-direction: column; gap: 20px; padding: 20px !important; }

.attachment-item { width: 100%; }

/* 图片盒子 */
.full-width-image-box {
  width: 100%;
  border: 1px solid #eee;
  border-radius: 4px;
  overflow: hidden;
  background: #fafafa;
}
.att-header {
  padding: 8px 12px;
  background: #f2f2f2;
  border-bottom: 1px solid #eee;
  font-size: 13px;
  color: #666;
  display: flex; align-items: center; font-family: sans-serif;
}
.att-name { margin-left: 5px; font-weight: bold; }

/* 关键：图片样式 */
.full-image {
  display: block;
  width: 100%; /* 撑满宽度 */
  height: auto; /* 高度自适应 */
  min-height: 200px; /* 最小高度，防止加载时塌陷 */
  background: #fff;
}

/* 非图片文件卡片 */
.file-card-row {
  display: flex; align-items: center; padding: 12px;
  background: #fdfdfd; border: 1px solid #dcdfe6; border-radius: 4px;
  cursor: pointer; transition: all 0.2s;
}
.file-card-row:hover { border-color: #409EFF; background: #ecf5ff; }
.file-icon { margin-right: 12px; display: flex; align-items: center; }
.file-info { flex: 1; overflow: hidden; }
.fname { font-size: 14px; font-weight: bold; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: sans-serif; }
.ftip { font-size: 12px; color: #999; margin-top: 4px; font-family: sans-serif; }
.empty-tip { color: #999; font-style: italic; }

/* 预览弹窗 */
.preview-body { height: 75vh; display: flex; align-items: center; justify-content: center; background: #000; overflow: hidden; }
.full-iframe { width: 100%; height: 100%; border: none; background: #fff; }
.download-tip { text-align: center; color: #fff; }
</style>