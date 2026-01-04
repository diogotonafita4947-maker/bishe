<template>
    <div class="grade-container" v-loading="loading">
      <el-page-header @back="goBack" content="实训作业阅卷" style="margin-bottom: 20px;" />
  
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card shadow="never">
            <template #header>
              <div class="card-header">
                <span>{{ studentName }} 的实训报告</span>
                <el-tag>提交于: {{ submitTime }}</el-tag>
              </div>
            </template>
            
            <div class="paper-content">
              <div v-for="(item, index) in templateStructure" :key="index" class="form-item">
                <h3 v-if="item.type === 'header'" class="section-title">{{ item.value }}</h3>
                
                <div v-if="item.type === 'input'" class="qa-box">
                  <div class="question-label">{{ item.label }}</div>
                  <div class="answer-text">{{ studentData[item.label] || '（未填写）' }}</div>
                </div>
  
                <div v-if="item.type === 'textarea'" class="qa-box">
                  <div class="question-label">{{ item.label }}</div>
                  <div class="answer-box">{{ studentData[item.label] || '（未填写）' }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
  
        <el-col :span="8">
          <el-card shadow="hover" class="grade-panel">
            <template #header>
              <span style="font-weight: bold;">评分与评语</span>
            </template>
            
            <el-form label-position="top">
              <el-form-item label="给予分数 (0-100)">
                <el-input-number v-model="gradeForm.score" :min="0" :max="100" style="width: 100%" />
              </el-form-item>
              
              <el-form-item label="教师评语">
                <el-input v-model="gradeForm.teacher_comment" type="textarea" :rows="6" placeholder="请输入评语..." />
              </el-form-item>
  
              <el-button type="primary" style="width: 100%; margin-top: 10px;" @click="submitGrade">
                提交评分
              </el-button>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import http from '../http'
  import { ElMessage } from 'element-plus'
  
  const route = useRoute()
  const router = useRouter()
  const reportId = route.params.id // 获取网址里的报告ID
  
  const loading = ref(true)
  const studentName = ref('')
  const submitTime = ref('')
  const templateStructure = ref([]) // 题目结构
  const studentData = ref({})       // 学生填的答案
  
  // 评分表单
  const gradeForm = ref({
    score: 0,
    teacher_comment: ''
  })
  
  const initGrade = async () => {
    try {
      // 1. 获取这份报告的详细信息
      const reportRes = await http.get(`reports/${reportId}/`)
      const report = reportRes.data
      
      studentName.value = report.student_name
      submitTime.value = report.submitted_at ? report.submitted_at.substring(0, 16).replace('T', ' ') : '未知'
      studentData.value = report.content_data
      
      // 回显已有的分数（如果之前打过分）
      gradeForm.value.score = report.score || 80
      gradeForm.value.teacher_comment = report.teacher_comment || ''
  
      // 2. 获取对应的任务和模板，为了把题目显示出来
      const taskRes = await http.get(`tasks/${report.task}/`)
      const templateRes = await http.get(`templates/${taskRes.data.template}/`)
      
      templateStructure.value = templateRes.data.content_structure
  
    } catch (error) {
      console.error(error)
      ElMessage.error('加载失败')
    } finally {
      loading.value = false
    }
  }
  
  const submitGrade = async () => {
    try {
      // 发送 PATCH 请求更新部分字段
      await http.patch(`reports/${reportId}/`, gradeForm.value)
      ElMessage.success('评分已保存！')
      router.back()
    } catch (error) {
      ElMessage.error('保存失败')
    }
  }
  
  const goBack = () => {
    router.back()
  }
  
  onMounted(() => {
    initGrade()
  })
  </script>
  
  <style scoped>
  .grade-container { padding: 20px; max-width: 1200px; margin: 0 auto; }
  .section-title { margin-top: 20px; border-left: 4px solid #409EFF; padding-left: 10px; font-size: 16px; background-color: #f5f7fa; padding: 10px; }
  .qa-box { margin-bottom: 20px; padding: 10px; }
  .question-label { font-weight: bold; margin-bottom: 8px; color: #555; }
  .answer-text { border-bottom: 1px solid #eee; padding-bottom: 5px; color: #333; }
  .answer-box { background: #f9f9f9; padding: 10px; border-radius: 4px; border: 1px solid #eee; min-height: 50px; }
  .grade-panel { position: sticky; top: 20px; }
  </style>