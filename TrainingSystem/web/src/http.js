import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const http = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/', // 你的后端地址
  timeout: 5000
})

// ★ 核心：请求拦截器 (每次发请求前都会执行这里)
http.interceptors.request.use(config => {
  // 1. 从浏览器缓存里取出 Token
  const token = localStorage.getItem('access_token')

  // 2. 如果有 Token，就把它加到请求头里
  if (token) {
    // 注意：JWT 标准格式通常是 'Bearer ' + token
    config.headers.Authorization = 'Bearer ' + token
  }

  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器 (后端返回结果后会执行这里)
http.interceptors.response.use(response => {
  return response
}, error => {
  // 统一处理报错
  if (error.response) {
    if (error.response.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      // 可以在这里加跳转回登录页的逻辑
      // window.location.href = '/login'
    } else if (error.response.status === 403) {
      ElMessage.error('没有权限执行此操作')
    } else {
      ElMessage.error('服务器出错: ' + error.response.status)
    }
  } else {
    ElMessage.error('网络连接失败')
  }
  return Promise.reject(error)
})

export default http