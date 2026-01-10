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
          <p class="info-item"><el-icon><School /></el-icon> 班级：{{ task.target_class_name }}</p>
          <p class="info-item"><el-icon><Document /></el-icon> 模板：{{ task.template_title }}</p>
          <p class="info-item"><el-icon><Timer /></el-icon> 截止：{{ formatDate(task.end_time) }}</p>
        </div>
        <div class="card-footer">
          <el-button type="primary" link @click="checkStats(task)">查看提交情况</el-button>
          <el-popconfirm title="确定删除该任务吗？" @confirm="deleteTask(task.id)">
            <template #reference><el-button type="danger" link>删除</el-button></template>
          </el-popconfirm>
        </div>
      </el-card>
    </div>

    <el-dialog v-model="dialogVisible" title="发布新实训任务" width="600px" top="5vh">
      <el-form :model="form" label-width="100px" label-position="left">
        
        <el-form-item label="任务标题" required>
          <el-input v-model="form.title" placeholder="例如：Vue.js 组件通信实训" />
        </el-form-item>

        <el-form-item label="发布班级" required>
          <el-select v-model="form.target_class" placeholder="请选择班级" style="width: 100%">
            <el-option v-for="cls in myClasses" :key="cls.id" :label="cls.name" :value="cls.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="报告模板" required>
          <div style="display:flex; width:100%; gap:10px; align-items:center;">
            <el-select v-model="form.template" placeholder="选择模板" style="flex:1" @change="onTemplateChange">
              <el-option v-for="tpl in templates" :key="tpl.id" :label="tpl.title" :value="tpl.id">
                <span style="float: left">{{ tpl.title }}</span>
                <span style="float: right; color: #f56c6c; font-size: 12px; margin-left:10px" @click.stop="deleteTemplate(tpl.id)">
                  <el-icon><Delete /></el-icon>
                </span>
              </el-option>
            </el-select>
            <el-upload action="#" :auto-upload="false" :show-file-list="false" :on-change="handleTemplateUpload" accept=".docx">
              <el-button type="success" plain>上传Docx生成</el-button>
            </el-upload>
          </div>
          <div style="font-size:12px; color:#999; margin-top:5px; line-height:1.4">
            提示：上传只包含“实验原理”、“实验目的”等标题的 Word，系统会自动生成下方填写框。
          </div>
        </el-form-item>

        <el-form-item label="允许提交" required>
           <el-input-number v-model="form.max_submissions" :min="1" :max="10" label="次" />
           <span style="margin-left:10px; color:#999; font-size:12px">次 (学生提交后可覆盖，超次数不可交)</span>
        </el-form-item>

        <div v-if="teacherFields.length > 0" class="teacher-fill-area">
          <div class="area-header">
            <el-icon><EditPen /></el-icon> <strong>请完善实验内容（学生可见）：</strong>
          </div>
          <el-form-item 
            v-for="(field, idx) in teacherFields" 
            :key="idx" 
            :label="field.label"
            label-width="120px"
            style="margin-bottom: 15px;"
          >
            <el-input 
              v-model="field.value" 
              type="textarea" 
              :rows="3" 
              :placeholder="'在此输入 '+field.label+' 的具体内容...'" 
            />
          </el-form-item>
        </div>

        <el-form-item label="截止时间" required>
          <el-date-picker v-model="form.end_time" type="datetime" placeholder="选择截止时间" style="width: 100%" />
        </el-form-item>

      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createTask">确认发布</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="drawerVisible" title="提交统计" size="60%">
      <el-table :data="statsList" stripe>
        <el-table-column prop="student_name" label="姓名" width="100" />
        <el-table-column prop="student_number" label="学号" width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 'submitted'" type="success">已提交</el-tag>
            <el-tag v-else-if="scope.row.status === 'graded'" type="warning">已批改</el-tag>
            <el-tag v-else-if="scope.row.status === 'returned'" type="danger">已打回</el-tag>
            <el-tag v-else type="info">未提交</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="次数" prop="submit_count" align="center" width="80" />
        <el-table-column label="分数" prop="score" align="center" width="80">
          <template #default="scope">{{ scope.row.score || '-' }}</template>
        </el-table-column>
        
        <el-table-column label="操作" align="center">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status !== 'unsubmitted'" 
              type="primary" 
              link 
              @click="goToGrade(scope.row.report_id)"
            >
              {{ scope.row.status === 'graded' ? '修改评分' : '去批改' }}
            </el-button>
            <span v-else style="color:#ccc; font-size:12px">等待提交</span>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, School, Document, Timer, Delete, EditPen } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../http'

