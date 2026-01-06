<template>
    <div class="profile-container">
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>👤 个人中心</span>
          </div>
        </template>
  
        <div class="user-info">
          <div class="info-item">
            <span class="label">用户名：</span>
            <span class="value">{{ user.username }}</span>
          </div>
          <div class="info-item">
            <span class="label">身份：</span>
            <el-tag>{{ user.role === 'teacher' ? '教师' : '学生' }}</el-tag>
          </div>
  
          <el-divider />
  
          <div v-if="user.role === 'student'" class="class-section">
            <h3>🏫 我的班级</h3>
            
            <div v-if="user.class_group" class="has-class">
              <el-alert type="success" :closable="false" show-icon>
                <template #title>
                  已加入：<span style="font-weight: bold; font-size: 16px;">{{ user.class_group_name }}</span>
                </template>
              </el-alert>
            </div>
  
            <div v-else class="no-class">
              <el-alert 
                title="您尚未加入任何班级，无法接收实训任务！" 
                type="warning" 
                :closable="false" 
                show-icon 
                style="margin-bottom: 15px;" 
              />
              <div class="join-box">
                <el-input 
                  v-model="inviteCode" 
                  placeholder="请输入6位邀请码" 
                  style="margin-right: 10px;" 
                  maxlength="6"
                >
                  <template #prefix><el-icon><Key /></el-icon></template>
                </el-input>
                <el-button type="primary" @click="joinClass" :loading="joining">加入</el-button>
              </div>
            </div>
          </div>
  
          <el-divider />
  
          <el-button type="danger" plain style="width: 100%" @click="handleLogout">
            <el-icon style="margin-right: 5px"><SwitchButton /></el-icon> 退出登录
          </el-button>
        </div>
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import http from '../http'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { Key, SwitchButton } from '@element-plus/icons-vue'
  
  const router = useRouter()
  const user = ref({})
  const inviteCode = ref('')
  const joining = ref(false)
  
  // 1. 获取个人信息
  const fetchProfile = async () => {
    try {
      const res = await http.get('users/me/')
      user.value = res.data
    } catch (error) {
      console.error(error)
    }
  }
  
  // 2. 加入班级逻辑
  const joinClass = async () => {
    if (!inviteCode.value) return ElMessage.warning('请输入邀请码')
    
    joining.value = true
    try {
      // 第一步：先去后台查这个邀请码对应的班级ID
      // 注意：这里我们简单粗N暴地拉取所有班级并在前端匹配。
      // 实际生产环境应该写一个后端接口 /classes/check_code?code=xxx
      const allClassRes = await http.get('classes/')
      const targetClass = allClassRes.data.find(c => c.invite_code === inviteCode.value)
      
      if (!targetClass) {
        ElMessage.error('邀请码无效，找不到该班级')
        joining.value = false
        return
      }
  
      // 第二步：更新用户的 class_group 字段
      await http.patch(`users/${user.value.id}/`, {
        class_group: targetClass.id
      })
  
      ElMessage.success(`恭喜！成功加入 ${targetClass.name}`)
      inviteCode.value = ''
      fetchProfile() // 刷新显示
  
    } catch (error) {
      console.error(error)
      ElMessage.error('加入失败，请重试')
    } finally {
      joining.value = false
    }
  }
  
  // 3. 退出登录逻辑
  const handleLogout = () => {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '退出',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      localStorage.clear() // 清除 Token
      router.push('/login') // 回到登录页
      ElMessage.success('已安全退出')
    })
  }
  
  onMounted(() => {
    fetchProfile()
  })
  </script>
  
  <style scoped>
  .profile-container { padding: 40px 20px; display: flex; justify-content: center; }
  .box-card { width: 100%; max-width: 480px; }
  .card-header { font-size: 18px; font-weight: bold; }
  .info-item { display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 16px; }
  .label { color: #606266; }
  .join-box { display: flex; margin-top: 10px; }
  </style>