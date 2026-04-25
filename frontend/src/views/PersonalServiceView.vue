<template>
  <div class="personal-page">
    <TopNav />
    <div class="page-wrap">
      <div class="page-header">
        <h1>个性化服务</h1>
        <p>查看你的投稿状态、驳回原因，并可修改后重新提交审核。</p>
      </div>

      <div class="weekly-card">
        <div class="weekly-header">
          <div>
            <h2>一周菜品推荐</h2>
            <p>根据你的浏览、收藏、点赞行为，为你生成一周菜谱安排。</p>
          </div>

          <button class="refresh-btn" @click="loadWeeklyMenu" :disabled="weeklyLoading">
            {{ weeklyLoading ? '生成中...' : '换一组推荐' }}
          </button>
        </div>

        <div v-if="weeklyLoading" class="weekly-loading">
          正在生成一周推荐...
        </div>

        <div v-else-if="weeklyMessage" class="weekly-message">
          {{ weeklyMessage }}
        </div>

        <div v-else-if="weeklyMenu.length" class="weekly-grid">
          <div
            v-for="item in weeklyMenu"
            :key="item.day"
            class="weekly-item"
            @click="goRecipeDetail(item.id)"
          >
            <div class="weekly-day">{{ item.day }}</div>

            <div class="weekly-image">
              <img
                :src="item.image ? `http://localhost:8000${item.image}` : 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80'"
                :alt="item.title"
              />
            </div>

            <div class="weekly-info">
              <h3>{{ item.title }}</h3>

              <div class="weekly-meta">
                <span>{{ item.category || '未分类' }}</span>
                <span>{{ item.difficulty || '未标注' }}</span>
                <span>{{ item.cook_time || '未填写' }}</span>
              </div>

              <p class="weekly-desc">
                {{ item.description || '暂无简介' }}
              </p>

              <div class="weekly-reason">
                推荐理由：{{ item.reason }}
              </div>
            </div>
          </div>
        </div>

        <div v-else class="weekly-empty">
          暂无推荐结果，请先浏览、收藏或点赞一些菜谱。
        </div>
      </div>

      <div class="card">
        <div class="card-title">我的投稿</div>

        <div v-if="submissions.length" class="submission-list">
          <div v-for="item in submissions" :key="item.id" class="submission-item">
            <div class="main">
              <div class="title-row">
                <h3>{{ item.title }}</h3>
                <span class="status" :class="item.review_status">
                  {{
                    item.review_status === 'pending'
                      ? '待审核'
                      : item.review_status === 'approved'
                        ? '审核通过'
                        : '审核驳回'
                  }}
                </span>
              </div>

              <p>提交时间：{{ item.created_at }}</p>
              <p v-if="item.reviewed_at">审核时间：{{ item.reviewed_at }}</p>
              <p v-if="item.review_comment">审核意见：{{ item.review_comment }}</p>
            </div>

            <div class="actions">
              <button
                v-if="item.can_resubmit"
                class="primary-btn"
                @click="goEdit(item.id)"
              >
                修改后重新提交
              </button>
            </div>
          </div>
        </div>

        <div v-else class="empty">你还没有提交过菜谱</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopNav from '../components/TopNav.vue'

const router = useRouter()
const submissions = ref([])
const weeklyMenu = ref([])
const weeklyLoading = ref(false)
const weeklyMessage = ref('')

const loadWeeklyMenu = async () => {
  weeklyLoading.value = true
  weeklyMessage.value = ''

  try {
    const res = await fetch(
      `http://localhost:8000/api/recipes/week-recommend/?refresh=${Date.now()}`,
      {
        credentials: 'include'
      }
    )

    const data = await res.json()

    if (data.success) {
      weeklyMenu.value = data.weekly_menu || []
    } else {
      weeklyMessage.value = data.message || '一周推荐生成失败'
      weeklyMenu.value = []
    }
  } catch (error) {
    console.error('加载一周推荐失败：', error)
    weeklyMessage.value = '一周推荐加载失败，请检查后端服务'
    weeklyMenu.value = []
  } finally {
    weeklyLoading.value = false
  }
}

