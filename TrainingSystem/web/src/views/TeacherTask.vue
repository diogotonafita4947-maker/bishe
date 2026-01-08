<template>
  <div class="task-container">
    <div class="header">
      <h2>实训任务管理</h2>
      <el-button type="primary" icon="Plus" @click="openCreateDialog">发布新任务</el-button>
    </div>

    <div class="task-list" v-loading="loading">
      <el-empty v-if="tasks.length === 0" description="暂无发布记录" />
      
      <el-card v-for="task in tasks" :key="task.id" class="task-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="task-title">{{ task.title }}</span>
            <el-tag :type="isExpired(task.end_time) ? 'info' : 'success'">
              {{ isExpired(task.end_time) ? '已截止' : '进行中' }}
            </el-tag>
          </div>
        </template>
        <div class="card-content">
          <p class="info-item"><el-icon><School /></el-icon> 发布对象：{{ task.target_class_name }}</p>
          <p class="info-item"><el-icon><Document /></el-icon> 使用模板：{{ task.template_title }}</p>
          <p class="info-item"><el-icon><Timer /></el-icon> 截止时间：{{ formatDate(task.end_time) }}</p>
        </div>
        <div class="card-footer">
          <el-button type="primary" link @click="checkStats(task)">查看提交情况</el-button>
          <el-popconfirm title="确定删除该任务吗？" @confirm="deleteTask(task.id)">
            <template #reference>
              <el-button type="danger" link>删除</el-button>
            </template>
          </el-popconfirm>
        </div>
      </el-card>
    </div>

    <el-dialog v-model="dialogVisible" title="发布新实训任务" width="550px">
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item label="任务标题" required>
          <el-input v-model="form.title" placeholder="例如：Vue.js 组件通信实训" />
        </el-form-item>

        <el-form-item label="发布班级" required>
          <el-select v-model="form.target_class" placeholder="请选择教学班级" style="width: 100%">
            <el-option v-for="cls in myClasses" :key="cls.id" :label="cls.name" :value="cls.id" />
          </el-select>
          <div v-if="myClasses.length === 0" style="font-size:12px; color:#f56c6c; margin-top:5px">
            暂无班级，请先去“班级管理”创建。
          </div>
        </el-form-item>

        <el-form-item label="报告模板" required>
          <div style="display:flex; width:100%; gap:10px;">
            <el-select v-model="form.template" placeholder="请选择或上传模板" style="flex:1">
              <el-option v-for="tpl in templates" :key="tpl.id" :label="tpl.title" :value="tpl.id" />
            </el-select>
            <el-upload
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleTemplateUpload"
              accept=".docx"
            >
              <el-button type="success" icon="Upload" plain>上传Docx生成</el-button>
            </el-upload>
          </div>
          <p style="font-size:12px; color:#999; margin-top:5px">
            提示：上传 Word 文档，系统自动识别标题和正文生成在线模板。
          </p>
        </el-form-item>

        <el-form-item label="截止时间" required>
          <el-date-picker
            v-model="form.end_time"
            type="datetime"
            placeholder="选择截止时间"
            style="width: 100%"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createTask" :disabled="!form.target_class">
          确认发布
        </el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="drawerVisible" title="任务提交统计" size="60%">
      <el-table :data="statsList" stripe>
        <el-table-column prop="student_name" label="姓名" />
        <el-table-column prop="student_number" label="学号" />
        <el-table-column label="状态" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 'submitted'" type="success">已提交</el-tag>
            <el-tag v-else-if="scope.row.status === 'graded'" type="warning">已批改</el-tag>
            <el-tag v-else type="info">未提交</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center">
          <template #default="scope">
             <el-button v-if="scope.row.status !== 'unsubmitted'" type="primary" link @click="goToGrade(scope.row.report_id)">批阅</el-button>
             <span v-else style="color:#ccc">--</span>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, School, Document, Timer, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElLoading } from 'element-plus'
import http from '../http'

const router = useRouter()
const loading = ref(false)
const tasks = ref([])
const myClasses = ref([])
const templates = ref([])
const dialogVisible = ref(false)
const drawerVisible = ref(false)
const statsList = ref([])

const form = reactive({
  title: '',
  target_class: '',
  template: '',
  end_time: '',
  start_time: new Date().toISOString()
})

onMounted(() => { fetchData() })

const fetchData = async () => {
  loading.value = true
  try {
    const taskRes = await http.get('tasks/')
    tasks.value = taskRes.data
    const classRes = await http.get('classes/')
    myClasses.value = classRes.data
    const tplRes = await http.get('templates/')
    templates.value = tplRes.data
  } catch (e) { ElMessage.error('数据加载失败') } 
  finally { loading.value = false }
}

const openCreateDialog = () => {
  if (myClasses.value.length === 0) return ElMessage.warning('请先创建班级！')
  form.target_class = myClasses.value[0]?.id
  form.template = templates.value.length > 0 ? templates.value[0].id : ''
  form.title = ''
  form.end_time = ''
  dialogVisible.value = true
}

const handleTemplateUpload = async (file) => {
  if(!file.name.endsWith('.docx')) return ElMessage.error('必须是 .docx 文件')
  const loadingInstance = ElLoading.service({ text: '正在解析生成模板...', background: 'rgba(0,0,0,0.7)' })
  try {
    const fd = new FormData()
    fd.append('file', file.raw)
    const res = await http.post('templates/upload_docx/', fd)
    ElMessage.success(res.data.message)
    const tplRes = await http.get('templates/')
    templates.value = tplRes.data
    form.template = res.data.id // 自动选中新模版
  } catch(e) {
    ElMessage.error('解析失败，请检查文档格式')
  } finally {
    loadingInstance.close()
  }
}

const createTask = async () => {
  if(!form.title || !form.end_time || !form.template) return ElMessage.warning('请补全信息')
  try {
    form.start_time = new Date().toISOString()
    await http.post('tasks/', form)
    ElMessage.success('发布成功！')
    dialogVisible.value = false
    fetchData()
  } catch(e) { ElMessage.error('发布失败') }
}

const deleteTask = async (id) => {
  try {
    await http.delete(`tasks/${id}/`)
    ElMessage.success('删除成功')
    fetchData()
  } catch(e) { ElMessage.error('删除失败') }
}

const checkStats = async (task) => {
  try {
    const res = await http.get(`tasks/${task.id}/statistics/`)
    statsList.value = res.data
    drawerVisible.value = true
  } catch(e) { ElMessage.error('获取统计失败') }
}

const goToGrade = (reportId) => { ElMessage.info('跳转批阅: ' + reportId) }
const isExpired = (time) => new Date(time) < new Date()
const formatDate = (str) => new Date(str).toLocaleString()
</script>

<style scoped>
.task-container { padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.task-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
.task-card { border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.task-title { font-weight: bold; font-size: 16px; }
.card-content { padding: 15px 0; color: #606266; font-size: 14px; }
.info-item { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.card-footer { border-top: 1px solid #eee; padding-top: 10px; display: flex; justify-content: flex-end; gap: 10px; }
</style>