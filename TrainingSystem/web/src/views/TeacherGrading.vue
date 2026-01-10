<template>
    <div class="grading-layout" v-loading="loading">
      
      <div class="grading-header">
        <div class="left">
          <el-button link @click="router.back()" class="nav-btn">
            <el-icon><ArrowLeft /></el-icon> 返回列表
          </el-button>
          <span class="separator">|</span>
          <span class="doc-name">{{ taskTitle }} - {{ studentName }}</span>
        </div>
        <div class="right">
          <el-button type="primary" size="small" @click="submitGrade" :loading="submitting">
            提交评分
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
  
            <div class="info-grid">
              <div class="info-item"><span class="label">学生姓名：</span><span class="value">{{ studentName }}</span></div>
              <div class="info-item"><span class="label">学号：</span><span class="value">{{ studentNumber }}</span></div>
              <div class="info-item"><span class="label">班级：</span><span class="value">{{ studentClass }}</span></div>
              <div class="info-item"><span class="label">指导教师：</span><span class="value">{{ teacherName }}</span></div>
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
  
                  <div v-else-if="item.type === 'textarea'" class="answer-wrapper">
                    <div class="input-label">【 {{ item.label }} 】</div>
                    <div 
                      class="student-answer-box" 
                      v-html="item.value || '<span style=\'color:#ccc\'>（该生未填写此项）</span>'"
                    ></div>
                  </div>
  
                  <div v-else-if="item.type === 'upload'" class="upload-wrapper">
                    <div class="section-subtitle">
                      <el-icon><Paperclip /></el-icon> 附件下载 ({{ item.label }})
                    </div>
                    
                    <div v-if="fileList.length === 0" class="no-file-tip">
                      该生未提交额外附件
                    </div>
                    
                    <div class="file-list">
                      <div v-for="file in fileList" :key="file.id" class="file-item download-mode">
                        <div class="f-left">
                          <el-icon class="file-icon"><DocumentChecked /></el-icon> 
                          <span class="fname">{{ file.name }}</span>
                        </div>
                        <el-button type="primary" link @click="downloadFile(file.url)">
                          <el-icon><Download /></el-icon> 点击下载
                        </el-button>
                      </div>
                    </div>
                  </div>
  
                </template>
              </div>
            </div>
  
            <div class="grading-section">
              <div class="grading-title">教师评分区</div>
              <div class="grading-form">
                <div class="form-row">
                  <span class="form-label">总得分数：</span>
                  <el-input-number v-model="gradeForm.score" :min="0" :max="100" controls-position="right" size="large" class="score-input" />
                  <span class="score-suffix">分</span>
                </div>
                <div class="form-row vertical">
                  <span class="form-label">教师评语：</span>
                  <el-input v-model="gradeForm.feedback" type="textarea" :rows="4" placeholder="请输入评语..." class="feedback-input" />
                </div>
                <div class="form-actions">
                  <el-button type="warning" size="large" @click="rejectReport" style="width: 150px; margin-right: 20px;">打回重写</el-button>
                  <el-button type="danger" size="large" @click="submitGrade" :loading="submitting" style="width: 200px;">确认评分</el-button>
                </div>
              </div>
            </div>
  
          </div>
          <div class="bottom-spacer"></div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ArrowLeft, DocumentChecked, Download, Paperclip } from '@element-plus/icons-vue' // 引入新图标
  import { ElMessage, ElMessageBox } from 'element-plus'
  import http from '../http'
  
  const route = useRoute(); const router = useRouter(); const reportId = route.params.reportId
  const loading = ref(true); const submitting = ref(false)
  const taskTitle = ref(''); const studentName = ref(''); const studentNumber = ref(''); const studentClass = ref(''); const teacherName = ref('')
  const reportContent = ref([]); const fileList = ref([])
  const gradeForm = reactive({ score: 80, feedback: '阅。' })
  
  onMounted(async () => {
    try {
      const res = await http.get(`reports/${reportId}/`); const data = res.data
      taskTitle.value = data.task_title; studentName.value = data.student_name; studentNumber.value = data.student_number
      studentClass.value = data.student_class || ''; teacherName.value = data.teacher_name || ''
      if (data.score !== null) gradeForm.score = data.score; if (data.feedback) gradeForm.feedback = data.feedback
      
      // 过滤附件：只显示非图片的文档
      const isImage = (n) => n.match(/\.(jpeg|jpg|gif|png|webp|bmp)$/i)
      
      // ★★★ 核心修复：文件名解码 ★★★
      fileList.value = data.attachments_list
        .filter(f => !isImage(f.file))
        .map(f => ({ 
          name: decodeURIComponent(f.file.split('/').pop()), // 这里解决了 %E6... 乱码
          url: f.file, 
          id: f.id 
        }))
  
      const savedContent = data.content_data || []; const templateStruct = data.template_structure || []
      const filteredTemplate = templateStruct.filter(item => item.key !== 'auto_score' && item.key !== 'auto_feedback')
  
      let currentStruct = filteredTemplate.map((tplItem, idx) => {
        if (tplItem.type === 'teacher_block') return tplItem
        if (tplItem.type === 'info_row') {
             if (tplItem.key === 'auto_class') return { ...tplItem, value: studentClass.value }
             if (tplItem.key === 'auto_teacher') return { ...tplItem, value: teacherName.value }
             if (tplItem.key === 'auto_name') return { ...tplItem, value: studentName.value }
             if (tplItem.key === 'auto_number') return { ...tplItem, value: studentNumber.value }
        }
        const savedItem = savedContent.find(s => s.label === tplItem.label)
        return { ...tplItem, value: savedItem ? savedItem.value : '' }
      })
      reportContent.value = currentStruct
    } catch(e) { ElMessage.error('加载失败') } finally { loading.value = false }
  })
  
  const downloadFile = (url) => { 
    // 打开新窗口触发下载
    window.open(url, '_blank') 
  }
  
  const submitGrade = async () => {
    submitting.value = true
    try { await http.post(`reports/${reportId}/grade/`, gradeForm); ElMessage.success('评分已提交'); router.back() } catch(e) { ElMessage.error('提交失败') } finally { submitting.value = false }
  }
  const rejectReport = async () => {
    ElMessageBox.confirm('确定要打回该作业吗？', '提示', { type: 'warning', confirmButtonText: '打回' })
      .then(async () => {
        try { await http.post(`reports/${reportId}/reject/`); ElMessage.success('已打回'); router.back() } catch(e) { ElMessage.error('操作失败') }
      })
  }
  </script>
  
  <style scoped>
  /* 样式复用 */
  .grading-layout { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; background-color: #525659; overflow: hidden; }
  .grading-header { height: 50px; background: #fff; border-bottom: 1px solid #dcdfe6; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; flex-shrink: 0; z-index: 100; }
  .nav-btn { font-size: 14px; color: #333; }
  .separator { margin: 0 15px; color: #ddd; }
  .doc-name { font-weight: bold; font-size: 14px; color: #333; }
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
  .input-label { font-weight: bold; font-size: 15px; margin-bottom: 10px; color: #000; margin-top: 20px; background: #f2f2f2; padding: 4px 10px; border-radius: 4px; display: inline-block; }
  .student-answer-box { min-height: 50px; padding: 10px; border: 1px dashed #ccc; font-family: 'FangSong', serif; font-size: 16px; line-height: 1.6; color: #333; }
  :deep(.student-answer-box img) { max-width: 100%; height: auto; display: block; margin: 10px 0; border: 1px solid #eee; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
  
  /* 附件区优化 */
  .section-subtitle { font-size: 15px; font-weight: bold; margin-top: 30px; margin-bottom: 15px; display: flex; align-items: center; gap: 5px; color: #2c3e50; }
  .no-file-tip { color: #999; font-size: 13px; font-style: italic; margin-bottom: 10px; padding-left: 10px; }
  .file-list { margin-bottom: 10px; border: 1px solid #eee; border-radius: 4px; overflow: hidden; }
  .file-item.download-mode { 
    display: flex; justify-content: space-between; align-items: center; 
    padding: 10px 15px; border-bottom: 1px solid #eee; background: #fcfcfc; transition: all 0.2s; 
  }
  .file-item.download-mode:last-child { border-bottom: none; }
  .file-item.download-mode:hover { background: #f0f9eb; }
  .f-left { display: flex; align-items: center; gap: 8px; color: #333; font-size: 14px; }
  .file-icon { color: #67c23a; font-size: 16px; }
  .fname { font-weight: 500; }
  
  .grading-section { margin-top: 60px; border: 2px solid #d9001b; padding: 20px; border-radius: 8px; background: #fff5f5; position: relative; }
  .grading-title { position: absolute; top: -14px; left: 20px; background: #d9001b; color: #fff; padding: 2px 15px; font-size: 14px; border-radius: 4px; font-weight: bold; }
  .grading-form { margin-top: 10px; }
  .form-row { display: flex; align-items: center; margin-bottom: 20px; }
  .form-row.vertical { flex-direction: column; align-items: flex-start; }
  .form-label { font-weight: bold; font-size: 16px; color: #d9001b; min-width: 90px; }
  .score-suffix { font-size: 16px; font-weight: bold; color: #d9001b; margin-left: 10px; }
  .feedback-input :deep(.el-textarea__inner) { border-color: #f79999; font-size: 15px; color: #d9001b; }
  .score-input :deep(.el-input__wrapper) { box-shadow: 0 0 0 1px #f79999 inset; }
  .form-actions { text-align: center; margin-top: 20px; display: flex; justify-content: center; gap: 20px; }
  .bottom-spacer { height: 100px; width: 100%; flex-shrink: 0; }
  </style>