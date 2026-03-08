<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const { t } = useI18n()
const router = useRouter()

// 存储任务列表
const publishedTasks = ref([])
const takenTasks = ref([])
const activeTab = ref('published') // 默认显示“我发布的”

// 评价弹窗相关变量
const rateDialogVisible = ref(false)
const currentRateTask = ref(null)
const rateScore = ref(5) // 默认 5 星
const rateContent = ref('')

// 获取我的任务数据
const fetchMyTasks = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/my_tasks')
    if (response.data.code === 200) {
      publishedTasks.value = response.data.data.published_tasks
      takenTasks.value = response.data.data.taken_tasks
    } else {
      ElMessage.error(response.data.msg)
    }
  } catch (error) {
    ElMessage.error("获取数据失败")
  }
}

// 1. 撤销任务
const handleRevoke = async (taskId) => {
  try {
    await ElMessageBox.confirm(t('confirmRevoke'), t('tip'), { 
      type: 'warning',
      confirmButtonText: t('confirm'),
      cancelButtonText: t('cancel')
    })
    const res = await axios.post('http://localhost:5000/api/task/revoke', { task_id: taskId })
    if (res.data.code === 200) {
      // 🌟 【修改这里】不再用 res.data.msg，用字典里的词
      ElMessage.success("🎉 " + t('msgRevokeSuccess'))
      fetchMyTasks() 
    } else {
      ElMessage.error(res.data.msg) // 失败的报错暂时保留后端的，因为情况多变
    }
  } catch (e) { /* 取消就不管 */ }
}

// 2. 验收完成
const handleSettle = async (taskId) => {
  try {
    await ElMessageBox.confirm(t('confirmSettle'), t('tip'), { 
      type: 'info',
      confirmButtonText: t('confirm'),
      cancelButtonText: t('cancel')
    })
    const res = await axios.post('http://localhost:5000/api/task/settle', { task_id: taskId })
    if (res.data.code === 200) {
      // 🌟 【修改这里】不再用 res.data.msg，用字典里的词
      ElMessage.success("✅ " + t('msgSettleSuccess'))
      fetchMyTasks()
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (e) {}
}

// 3. 打开评价弹窗
const openRateDialog = (task) => {
  currentRateTask.value = task
  rateScore.value = 5
  rateContent.value = ''
  rateDialogVisible.value = true
}

// 4. 提交评价并打款
const submitFeedback = async () => {
  if (!rateContent.value) {
    ElMessage.warning("请填写评语")
    return
  }
  try {
    const res = await axios.post('http://localhost:5000/api/task/feedback', {
      task_id: currentRateTask.value.id,
      rating: rateScore.value,
      content: rateContent.value
    })
    if (res.data.code === 200) {
      ElMessage.success("💰 " + res.data.msg)
      rateDialogVisible.value = false
      fetchMyTasks()
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (e) {
    ElMessage.error("请求失败")
  }
}

onMounted(() => {
  fetchMyTasks()
})

// 5. 接单者放弃任务 (反悔机制)
const handleAbandon = async (taskId) => {
  try {
    // 这里故意用了 type: 'error'，让弹窗的图标变成红色的警告叉号
    await ElMessageBox.confirm(t('confirmAbandon'), t('tip'), { 
      type: 'error',
      confirmButtonText: t('confirm'),
      cancelButtonText: t('cancel')
    })
    
    const res = await axios.post('http://localhost:5000/api/task/abandon', { task_id: taskId })
    
    if (res.data.code === 200) {
      ElMessage.success("⚠️ " + t('msgAbandonSuccess'))
      fetchMyTasks() // 刷新我的任务列表
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (e) {
    // 用户害怕了，点击取消，什么都不做
  }
}

</script>

<template>
  <div class="my-tasks-container">
    <div class="header">
      <h2>{{ t('myTasksTitle') }}</h2>
      <el-button @click="router.push('/lobby')" plain>{{ t('backLobby') }}</el-button>
    </div>

    <el-card class="box-card">
      <el-tabs v-model="activeTab">
        
        <el-tab-pane :label="t('tabPublished')" name="published">
          <div v-for="task in publishedTasks" :key="task.id" class="list-item">
            <div class="task-info">
              <h4>{{ task.title }} <el-tag size="small" type="warning">{{ task.reward_points }} 分</el-tag></h4>
              
              <el-tag v-if="task.status === 0" type="info">{{ t('status0') }}</el-tag>
              <el-tag v-else-if="task.status === 1" type="primary">{{ t('status1') }}</el-tag>
              <el-tag v-else-if="task.status === 2 && !task.has_feedback" type="danger">{{ t('status2') }}</el-tag>
              <el-tag v-else type="success">{{ t('statusDone') }}</el-tag>
            </div>

            <div class="task-actions">
              <el-button v-if="task.status === 0" type="danger" size="small" plain @click="handleRevoke(task.id)">{{ t('btnRevoke') }}</el-button>
              <el-button v-if="task.status === 1" type="primary" size="small" @click="handleSettle(task.id)">{{ t('btnSettle') }}</el-button>
              <el-button v-if="task.status === 2 && !task.has_feedback" type="success" size="small" @click="openRateDialog(task)">{{ t('btnRate') }}</el-button>
            </div>
          </div>
          <el-empty v-if="publishedTasks.length === 0" description="暂无数据"></el-empty>
        </el-tab-pane>

        <el-tab-pane :label="t('tabTaken')" name="taken">
          <div v-for="task in takenTasks" :key="task.id" class="list-item">
            <div class="task-info">
              <h4>{{ task.title }} <el-tag size="small" type="warning">{{ task.reward_points }} 分</el-tag></h4>
              
              <el-tag v-if="task.status === 1" type="primary">{{ t('status1') }}</el-tag>
              <el-tag v-else-if="task.status === 2 && !task.has_feedback" type="warning">待对方放款</el-tag>
              <el-tag v-else type="success">积分已入账</el-tag>
            </div>

            <div class="task-actions">
              <el-button 
                v-if="task.status === 1" 
                type="danger" 
                size="small" 
                plain 
                @click="handleAbandon(task.id)"
              >
                {{ t('btnAbandon') }}
              </el-button>
            </div>
          </div>
          <el-empty v-if="takenTasks.length === 0" description="暂无数据"></el-empty>
        </el-tab-pane>

      </el-tabs>
    </el-card>

    <el-dialog v-model="rateDialogVisible" :title="t('rateTitle')" width="400px">
      <div v-if="currentRateTask">
        <p>任务：<b>{{ currentRateTask.title }}</b></p>
        <div style="margin: 20px 0;">
          <el-rate v-model="rateScore" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" />
        </div>
        <el-input v-model="rateContent" type="textarea" :rows="3" :placeholder="t('rateContentPlace')" />
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="rateDialogVisible = false">{{ t('closeBtn') }}</el-button>
          <el-button type="success" @click="submitFeedback">{{ t('submitRate') }}</el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<style scoped>
.my-tasks-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 30px 20px;
  font-family: sans-serif;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}
.list-item:last-child {
  border-bottom: none;
}
.task-info h4 {
  margin: 0 0 8px 0;
  color: #333;
}
</style>