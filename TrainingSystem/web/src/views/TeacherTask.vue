<template>
  <div class="dashboard-container">
    <div class="nav-bar">
      <div class="brand">📚 实训任务管理</div>
      <el-button @click="router.push('/teacher/dashboard')" round>
        <el-icon style="margin-right: 5px"><HomeFilled /></el-icon> 返回工作台
      </el-button>
    </div>

    <div class="content-area">
      <div class="guide-box">
        <div class="guide-text">
          <h3>🚀 发布新实训</h3>
          <p>请详细填写实训目的、原理及要求，学生端将仅需填写步骤与心得。</p>
        </div>
        <el-button type="primary" size="large" @click="openCreateDialog" class="create-btn">
          <el-icon><Plus /></el-icon> 立即发布
        </el-button>
      </div>

      <el-table :data="taskList" stripe style="margin-top: 20px;" v-loading="loading">
        <el-table-column prop="title" label="任务标题" min-width="150" />
        <el-table-column prop="target_class_name" label="班级" width="120">
          <template #default="scope"><el-tag>{{ scope.row.target_class_name }}</el-tag></template>
        </el-table-column>
        <el-table-column label="实训地点" min-width="120">
          <template #default="scope">
            {{ scope.row.task_details?.location || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="截止时间" width="160">
          <template #default="scope">{{ formatTime(scope.row.end_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" plain size="small" @click="goGrade(scope.row.id)">
              <el-icon style="margin-right: 4px"><DataAnalysis /></el-icon> 批阅
            </el-button>
            <el-button type="danger" link size="small" @click="deleteTask(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="发布实训任务" width="800px" top="5vh" destroy-on-close>
      <el-form :model="form" label-position="top" :rules="rules" ref="formRef">
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="1. 实训(验)名称" prop="title">
              <el-input v-model="form.title" placeholder="例如：Java Web开发基础实验" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="2. 实训(验)地点" prop="location">
              <el-input v-model="form.details.location" placeholder="例如：实训楼 B304" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="目标班级" prop="target_class">
              <el-select v-model="form.target_class" placeholder="选择班级" style="width: 100%">
                <el-option v-for="c in classList" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止时间" prop="end_time">
              <el-date-picker v-model="form.end_time" type="datetime" placeholder="选择截止日期" style="width: 100%" value-format="YYYY-MM-DDTHH:mm:ss"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">实训详情配置 (学生可见)</el-divider>

        <el-form-item label="3. 实验(训)目的">
          <el-input type="textarea" :rows="3" v-model="form.details.purpose" placeholder="请输入本次实验的主要目的..." />
        </el-form-item>

        <el-form-item label="4. 实验(训)仪器与用具">
          <el-input type="textarea" :rows="2" v-model="form.details.instruments" placeholder="例如：计算机、PyCharm、JDK 1.8..." />
        </el-form-item>

        <el-form-item label="5. 实验(训)任务及要求">
          <el-input type="textarea" :rows="3" v-model="form.details.requirements" placeholder="请列出具体任务点和完成要求..." />
        </el-form-item>

        <el-form-item label="6. 实验(训)原理">
          <el-input type="textarea" :rows="4" v-model="form.details.principle" placeholder="简述实验涉及的理论基础或技术原理..." />
        </el-form-item>

        <el-form-item v-show="false">
          <el-select v-model="form.template"></el-select>
        </el-form-item>

      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createTask" :loading="creating">立即发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../http'
import { useRouter } from 'vue-router'
import { Plus, HomeFilled, DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const creating = ref(false)
const taskList = ref([])
const classList = ref([])
const dialogVisible = ref(false)
const formRef = ref(null)

const form = ref({
  title: '',
  target_class: '',
  template: '',
  end_time: '',
  // ★ 核心：把老师填的这几项打包存入 details
  details: {
    location: '',
    purpose: '',
    instruments: '',
    requirements: '',
    principle: ''
  }
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  target_class: [{ required: true, message: '请选择班级', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择时间', trigger: 'change' }]
}

const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await http.get('tasks/')
    taskList.value = res.data
  } catch (e) { console.error(e) } 
  finally { loading.value = false }
}

const fetchOptions = async () => {
  const cRes = await http.get('classes/')
  classList.value = cRes.data
  
  // 自动查找并选中“标准实验报告模板 (学生填写版)”
  const tRes = await http.get('templates/')
  const standard = tRes.data.find(t => t.title.includes('学生填写版'))
  if(standard) {
    form.value.template = standard.id
  } else if (tRes.data.length > 0) {
    form.value.template = tRes.data[0].id // 找不到就默认选第一个
  }
}

const openCreateDialog = () => {
  // 重置表单
  form.value.title = ''
  form.value.target_class = ''
  form.value.end_time = ''
  form.value.details = { location: '', purpose: '', instruments: '', requirements: '', principle: '' }
  dialogVisible.value = true
}

const createTask = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if(!form.value.template) return ElMessage.warning('系统未检测到模板，请联系管理员运行初始化脚本')

      // ★ 将 details 字段打包进 task_details 发送给后端
      const payload = {
        ...form.value,
        start_time: new Date().toISOString(),
        task_details: form.value.details // 对应后端的 JSONField
      }

      creating.value = true
      try {
        await http.post('tasks/', payload)
        ElMessage.success('发布成功')
        dialogVisible.value = false
        fetchTasks()
      } catch (e) { ElMessage.error('发布失败') }
      finally { creating.value = false }
    }
  })
}

const deleteTask = (id) => {
  ElMessageBox.confirm('确定删除该任务吗？', '警告', { type: 'warning' })
    .then(async () => {
      await http.delete(`tasks/${id}/`)
      ElMessage.success('已删除')
      fetchTasks()
    })
}

const goGrade = (taskId) => router.push(`/teacher/task/${taskId}/stats`)
const formatTime = (t) => t ? t.substring(0, 16).replace('T', ' ') : '-'

onMounted(() => {
  fetchTasks()
  fetchOptions()
})
</script>

<style scoped>
.dashboard-container { min-height: 100vh; background: #f5f7fa; }
.nav-bar { height: 60px; background: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 30px; box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05); }
.brand { font-size: 18px; font-weight: bold; color: #333; }
.content-area { padding: 30px; max-width: 1000px; margin: 0 auto; }
.guide-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 30px; color: #fff; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 8px 20px rgba(118, 75, 162, 0.3); }
.guide-text h3 { margin: 0 0 10px 0; font-size: 24px; }
.guide-text p { margin: 0; opacity: 0.9; }
.create-btn { background: #fff; color: #764ba2; border: none; font-weight: bold; }
</style>