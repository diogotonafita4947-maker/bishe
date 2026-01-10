<template>
  <div class="layout-container">
    <div class="sidebar">
      <div class="logo-area"><el-icon><Monitor /></el-icon> 教师工作台</div>
      <ul class="menu-list">
        <li :class="{ active: currentMenu === 'overview' }" @click="currentMenu = 'overview'"><el-icon><Odometer /></el-icon> 概览</li>
        <li :class="{ active: currentMenu === 'classes' }" @click="currentMenu = 'classes'"><el-icon><UserFilled /></el-icon> 班级管理</li>
        <li :class="{ active: currentMenu === 'tasks' }" @click="currentMenu = 'tasks'"><el-icon><List /></el-icon> 实训任务</li>
        <li :class="{ active: currentMenu === 'templates' }" @click="currentMenu = 'templates'"><el-icon><Document /></el-icon> 模版管理</li>
      </ul>
    </div>

    <div class="main-content">
      <div class="top-header">
        <div class="welcome-text">你好，<strong>{{ userStore.user.real_name || userStore.user.username }}</strong> 老师</div>
        <el-button type="danger" link @click="handleLogout">退出</el-button>
      </div>

      <div class="content-body">
        
        <div v-if="currentMenu === 'overview'" class="view-section">
          <div class="stats-cards">
            <div class="card"><div class="card-title">我的班级</div><div class="card-num">{{ myClasses.length }}</div></div>
            <div class="card"><div class="card-title">已发布任务</div><div class="card-num">{{ tasks.length }}</div></div>
            <div class="card"><div class="card-title">模版数量</div><div class="card-num">{{ templates.length }}</div></div>
          </div>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="openPublishDialog"><el-icon><Plus /></el-icon> 发布新任务</el-button>
          </div>
        </div>

        <div v-if="currentMenu === 'classes'" class="view-section">
          <div class="section-header"><h3>班级管理</h3><el-button type="primary" @click="createClass">创建新班级</el-button></div>
          <el-table :data="myClasses" stripe><el-table-column prop="name" label="班级名称" /><el-table-column prop="invite_code" label="邀请码" /><el-table-column label="人数"><template #default="scope">{{scope.row.student_count||0}}</template></el-table-column></el-table>
        </div>

        <div v-if="currentMenu === 'tasks'" class="view-section">
          <div class="section-header"><h3>实训任务列表</h3><el-button type="primary" @click="openPublishDialog">发布新任务</el-button></div>
          <el-table :data="tasks" stripe>
            <el-table-column prop="title" label="任务标题" />
            <el-table-column prop="target_class_name" label="目标班级" />
            <el-table-column label="截止时间"><template #default="scope">{{ formatDate(scope.row.end_time) }}</template></el-table-column>
            <el-table-column label="操作"><template #default="scope"><el-button link type="primary" @click="goToGrading(scope.row.id)">批改</el-button></template></el-table-column>
          </el-table>
        </div>

        <div v-if="currentMenu === 'templates'" class="view-section">
          <div class="section-header">
            <h3>报告模版库</h3>
            <el-upload action="#" :http-request="handleUploadTemplate" :show-file-list="false" accept=".docx">
              <el-button type="success"><el-icon><DocumentAdd /></el-icon> 上传 Word 模版</el-button>
            </el-upload>
          </div>
          <el-alert title="★ 制作模版规则：用 {{内容}} 代表老师发布时填写（如 {{实验目的}}），用 【内容】 代表学生填写（如 【实验心得】）。" type="warning" show-icon :closable="false" style="margin-bottom: 20px;" />
          <el-table :data="templates" stripe>
            <el-table-column prop="title" label="模版名称" />
            <el-table-column prop="created_at" label="创建时间"><template #default="scope">{{ formatDate(scope.row.created_at) }}</template></el-table-column>
            <el-table-column label="操作"><template #default="scope"><el-button link type="danger" @click="deleteTemplate(scope.row.id)">删除</el-button></template></el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <el-dialog v-model="showPublishDialog" title="发布新实训任务" width="600px" top="5vh">
      <el-form :model="newTask" label-width="110px">
        <el-form-item label="任务名称"><el-input v-model="newTask.title" placeholder="例如：Vue3组件通信实训" /></el-form-item>
        <el-form-item label="实训地点"><el-input v-model="newTask.location" /></el-form-item>
        <el-form-item label="选择班级">
          <el-select v-model="newTask.target_class" placeholder="选择班级" style="width: 100%">
            <el-option v-for="c in myClasses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="使用模版">
          <el-select v-model="newTask.template" placeholder="请选择模版" style="width: 100%" @change="onTemplateChange">
            <el-option v-for="t in templates" :key="t.id" :label="t.title" :value="t.id" />
          </el-select>
        </el-form-item>

        <div v-if="dynamicFields.length > 0" class="dynamic-area">
          <div class="area-title">请填写以下模版内容：</div>
          <el-form-item 
            v-for="(field, index) in dynamicFields" 
            :key="index" 
            :label="field.label"
            label-width="110px"
          >
            <el-input 
              v-model="field.value" 
              type="textarea" 
              :rows="3" 
              :placeholder="'在此输入 ' + field.label + ' 的具体内容...'"
            />
          </el-form-item>
        </div>

        <el-form-item label="截止时间"><el-date-picker v-model="newTask.end_time" type="datetime" style="width: 100%" /></el-form-item>
        <el-form-item label="提交次数"><el-input-number v-model="newTask.max_submissions" :min="1" :max="10" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPublishDialog = false">取消</el-button>
        <el-button type="primary" @click="publishTask">立即发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Monitor, Odometer, UserFilled, List, Document, Plus, User, DocumentAdd } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../http'
