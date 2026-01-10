<template>
  <div class="dashboard-container">
    <div class="welcome-banner">
      <div class="left">
        <h2>你好，{{ realName }} 同学</h2>
        <p>已加入 {{ classes.length }} 个班级</p>
      </div>
      <div class="right">
        <el-button type="warning" plain @click="logout">退出登录</el-button>
      </div>
    </div>

    <div class="main-content">
      <div class="section-header">
        <div class="title"><el-icon><School /></el-icon> 我的班级</div>
        <el-button type="primary" size="large" icon="Plus" @click="dialogVisible = true">加入新班级</el-button>
      </div>

      <div class="class-grid" v-loading="loading">
        <el-empty v-if="classes.length === 0" description="您还没有加入任何班级，快去要邀请码吧！" />
        
        <el-card 
          v-for="cls in classes" 
          :key="cls.id" 
          class="class-card" 
          shadow="hover"
          @click="enterClass(cls)"
        >
          <div class="card-bg">
            <el-icon class="bg-icon"><Reading /></el-icon>
          </div>
          <div class="card-content">
            <h3 class="class-name">{{ cls.name }}</h3>
            <div class="class-info">
              <p><el-icon><User /></el-icon> 教师：{{ cls.teacher_name }}</p>
              <p><el-icon><Calendar /></el-icon> 加入时间：{{ new Date(cls.created_at).toLocaleDateString() }}</p>
            </div>
            <div class="enter-tip">点击进入课堂 <el-icon><Right /></el-icon></div>
          </div>
        </el-card>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="加入班级" width="400px">
      <el-input v-model="inviteCode" placeholder="请输入6位班级邀请码" size="large" prefix-icon="Key" />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="joinClass" :loading="joining">确认加入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
// ★★★ 修复点：将 Date 改为 Calendar ★★★
import { School, User, Calendar, Right, Reading, Key, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import http from '../http'

const router = useRouter()
const loading = ref(false)
const joining = ref(false)
const dialogVisible = ref(false)
const inviteCode = ref('')
const realName = ref('')
const classes = ref([])

onMounted(fetchData)

async function fetchData() {
  loading.value = true
  try {
    const res = await http.get('users/me/')
    realName.value = res.data.real_name || res.data.username
    classes.value = res.data.joined_classes || []
  } catch(e) {
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

const joinClass = async () => {
  if (!inviteCode.value) return ElMessage.warning('请输入邀请码')
  joining.value = true
  try {
    await http.post('classes/join_class/', { invite_code: inviteCode.value })
    ElMessage.success('加入成功！')
    dialogVisible.value = false
    inviteCode.value = ''
    fetchData() 
  } catch(e) {
    ElMessage.error(e.response?.data?.error || '加入失败')
  } finally {
    joining.value = false
  }
}

const enterClass = (cls) => {
  router.push(`/student/class/${cls.id}`)
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.dashboard-container { min-height: 100vh; background: #f5f7fa; }
.welcome-banner { background: #409EFF; color: #fff; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }
.main-content { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.title { font-size: 20px; font-weight: bold; display: flex; align-items: center; gap: 10px; color: #333; }

.class-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; }

.class-card { 
  border-radius: 12px; cursor: pointer; position: relative; overflow: hidden; border: none; 
  transition: transform 0.3s, box-shadow 0.3s;
}
.class-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }

.card-bg { position: absolute; right: -20px; top: -20px; opacity: 0.1; transform: rotate(15deg); }
.bg-icon { font-size: 150px; color: #409EFF; }

.card-content { position: relative; z-index: 1; padding: 10px; }
.class-name { margin: 0 0 15px; font-size: 18px; color: #333; }
.class-info p { margin: 5px 0; color: #666; font-size: 14px; display: flex; align-items: center; gap: 8px; }
.enter-tip { margin-top: 20px; color: #409EFF; font-size: 13px; font-weight: bold; display: flex; align-items: center; justify-content: flex-end; gap: 5px; opacity: 0; transition: opacity 0.3s; }
.class-card:hover .enter-tip { opacity: 1; }
</style>