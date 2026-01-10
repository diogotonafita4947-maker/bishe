<template>
  <div class="admin-dashboard">
    <div class="header">
      <h2><el-icon><Monitor /></el-icon> 教务管理后台</h2>
      <div class="user-info">
        <el-tag type="warning">超级管理员</el-tag>
        <span class="username">{{ userStore.user.username || 'admin' }}</span>
        <el-button size="small" type="danger" plain @click="handleLogout">退出</el-button>
      </div>
    </div>

    <div class="upload-section">
      <div class="section-title"><el-icon><FolderOpened /></el-icon> 智能花名册导入</div>
      <div class="upload-box">
        <el-upload
          class="upload-dragger"
          drag
          action="#"
          :http-request="handleUpload"
          :show-file-list="false"
          accept=".xlsx, .xls"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将 .xlsx 文件拖到此处，或 <em>点击上传</em>
          </div>
        </el-upload>

        <div class="tips-box">
          <div class="tip-item active">
            <el-icon><User /></el-icon>
            <div class="t-content">
              <div class="t-title">学生 (自动识别)</div>
              <div class="t-desc">必需列：学号、姓名</div>
              <div class="t-desc">可选列：学院、专业、班级</div>
            </div>
          </div>
          <div class="tip-item">
            <el-icon><Avatar /></el-icon>
            <div class="t-content">
              <div class="t-title">教师 (自动识别)</div>
              <div class="t-desc">必需列：工号、姓名</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="list-section">
      <el-tabs v-model="activeTab" class="custom-tabs" @tab-change="fetchWhitelist">
        <el-tab-pane label="学生名单管理" name="student">
          <template #label>
            <span class="custom-label"><el-icon><User /></el-icon> 学生名单管理</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="教师名单管理" name="teacher">
          <template #label>
            <span class="custom-label"><el-icon><Avatar /></el-icon> 教师名单管理</span>
          </template>
        </el-tab-pane>
      </el-tabs>

      <div class="toolbar">
        <el-input 
          v-model="keyword" 
          :placeholder="activeTab==='student'?'搜索姓名、学号...':'搜索姓名、工号...'" 
          style="width: 300px" 
          clearable
          @clear="fetchWhitelist"
          @keyup.enter="fetchWhitelist"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="fetchWhitelist">查询</el-button>
        <div style="flex:1"></div>
        <el-tag type="info">共 {{ total }} 人</el-tag>
      </div>

      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="姓名" width="120" />
        
        <template v-if="activeTab === 'student'">
          <el-table-column prop="student_id" label="学号" width="150" sortable />
          <el-table-column prop="college" label="学院" />
          <el-table-column prop="major" label="专业" />
        </template>
        <template v-else>
          <el-table-column prop="teacher_id" label="工号" width="150" sortable />
        </template>

        <el-table-column prop="is_registered" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.is_registered ? 'success' : 'info'">
              {{ scope.row.is_registered ? '已注册' : '未激活' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled, FolderOpened, User, Avatar, Monitor, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import http from '../http'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('student')
const tableData = ref([])
const loading = ref(false)
const keyword = ref('')
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

onMounted(() => {
  fetchWhitelist()
})

// ★★★ 核心：获取名单数据 ★★★
const fetchWhitelist = async () => {
  loading.value = true
  try {
    const res = await http.get('users/get_whitelist/', {
      params: {
        type: activeTab.value,
        page: currentPage.value,
        pageSize: pageSize.value,
        keyword: keyword.value
      }
    })
    // 适配后端返回的 { total: 10, list: [...] } 格式
    tableData.value = res.data.list
    total.value = res.data.total
  } catch (e) {
    ElMessage.error('获取名单失败')
  } finally {
    loading.value = false
  }
}

// ★★★ 核心：上传文件 ★★★
const handleUpload = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  // 告诉后端我们要导入的是 student 还是 teacher，虽然后端有智能识别，传了更稳
  formData.append('type', activeTab.value) 

  try {
    // 注意接口名是 upload_roster
    const res = await http.post('users/upload_roster/', formData)
    ElMessage.success(res.data.message || '导入成功')
    
    // ★★★ 导入成功后，立即刷新下面的列表 ★★★
    fetchWhitelist()
    
  } catch (e) {
    console.error(e)
    ElMessage.error(e.response?.data?.error || '导入失败')
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchWhitelist()
}

const handleLogout = () => {
  userStore.clearUser()
  router.push('/login')
}
</script>

<style scoped>
.admin-dashboard { min-height: 100vh; background-color: #f5f7fa; padding-bottom: 30px; }
.header { height: 60px; background: #001529; color: #fff; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.header h2 { font-size: 18px; display: flex; align-items: center; gap: 10px; margin: 0; font-weight: 500; }
.user-info { display: flex; align-items: center; gap: 15px; }
.username { font-size: 14px; opacity: 0.9; }

.upload-section { margin: 20px auto; width: 90%; max-width: 1000px; background: #fff; border-radius: 8px; padding: 25px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.section-title { font-size: 16px; font-weight: bold; color: #333; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; border-left: 4px solid #409EFF; padding-left: 10px; }

.upload-box { display: flex; gap: 30px; align-items: flex-start; flex-wrap: wrap; }
.upload-dragger { width: 360px; }
.upload-dragger :deep(.el-upload-dragger) { border-radius: 8px; }

.tips-box { flex: 1; display: flex; flex-direction: column; gap: 15px; min-width: 280px; }
.tip-item { display: flex; gap: 15px; padding: 15px; border-radius: 8px; background: #f8f9fa; border: 1px solid #eee; transition: all 0.3s; }
.tip-item.active { background: #ecf5ff; border-color: #d9ecff; }
.tip-item .el-icon { font-size: 24px; color: #606266; margin-top: 2px; }
.tip-item.active .el-icon { color: #409EFF; }
.t-title { font-weight: bold; font-size: 14px; color: #303133; margin-bottom: 5px; }
.t-desc { font-size: 12px; color: #909399; line-height: 1.5; }

.list-section { margin: 0 auto; width: 90%; max-width: 1000px; background: #fff; border-radius: 8px; padding: 0 20px 20px 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.custom-tabs :deep(.el-tabs__nav-wrap::after) { height: 1px; background-color: #eee; }
.custom-tabs :deep(.el-tabs__item) { height: 55px; font-size: 15px; }
.custom-label { display: flex; align-items: center; gap: 6px; }

.toolbar { display: flex; gap: 10px; align-items: center; margin: 20px 0; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>