<script setup>
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const { t, locale } = useI18n()
const router = useRouter()

// 设置语言的方法
const setLanguage = (lang) => {
  locale.value = lang
}

// 路由跳转方法
const goToLogin = () => {
  router.push('/login')
}
const goToRegister = () => {
  router.push('/register') // 跳转到注册页
}
</script>

<template>
  <div class="home-container">
    
    <div class="content">
      <img src="https://img.icons8.com/illustrations/external-pack-flat-juicy-fish-outline-juicy-fish/256/external-campus-university-pack-flat-juicy-fish-outline-juicy-fish.png" class="logo" />
      
      <h1 class="title">{{ t('welcome') }}</h1>
      <p class="subtitle">{{ t('subtitle') }}</p>

      <div class="actions">
        <el-button type="success" size="large" @click="goToLogin">{{ t('loginBtn') }}</el-button>
        <el-button type="primary" size="large" plain @click="goToRegister">{{ t('registerBtn') }}</el-button>
      </div>
    </div>

    <div class="lang-bottom">
      <el-button 
        :type="locale === 'zh' ? 'primary' : 'default'" 
        size="large" 
        @click="setLanguage('zh')">
        🇨🇳 中文
      </el-button>
      
      <el-button 
        :type="locale === 'en' ? 'primary' : 'default'" 
        size="large" 
        @click="setLanguage('en')">
        🇬🇧 English
      </el-button>
    </div>

  </div>
</template>

<style scoped>
.home-container {
  height: 100vh;
  display: flex;
  flex-direction: column; /* 改为纵向排列以便放底部元素 */
  justify-content: center;
  align-items: center;
  background-color: #f0f4f8; 
  position: relative;
}
.content {
  text-align: center;
  max-width: 600px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.05);
  margin-bottom: 80px; /* 给底部按钮留出空间 */
}
.logo {
  width: 150px;
  margin-bottom: 20px;
}
.title {
  color: #333;
  font-size: 28px;
  margin-bottom: 15px;
}
.subtitle {
  color: #666;
  line-height: 1.8;
  margin-bottom: 30px;
}
.actions {
  display: flex;
  gap: 20px;
  justify-content: center;
}
/* 底部语言按钮的样式 */
.lang-bottom {
  position: absolute;
  bottom: 50px; /* 距离底部 50px */
  display: flex;
  gap: 30px; /* 两个按钮的间距 */
}
</style>