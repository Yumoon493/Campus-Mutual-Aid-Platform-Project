import { createApp } from 'vue'
import App from './App.vue'
import router from './router' 
import ElementPlus from 'element-plus' 
import 'element-plus/dist/index.css' 
import i18n from './i18n' 
import axios from 'axios' // 引入 axios

// 【核心修复】告诉 Axios：以后无论去哪个页面发请求，都必须带上凭证！
axios.defaults.withCredentials = true 

const app = createApp(App)

app.use(router) 
app.use(ElementPlus) 
app.use(i18n) 
app.mount('#app')