<template>
    <div class="dashboard-container">
      <div class="nav-bar">
        <div class="brand">🎓 教师工作台</div>
        <div class="right-actions">
          <el-button class="add-btn" circle @click="dialogVisible = true" title="创建新班级">
            <el-icon><Plus /></el-icon>
          </el-button>
  
          <el-dropdown @command="handleCommand">
            <div class="avatar-box">
              <el-avatar :size="32" style="background: #E6A23C; font-size: 14px;">教</el-avatar>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
  
      <div class="content-area">
        <div class="welcome-bar">
          <h2>我管理的班级</h2>
          <p>共管理 {{ classList.length }} 个教学班级</p>
        </div>
  
        <div class="grid-layout" v-loading="loading">
          
          <div 
            v-for="cls in classList" 
            :key="cls.id" 
            class="course-card" 
            @click="handleClassClick(cls)"
          >
            <div class="card-cover" :style="{ background: getRandomGradient(cls.id) }">
              <span class="class-abbr">{{ cls.name.substring(0, 2) }}</span>
              <div class="cover-tag">邀请码: {{ cls.invite_code }}</div>
            </div>
            <div class="card-body">
              <div class="card-title">{{ cls.name }}</div>
              <div class="card-info">
                <span><el-icon><User /></el-icon> 学生管理</span>
                <el-divider direction="vertical" />
                <span><el-icon><EditPen /></el-icon> 发布任务</span>
              </div>
            </div>
          </div>
  
          <div class="create-card" @click="dialogVisible = true">
            <el-icon :size="40" color="#dcdfe6"><Plus /></el-icon>
            <p>创建新班级</p>
          </div>
  
        </div>
      </div>
  
      <el-dialog v-model="dialogVisible" title="创建新班级" width="400px" center>
        <el-form :model="form" label-position="top">
          <el-form-item label="班级名称">
            <el-input v-model="form.name" placeholder="例如：24级计算机应用4班" size="large" />
          </el-form-item>
          <el-form-item label="邀请码 (6位唯一代码)">
            <el-input v-model="form.invite_code" placeholder="如：RJ2404" maxlength="6" size="large">
              <template #prefix><el-icon><Key /></el-icon></template>
            </el-input>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createClass" :loading="creating">立即创建</el-button>
        </template>
      </el-dialog>
  
      <el-dialog v-model="actionDialogVisible" :title="currentClass.name" width="300px" center>
        <div class="action-list">
          <el-button type="primary" size="large" @click="goTasks(currentClass)" style="width: 100%; margin-bottom: 15px;">
            <el-icon style="margin-right: 5px"><Collection /></el-icon> 进入作业管理
          </el-button>
          <el-button plain size="large" @click="openMembers(currentClass)" style="width: 100%; margin-left: 0;">
            <el-icon style="margin-right: 5px"><User /></el-icon> 学生成员管理
          </el-button>
        </div>
      </el-dialog>
  
      <el-dialog v-model="memberDialogVisible" :title="currentClass.name + ' - 学生名单'" width="600px">
          <el-table :data="studentList" height="300" border stripe>
            <el-table-column prop="username" label="姓名" />
            <el-table-column prop="student_id" label="学号" />
            <el-table-column label="操作" width="100" align="center">
              <template #default="scope">
                <el-button type="danger" link size="small" @click="removeStudent(scope.row)">移出</el-button>
              </template>
            </el-table-column>
          </el-table>
      </el-dialog>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import http from '../http'
  import { useRouter } from 'vue-router'
  import { Plus, User, EditPen, Key, Collection } from '@element-plus/icons-vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  
  const router = useRouter()
  const loading = ref(false)
  const creating = ref(false)
  const classList = ref([])
  
  // 弹窗控制
  const dialogVisible = ref(false)
  const actionDialogVisible = ref(false)
  const memberDialogVisible = ref(false)
  
  const form = ref({ name: '', invite_code: '' })
  const currentClass = ref({})
  const studentList = ref([])
  
  // 1. 获取班级列表
  const fetchClasses = async () => {
    loading.value = true
    try {
      const res = await http.get('classes/')
      classList.value = res.data
    } catch (error) { console.error(error) } 
    finally { loading.value = false }
  }
  
  // 2. 创建班级
  const createClass = async () => {
    if(!form.value.name || !form.value.invite_code) return ElMessage.warning('请填写完整')
    creating.value = true
    try {
      await http.post('classes/', form.value)
      ElMessage.success('创建成功')
      dialogVisible.value = false
      form.value = { name: '', invite_code: '' }
      fetchClasses()
    } catch (e) { ElMessage.error('创建失败，邀请码可能已存在') }
    finally { creating.value = false }
  }
  
  // 3. 点击班级卡片 -> 弹出操作选择
  const handleClassClick = (cls) => {
    currentClass.value = cls
    actionDialogVisible.value = true
  }
  
  // 4. 跳转去发任务
  const goTasks = (cls) => {
    // 这里可以带上班级ID参数，或者直接去任务管理页
    router.push('/teacher/tasks')
  }
  
  // 5. 查看成员
  const openMembers = async (cls) => {
    actionDialogVisible.value = false
    memberDialogVisible.value = true
    const res = await http.get(`users/?class_group=${cls.id}`)
    studentList.value = res.data
  }
  
  const removeStudent = async (student) => {
      try {
          await ElMessageBox.confirm('确定移除该学生吗?', '提示', {type: 'warning'})
          await http.patch(`users/${student.id}/`, { class_group: null })
          ElMessage.success('已移除')
          const res = await http.get(`users/?class_group=${currentClass.value.id}`)
          studentList.value = res.data
      } catch(e) {}
  }
  
  const handleCommand = (cmd) => {
    if(cmd === 'logout') { localStorage.clear(); router.push('/login') }
    if(cmd === 'profile') router.push('/profile')
  }
  
  // 随机渐变色
  const getRandomGradient = (id) => {
    const gradients = [
      'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
      'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)',
      'linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)',
      'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    ]
    return gradients[id % gradients.length]
  }
  
  onMounted(() => fetchClasses())
  </script>
  
  <style scoped>
  .dashboard-container { min-height: 100vh; background: #f7f8fa; }
  .nav-bar { height: 56px; background: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
  .brand { font-size: 18px; font-weight: bold; color: #333; }
  .right-actions { display: flex; align-items: center; gap: 15px; }
  .add-btn { border: none; font-size: 20px; color: #606266; }
  .add-btn:hover { background: #f2f3f5; color: #409EFF; }
  
  .content-area { padding: 20px; max-width: 1000px; margin: 0 auto; }
  .welcome-bar { margin-bottom: 20px; }
  .welcome-bar h2 { margin: 0; font-weight: 600; color: #333; }
  .welcome-bar p { margin: 5px 0 0; color: #999; font-size: 14px; }
  
  /* 网格布局 */
  .grid-layout { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }
  
  /* 班级卡片 */
  .course-card { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); cursor: pointer; transition: transform 0.2s; }
  .course-card:hover { transform: translateY(-3px); box-shadow: 0 6px 16px rgba(0,0,0,0.1); }
  .card-cover { height: 110px; position: relative; padding: 15px; color: #fff; }
  .class-abbr { font-size: 36px; font-weight: bold; opacity: 0.3; }
  .cover-tag { position: absolute; right: 10px; top: 10px; background: rgba(0,0,0,0.2); padding: 2px 8px; border-radius: 4px; font-size: 12px; }
  
  .card-body { padding: 15px; }
  .card-title { font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .card-info { display: flex; align-items: center; justify-content: space-between; font-size: 13px; color: #666; }
  
  /* 创建卡片 */
  .create-card { height: 194px; background: #fff; border: 2px dashed #e0e0e0; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #909399; cursor: pointer; transition: all 0.2s; }
  .create-card:hover { border-color: #409EFF; color: #409EFF; background: #f0f9eb; }
  </style>