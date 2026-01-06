<template>
    <div class="class-container">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span class="title">🏫 班级管理</span>
            
            <div class="actions">
               <el-button @click="router.push('/profile')" round style="margin-right: 10px;">
                <el-icon style="margin-right: 5px"><User /></el-icon> 个人中心
              </el-button>
              <el-button type="primary" @click="dialogVisible = true">
                <el-icon><Plus /></el-icon> 新建班级
              </el-button>
            </div>
          </div>
        </template>
  
        <el-table :data="classList" stripe v-loading="loading">
          <el-table-column prop="name" label="班级名称" min-width="150" />
          
          <el-table-column prop="invite_code" label="加入邀请码" width="150">
            <template #default="scope">
              <el-tag size="large" effect="dark" type="success" style="font-size: 16px; letter-spacing: 1px;">
                {{ scope.row.invite_code }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="created_at" label="创建时间" width="180">
             <template #default="scope">{{ formatTime(scope.row.created_at) }}</template>
          </el-table-column>
  
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button type="primary" plain size="small" @click="openMemberDialog(scope.row)">
                <el-icon style="margin-right: 4px"><UserFilled /></el-icon> 成员管理
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
  
      <el-dialog v-model="dialogVisible" title="创建新班级" width="400px">
        <el-form :model="form">
          <el-form-item label="班级名称" label-width="80px">
            <el-input v-model="form.name" placeholder="例如：2023级软件工程1班" />
          </el-form-item>
          <el-form-item label="邀请码" label-width="80px">
            <el-input v-model="form.invite_code" placeholder="输入6位字符，如：RJ2301" maxlength="6" />
            <div style="font-size: 12px; color: #999; line-height: 1.2; margin-top: 5px;">
              学生需要输入此代码才能加入班级。
            </div>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createClass">确定创建</el-button>
        </template>
      </el-dialog>
  
      <el-dialog v-model="memberDialogVisible" :title="`成员管理 - ${currentClass.name}`" width="600px">
        <div v-loading="memberLoading">
          <div style="margin-bottom: 15px; color: #666;">
            当前班级共 <span style="color: #409EFF; font-weight: bold;">{{ studentList.length }}</span> 人
          </div>
  
          <el-table :data="studentList" height="300" border>
            <el-table-column prop="username" label="姓名" />
            <el-table-column prop="student_id" label="学号" width="150">
              <template #default="scope">{{ scope.row.student_id || '-' }}</template>
            </el-table-column>
            
            <el-table-column label="操作" width="100" align="center">
              <template #default="scope">
                <el-button 
                  type="danger" 
                  link 
                  size="small" 
                  @click="removeStudent(scope.row)"
                >
                  移除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-dialog>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import http from '../http'
  import { useRouter } from 'vue-router'
  import { Plus, User, UserFilled } from '@element-plus/icons-vue' // 引入新图标
  import { ElMessage, ElMessageBox } from 'element-plus'
  
  const router = useRouter()
  const loading = ref(false)
  const classList = ref([])
  const dialogVisible = ref(false)
  const form = ref({ name: '', invite_code: '' })
  
  // 成员管理相关数据
  const memberDialogVisible = ref(false)
  const memberLoading = ref(false)
  const currentClass = ref({})
  const studentList = ref([])
  
  // 1. 获取班级列表
  const fetchClasses = async () => {
    loading.value = true
    try {
      const res = await http.get('classes/')
      classList.value = res.data
    } catch (error) {
      console.error(error)
    } finally {
      loading.value = false
    }
  }
  
  // 2. 创建班级
  const createClass = async () => {
    if(!form.value.name || !form.value.invite_code) return ElMessage.warning('请填写完整')
    try {
      await http.post('classes/', form.value)
      ElMessage.success('班级创建成功')
      dialogVisible.value = false
      form.value = { name: '', invite_code: '' }
      fetchClasses()
    } catch (error) {
      ElMessage.error('创建失败，可能是邀请码已存在')
    }
  }
  
  // 3. ★ 打开成员列表
  const openMemberDialog = async (row) => {
    currentClass.value = row
    memberDialogVisible.value = true
    fetchStudents(row.id)
  }
  
  // 4. ★ 获取该班级的所有学生
  const fetchStudents = async (classId) => {
    memberLoading.value = true
    try {
      // 调用我们刚写的后端筛选接口
      const res = await http.get(`users/?class_group=${classId}`)
      studentList.value = res.data
    } catch (error) {
      console.error(error)
      ElMessage.error('获取成员失败')
    } finally {
      memberLoading.value = false
    }
  }
  
  // 5. ★ 移除学生 (踢人)
  const removeStudent = (student) => {
    ElMessageBox.confirm(
      `确定要将学生 "${student.username}" 移除出本班级吗？`,
      '移除确认',
      { type: 'warning' }
    ).then(async () => {
      try {
        // 核心逻辑：把该用户的 class_group 字段设为 null
        await http.patch(`users/${student.id}/`, {
          class_group: null
        })
        ElMessage.success('移除成功')
        // 刷新列表
        fetchStudents(currentClass.value.id)
      } catch (error) {
        ElMessage.error('移除失败')
      }
    })
  }
  
  const formatTime = (t) => t ? t.substring(0, 10) : '-'
  
  onMounted(() => {
    fetchClasses()
  })
  </script>
  
  <style scoped>
  .class-container { padding: 20px; max-width: 1000px; margin: 0 auto; }
  .card-header { display: flex; justify-content: space-between; align-items: center; }
  .title { font-size: 18px; font-weight: bold; }
  </style>