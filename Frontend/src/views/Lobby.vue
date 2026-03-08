<script setup>
// 🌟 修复报错：把所有需要的工具都写在这一行里，绝对不重复！
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const { t, locale } = useI18n()
const router = useRouter()

const taskList = ref([])
const userRole = ref(parseInt(localStorage.getItem('user_role')) || 0)

const dialogVisible = ref(false)
const currentTask = ref({}) 
const postDialogVisible = ref(false)

// ====== 1. 融合了“分类”和“AI参数”的表单 ======
const postForm = ref({ 
  title: '', 
  desc: '', 
  category: 'delivery', // 默认分类
  time_est: 0.5,        // AI参数：预估耗时
  skill: 0.0,           // AI参数：技能门槛
  urgency: 0.0,         // AI参数：紧急程度
  points: 1             // 最终悬赏积分
})

// ====== 2. AI 动态定价专属变量 ======
const suggestedPoints = ref(1) 
const isCalculating = ref(false) 

// ====== 3. 带防抖的 AI 估价请求函数 ======
let timeoutId = null
const fetchSuggestedPrice = () => {
  if (timeoutId) clearTimeout(timeoutId)
  
  timeoutId = setTimeout(async () => {
    isCalculating.value = true 
    try {
      const res = await axios.post('http://localhost:5000/api/task/ai_suggest_price', {
        time_est: postForm.value.time_est,
        skill: postForm.value.skill,
        urgency: postForm.value.urgency
      })
      if (res.data.code === 200) {
        suggestedPoints.value = res.data.suggested_points
        // 如果用户当前的积分低于 AI 建议值，自动上调
        if (postForm.value.points < suggestedPoints.value) {
          postForm.value.points = suggestedPoints.value
        }
      }
    } catch (error) {
      console.error("AI 估价接口请求失败", error)
    } finally {
      isCalculating.value = false 
    }
  }, 500) 
}

// 监听这三个变量，一动就呼叫 AI
watch(
  () => [postForm.value.time_est, postForm.value.skill, postForm.value.urgency],
  () => { fetchSuggestedPrice() },
  { deep: true }
)

// ====== 4. 分类筛选专属逻辑 ======
const activeCategory = ref('all')
const filteredTasks = computed(() => {
  if (activeCategory.value === 'all') return taskList.value
  return taskList.value.filter(task => task.category === activeCategory.value)
})

const toggleLanguage = () => { locale.value = locale.value === 'zh' ? 'en' : 'zh' }

const handleLogout = async () => {
  try {
    await axios.post('http://localhost:5000/api/logout')
    ElMessage.success("已安全退出")
    localStorage.clear()
    router.push('/') 
  } catch (error) { console.error(error) }
}

const fetchTasks = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/tasks')
    if (response.data.code === 200) { taskList.value = response.data.data }
  } catch (error) {}
}

const openTaskDetail = (task) => { currentTask.value = task; dialogVisible.value = true }

const goToUserProfile = (username) => {
  dialogVisible.value = false
  router.push({ path: '/profile', query: { username: username } })
}

const claimTask = async () => {
  if (!confirm("确定要接下这个任务吗？ / Are you sure?")) return;
  try {
    const response = await axios.post('http://localhost:5000/api/task/claim', { task_id: currentTask.value.id })
    if (response.data.code === 200) {
      ElMessage.success("🎉 " + t('msgClaimSuccess'))
      dialogVisible.value = false; fetchTasks() 
    } else { ElMessage.error("❌ " + response.data.msg) }
  } catch (error) {}
}

const handlePostTask = async () => {
  if (!postForm.value.title || !postForm.value.desc) { 
    ElMessage.warning("请填写完整信息")
    return 
  }
  // 🌟 AI 底线防御
  if (postForm.value.points < suggestedPoints.value) {
    ElMessage.warning(`积分不可低于 AI 评估的底线：${suggestedPoints.value} 分`)
    return
  }

  try {
    const response = await axios.post('http://localhost:5000/api/task/post', {
      title: postForm.value.title,
      desc: postForm.value.desc,
      points: postForm.value.points,
      category: postForm.value.category
    })
    if (response.data.code === 200) {
      ElMessage.success("🎉 " + t('msgPostSuccess'))
      postDialogVisible.value = false 
      // 重置表单，恢复默认值
      postForm.value = { title: '', desc: '', category: 'delivery', time_est: 0.5, skill: 0.0, urgency: 0.0, points: 1 } 
      suggestedPoints.value = 1
      fetchTasks() 
    } else { ElMessage.error("❌ " + response.data.msg) }
  } catch (error) {}
}

