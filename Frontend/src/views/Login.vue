<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import axios from 'axios'
// 引入 Element Plus 的高级弹窗组件
import { ElMessage } from 'element-plus'

// 召唤翻译官和路由器
const { t } = useI18n()
const router = useRouter()

// 定义两个变量，用来绑定输入框里填写的账号和密码
const username = ref('')
const password = ref('')

// 点击登录按钮时触发的动作
const handleLogin = async () => {
  // 1. 简单的表单校验：没填东西不准点
  if (!username.value || !password.value) {
    ElMessage.warning(t('usernamePlace')) // 弹出黄色的警告提示
    return
  }

  try {
    // 2. 派 Axios 带着账号密码去 5000 端口敲门
    const response = await axios.post('http://localhost:5000/api/login', {
      username: username.value,
      password: password.value
    })

    // 3. 听听 Flask 后端怎么说
    if (response.data.code === 200) {
      // 🌟 【修改这里】不再用 response.data.msg
      ElMessage.success("🎉 " + t('msgLoginSuccess')) 

      localStorage.setItem('user_role', response.data.data.role)
      localStorage.setItem('username', response.data.data.username)
      
      router.push('/lobby')
    } else {
      ElMessage.error("❌ 失败：" + response.data.msg)
    }
  } catch (error) {
    console.error("登录出错：", error)
    ElMessage.error("网络请求失败，请检查后端是否运行！")
  }
}

// 返回首页的方法
const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="title">{{ t('loginTitle') }}</h2>

      <el-form label-position="top">
        <el-form-item :label="t('username')">
          <el-input v-model="username" :placeholder="t('usernamePlace')"></el-input>
        </el-form-item>

        <el-form-item :label="t('password')">
          <el-input v-model="password" type="password" :placeholder="t('passwordPlace')" show-password></el-input>
        </el-form-item>

        <el-button type="success" class="full-btn" @click="handleLogin">
          {{ t('loginBtn') }}
        </el-button>

        <el-button class="full-btn back-btn" @click="goBack" plain>
          {{ t('backHome') }}
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
/* 登录页面的背景和居中排版 */
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f4f8;
}
.login-card {
  width: 400px;
  padding: 10px 20px 20px 20px;
  border-radius: 12px;
}
.title {
  text-align: center;
  margin-bottom: 25px;
  color: #333;
}
.full-btn {
  width: 100%;
  margin-top: 15px;
}
.back-btn {
  margin-left: 0; /* 修正 Element Plus 默认的左边距 */
  margin-top: 15px;
}
</style>