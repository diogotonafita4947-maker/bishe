<template>
  <div class="overview-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <h3>我的班级</h3>
          <div class="num">{{ stats.class_count || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <h3>已发布任务</h3>
          <div class="num">{{ stats.task_count || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <h3>待批阅</h3>
          <div class="num">{{ stats.report_count || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <div style="margin-top: 30px;">
      <el-button type="primary" size="large" icon="Plus" @click="$router.push('/teacher/tasks')">
        发布新任务
      </el-button>
      <el-button type="success" size="large" icon="User" @click="$router.push('/teacher/classes')">
        班级管理
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus, User } from '@element-plus/icons-vue'
const stats = ref({}) 
</script>

<style scoped>
.overview-container { padding: 20px; }
.stat-card { text-align: center; }
.num { font-size: 32px; font-weight: bold; color: #409EFF; margin-top: 10px; }
</style>