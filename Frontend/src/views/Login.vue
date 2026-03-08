<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import axios from 'axios'

import { ElMessage } from 'element-plus'


const { t } = useI18n()
const router = useRouter()


const username = ref('')
const password = ref('')


const handleLogin = async () => {

  if (!username.value || !password.value) {
    ElMessage.warning(t('usernamePlace')) 
    return
  }

  try {
    
    const response = await axios.post('http://localhost:5000/api/login', {
      username: username.value,
      password: password.value
    })

    
    if (response.data.code === 200) {
      
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
  margin-left: 0; 
  margin-top: 15px;
}

</style>
