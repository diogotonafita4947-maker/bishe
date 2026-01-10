<template>
  <div class="task-manage">
    <div class="header">
      <h2>实训任务管理</h2>
      <el-button type="primary" icon="Plus" @click="openCreateDialog">发布新任务</el-button>
    </div>

    <el-table :data="tasks" style="width: 100%" v-loading="loading">
      <el-table-column prop="title" label="任务标题" />
      <el-table-column prop="target_class_name" label="目标班级" />
      <el-table-column prop="template_title" label="使用模板" />
      <el-table-column prop="location" label="实训地点" width="180" /> <el-table-column label="截止时间" width="180">
        <template #default="scope">
          {{ new Date(scope.row.end_time).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button type="danger" size="small" icon="Delete" @click="deleteTask(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="发布新实训任务" width="600px">
      <el-form :model="form" label-width="100px">
        
        <el-form-item label="任务标题" required>
          <el-input v-model="form.title" placeholder="例如：Vue.js 组件开发实训" />
        </el-form-item>

        <el-form-item label="实训地点" required>
          <el-input v-model="form.location" placeholder="例如：实训楼 B204" />
        </el-form-item>

        <el-form-item label="发布班级" required>
          <el-select v-model="form.target_class" placeholder="请选择班级">
            <el-option v-for="cls in classes" :key="cls.id" :label="cls.name" :value="cls.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="选择模板" required>
          <el-select v-model="form.template" placeholder="请选择报告模板" @change="handleTemplateChange">
            <el-option v-for="tpl in templates" :key="tpl.id" :label="tpl.title" :value="tpl.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="截止时间" required>
          <el-date-picker v-model="form.end_time" type="datetime" placeholder="选择截止日期时间" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="允许提交" required>
           <el-input-number v-model="form.max_submissions" :min="1" :max="10" /> 次 <span style="font-size:12px; color:#999; margin-left:10px">(学生提交后可覆盖，超次数不可交)</span>
        </el-form-item>

        <div v-if="previewStruct.length > 0" class="teacher-fill-area">
          <div class="area-title"><el-icon><Edit /></el-icon> 请完善实验内容 (学生可见)：</div>
          <div v-for="(item, index) in previewStruct" :key="index" class="fill-item">
            <div class="fill-label">{{ item.label }}</div>
            <el-input type="textarea" v-model="item.value" :rows="3" :placeholder="'在此输入 '+item.label+' 的具体内容...'" />
          </div>
        </div>

      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTask" :loading="submitting">确认发布</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Delete, Edit } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../http'

const loading = ref(false)
const tasks = ref([])
const classes = ref([])
const templates = ref([])
const dialogVisible = ref(false)
const submitting = ref(false)

const form = reactive({
  title: '',
  location: '计算机实训中心', // 默认值
  target_class: '',
  template: '',
  end_time: '',
  max_submissions: 3,
  task_context: {}
})

const previewStruct = ref([]) 

onMounted(() => {
  fetchData()
  fetchOptions()
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await http.get('tasks/')
    tasks.value = res.data
  } catch(e) {} finally { loading.value = false }
}

const fetchOptions = async () => {
  const cRes = await http.get('classes/')
  classes.value = cRes.data
  const tRes = await http.get('templates/')
  templates.value = tRes.data
}

const openCreateDialog = () => {
  form.title = ''
  form.location = '计算机实训中心'
  form.target_class = ''
  form.template = ''
  form.end_time = ''
  form.max_submissions = 3
  form.task_context = {}
  previewStruct.value = []
  dialogVisible.value = true
}

const handleTemplateChange = (tplId) => {
  const tpl = templates.value.find(t => t.id === tplId)
  if (!tpl) return
  const struct = tpl.content_structure || []
  // 筛选出 type='teacher_block' 的项供老师填写
  previewStruct.value = struct
    .filter(item => item.type === 'teacher_block')
    .map(item => ({ label: item.label, value: '' })) // 这里的 value 将作为老师填写的默认值
}

const submitTask = async () => {
  if(!form.title || !form.target_class || !form.template || !form.end_time) {
    return ElMessage.warning('请填写完整信息')
  }
  
  // 收集老师填写的动态内容
  const context = {}
  previewStruct.value.forEach(item => {
    context[item.label] = item.value
  })
  form.task_context = context

  // 构造提交数据
  // 注意：start_time 后端必填，这里默认设为当前时间
  const postData = {
    ...form,
    start_time: new Date().toISOString()
  }

  submitting.value = true
  try {
    await http.post('tasks/', postData)
    ElMessage.success('发布成功')
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('发布失败')
  } finally {
    submitting.value = false
  }
}

const deleteTask = (row) => {
  ElMessageBox.confirm('确定删除该任务吗？删除后学生提交的报告也将被删除！', '警告', { type: 'warning' })
    .then(async () => {
      await http.delete(`tasks/${row.id}/`)
      ElMessage.success('已删除')
      fetchData()
    })
}
</script>

<style scoped>
.task-manage { padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.teacher-fill-area { margin-top: 20px; padding: 15px; background: #f0f9eb; border: 1px dashed #67c23a; border-radius: 4px; }
.area-title { font-weight: bold; color: #67c23a; margin-bottom: 10px; display: flex; align-items: center; gap: 5px; }
.fill-item { margin-bottom: 10px; }
.fill-label { font-size: 14px; margin-bottom: 5px; color: #606266; }
</style>