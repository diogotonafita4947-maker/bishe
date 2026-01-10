<template>
  <div class="editor-layout" v-loading="loading">
    
    <div class="editor-header">
      <div class="header-left">
        <el-button link @click="router.back()" class="nav-btn">
          <el-icon><ArrowLeft /></el-icon> 返回列表
        </el-button>
        <span class="separator">|</span>
        <span class="doc-name">{{ taskTitle }}</span>
      </div>
      
      <div class="header-right">
        <div class="status-box">
          <div v-if="reportStatus === 'graded'" class="status-text graded">
            <el-icon><CircleCheckFilled /></el-icon> 已结束
            <span class="header-score"> | 最终成绩：{{ score }} 分</span>
          </div>

          <div v-else-if="reportStatus === 'returned'" class="status-text returned">
            <el-icon><WarningFilled /></el-icon> 作业被退回 (请修改重交)
            <span class="count-text">第 {{ submitCount }} / {{ maxSubmissions }} 次</span>
          </div>

          <div v-else-if="reportStatus === 'submitted'" class="status-text submitted">
            <el-icon><Clock /></el-icon> 已提交 (等待批改)
            <span class="count-text">第 {{ submitCount }} / {{ maxSubmissions }} 次</span>
          </div>

          <div v-else class="status-text draft">
            <el-icon><Edit /></el-icon> 草稿 (自动保存中)
            <span class="count-text">第 {{ submitCount }} / {{ maxSubmissions }} 次</span>
          </div>
        </div>
        
        <el-button 
          v-if="reportStatus === 'graded'"
          type="info" 
          plain
          disabled
          class="action-btn"
        >
          已完成
        </el-button>

        <el-button 
          v-else
          type="primary" 
          class="action-btn" 
          @click="submitReport" 
          :disabled="!canEdit"
        >
          {{ reportStatus==='returned' ? '重新提交' : '提交作业' }}
        </el-button>
      </div>
    </div>

    <div class="scroll-container">
      <div class="paper-wrapper">
        <div class="a4-sheet">
          <div class="sheet-header">
            <h1 class="main-title">{{ taskTitle }}</h1>
            <div class="sub-title">计算机工程学院 · 实训实验报告</div>
          </div>

          <div class="info-table-container">
            <div class="info-grid">
              <template v-for="(item, index) in reportContent">
                <div v-if="item.type === 'info_row'" :key="'info-'+index" class="info-item">
                  <span class="label">{{ item.label }}：</span>
                  <span class="value">{{ item.value }}</span>
                </div>
              </template>
            </div>
          </div>
          <div class="sheet-divider"></div>

          <div class="sheet-content">
            <div v-for="(item, index) in reportContent" :key="index" class="content-row">
              <template v-if="item.type !== 'info_row'">
                
                <div v-if="item.type === 'teacher_block'" class="static-block">
                  <div class="block-label">{{ item.label }}</div>
                  <div class="block-text">{{ item.value }}</div>
                </div>

                <div v-else-if="item.type === 'header'" class="section-title">{{ item.value }}</div>
                <div v-else-if="item.type === 'paragraph'" class="normal-text">{{ item.value }}</div>

                <div v-else-if="item.type === 'textarea'" class="input-wrapper">
                  <div class="input-label">【 {{ item.label }} 】</div>
                  <div v-if="!canEdit" class="read-only-box" v-html="item.value || '未填写'"></div>
                  <RichEditor
                    v-else
                    v-model="item.value"
                    :report-id="reportId"
                    placeholder="在此输入内容 (支持截图粘贴)"
                    @update:modelValue="handleInput"
                  />
                </div>

                <div v-else-if="item.type === 'upload'" class="upload-wrapper">
                  <div class="section-subtitle">{{ item.label }}</div>
                  <div class="file-list" v-if="fileList.length > 0">
                    <div v-for="file in fileList" :key="file.id" class="file-item">
                      <div class="f-info"><el-icon><Document /></el-icon> {{ file.name }}</div>
                      <el-button v-if="canEdit" link type="danger" size="small" @click="handleFileRemove(file)">删除</el-button>
                    </div>
                  </div>
                  <el-upload
                    v-if="canEdit"
                    action="#"
                    :auto-upload="true"
                    :http-request="handleFileUpload"
                    :show-file-list="false"
                    class="upload-btn-area"
                  >
                    <el-button link type="primary" size="default">+ 上传文件</el-button>
                  </el-upload>
                </div>

              </template>
            </div>
          </div>

          <div v-if="reportStatus === 'graded'" class="grading-box">
            <div class="grading-line"><strong>最终得分：</strong> <span class="score-num">{{ score }}</span> 分</div>
            <div class="grading-line"><strong>教师评语：</strong> <div class="feedback-html" v-html="feedback || '暂无评语'"></div></div>
          </div>

        </div> 
        <div class="bottom-spacer"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Document, CircleCheckFilled, WarningFilled, Clock, Edit } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../http'
