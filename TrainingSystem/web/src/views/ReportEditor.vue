<template>
  <div class="editor-container" v-loading="loading" element-loading-text="正在加载试卷...">
    
    <div class="editor-header">
      <el-page-header @back="goBack" :content="taskTitle || '实训报告编辑器'" />
      <div>
        <el-tag type="warning" style="margin-right: 10px;" v-if="reportStatus">{{ reportStatus }}</el-tag>
        <el-button type="primary" @click="saveReport">提交报告</el-button>
      </div>
    </div>

    <el-card class="paper-card">
      <div class="paper-content">
        
        <div v-for="(item, index) in templateStructure" :key="index" class="form-item">
          
          <h3 v-if="item.type === 'header'" class="section-title">{{ item.value }}</h3>
          
          <div v-if="item.type === 'input'" class="input-wrapper">
            <span class="label">{{ item.label }}：</span>
            <el-input v-model="formData[item.label]" :placeholder="'请输入' + item.label" />
          </div>

          <div v-if="item.type === 'textarea'" class="input-wrapper">
            <div class="label">{{ item.label }}：</div>
            <el-input 
              v-model="formData[item.label]" 
              type="textarea" 
              :rows="item.rows || 5" 
              placeholder="请输入详细内容..." 
            />
          </div>

        </div>

        <el-empty v-if="!loading && templateStructure.length === 0" description="模板加载为空，请检查后台是否配置了 JSON 结构" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '../http' // ★ 重点：必须用我们封装好的 http
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const taskId = route.params.id

const loading = ref(true)
const taskTitle = ref('')
const reportStatus = ref('')
const templateStructure = ref([])
const formData = ref({})

// --- 核心：加载数据 ---
const initEditor = async () => {
  try {
    // ★ 1. 获取任务详情 (使用 http，不用写完整网址)
    const taskRes = await http.get(`tasks/${taskId}/`)
    taskTitle.value = taskRes.data.title
    const templateId = taskRes.data.template
    
    // ★ 2. 获取模板结构
    const templateRes = await http.get(`templates/${templateId}/`)
    templateStructure.value = templateRes.data.content_structure
    
    console.log('加载成功:', templateStructure.value)

  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('无法加载实训任务，请检查登录状态或后端。')
  } finally {
    loading.value = false
  }
}

// --- 提交报告 ---
const saveReport = async () => {
  const payload = {
    task: taskId,
    content_data: formData.value,
    status: 'submitted'
  }

  try {
    // ★ 3. 提交数据
    await http.post('reports/', payload)
    
    ElMessage.success('作业提交成功！')
    reportStatus.value = '已提交'
    setTimeout(() => { router.back() }, 1000)

  } catch (error) {
    console.error('提交失败:', error)
    if (error.response && JSON.stringify(error.response.data).includes('unique')) {
      ElMessage.warning('你已经提交过这份作业了。')
    } else {
      ElMessage.error('提交失败，请重试')
    }
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  initEditor()
})
</script>

<style scoped>
.editor-container { padding: 20px; max-width: 900px; margin: 0 auto; min-height: 80vh; }
.editor-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.paper-card { min-height: 600px; padding: 20px; }
.section-title { margin-top: 30px; margin-bottom: 20px; border-left: 5px solid #409EFF; padding-left: 12px; font-size: 18px; color: #303133; }
.input-wrapper { margin-bottom: 25px; }
.label { font-weight: bold; margin-bottom: 10px; display: block; color: #606266; }
</style>