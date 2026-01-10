import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 从 localStorage 获取用户信息，防止刷新丢失
  const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
  const token = ref(localStorage.getItem('token') || '')

  // 登录操作
  const setUser = (userData, tokenValue) => {
    user.value = userData
    token.value = tokenValue
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('token', tokenValue)
  }

  // 退出登录
  const clearUser = () => {
    user.value = {}
    token.value = ''
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  return { 
    user, 
    token, 
    setUser, 
    clearUser 
  }
})