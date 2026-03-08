<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
// 🌟 引入 useRoute，它是专门用来读取网址参数的“眼睛”
import { useRouter, useRoute } from 'vue-router' 
import { ElMessage } from 'element-plus'

const { t } = useI18n()
const router = useRouter()
const route = useRoute() // 实例化这双“眼睛”

const userInfo = ref({
  username: '',
  balance: 0,
  role: 0,
  feedbacks: []
})

const fetchProfile = async () => {
  try {
    // 1. 去网址上找找有没有 ?username=xxx
    const targetUsername = route.query.username 
    
    // 2. 带着这个名字去敲后端的门（如果 targetUsername 是空的，Axios 就会正常查自己）
    const res = await axios.get('http://localhost:5000/api/profile', {
      params: { username: targetUsername }
    })
    
    if (res.data.code === 200) {
      userInfo.value = res.data.data
    } else {
      ElMessage.error(res.data.msg)
      router.push('/lobby')
    }
  } catch (e) {
    ElMessage.error("网络错误")
  }
}

// 页面刚加载时，查一次数据
onMounted(() => {
  fetchProfile()
})

// 🌟 新增的高级魔法：监听网址变化。
// 如果用户本来就在看别人的主页，又点了一个别的名字，页面数据需要实时刷新
watch(() => route.query.username, () => {
  fetchProfile()
})
</script>

<template>
  <div class="profile-container">
    <div class="header">
      <h2>{{ t('profileTitle') }}</h2>
      <el-button @click="router.push('/lobby')" plain>{{ t('backLobby') }}</el-button>
    </div>

    <el-card class="info-card">
      <div class="info-content"> <div class="user-main">
          <el-avatar :size="80" style="background-color: #4CAF50; font-size: 30px;">
            {{ userInfo.username.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="user-text">
            <h1>{{ userInfo.username }}</h1>
            <el-tag :type="userInfo.role === 1 ? 'danger' : 'info'">
              {{ userInfo.role === 1 ? t('roleAdmin') : t('roleUser') }}
            </el-tag>
          </div>
        </div>
        
        <div class="balance-box">
          <p>{{ t('myBalance') }}</p>
          <h2 class="points">💰 {{ userInfo.balance }}</h2>
        </div>
      </div> 
    </el-card>

    <el-card class="reviews-card">
      <h3>⭐ {{ t('receivedReviews') }}</h3>
      <div v-if="userInfo.feedbacks.length > 0">
        <div v-for="(fb, index) in userInfo.feedbacks" :key="index" class="review-item">
          <div class="review-header">
            <b>{{ fb.from_user }}</b> 给了你评价：
            <el-rate v-model="fb.rating" disabled show-score text-color="#ff9900" />
          </div>
          <p class="review-content">"{{ fb.content }}"</p>
        </div>
      </div>
      <el-empty v-else :description="t('noReviews')"></el-empty>
    </el-card>

  </div>
</template>

<style scoped>
.profile-container { max-width: 800px; margin: 0 auto; padding: 30px 20px; font-family: sans-serif; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.info-card { margin-bottom: 20px; }
/* 修复了这里：不再强制所有卡片横向排版 */
.info-content { display: flex; width: 100%; justify-content: space-between; align-items: center; }
.user-main { display: flex; align-items: center; gap: 20px; }
.user-text h1 { margin: 0 0 10px 0; color: #333; }
.balance-box { text-align: right; }
.balance-box p { margin: 0 0 5px 0; color: #666; font-size: 14px; }
.points { margin: 0; color: #ff9800; font-size: 36px; }
.reviews-card h3 { margin-top: 0; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.review-item { border-bottom: 1px dashed #eee; padding: 15px 0; }
.review-item:last-child { border-bottom: none; }
.review-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; color: #555; }
.review-content { color: #333; font-style: italic; background: #f5f7fa; padding: 15px; border-radius: 6px; margin: 0; }
</style>