import RichEditor from '../components/RichEditor.vue'

const route = useRoute(); const router = useRouter(); const taskId = route.params.id
const loading = ref(true)
const reportId = ref(null); const taskTitle = ref(''); const reportStatus = ref('draft')
const score = ref(0); const feedback = ref('')
const submitCount = ref(0); const maxSubmissions = ref(1)

const studentName = ref(''); const studentNumber = ref(''); const studentClass = ref(''); const teacherName = ref('')
const reportContent = ref([]); const fileList = ref([])

const canEdit = computed(() => {
  return reportStatus.value === 'draft' || reportStatus.value === 'returned'
})

const handleGlobalPaste = async (event) => {
  if (!canEdit.value) return 
}
onMounted(() => { initData(); window.addEventListener('paste', handleGlobalPaste) })
onUnmounted(() => { window.removeEventListener('paste', handleGlobalPaste) })

const initData = async () => {
  try {
    const res = await http.get(`tasks/${taskId}/my_report/`)
    const data = res.data
    reportId.value = data.id; taskTitle.value = data.task_title; reportStatus.value = data.status
    studentName.value = data.student_name; studentNumber.value = data.student_number
    studentClass.value = data.student_class || ''; teacherName.value = data.teacher_name || ''
    score.value = data.score; feedback.value = data.feedback
    submitCount.value = data.submit_count; maxSubmissions.value = data.task_max_submissions

    const isImage = (n) => n.match(/\.(jpeg|jpg|gif|png|webp|bmp)$/i)
    fileList.value = data.attachments_list
      .filter(f => !isImage(f.file))
      .map(f => ({ 
        name: decodeURIComponent(f.file.split('/').pop()), 
        url: f.file, 
        id: f.id 
      }))

    const savedContent = data.content_data || []; const templateStruct = data.template_structure || []
    const filteredTemplate = templateStruct.filter(item => item.key !== 'auto_score' && item.key !== 'auto_feedback')

    let currentStruct = []
    if (!savedContent.length) {
      currentStruct = filteredTemplate.map(item => {
        let val = ''
        if (item.key === 'auto_name') val = studentName.value
        else if (item.key === 'auto_number') val = studentNumber.value
        else if (item.key === 'auto_class') val = studentClass.value
        else if (item.key === 'auto_task') val = taskTitle.value
        else if (item.key === 'auto_teacher') val = teacherName.value
        else if (item.key === 'auto_date') val = new Date().toLocaleDateString()
        if (item.type === 'teacher_block' && item.value) val = item.value
        return { ...item, value: val }
      })
    } else {
      currentStruct = filteredTemplate.map((tplItem, idx) => {
        if (tplItem.type === 'info_row') {
           if (tplItem.key === 'auto_class') return { ...tplItem, value: studentClass.value }
           if (tplItem.key === 'auto_teacher') return { ...tplItem, value: teacherName.value }
           if (tplItem.key === 'auto_name') return { ...tplItem, value: studentName.value }
        }
        if (tplItem.type === 'teacher_block') return tplItem 
        const savedItem = savedContent.find(s => s.label === tplItem.label)
        return { ...tplItem, value: savedItem ? savedItem.value : (tplItem.value || '') }
      })
    }
    reportContent.value = currentStruct
  } catch (e) { ElMessage.error('加载失败') } 
  finally { loading.value = false }
}

const handleInput = () => { if(canEdit.value) setTimeout(() => saveReport('draft', true), 1000) }
const handleFileUpload = async (o) => { if(!canEdit.value) return; const fd = new FormData(); fd.append('file', o.file); await http.post(`reports/${reportId.value}/upload_attachment/`, fd); initData() }
const handleFileRemove = async (f) => { if(!canEdit.value) return; await http.delete(`reports/${reportId.value}/remove_attachment/`, { data: { attachment_id: f.id } }); initData() }

