<template>
  <div class="study-layout">
    
    <div class="sidebar">
      <div class="sidebar-header">
        <div class="back-link" @click="router.push('/student/dashboard')">
          <el-icon><ArrowLeft /></el-icon> 返回首页
        </div>
        <h3 class="course-name">{{ className || '实训课程' }}</h3>
        <div class="progress-info">共 {{ taskList.length }} 个任务</div>
      </div>
      <div class="task-list-scroll">
        <div 
          v-for="(task, index) in taskList" 
          :key="task.id" 
          class="nav-item"
          :class="{ 'active': currentTaskId === task.id }"
          @click="selectTask(task)"
        >
          <div class="nav-icon">
            <span class="index-num" v-if="currentTaskId !== task.id">{{ index + 1 }}</span>
            <el-icon v-else><CaretRight /></el-icon>
          </div>
          <div class="nav-info">
            <div class="nav-title">{{ task.title }}</div>
            <div class="nav-status">
              <span class="status-dot" :class="getTaskStatusClass(task)"></span>
              <span class="status-text">{{ getTaskStatusText(task) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="sidebar-footer">
        <div class="user-row" @click="router.push('/profile')">
          <el-avatar :size="30" style="background:#409EFF">{{ user.username ? user.username[0] : '我' }}</el-avatar>
          <span class="username">{{ user.username }}</span>
        </div>
      </div>
    </div>

    <div class="main-content">
      <div v-if="!currentTaskId" class="welcome-banner">
        <div class="banner-inner">
          <el-icon :size="80" color="#fff" style="opacity:0.8"><Collection /></el-icon>
          <h1>请在左侧选择实训任务</h1>
        </div>
      </div>

      <div v-else class="workspace-wrapper" v-loading="detailLoading">
        <div class="toolbar">
          <h2 class="current-task-title">{{ currentTaskTitle }}</h2>
          <div class="actions">
             <el-tag v-if="reportStatus === 'submitted'" type="success">已提交</el-tag>
             <el-tag v-else type="warning">编写中</el-tag>
             <el-button v-if="!isReadOnly" type="primary" @click="submitReport" :loading="saving">提交报告</el-button>
             <el-button v-if="!isReadOnly" @click="saveDraft">保存草稿</el-button>
          </div>
        </div>

        <div class="paper-scroll-area">
          <div class="a4-paper">
            <div class="paper-header">
              <h1>实 训 (验) 报 告</h1>
            </div>

            <div class="report-table">
              <div class="rt-row">
                <div class="rt-label">姓 名</div>
                <div class="rt-content">{{ user.username }}</div>
                <div class="rt-label">专业班级</div>
                <div class="rt-content">{{ className }}</div>
                <div class="rt-label">学 号</div>
                <div class="rt-content">{{ user.student_id || '暂无' }}</div>
              </div>
              <div class="rt-row">
                <div class="rt-label">实训名称</div>
                <div class="rt-content span-3">{{ currentTaskTitle }}</div>
                <div class="rt-label">指导教师</div>
                <div class="rt-content">{{ currentTeacher }}</div>
              </div>
              <div class="rt-row">
                <div class="rt-label">实训地点</div>
                <div class="rt-content span-3">{{ taskDetails.location || '线上' }}</div>
                <div class="rt-label">日期时间</div>
                <div class="rt-content">{{ formatTime(new Date()) }}</div>
              </div>

              <div class="rt-block">
                <div class="rt-block-label">实训(验)目的</div>
                <div class="rt-block-content readonly-text">{{ taskDetails.purpose || '暂无内容' }}</div>
              </div>
              <div class="rt-block">
                <div class="rt-block-label">仪器与用具</div>
                <div class="rt-block-content readonly-text">{{ taskDetails.instruments || '暂无内容' }}</div>
              </div>
              <div class="rt-block">
                <div class="rt-block-label">任务及要求</div>
                <div class="rt-block-content readonly-text">{{ taskDetails.requirements || '暂无内容' }}</div>
              </div>
              <div class="rt-block" v-if="taskDetails.principle">
                <div class="rt-block-label">实训(验)原理</div>
                <div class="rt-block-content readonly-text">{{ taskDetails.principle }}</div>
              </div>

              <div class="rt-block input-block">
                <div class="rt-block-label">实训(验)步骤<br>或过程</div>
                <div class="rt-block-content">
                  <el-input 
                    type="textarea" 
                    :autosize="{ minRows: 15 }" 
                    v-model="studentSteps" 
                    :disabled="isReadOnly"
                    placeholder="在此处输入步骤。提示：可直接 Ctrl+V 粘贴截图，系统会自动识别并添加到下方附件列表。"
                    class="paper-input"
                    @paste="handlePaste"
                    style="margin-bottom: 20px;"
                  />

                  <div class="upload-zone" v-if="!isReadOnly">
                    <el-divider content-position="left" style="margin: 10px 0;">📎 附件与截图 (无限上传)</el-divider>
                    
                    <div v-if="serverAttachments.length > 0" class="file-grid">
                      <div v-for="att in serverAttachments" :key="att.id" class="file-item">
                        <el-icon><Document /></el-icon>
                        <a :href="att.file" target="_blank" class="file-link">
                          {{ decodeURIComponent(att.file.split('/').pop()) }}
                        </a>
                        <el-icon 
                          v-if="!isReadOnly" 
                          class="delete-icon" 
                          @click="deleteServerFile(att.id)"
                        ><Close /></el-icon>
                      </div>
                    </div>

                    <div v-if="pendingFiles.length > 0" class="file-grid pending">
                      <div v-for="(file, index) in pendingFiles" :key="index" class="file-item pending-item">
                        <el-tag size="small" type="warning" style="margin-right:5px">待保存</el-tag>
                        <span>{{ file.name }}</span>
                        <el-icon class="delete-icon" @click="removePendingFile(index)"><Close /></el-icon>
                      </div>
                    </div>

                    <el-upload
                      class="drag-uploader"
                      drag
                      action="#"
                      :auto-upload="false"
                      :on-change="handleFileChange"
                      multiple
                      :show-file-list="false"
                    >
                      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                      <div class="el-upload__text">
                        将文件拖到此处，粘贴截图，或 <em>点击上传</em>
                      </div>
                    </el-upload>
                  </div>
                </div>
              </div>

              <div class="rt-block input-block">
                <div class="rt-block-label">结论与心得</div>
                <div class="rt-block-content">
                  <el-input 
                    type="textarea" 
                    :autosize="{ minRows: 8 }" 
                    v-model="studentConclusion" 
                    :disabled="isReadOnly"
                    placeholder="请输入结论与心得..."
                    class="paper-input"
                  />
                </div>
              </div>
              
              <div class="rt-block" v-if="reportStatus === 'graded'">
                <div class="rt-block-label">教师评语</div>
                <div class="rt-block-content readonly-text" style="color: #E6A23C;">
                   <p><strong>评分：{{ reportScore }}</strong></p>
                   <p>{{ teacherComment || '暂无评语' }}</p>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import http from '../http'
import { useRouter } from 'vue-router'
import { ArrowLeft, CaretRight, Collection, User, UploadFilled, Document, Close } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const user = ref({})
const listLoading = ref(false)
const detailLoading = ref(false)
const taskList = ref([])
const currentTaskId = ref(null)
const className = ref('')
const currentTeacher = ref('')

const currentTaskTitle = ref('')
const taskDetails = ref({}) 
const formData = ref({}) 
const studentSteps = ref('') 
const studentConclusion = ref('') 

const reportId = ref(null)
const reportStatus = ref('draft')
const reportScore = ref(0)
const teacherComment = ref('')

// 文件状态
const serverAttachments = ref([]) // 已保存的文件
const pendingFiles = ref([])      // 待上传的文件
const saving = ref(false)

const isReadOnly = computed(() => ['submitted', 'graded'].includes(reportStatus.value))

const init = async () => {
  listLoading.value = true
  try {
    const uRes = await http.get('users/me/')
    user.value = uRes.data
    className.value = uRes.data.class_group_name
    
    const tRes = await http.get('tasks/')
    taskList.value = tRes.data
  } catch (e) { console.error(e) }
  finally { listLoading.value = false }
}

const selectTask = async (task) => {
  currentTaskId.value = task.id
  currentTaskTitle.value = task.title
  currentTeacher.value = task.teacher_name
  taskDetails.value = task.task_details || {} 
  
  detailLoading.value = true
  formData.value = {}
  studentSteps.value = ''
  studentConclusion.value = ''
  reportId.value = null
  reportStatus.value = 'draft'
  
  serverAttachments.value = []
  pendingFiles.value = []
  
  try {
    const repRes = await http.get(`reports/?task=${task.id}`)
    if (repRes.data.length > 0) {
      const r = repRes.data[0]
      reportId.value = r.id
      formData.value = r.content_data || {}
      reportStatus.value = r.status
      reportScore.value = r.score
      teacherComment.value = r.teacher_comment
      
      // 加载附件
      if (r.attachments_list) {
        serverAttachments.value = r.attachments_list
      } else if (r.attachment) {
        // 兼容旧数据
        serverAttachments.value = [{ id: 'old', file: r.attachment }]
      }
      
      const keys = Object.keys(formData.value)
      keys.forEach(k => {
        if(k.includes('步骤') || k.includes('过程')) studentSteps.value = formData.value[k]
        if(k.includes('心得') || k.includes('结论')) studentConclusion.value = formData.value[k]
      })
    }
  } catch (e) { console.error(e) }
  finally { detailLoading.value = false }
}

// 粘贴处理
const handlePaste = (event) => {
  if (isReadOnly.value) return
  const items = (event.clipboardData || event.originalEvent.clipboardData).items
  for (let index in items) {
    const item = items[index]
    if (item.kind === 'file' && item.type.indexOf('image') !== -1) {
      const blob = item.getAsFile()
      const file = new File([blob], `screenshot_${Date.now()}.png`, { type: 'image/png' })
      pendingFiles.value.push(file)
      ElMessage.success('已检测到截图，添加到待上传列表')
    }
  }
}

const handleFileChange = (uploadFile) => {
  pendingFiles.value.push(uploadFile.raw)
}

const removePendingFile = (index) => {
  pendingFiles.value.splice(index, 1)
}

const deleteServerFile = async (attId) => {
  if (attId === 'old') {
    ElMessage.warning('旧版数据不支持删除')
    return
  }
  try {
    await ElMessageBox.confirm('确定删除该附件吗？', '提示', { type: 'warning' })
    await http.delete(`reports/${reportId.value}/remove_attachment/?attachment_id=${attId}`)
    serverAttachments.value = serverAttachments.value.filter(f => f.id !== attId)
    ElMessage.success('已删除')
  } catch(e) {}
}

const sendData = async (status) => {
  formData.value['实验步骤/过程内容'] = studentSteps.value
  formData.value['结论与心得'] = studentConclusion.value

  const data = new FormData()
  data.append('task', currentTaskId.value)
  data.append('content_data', JSON.stringify(formData.value))
  data.append('status', status)
  
  // 批量添加新文件
  pendingFiles.value.forEach(file => {
    data.append('new_attachments', file)
  })
  
  const config = { headers: { 'Content-Type': 'multipart/form-data' } }
  
  if (reportId.value) {
    const res = await http.patch(`reports/${reportId.value}/`, data, config)
    pendingFiles.value = []
    if (res.data.attachments_list) serverAttachments.value = res.data.attachments_list
  } else {
    const res = await http.post('reports/', data, config)
    reportId.value = res.data.id
    pendingFiles.value = []
    if (res.data.attachments_list) serverAttachments.value = res.data.attachments_list
  }
}

const saveDraft = async () => {
  saving.value = true
  try { await sendData('draft'); ElMessage.success('已保存') } 
  catch(e) { ElMessage.error('保存失败') }
  finally { saving.value = false }
}

const submitReport = async () => {
  try {
    await ElMessageBox.confirm('确定提交吗？', '提示', { type: 'warning' })
    saving.value = true
    await sendData('submitted')
    reportStatus.value = 'submitted'
    ElMessage.success('提交成功！')
  } catch(e) {}
  finally { saving.value = false }
}

const getTaskStatusText = (t) => new Date() > new Date(t.end_time) ? '已截止' : '进行中'
const getTaskStatusClass = (t) => new Date() > new Date(t.end_time) ? 'gray' : 'green'
const formatTime = (d) => new Date(d).toLocaleDateString()

onMounted(init)
</script>

<style scoped>
/* 整体布局 */
.study-layout { display: flex; height: 100vh; width: 100vw; background: #eff1f3; overflow: hidden; }

/* 左侧 */
.sidebar { width: 280px; background: #fff; border-right: 1px solid #dcdfe6; display: flex; flex-direction: column; flex-shrink: 0; z-index: 20; }
.sidebar-header { padding: 24px 20px; border-bottom: 1px solid #f2f4f7; }
.back-link { font-size: 13px; color: #909399; cursor: pointer; display: flex; align-items: center; margin-bottom: 12px; transition: color 0.3s; }
.back-link:hover { color: #409EFF; }
.course-name { margin: 0; font-size: 18px; color: #303133; font-weight: 700; letter-spacing: 0.5px; }
.progress-info { font-size: 12px; color: #909399; margin-top: 8px; }
.task-list-scroll { flex: 1; overflow-y: auto; padding: 12px 0; }
.task-list-scroll::-webkit-scrollbar { width: 4px; }
.task-list-scroll::-webkit-scrollbar-thumb { background: #e0e0e0; border-radius: 2px; }
.nav-item { display: flex; padding: 14px 24px; cursor: pointer; border-left: 3px solid transparent; transition: all 0.2s; align-items: flex-start; }
.nav-item:hover { background: #f5f7fa; }
.nav-item.active { background: #ecf5ff; border-left-color: #409EFF; }
.nav-icon { margin-right: 12px; margin-top: 3px; }
.index-num { display: inline-block; width: 20px; height: 20px; background: #eee; color: #909399; text-align: center; line-height: 20px; border-radius: 50%; font-size: 12px; font-weight: bold; }
.nav-item.active .index-num { background: #409EFF; color: #fff; }
.nav-info { flex: 1; }
.nav-title { font-size: 14px; color: #303133; margin-bottom: 6px; line-height: 1.5; font-weight: 500; }
.nav-status { font-size: 12px; color: #909399; display: flex; align-items: center; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; margin-right: 6px; }
.status-dot.green { background: #67C23A; }
.status-dot.gray { background: #909399; }
.sidebar-footer { padding: 16px 24px; border-top: 1px solid #f2f4f7; }
.user-row { display: flex; align-items: center; cursor: pointer; color: #606266; font-size: 14px; font-weight: 500; }
.username { margin-left: 12px; }

/* 右侧 */
.main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: #eff1f3; position: relative; }
.welcome-banner { flex: 1; display: flex; align-items: center; justify-content: center; color: #fff; background: linear-gradient(135deg, #74ebd5 0%, #ACB6E5 100%); }
.banner-inner { text-align: center; }
.banner-inner h1 { margin-top: 20px; font-weight: 300; letter-spacing: 2px; }
.workspace-wrapper { display: flex; flex-direction: column; height: 100%; }
.toolbar { height: 60px; background: #fff; border-bottom: 1px solid #dcdfe6; display: flex; justify-content: space-between; align-items: center; padding: 0 40px; flex-shrink: 0; z-index: 10; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.current-task-title { font-size: 18px; font-weight: 700; color: #303133; margin: 0; }
.actions { display: flex; gap: 12px; align-items: center; }

/* 滚动区 */
.paper-scroll-area { flex: 1; overflow-y: auto; background: #eff1f3; padding: 30px 0; display: flex; flex-direction: column; align-items: center; }
.a4-paper { width: 100%; max-width: 210mm; min-height: auto; background: #fff; padding: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-radius: 4px; margin-bottom: 80px; }
.paper-header { border-bottom: 2px solid #333; margin-bottom: 30px; padding-bottom: 15px; }
.paper-header h1 { text-align: center; font-size: 28px; font-family: "SimSun", serif; margin: 0; letter-spacing: 5px; font-weight: 900; color: #000; }

/* 表格 */
.report-table { border: 1px solid #333; display: flex; flex-direction: column; font-family: "SimSun", serif; font-size: 15px; color: #000; }
.rt-row { display: flex; border-bottom: 1px solid #333; }
.rt-row:last-child { border-bottom: none; }
.rt-label { background: #f7f7f7; display: flex; align-items: center; justify-content: center; padding: 10px 5px; font-weight: bold; border-right: 1px solid #333; width: 120px; flex-shrink: 0; text-align: center; }
.rt-content { flex: 1; padding: 10px 15px; display: flex; align-items: center; border-right: 1px solid #333; min-height: 45px; }
.rt-content:last-child { border-right: none; }
.rt-content.span-3 { flex: 3; }
.rt-block { display: flex; border-bottom: 1px solid #333; }
.rt-block:last-child { border-bottom: none; }
.rt-block-label { background: #f7f7f7; width: 70px; padding: 30px 5px; display: flex; align-items: center; justify-content: center; text-align: center; font-weight: bold; border-right: 1px solid #333; flex-shrink: 0; writing-mode: vertical-lr; letter-spacing: 4px; }
.rt-block-content { flex: 1; padding: 20px; min-height: 180px; white-space: pre-wrap; line-height: 1.8; }
:deep(.paper-input .el-textarea__inner) { border: none; box-shadow: none; padding: 0; resize: none; font-family: "SimSun", serif; font-size: 16px; line-height: 1.8; color: #000; background: transparent; min-height: 100%; }
:deep(.paper-input .el-textarea__inner:focus) { background: transparent; outline: none; }
:deep(.paper-input .el-textarea__inner::placeholder) { color: #ccc; }

/* 拖拽上传 */
.drag-uploader { width: 100%; }
:deep(.el-upload-dragger) {
  width: 100%; min-height: 120px; height: auto;
  background-color: #fcfcfc; border: 1px dashed #dcdfe6; border-radius: 4px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 20px 0;
}
:deep(.el-upload-dragger:hover) { border-color: #409EFF; background-color: #ecf5ff; }
:deep(.el-upload-dragger .el-icon--upload) { font-size: 40px; color: #c0c4cc; margin-bottom: 10px; margin-top: 0; }
:deep(.el-upload__text) { font-size: 14px; color: #606266; line-height: 1.5; text-align: center; }

.file-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; }
.file-item { display: flex; align-items: center; padding: 8px 12px; background: #fdfdfd; border: 1px solid #eee; border-radius: 4px; font-size: 13px; color: #606266; }
.file-item.pending-item { background: #fdf6ec; border-color: #faecd8; }
.file-link { color: #409EFF; text-decoration: none; margin: 0 8px; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.delete-icon { cursor: pointer; color: #999; margin-left: 5px; }
.delete-icon:hover { color: #F56C6C; }
</style>