const goRecipeDetail = (id) => {
  router.push(`/recipe/${id}`)
}

const loadSubmissions = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/recipes/my-submissions/', {
      credentials: 'include'
    })
    const data = await res.json()
    submissions.value = data.submissions || []
  } catch (error) {
    submissions.value = []
  }
}

const getCookie = (name) => {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith(name + '='))

  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : ''
}

const markRead = async () => {
  try {
    const csrftoken = getCookie('csrftoken')

    await fetch('http://localhost:8000/api/recipes/my-submissions/read/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }
    })
  } catch (error) {
    console.error('标记已读失败', error)
  }
}

const goEdit = (id) => {
  router.push(`/submission/edit/${id}`)
}

onMounted(async () => {
  await loadSubmissions()
  await markRead()
  await loadWeeklyMenu()
})
</script>

<style scoped>
.weekly-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 28px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
}

.weekly-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 22px;
}

.weekly-header h2 {
  margin: 0 0 8px;
  font-size: 28px;
  color: #1f2937;
}

.weekly-header p {
  margin: 0;
  color: #64748b;
  font-size: 15px;
}

.refresh-btn {
  border: none;
  background: #2490ff;
  color: #fff;
  padding: 11px 18px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.refresh-btn:hover {
  background: #1677d2;
}

.weekly-loading,
.weekly-message,
.weekly-empty {
  padding: 28px;
  text-align: center;
  color: #64748b;
  background: #f8fafc;
  border-radius: 16px;
}

.weekly-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.weekly-item {
  display: flex;
  gap: 16px;
  background: #f8fafc;
  border: 1px solid #e5edf5;
  border-radius: 18px;
  padding: 14px;
  cursor: pointer;
  transition: 0.2s ease;
  position: relative;
}

.weekly-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  border-color: #bfdbfe;
}

.weekly-day {
  position: absolute;
  left: 14px;
  top: 14px;
  background: #2490ff;
  color: #fff;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
  z-index: 2;
}

.weekly-image {
  width: 150px;
  height: 120px;
  flex-shrink: 0;
  border-radius: 14px;
  overflow: hidden;
  background: #e5e7eb;
}

.weekly-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.weekly-info {
  flex: 1;
  min-width: 0;
}

.weekly-info h3 {
  margin: 0 0 10px;
  font-size: 20px;
  color: #1f2937;
}

.weekly-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.weekly-meta span {
  background: #eef6ff;
  color: #2563eb;
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
}

.weekly-desc {
  margin: 0 0 10px;
  color: #64748b;
  line-height: 1.6;
  font-size: 14px;
}

.weekly-reason {
  color: #16a34a;
  background: #ecfdf5;
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 13px;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .weekly-grid {
    grid-template-columns: 1fr;
  }

  .weekly-item {
    flex-direction: column;
  }

  .weekly-image {
    width: 100%;
    height: 180px;
  }
}

.personal-page {
  min-height: 100vh;
  background: #f5f7fb;
}
.page-wrap {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 20px 40px;
}
.page-header {
  margin-bottom: 20px;
}
.page-header h1 {
  margin: 0 0 8px;
}
.card {
  background: #fff;
  border-radius: 16px;
  padding: 22px;
}
.card-title {
  font-size: 22px;
  font-weight: 800;
  margin-bottom: 18px;
}
.submission-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.submission-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
  border: 1px solid #e5edf5;
  border-radius: 14px;
  background: #f8fafc;
}
.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.status {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
}
.status.pending {
  background: #fef3c7;
  color: #b45309;
}
.status.approved {
  background: #dcfce7;
  color: #15803d;
}
.status.rejected {
  background: #fee2e2;
  color: #dc2626;
}
.primary-btn {
  border: none;
  background: #2490ff;
  color: #fff;
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
}
.empty {
  text-align: center;
  color: #64748b;
  padding: 28px 0;
}
</style>