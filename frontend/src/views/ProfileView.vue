<template>
  <div class="profile-page">
    <div class="profile-container">
      <div class="profile-header card">
        <div class="profile-user">
          <div class="avatar">
            {{ profileUsername ? profileUsername.slice(0, 1).toUpperCase() : 'U' }}
          </div>
          <div class="user-meta">
            <h1>个人中心</h1>
            <p v-if="profileUsername">当前用户：{{ profileUsername }}</p>
            <p v-else>正在加载用户信息...</p>
          </div>
        </div>
      </div>

      <div class="tab-bar card">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'favorites' }"
          @click="switchTab('favorites')"
        >
          我的收藏
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'history' }"
          @click="switchTab('history')"
        >
          浏览历史
        </button>
      </div>

      <div class="content-card card">
        <div v-if="activeTab === 'favorites'">
          <div class="section-title">我的收藏</div>

          <div v-if="favorites.length" class="list-wrap">
            <div
              v-for="item in favorites"
              :key="item.id"
              class="list-item"
            >
              <div class="item-main">
                <div class="item-title">{{ item.dish_name }}</div>
                <div class="item-time">收藏时间：{{ item.created_at }}</div>
              </div>

              <div class="item-actions">
                <button class="small-btn" @click="goDishGraph(item.dish_name)">
                  查看图谱
                </button>
                <button class="small-btn" @click="goRecipeDetail(item.recipe_id, item.dish_name)">
                  查看详情
                </button>
                <button class="danger-btn" @click="removeFavorite(item.recipe_id)">
                  取消收藏
                </button>
              </div>
            </div>
          </div>

          <div v-else class="empty-block">你还没有收藏任何菜品</div>
        </div>

        <div v-if="activeTab === 'history'">
          <div class="section-title">浏览历史</div>

          <div v-if="histories.length" class="list-wrap">
            <div
              v-for="(item, index) in histories"
              :key="index"
              class="list-item"
            >
              <div class="item-main">
                <div class="item-title">{{ item.dish_name }}</div>
                <div class="item-time">浏览时间：{{ item.viewed_at }}</div>
              </div>

              <div class="item-actions">
                <button class="small-btn" @click="goDishGraph(item.dish_name)">
                  再看一次
                </button>
              </div>
            </div>
          </div>

          <div v-else class="empty-block">你还没有浏览记录</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getUserInfoApi, getHistoryApi } from '../api'

const router = useRouter()
const route = useRoute()

const API_BASE = 'http://localhost:8000'

const profileUsername = ref('')
const favorites = ref([])
const histories = ref([])
const activeTab = ref('favorites')

const getCookie = (name) => {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith(name + '='))

  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : ''
}

const fetchJson = async (url, options = {}) => {
  const response = await fetch(url, {
    credentials: 'include',
    ...options,
  })

  const text = await response.text()

  let data = {}
  try {
    data = text ? JSON.parse(text) : {}
  } catch (error) {
    throw new Error(`接口返回格式错误：${text.slice(0, 200)}`)
  }

  if (!response.ok) {
    throw new Error(data.message || `请求失败，状态码：${response.status}`)
  }

  return data
}

const ensureCsrfCookie = async () => {
  await fetch(`${API_BASE}/api/csrf/`, {
    credentials: 'include',
  })
}

const loadUserInfo = async () => {
  try {
    const data = await getUserInfoApi()

    if (data.success && data.is_authenticated) {
      profileUsername.value = data.username
    } else {
      router.push('/login')
    }
  } catch (error) {
    console.error('加载用户信息失败', error)
    router.push('/login')
  }
}

const loadFavorites = async () => {
  try {
    const data = await fetchJson(`${API_BASE}/api/recipes/favorites/`)
    favorites.value = data.favorites || []
  } catch (error) {
    console.error('加载收藏失败', error)
    favorites.value = []
  }
}

const loadHistories = async () => {
  try {
    const data = await getHistoryApi()
    histories.value = data.histories || []
  } catch (error) {
    console.error('加载历史失败', error)
    histories.value = []
  }
}

const switchTab = async (tab) => {
  activeTab.value = tab
  router.replace({
    path: '/profile',
    query: { tab },
  })

  if (tab === 'favorites') {
    await loadFavorites()
  } else if (tab === 'history') {
    await loadHistories()
  }
}

const goDishGraph = (dishName) => {
  router.push(`/graph?dish=${encodeURIComponent(dishName)}`)
}

const goRecipeDetail = (recipeId, dishName) => {
  router.push({
    path: `/recipe/${recipeId}`,
    query: {
      from: 'profile',
      name: dishName || '',
    },
  })
}

const removeFavorite = async (recipeId) => {
  try {
    const csrftoken = getCookie('csrftoken')

    const data = await fetchJson(`${API_BASE}/api/recipes/favorite/remove/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({
        recipe_id: recipeId,
      }),
    })

    if (data.success) {
      await loadFavorites()
    } else {
      alert(data.message || '取消收藏失败')
    }
  } catch (error) {
    console.error('取消收藏失败', error)
    alert(error.message || '取消收藏失败')
  }
}

onMounted(async () => {
  const tab = route.query.tab
  if (tab === 'history' || tab === 'favorites') {
    activeTab.value = tab
  }

  await ensureCsrfCookie()
  await loadUserInfo()
  await loadFavorites()
  await loadHistories()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f5f7fb;
  padding: 24px;
  box-sizing: border-box;
}

.profile-container {
  max-width: 1100px;
  margin: 0 auto;
}

.card {
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
}

.profile-header {
  padding: 24px;
  margin-bottom: 20px;
}

.profile-user {
  display: flex;
  align-items: center;
  gap: 18px;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 999px;
  background: linear-gradient(135deg, #60a5fa, #8b5cf6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 800;
}

.user-meta h1 {
  margin: 0 0 8px;
  font-size: 30px;
}

.user-meta p {
  margin: 0;
  color: #64748b;
}

.tab-bar {
  display: flex;
  gap: 12px;
  padding: 14px;
  margin-bottom: 20px;
}

.tab-btn {
  border: none;
  background: #eef2f7;
  color: #334155;
  padding: 10px 18px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

.tab-btn.active {
  background: #2490ff;
  color: white;
}

.content-card {
  padding: 22px;
}

.section-title {
  font-size: 22px;
  font-weight: 800;
  margin-bottom: 18px;
}

.list-wrap {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 18px;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #e5edf5;
}

.item-main {
  min-width: 0;
}

.item-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 6px;
  color: #1f2937;
}

.item-time {
  color: #64748b;
  font-size: 14px;
}

.item-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.small-btn,
.danger-btn {
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 700;
}

.small-btn {
  background: #eef6ff;
  color: #2490ff;
}

.danger-btn {
  background: #fff1f2;
  color: #e11d48;
}

.empty-block {
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  color: #64748b;
  border-radius: 16px;
  padding: 28px;
  text-align: center;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 14px;
  }

  .profile-user,
  .list-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .item-actions {
    width: 100%;
  }
}
</style>