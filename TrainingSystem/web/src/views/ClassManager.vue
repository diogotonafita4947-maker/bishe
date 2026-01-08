<template>
  <div class="class-container">
    <div class="header">
      <h2>我的教学班级</h2>
      <el-button type="primary" icon="Plus" @click="dialogVisible = true">创建新班级</el-button>
    </div>

    <div class="class-list" v-loading="loading">
      <el-empty v-if="classes.length === 0" description="暂无班级，请创建后将邀请码发给学生" />
      
      <el-card v-for="cls in classes" :key="cls.id" class="class-card" shadow="hover">
        <template #header>
          <div class="card-title">
            <span>{{ cls.name }}</span>
            <el-tag size="large" effect="dark" type="warning" style="font-weight:bold; letter-spacing:1px">
              邀请码: {{ cls.invite_code }}
            </el-tag>
          </div>
        </template>
        <div class="card-content">
          <div class="info-row">
            <span class="label">学生人数：</span>
            <span class="val">{{ cls.student_count || 0 }} 人</span>
          </div>
          <p class="tip">邀请码由系统随机生成，请告知学生。</p>
          <div class="btn-group">
            <el-button type="primary" link @click="viewStudents(cls)">管理名单</el-button>
            <el-popconfirm title="确定解散该班级吗？" @confirm="deleteClass(cls.id)">
              <template #reference>
                <el-button type="danger" link>解散</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </el-card>
    </div>

    <el-dialog v-model="dialogVisible" title="创建教学班级" width="400px">
      <el-form :model="form">
        <el-form-item label="班级名称">
          <el-input v-model="form.name" placeholder="例如：Java实训-周三班" />
        </el-form-item>
        <el-alert title="邀请码将由系统自动生成，确保不重复" type="info" :closable="false" show-icon />
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createClass">立即创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="studentVisible" :title="currentClass?.name + ' - 学生名单'" width="600px">
      <el-table :data="studentList" stripe height="400">
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="student_id" label="学号" width="150" />
        <el-table-column label="操作" align="center">
          <template #default="scope">
            <el-button type="danger" link size="small">移出班级</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import http from '../http'

const loading = ref(false)
const classes = ref([])
const dialogVisible = ref(false)
const studentVisible = ref(false)
const currentClass = ref(null)
const studentList = ref([])

const form = reactive({ name: '' })

onMounted(() => {
  fetchClasses()
})

const fetchClasses = async () => {
  loading.value = true
  try {
    const res = await http.get('classes/')
    classes.value = res.data
    classes.value.forEach(async (cls) => {
      const sRes = await http.get(`classes/${cls.id}/students/`)
      cls.student_count = sRes.data.length
    })
  } catch (e) {
    ElMessage.error('获取班级失败')
  } finally {
    loading.value = false
  }
}

const createClass = async () => {
  if (!form.name) return ElMessage.warning('请输入班级名称')
  try {
    // 只有 name，没有 invite_code，后端会自动生成
    await http.post('classes/', form)
    ElMessage.success('创建成功！')
    dialogVisible.value = false
    form.name = ''
    fetchClasses()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '创建失败')
  }
}

const deleteClass = async (id) => {
  try {
    await http.delete(`classes/${id}/`)
    ElMessage.success('已解散')
    fetchClasses()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const viewStudents = async (cls) => {
  currentClass.value = cls
  studentVisible.value = true
  try {
    const res = await http.get(`classes/${cls.id}/students/`)
    studentList.value = res.data
  } catch (e) {
    ElMessage.error('获取名单失败')
  }
}
</script>

<style scoped>
.class-container { padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.class-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
.class-card { border-radius: 8px; }
.card-title { display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 16px; }
.card-content { padding: 10px 0; }
.info-row { font-size: 14px; margin-bottom: 10px; }
.tip { font-size: 12px; color: #909399; margin-bottom: 15px; background: #f4f4f5; padding: 8px; border-radius: 4px; }
.btn-group { border-top: 1px solid #eee; padding-top: 10px; display: flex; justify-content: flex-end; gap: 10px; }
</style>