const handleAdminDelete = async () => {
  try {
    await ElMessageBox.confirm(t('confirmAdminDelete'), t('tip'), { type: 'warning', confirmButtonText: t('confirm'), cancelButtonText: t('cancel') })
    const res = await axios.post('http://localhost:5000/api/admin/delete', { task_id: currentTask.value.id })
    if (res.data.code === 200) {
      ElMessage.success("🛡️ " + res.data.msg); dialogVisible.value = false; fetchTasks() 
    } else { ElMessage.error(res.data.msg) }
  } catch (e) {}
}

onMounted(() => { fetchTasks() })
</script>

<template>
  <div class="app-container">
    
    <div class="header">
      <h1 class="title">{{ t('lobbyTitle') }}</h1>
      <div class="header-actions">
        <el-button type="success" @click="postDialogVisible = true">{{ t('postTaskBtn') }}</el-button>
        <el-button type="primary" plain @click="router.push('/my-tasks')">{{ t('myTasksBtn') }}</el-button>
        <el-button type="warning" plain @click="router.push('/profile')">{{ t('profileBtn') }}</el-button>
        <el-button round @click="toggleLanguage" style="margin-left: 15px;">{{ t('switchLang') }}</el-button>
        <el-button type="danger" plain @click="handleLogout">{{ t('logoutBtn') }}</el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-radio-group v-model="activeCategory" size="large">
        <el-radio-button label="all">{{ t('catAll') }}</el-radio-button>
        <el-radio-button label="delivery">{{ t('cat_delivery') }}</el-radio-button>
        <el-radio-button label="study">{{ t('cat_study') }}</el-radio-button>
        <el-radio-button label="other">{{ t('cat_other') }}</el-radio-button>
      </el-radio-group>
    </div>
    
    <div class="task-grid">
      <div v-for="task in filteredTasks" :key="task.id" class="task-card" @click="openTaskDetail(task)">
        <h3 class="task-title">
          <el-tag size="small" type="info" style="margin-right: 8px; vertical-align: top;">
            {{ t('cat_' + (task.category || 'other')) }}
          </el-tag>
          {{ task.title }}
        </h3>
        <el-tag type="warning" effect="dark" round>
          {{ t('reward') }} {{ task.reward_points }}
        </el-tag>
      </div>
      <el-empty v-if="filteredTasks.length === 0" description="没有符合该分类的任务" style="grid-column: 1 / -1;"></el-empty>
    </div>

    <el-dialog v-model="dialogVisible" :title="t('taskDetail')" width="400px">
      <div v-if="currentTask.id" class="dialog-content">
        <h2>
          <el-tag size="small" type="info" style="margin-right: 8px;">{{ t('cat_' + (currentTask.category || 'other')) }}</el-tag>
          {{ currentTask.title }}
        </h2>
        <p class="dialog-desc">{{ currentTask.description }}</p>
        <div class="dialog-meta">
          <span>{{ t('publisher') }} <b class="clickable-name" @click="goToUserProfile(currentTask.publisher_name)">@{{ currentTask.publisher_name }}</b></span>
          <span style="color: #ff9800; font-weight: bold;">{{ t('reward') }} {{ currentTask.reward_points }} {{ t('points') }}</span>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">{{ t('closeBtn') }}</el-button>
          <el-button v-if="userRole === 1" type="danger" @click="handleAdminDelete">{{ t('adminDeleteBtn') }}</el-button>
          <el-button type="success" @click="claimTask">{{ t('helpBtn') }}</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="postDialogVisible" :title="t('postTaskBtn')" width="500px">
      <el-form label-position="top">
        
        <el-form-item :label="t('taskCategory')">
          <el-select v-model="postForm.category" style="width: 100%">
            <el-option :label="t('cat_delivery')" value="delivery" />
            <el-option :label="t('cat_study')" value="study" />
            <el-option :label="t('cat_other')" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item :label="t('postTitle')">
          <el-input v-model="postForm.title" :placeholder="t('postTitlePlace')"></el-input>
        </el-form-item>
        <el-form-item :label="t('postDesc')">
          <el-input type="textarea" :rows="3" v-model="postForm.desc" :placeholder="t('postDescPlace')"></el-input>
        </el-form-item>

        <div class="ai-params-box">
          <el-form-item :label="t('aiTimeEst')">
            <el-input-number v-model="postForm.time_est" :min="0.5" :step="0.5" style="width: 100%"></el-input-number>
          </el-form-item>

          <el-form-item :label="t('aiSkill')">
            <el-select v-model="postForm.skill" style="width: 100%">
              <el-option :label="t('aiSkill0')" :value="0.0" />
              <el-option :label="t('aiSkill1')" :value="0.5" />
              <el-option :label="t('aiSkill2')" :value="1.0" />
            </el-select>
          </el-form-item>

          <el-form-item :label="t('aiUrgency')">
            <el-switch
              v-model="postForm.urgency"
              :active-value="1.0"
              :inactive-value="0.0"
              :active-text="t('aiUrgUrgent')"
              :inactive-text="t('aiUrgNormal')"
              style="--el-switch-on-color: #ff4949; --el-switch-off-color: #13ce66"
            />
          </el-form-item>
        </div>

        <div class="ai-suggestion-panel" v-loading="isCalculating" element-loading-background="rgba(240, 248, 255, 0.8)">
          <div class="ai-icon">✨ DTVC-Net</div>
          <div class="ai-text">
            {{ t('aiSuggestTitle') }} <strong>{{ suggestedPoints }}</strong> {{ t('aiSuggestUnit') }}
          </div>
        </div>

        <el-form-item :label="t('aiFinalPoints')">
          <el-input-number v-model="postForm.points" :min="suggestedPoints" :max="999"></el-input-number>
        </el-form-item>

      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="postDialogVisible = false">{{ t('closeBtn') }}</el-button>
          <el-button type="primary" @click="handlePostTask">{{ t('submitPost') }}</el-button>
        </span>
      </template>
    </el-dialog>
    
  </div>
