import { createApp } from 'vue'
import App from './App.vue'
import router from './router' 
import ElementPlus from 'element-plus' 
import 'element-plus/dist/index.css' 
import i18n from './i18n' 
import axios from 'axios' // 引入 axios


axios.defaults.withCredentials = true 

const app = createApp(App)

app.use(router) 
app.use(ElementPlus) 
app.use(i18n) 
app.mount('#app')