const saveReport = async (statusType, silent=false) => {
  const contentToSave = reportContent.value.map(item => ({ type: item.type, label: item.label, value: item.value }))
  try {
    await http.patch(`reports/${reportId.value}/`, { content_data: contentToSave, status: statusType })
    if (statusType === 'submitted') {
      ElMessage.success('提交成功！')
      initData()
    }
  } catch(e) { if(!silent) ElMessage.error('保存失败') }
}

const submitReport = () => {
  if (submitCount.value >= maxSubmissions.value) return ElMessage.warning(`已达到最大提交次数 (${maxSubmissions.value}次)，无法再次提交`)
  ElMessageBox.confirm('提交后将无法修改，除非老师打回。确认提交？', '提示', { type: 'warning' }).then(() => saveReport('submitted'))
}
</script>

<style scoped>
.editor-layout { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; background-color: #525659; overflow: hidden; }
.editor-header { height: 50px; background: #fff; border-bottom: 1px solid #dcdfe6; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; flex-shrink: 0; z-index: 100; }
.nav-btn { font-size: 14px; color: #333; }
.separator { margin: 0 15px; color: #ddd; }
.doc-name { font-weight: bold; font-size: 14px; color: #333; }
.status-box { display: flex; flex-direction: column; align-items: flex-end; margin-right: 15px; }
.status-text { font-size: 13px; font-weight: bold; display: flex; align-items: center; gap: 5px; }
.status-text.draft { color: #666; }
.status-text.submitted { color: #409EFF; }
.status-text.returned { color: #f56c6c; }
.status-text.graded { color: #67c23a; }
.header-score { font-size: 14px; font-weight: bold; color: #67c23a; margin-left: 5px; }
.count-text { font-size: 10px; color: #999; font-weight: normal; }
.action-btn { border-radius: 2px; }
.scroll-container { flex: 1; overflow-y: auto; width: 100%; background-color: #525659; padding-top: 30px; }
.paper-wrapper { display: flex; flex-direction: column; align-items: center; width: 100%; }
.a4-sheet { width: 210mm; min-height: 297mm; height: auto; background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.15); padding: 25mm 20mm; box-sizing: border-box; margin-bottom: 0; }
.main-title { text-align: center; font-family: 'SimHei', sans-serif; font-size: 24px; color: #000; margin-bottom: 8px; }
.sub-title { text-align: center; font-size: 12px; color: #666; margin-bottom: 30px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 40px; }
.info-item { display: flex; align-items: baseline; font-size: 14px; }
.label { font-weight: bold; min-width: 80px; text-align: right; color: #333; }
.value { flex: 1; border-bottom: 1px solid #000; padding: 0 5px; text-align: center; font-family: 'KaiTi', serif; height: 22px; }
.sheet-divider { height: 2px; background: #000; margin: 20px 0 30px 0; }
.content-row { margin-bottom: 20px; }
.static-block { margin-bottom: 25px; }
.block-label { font-weight: bold; font-size: 15px; margin-bottom: 5px; color: #000; font-family: 'SimHei', sans-serif; }
.block-text { font-size: 14px; line-height: 1.6; color: #333; text-indent: 2em; }
.section-title { font-size: 16px; font-weight: bold; margin-top: 25px; margin-bottom: 10px; color: #000; font-family: 'SimHei', sans-serif; }
.normal-text { font-size: 14px; line-height: 1.6; margin-bottom: 10px; text-indent: 2em; color: #333; }
.input-wrapper { margin-bottom: 15px; }
.input-label { font-weight: bold; font-size: 15px; margin-bottom: 5px; color: #000; margin-top: 20px; }
.read-only-box { min-height: 100px; padding: 10px; border: 1px solid #eee; background: #fdfdfd; color: #666; }
.read-only-box :deep(img) { max-width: 100%; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.section-subtitle { font-size: 14px; font-weight: bold; margin-top: 30px; margin-bottom: 10px; }
.file-list { margin-bottom: 10px; }
.file-item { display: flex; justify-content: space-between; font-size: 13px; color: #333; border-bottom: 1px solid #eee; padding: 5px 0; }
.f-info { display: flex; align-items: center; gap: 5px; }
.upload-btn-area { margin-top: 5px; }
.grading-box { margin-top: 50px; border-top: 2px solid #000; padding-top: 20px; }
.grading-line { margin-bottom: 10px; font-size: 15px; }
.score-num { font-size: 20px; font-weight: bold; color: #d9001b; }
.bottom-spacer { height: 100px; width: 100%; flex-shrink: 0; }
</style>