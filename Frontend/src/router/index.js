import { createRouter, createWebHistory } from 'vue-router'
import Lobby from '../views/Lobby.vue'
import Login from '../views/Login.vue'

import Home from '../views/Home.vue' // 引入新建的首页
import Register from '../views/Register.vue' // 引入注册页
import MyTasks from '../views/MyTasks.vue' // 【新增这一行】引入个人中心
import Profile from '../views/Profile.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },      // 【修改这里】访问根目录时，展示漂亮的首页
    { path: '/lobby', component: Lobby }, // 访问 /lobby 时，展示 Lobby.vue
    { path: '/login', component: Login } , // 访问 /login 时，展示 Login.vue
    { path: '/register', component: Register }, // 添加注册页的导航路线
    { path: '/my-tasks', component: MyTasks }, // 【新增这一行】添加路由
    { path: '/profile', component: Profile }
  ]
})

export default router