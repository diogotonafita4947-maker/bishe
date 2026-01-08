<template>
    <div class="admin-container">
      <div class="nav-bar">
        <div class="brand">🛡️ 教务管理后台</div>
        <div class="user-info">
          <el-tag type="warning" style="margin-right:10px">超级管理员</el-tag>
          <span>{{ adminName }}</span>
          <el-button type="danger" size="small" plain @click="logout" style="margin-left: 15px">退出</el-button>
        </div>
      </div>
  
      <div class="content-area">
        
        <el-card shadow="hover" class="upload-card">
          <template #header>
            <div class="card-header">
              <span>📂 智能花名册导入</span>
              <el-button type="primary" link @click="showGuide = !showGuide">{{ showGuide ? '收起说明' : '查看格式说明' }}</el-button>
            </div>
          </template>
          
          <div class="card-body">
            <div class="upload-row">
              <div class="upload-area">
                <el-upload
                  class="upload-demo"
                  drag
                  action="#"
                  :auto-upload="false"
                  :on-change="handleUpload"
                  :show-file-list="false"
                  accept=".xlsx"
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">将 .xlsx 文件拖到此处，或 <em>点击上传</em></div>
                </el-upload>
              </div>
              
              <div class="format-guide" v-if="showGuide">
                 <div class="guide-item student-guide">
                    <div class="guide-title">👤 学生 (3列)</div>
                    <div class="guide-code">A:姓名 | B:学号 | C:班级</div>
                 </div>
                 <div class="guide-item teacher-guide">
                    <div class="guide-title">🎓 教师 (2列)</div>
                    <div class="guide-code">A:姓名 | B:工号</div>
                 </div>
              </div>
            </div>
          </div>
        </el-card>
  
        <el-card shadow="never" class="data-card">
          <el-tabs v-model="activeTab" class="custom-tabs">
            
            <el-tab-pane label="👤 学生名单管理" name="student">
              <div class="table-tool">
                <div class="left">
                  <el-input 
                    v-model="searchStudent" 
                    placeholder="搜索姓名、学号..." 
                    prefix-icon="Search" 
                    clearable
                    style="width: 250px; margin-right: 10px" 
                  />
                  <el-button type="primary" icon="Plus" @click="openAddDialog('student')">单独添加学生</el-button>
                </div>
                <el-tag type="info">共 {{ studentList.length }} 人</el-tag>
              </div>
  
              <el-table :data="filterStudents" stripe style="width: 100%" height="400">
                <el-table-column prop="name" label="姓名" width="120" />
                <el-table-column prop="student_id" label="学号" width="150" sortable />
                <el-table-column prop="class_name" label="行政班级" sortable />
                <el-table-column label="状态" width="100" align="center">
                  <template #default="scope">
                    <el-tag v-if="scope.row.is_registered" type="success" size="small">已激活</el-tag>
                    <el-tag v-else type="info" size="small">未注册</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="100" align="center">
                  <template #default="scope">
                    <el-popconfirm title="确定删除该学生吗?" @confirm="handleDelete('student', scope.row.id)">
                      <template #reference>
                         <el-button type="danger" link size="small">删除</el-button>
                      </template>
                    </el-popconfirm>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
  
            <el-tab-pane label="🎓 教师名单管理" name="teacher">
              <div class="table-tool">
                <div class="left">
                  <el-input 
                    v-model="searchTeacher" 
                    placeholder="搜索姓名或工号..." 
                    prefix-icon="Search" 
                    clearable
                    style="width: 250px; margin-right: 10px" 
                  />
                  <el-button type="success" icon="Plus" @click="openAddDialog('teacher')">单独添加教师</el-button>
                </div>
                <el-tag type="info">共 {{ teacherList.length }} 人</el-tag>
              </div>
  
              <el-table :data="filterTeachers" stripe style="width: 100%" height="400">
                <el-table-column prop="name" label="姓名" width="150" />
                <el-table-column prop="teacher_id" label="工号" width="150" sortable />
                <el-table-column label="状态" align="center">
                  <template #default="scope">
                    <el-tag v-if="scope.row.is_registered" type="success" size="small">已激活</el-tag>
                    <el-tag v-else type="info" size="small">未注册</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="100" align="center">
                  <template #default="scope">
                     <el-popconfirm title="确定删除该教师吗?" @confirm="handleDelete('teacher', scope.row.id)">
                      <template #reference>
                         <el-button type="danger" link size="small">删除</el-button>
                      </template>
                    </el-popconfirm>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
        
      </div>
  
      <el-dialog v-model="addVisible" :title="addForm.role === 'student' ? '添加学生' : '添加教师'" width="400px">
        <el-form :model="addForm" label-width="80px">
          <el-form-item label="姓名">
            <el-input v-model="addForm.name" placeholder="请输入姓名"></el-input>
          </el-form-item>
          <el-form-item :label="addForm.role === 'student' ? '学号' : '工号'">
            <el-input v-model="addForm.uid" placeholder="请输入数字ID"></el-input>
          </el-form-item>
          <el-form-item label="班级" v-if="addForm.role === 'student'">
            <el-input v-model="addForm.class_name" placeholder="例如：24计算机1班"></el-input>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="addVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmAdd">确定添加</el-button>
          </span>
        </template>
      </el-dialog>
  
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed, reactive } from 'vue'
  import { useRouter } from 'vue-router'
  import { UploadFilled, Warning, Search, Plus } from '@element-plus/icons-vue'
  import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
  import http from '../http'
  
  const router = useRouter()
  const adminName = ref('Admin')
  const showGuide = ref(true)
  const activeTab = ref('student')
  const studentList = ref([])
  const teacherList = ref([])
  const searchStudent = ref('')
  const searchTeacher = ref('')
  
  // 添加表单相关
  const addVisible = ref(false)
  const addForm = reactive({ role: 'student', name: '', uid: '', class_name: '' })
  
  onMounted(async () => {
    await fetchUserInfo()
    await fetchData()
  })
  
  const fetchUserInfo = async () => {
    try { const res = await http.get('users/me/'); adminName.value = res.data.username } catch(e) {}
  }
  
  const fetchData = async () => {
    try {
      const res = await http.get('users/get_whitelist/')
      studentList.value = res.data.students
      teacherList.value = res.data.teachers
    } catch(e) { ElMessage.error('获取名单数据失败') }
  }
  
  // 搜索过滤
  const filterStudents = computed(() => {
    if (!searchStudent.value) return studentList.value
    const q = searchStudent.value.toLowerCase()
    return studentList.value.filter(s => s.name.includes(q) || s.student_id.includes(q))
  })
  const filterTeachers = computed(() => {
    if (!searchTeacher.value) return teacherList.value
    const q = searchTeacher.value.toLowerCase()
    return teacherList.value.filter(t => t.name.includes(q) || t.teacher_id.includes(q))
  })
  
  // 打开添加弹窗
  const openAddDialog = (role) => {
    addForm.role = role
    addForm.name = ''
    addForm.uid = ''
    addForm.class_name = ''
    addVisible.value = true
  }
  
  // 确认添加
  const confirmAdd = async () => {
    if(!addForm.name || !addForm.uid) return ElMessage.warning('姓名和ID必填')
    if(addForm.role === 'student' && !addForm.class_name) return ElMessage.warning('学生必须填班级')
    
    try {
      await http.post('users/add_whitelist_item/', addForm)
      ElMessage.success('添加成功')
      addVisible.value = false
      await fetchData() // 刷新列表
    } catch(e) {
      ElMessage.error(e.response?.data?.error || '添加失败')
    }
  }
  
  // 删除功能
  const handleDelete = async (role, id) => {
    try {
      await http.post('users/delete_whitelist_item/', { role, id })
      ElMessage.success('删除成功')
      await fetchData() // 刷新列表
    } catch(e) {
      ElMessage.error('删除失败')
    }
  }
  
  // 上传逻辑 (同前，省略了部分重复注释)
  const handleUpload = async (uploadFile) => {
    if (!uploadFile.name.endsWith('.xlsx')) { ElMessage.error('必须是 .xlsx 文件！'); return }
    try {
      await ElMessageBox.confirm('确定导入吗？', '提示', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' })
      const loadingInstance = ElLoading.service({ lock: true, text: '处理中...', background: 'rgba(0,0,0,0.7)' })
      try {
        const fd = new FormData()
        fd.append('file', uploadFile.raw)
        const res = await http.post('users/upload_roster/', fd)
        ElMessage.success(res.data.message)
        await fetchData()
      } catch (reqError) {
        ElMessage.error(reqError.response?.data?.error || '导入失败')
      } finally { loadingInstance.close() }
    } catch(e) {}
  }
  
  const logout = () => { localStorage.removeItem('token'); router.push('/login') }
  </script>
  
  <style scoped>
  .admin-container { min-height: 100vh; background: #f0f2f5; display: flex; flex-direction: column; }
  .nav-bar { height: 60px; background: #001529; color: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; }
  .brand { font-size: 20px; font-weight: bold; }
  .content-area { flex: 1; padding: 30px; max-width: 1200px; margin: 0 auto; width: 100%; }
  .upload-card { margin-bottom: 20px; border-radius: 8px; }
  .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
  .upload-row { display: flex; gap: 20px; align-items: stretch; }
  .upload-area { flex: 1; }
  .format-guide { width: 300px; display: flex; flex-direction: column; gap: 10px; }
  .guide-item { padding: 10px; border-radius: 6px; font-size: 13px; }
  .student-guide { background: #ecf5ff; border: 1px solid #c6e2ff; }
  .teacher-guide { background: #f0f9eb; border: 1px solid #c2e7b0; }
  .guide-title { font-weight: bold; margin-bottom: 4px; }
  .guide-code { font-family: monospace; color: #666; }
  .data-card { border-radius: 8px; min-height: 500px; }
  .table-tool { display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; }
  .left { display: flex; align-items: center; }
  :deep(.el-upload-dragger) { padding: 20px; }
  </style>