</template>

<style scoped>
.app-container { max-width: 1000px; margin: 0 auto; padding: 30px 20px; font-family: sans-serif; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.title { color: #333; margin: 0; }
.header-actions { display: flex; gap: 10px; align-items: center; }

/* 🌟 分类标签栏样式 */
.filter-bar { display: flex; justify-content: center; margin-bottom: 30px; }

.task-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.task-card { border: 1px solid #ebeef5; border-radius: 10px; padding: 20px; background-color: #fff; cursor: pointer; transition: all 0.3s ease; display: flex; flex-direction: column; justify-content: space-between; min-height: 120px; }
.task-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.08); border-color: #c6e2ff; }
.task-title { margin: 0 0 15px 0; color: #2c3e50; font-size: 16px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.dialog-content h2 { margin-top: 0; color: #333; }
.dialog-desc { color: #666; line-height: 1.6; background: #f5f7fa; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
.dialog-meta { display: flex; justify-content: space-between; font-size: 14px; color: #888; }
.clickable-name { color: #409EFF; cursor: pointer; transition: color 0.2s; }
.clickable-name:hover { color: #79bbff; text-decoration: underline; }

/* ====== 🤖 AI 深度学习定价面板样式 ====== */
.ai-params-box {
  background-color: #fafafa;
  padding: 15px;
  border-radius: 8px;
  border: 1px dashed #dcdfe6;
  margin-bottom: 20px;
}
.ai-suggestion-panel {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  color: #fff;
  box-shadow: 0 4px 12px rgba(142, 197, 252, 0.4);
}
.ai-icon {
  font-weight: bold;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  margin-right: 15px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
.ai-text { font-size: 15px; }
.ai-text strong {
  font-size: 20px;
  color: #fffacd; 
  margin: 0 5px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}
</style>