import { useUserStore } from '../stores/user'

const router = useRouter(); const userStore = useUserStore()
const currentMenu = ref('overview'); const showPublishDialog = ref(false)
const myClasses = ref([]); const tasks = ref([]); const templates = ref([])

const newTask = ref({ title: '', location: '计算机实训中心', target_class: null, template: null, end_time: '', max_submissions: 3 })
const dynamicFields = ref([]) // ★ 用来存从模版里解析出来的“老师填空项”

onMounted(() => { loadData() })
const loadData = async () => {
  try {
    const [r1, r2, r3] = await Promise.all([http.get('classes/'), http.get('tasks/'), http.get('templates/')])
    myClasses.value = r1.data; tasks.value = r2.data; templates.value = r3.data
  } catch(e){}
}

const openPublishDialog = () => { loadData(); showPublishDialog.value = true; dynamicFields.value = [] }

// ★★★ 核心逻辑：选模版时，自动生成输入框 ★★★
const onTemplateChange = (tplId) => {
  const tpl = templates.value.find(t => t.id === tplId)
  if (!tpl) return
  
  // 过滤出类型为 teacher_block 的项 (就是后端解析出的 {{}} )
  dynamicFields.value = tpl.content_structure
    .filter(item => item.type === 'teacher_block')
    .map(item => ({
      label: item.label, // 比如 "实验目的"
      value: ''          // 初始值为空，等待老师填
    }))
}

const publishTask = async () => {
  if(!newTask.value.title || !newTask.value.target_class || !newTask.value.template) return ElMessage.warning('请填写完整')
  
  // ★★★ 将老师填好的内容打包成 JSON (task_context) 发给后端 ★★★
  const contextData = {}
  dynamicFields.value.forEach(f => {
    contextData[f.label] = f.value
  })

  await http.post('tasks/', {
    ...newTask.value,
    start_time: new Date(),
    task_context: contextData // 存入数据库
  })
  
  ElMessage.success('发布成功！')
  showPublishDialog.value = false
  loadData()
}

const handleUploadTemplate = async (opt) => {
  const fd = new FormData(); fd.append('file', opt.file)
  try { await http.post('templates/upload_docx/', fd); ElMessage.success('上传成功'); loadData() } catch(e) { ElMessage.error('上传失败') }
}
const deleteTemplate = async (id) => { await ElMessageBox.confirm('删除?'); await http.delete(`templates/${id}/`); loadData() }
const createClass = async () => { const {value} = await ElMessageBox.prompt('班级名称'); if(value) await http.post('classes/', {name:value}); loadData() }
const goToGrading = (id) => router.push(`/grading/${id}`)
const handleLogout = () => { userStore.clearUser(); router.push('/login') }
const formatDate = (s) => new Date(s).toLocaleString()
</script>

<style scoped>
.layout-container { display: flex; height: 100vh; background: #f0f2f5; }
.sidebar { width: 220px; background: #001529; color: #fff; display: flex; flex-direction: column; }
.logo-area { height: 60px; display: flex; align-items: center; justify-content: center; font-size: 18px; border-bottom: 1px solid #002140; }
.menu-list li { height: 50px; display: flex; align-items: center; padding-left: 20px; cursor: pointer; color: rgba(255,255,255,0.65); transition: 0.3s; gap:10px;}
.menu-list li:hover, .menu-list li.active { color: #fff; background: #1890ff; }
.main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.top-header { height: 60px; background: #fff; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
.content-body { flex: 1; padding: 20px; overflow-y: auto; }
.view-section { max-width: 1200px; margin: 0 auto; }
.stats-cards { display: flex; gap: 20px; margin-bottom: 20px; }
.card { flex: 1; background: #fff; padding: 20px; border-radius: 4px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.card-num { font-size: 30px; font-weight: bold; color: #1890ff; margin-top: 10px; }
.section-header { display: flex; justify-content: space-between; margin-bottom: 20px; align-items: center; }
.dynamic-area { background: #fdf6ec; padding: 15px; border: 1px dashed #e6a23c; border-radius: 4px; margin-bottom: 20px; }
.area-title { font-weight: bold; color: #e6a23c; margin-bottom: 10px; font-size: 14px; }
</style>