import { createApp } from 'vue'
import { createPinia } from 'pinia' // 必须引入这个
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

// 注册图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia()) // ★★★ 必须有这一行 ★★★
app.use(router)
app.use(ElementPlus)
app.mount('#app')