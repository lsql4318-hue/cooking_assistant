<template>
  <div class="page-box">
    <div class="header-card card">
      <div>
        <div class="badge">⭐ 个性化模块</div>
        <h1>个性化服务</h1>
        <p>查看我的收藏、浏览历史，并快速浏览菜品详细信息。</p>
      </div>
    </div>

    <div v-if="message" class="message-box">{{ message }}</div>

    <div class="content-layout">
      <div class="left-panel">
        <div class="card section-card">
          <div class="card-header">
            <h2>我的收藏</h2>
            <button class="secondary-btn" @click="loadFavorites">刷新</button>
          </div>

          <div v-if="favorites.length" class="item-list">
            <div
              v-for="(item, index) in favorites"
              :key="'fav-' + index"
              class="item-card"
            >
              <div class="item-info" @click="loadDishDetail(item.dish_name)">
                <p class="dish-name">🍽️ {{ item.dish_name }}</p>
                <p class="time">收藏时间：{{ item.created_at }}</p>
              </div>
              <button class="remove-btn" @click="removeFavorite(item.dish_name)">
                取消收藏
              </button>
            </div>
          </div>

          <div v-else class="empty-box">暂无收藏菜品</div>
        </div>

        <div class="card section-card">
          <div class="card-header">
            <h2>浏览历史</h2>
            <button class="secondary-btn" @click="loadHistories">刷新</button>
          </div>

          <div v-if="histories.length" class="item-list">
            <div
              v-for="(item, index) in histories"
              :key="'his-' + index"
              class="item-card history-card"
              @click="loadDishDetail(item.dish_name)"
            >
              <div class="item-info">
                <p class="dish-name">🕘 {{ item.dish_name }}</p>
                <p class="time">浏览时间：{{ item.viewed_at }}</p>
              </div>
            </div>
          </div>

          <div v-else class="empty-box">暂无浏览历史</div>
        </div>
      </div>

      <div class="right-panel">
        <div class="card detail-card">
          <h2>菜品详情</h2>

          <div v-if="dishDetail" class="detail-box">
            <div class="detail-line"><span class="label">菜名</span><span>{{ dishDetail.name }}</span></div>
            <div class="detail-line"><span class="label">评分</span><span>{{ dishDetail.rating }}</span></div>
            <div class="detail-line"><span class="label">难度</span><span>{{ dishDetail.difficulty }}</span></div>
            <div class="detail-line"><span class="label">烹饪时间</span><span>{{ dishDetail.cook_time }}</span></div>
            <div class="detail-line"><span class="label">热量</span><span>{{ dishDetail.calories }}</span></div>
            <div class="detail-line"><span class="label">糖</span><span>{{ dishDetail.sugar }}</span></div>
            <div class="detail-line"><span class="label">脂肪</span><span>{{ dishDetail.fat }}</span></div>

            <div v-if="dishDetail.ingredients?.length">
              <p class="sub-title">所需食材</p>
              <ul>
                <li v-for="(item, index) in dishDetail.ingredients" :key="'ing-' + index">
                  {{ item }}
                </li>
              </ul>
            </div>

            <div v-if="dishDetail.methods?.length">
              <p class="sub-title">做法</p>
              <ul>
                <li v-for="(item, index) in dishDetail.methods" :key="'method-' + index">
                  {{ item }}
                </li>
              </ul>
            </div>

            <div v-if="dishDetail.tastes?.length">
              <p class="sub-title">口味</p>
              <ul>
                <li v-for="(item, index) in dishDetail.tastes" :key="'taste-' + index">
                  {{ item }}
                </li>
              </ul>
            </div>
          </div>

          <div v-else class="empty-box">
            点击左侧收藏菜品或浏览历史后，这里显示详情
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const favorites = ref([])
const histories = ref([])
const message = ref('')
const dishDetail = ref(null)

const loadFavorites = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/favorites/', {
      credentials: 'include',
    })
    const data = await response.json()

    if (data.success) {
      favorites.value = data.favorites
    } else {
      message.value = data.message || '获取收藏失败'
    }
  } catch (error) {
    message.value = '请求失败，请检查 Django 服务是否启动'
  }
}

const loadHistories = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/history/', {
      credentials: 'include',
    })
    const data = await response.json()

    if (data.success) {
      histories.value = data.histories
    } else {
      message.value = data.message || '获取浏览历史失败'
    }
  } catch (error) {
    message.value = '请求失败，请检查 Django 服务是否启动'
  }
}

const removeFavorite = async (dishName) => {
  try {
    const response = await fetch('http://localhost:8000/api/favorites/remove/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        dish_name: dishName,
      }),
    })

    const data = await response.json()

    if (data.success) {
      message.value = data.message

      if (dishDetail.value && dishDetail.value.name === dishName) {
        dishDetail.value = null
      }

      await loadFavorites()
    } else {
      message.value = data.message || '取消收藏失败'
    }
  } catch (error) {
    message.value = '请求失败，请检查 Django 服务是否启动'
  }
}

const loadDishDetail = async (dishName) => {
  try {
    const response = await fetch(
      `http://localhost:8000/api/dish-detail/?name=${encodeURIComponent(dishName)}`,
      {
        credentials: 'include',
      }
    )
    const data = await response.json()

    if (data.success) {
      dishDetail.value = data.detail
    } else {
      message.value = data.message || '获取菜品详情失败'
    }
  } catch (error) {
    message.value = '请求失败，请检查 Django 服务是否启动'
  }
}

onMounted(async () => {
  await loadFavorites()
  await loadHistories()
})
</script>

<style scoped>
.page-box {
  padding: 0;
  font-family: Arial, sans-serif;
}

.card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 26px rgba(15, 23, 42, 0.06);
}

.header-card {
  padding: 24px;
  margin-bottom: 20px;
}

.badge {
  display: inline-block;
  background: #eef9f3;
  color: #1f8f5f;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 10px;
}

.header-card h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
}

.header-card p {
  margin: 0;
  color: #64748b;
}

.message-box {
  background: #fff7ed;
  color: #c2410c;
  border: 1px solid #fed7aa;
  padding: 12px 14px;
  border-radius: 12px;
  margin-bottom: 16px;
}

.content-layout {
  display: flex;
  gap: 20px;
}

.left-panel {
  flex: 1.2;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-panel {
  flex: 1;
}

.section-card,
.detail-card {
  padding: 22px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.secondary-btn {
  border: none;
  border-radius: 10px;
  background: #eef2f7;
  color: #1f2937;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: #f8fafc;
  padding: 15px;
  border-radius: 12px;
}

.history-card {
  cursor: pointer;
}

.item-info {
  flex: 1;
  cursor: pointer;
}

.dish-name {
  font-size: 17px;
  font-weight: 700;
  margin: 0 0 6px 0;
}

.time {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.remove-btn {
  border: none;
  background: #ef4444;
  color: white;
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
}

.empty-box {
  color: #94a3b8;
  padding: 20px 0;
}

.detail-box {
  background: #f8fafc;
  border-radius: 14px;
  padding: 18px;
}

.detail-line {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #e5edf5;
}

.label {
  color: #64748b;
  font-weight: 700;
}

.sub-title {
  margin-top: 14px;
  font-weight: 700;
}

.detail-box ul {
  padding-left: 20px;
  line-height: 1.8;
}
</style>