const router = useRouter()
const loading = ref(false)
const tasks = ref([])
const myClasses = ref([])
const templates = ref([])
const dialogVisible = ref(false)
const drawerVisible = ref(false)
const statsList = ref([])

const teacherFields = ref([]) 

const form = reactive({
  title: '',
  target_class: '',
  template: '',
  end_time: '',
  max_submissions: 3, // 默认3次
  task_context: {}
})

onMounted(() => fetchData())

const fetchData = async () => {
  loading.value = true
  try {
    const [tRes, cRes, tpRes] = await Promise.all([
      http.get('tasks/'), http.get('classes/'), http.get('templates/')
    ])
    tasks.value = tRes.data
    myClasses.value = cRes.data
    templates.value = tpRes.data
  } catch(e) {}
  loading.value = false
}

const onTemplateChange = (tplId) => {
  const tpl = templates.value.find(t => t.id === tplId)
  if (!tpl) return
  teacherFields.value = []
  tpl.content_structure.forEach(item => {
    if (item.type === 'teacher_block') {
      teacherFields.value.push({ label: item.label, value: '' })
    }
  })
}

const handleTemplateUpload = async (file) => {
  const fd = new FormData(); fd.append('file', file.raw)
  try {
    const res = await http.post('templates/upload_docx/', fd)
    ElMessage.success('上传并解析成功')
    await fetchData()
    form.template = res.data.id
    onTemplateChange(res.data.id)
  } catch(e) { ElMessage.error('上传失败') }
}

const deleteTemplate = async (id) => {
  ElMessageBox.confirm('确定删除该模板吗？', '警告', { type:'warning' }).then(async () => {
    try {
      await http.delete(`templates/${id}/`)
      ElMessage.success('已删除')
      fetchData()
      if(form.template === id) { form.template = ''; teacherFields.value = [] }
    } catch(e) { ElMessage.error('无法删除：可能已被任务引用或无权限') }
  })
}

const createTask = async () => {
  if(!form.title || !form.end_time || !form.template) return ElMessage.warning('请补全信息')
  
  const context = {}
  teacherFields.value.forEach(f => context[f.label] = f.value)
  form.task_context = context
  
  try {
    await http.post('tasks/', { ...form, start_time: new Date() })
    ElMessage.success('发布成功')
    dialogVisible.value = false
    fetchData()
  } catch(e) { ElMessage.error('发布失败') }
}

const deleteTask = async (id) => { await http.delete(`tasks/${id}/`); fetchData() }
const checkStats = async (task) => {
  const res = await http.get(`tasks/${task.id}/statistics/`)
  statsList.value = res.data
  drawerVisible.value = true
}
const isExpired = (t) => new Date(t) < new Date()
const formatDate = (s) => new Date(s).toLocaleString()
const openCreateDialog = () => {
  form.title = ''; form.end_time = ''; form.template = ''; teacherFields.value = []; form.max_submissions = 3;
  dialogVisible.value = true
}

const goToGrade = (reportId) => {
  router.push(`/teacher/grading/${reportId}`)
}
</script>

<style scoped>
.task-container { padding: 20px; }
.header { display: flex; justify-content: space-between; margin-bottom: 20px; }
.task-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.teacher-fill-area { background: #f0f9eb; padding: 15px; border-radius: 6px; margin-bottom: 20px; border: 1px dashed #67c23a; }
.area-header { color: #67c23a; margin-bottom: 10px; display: flex; align-items: center; gap: 5px; font-size: 14px; }
.info-item { display: flex; align-items: center; gap: 5px; margin-bottom: 5px; color: #666; font-size: 13px; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
.card-footer { margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee; text-align: right; }
</style>