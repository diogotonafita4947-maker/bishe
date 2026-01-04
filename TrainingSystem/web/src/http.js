import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from './router'

// 1. 创建一个 axios 实例
const http = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/', // 后端基础地址
  timeout: 5000 // 超时时间
})

// 2. 请求拦截器：这就是“自动亮证机”
// 每次发请求前，都会经过这里
http.interceptors.request.use(config => {
  // 从浏览器缓存里取出令牌
  const token = localStorage.getItem('access_token')
  
  // 如果有令牌，就把它贴在请求头里
  if (token) {
    // 注意：后端 SimpleJWT 默认前缀是 "Bearer " (有一个空格)
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 3. 响应拦截器：处理后端返回的结果
http.interceptors.response.use(response => {
  return response
}, error => {
  // 如果后端返回 401，说明令牌过期或假的，强制踢回登录页
  if (error.response && error.response.status === 401) {
    ElMessage.error('登录已过期，请重新登录')
    localStorage.removeItem('access_token') // 清除旧令牌
    router.push('/login')
  }
  return Promise.reject(error)
})

export default http