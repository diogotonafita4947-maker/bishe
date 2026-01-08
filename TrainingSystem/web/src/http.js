import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from './router'

const http = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  timeout: 5000
})

// ★★★ 请求拦截器：自动携带 Token ★★★
http.interceptors.request.use(config => {
  // 每次请求前，都去 localStorage 拿最新的 token
  const token = localStorage.getItem('token')
  if (token) {
    // 注意：Bearer 后面有个空格
    config.headers.Authorization = 'Bearer ' + token
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器
http.interceptors.response.use(response => {
  return response
}, error => {
  if (error.response) {
    // 401 代表 Token 过期或无效
    if (error.response.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      router.push('/login')
    } else {
      ElMessage.error(error.response.data.detail || '请求出错')
    }
  } else {
    ElMessage.error('网络连接失败')
  }
  return Promise.reject(error)
})

export default http