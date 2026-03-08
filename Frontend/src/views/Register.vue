<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const { t } = useI18n()
const router = useRouter()

// 绑定的表单数据
const username = ref('')
const email = ref('')
const password = ref('')

// 点击注册按钮的方法
const handleRegister = async () => {
  if (!username.value || !email.value || !password.value) {
    ElMessage.warning(t('usernamePlace') + " / " + t('emailPlace'))
    return
  }

  try {
    const response = await axios.post('http://localhost:5000/api/register', {
      username: username.value,
      email: email.value,
      password: password.value
    })

    if (response.data.code === 200) {
      ElMessage.success("🎉 " + response.data.msg)
      router.push('/login') // 注册成功，自动跳转去登录页
    } else {
      ElMessage.error("❌ " + response.data.msg) // 比如用户名已存在
    }
  } catch (error) {
    ElMessage.error("网络请求失败！")
  }
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="reg-container">
    <el-card class="reg-card">
      <h2 class="title">{{ t('regTitle') }}</h2>

      <el-form label-position="top">
        <el-form-item :label="t('username')">
          <el-input v-model="username" :placeholder="t('usernamePlace')"></el-input>
        </el-form-item>

        <el-form-item :label="t('email')">
          <el-input v-model="email" type="email" :placeholder="t('emailPlace')"></el-input>
        </el-form-item>

        <el-form-item :label="t('password')">
          <el-input v-model="password" type="password" :placeholder="t('passwordPlace')" show-password></el-input>
        </el-form-item>

        <el-button type="primary" class="full-btn" @click="handleRegister">
          {{ t('regActionBtn') }}
        </el-button>

        <el-button class="full-btn back-btn" @click="goBack" plain>
          {{ t('backHome') }}
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.reg-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f4f8;
}
.reg-card {
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