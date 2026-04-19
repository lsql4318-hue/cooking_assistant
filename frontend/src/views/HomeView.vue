<template>
  <div class="home-page">
    <TopNav />

    <section class="hero-section">
      <div class="hero-banner">
        <div class="hero-content">
          <h1>{{ banners[currentBanner].title }}</h1>
          <p>{{ banners[currentBanner].subtitle }}</p>
        </div>

        <div class="hero-dots">
          <span
            v-for="(item, index) in banners"
            :key="index"
            class="dot"
            :class="{ active: currentBanner === index }"
            @click="currentBanner = index"
          ></span>
        </div>
      </div>
    </section>

    <section class="search-section" id="search">
      <h2>今天想吃什么？</h2>
      <div class="search-box">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="输入菜名、食材或口味..."
          @keyup.enter="handleSearch"
        />
        <button @click="handleSearch">搜索</button>
      </div>

      <div class="hot-search">
        <span class="hot-label">热门搜索：</span>
        <span
          v-for="item in hotKeywords"
          :key="item"
          class="hot-tag"
          @click="quickSearch(item)"
        >
          {{ item }}
        </span>
      </div>
    </section>

    <section class="category-section">
      <div class="section-title-row">
        <h2>菜系分类</h2>
      </div>

      <div class="category-grid">
        <div
          v-for="item in categories"
          :key="item.name"
          class="category-card"
          @click="searchCategory(item.name)"
        >
          <div class="category-icon">{{ item.icon }}</div>
          <div class="category-name">{{ item.name }}</div>
        </div>
      </div>
    </section>

    <section class="recommend-section">
      <div class="section-title-row">
        <h2>热门菜谱</h2>
        <span class="more-link">查看更多 →</span>
      </div>

      <div class="recipe-grid">
        <div
          v-for="recipe in hotRecipes"
          :key="recipe.id"
          class="recipe-card"
          @click="goRecipeDetail(recipe.id)"
        >
          <div class="recipe-image-wrap">
            <img :src="recipe.image" :alt="recipe.title" class="recipe-image" />
            <span class="recipe-tag">{{ recipe.tag }}</span>
          </div>

          <div class="recipe-body">
            <h3>{{ recipe.title }}</h3>
            <p>{{ recipe.desc }}</p>

            <div class="recipe-meta">
              <span>🕒 {{ recipe.time }}</span>
              <span :class="['difficulty', recipe.levelClass]">{{ recipe.level }}</span>
            </div>

            <div class="recipe-stats">
              <span>👁 {{ recipe.views }}</span>
              <span>☆ {{ recipe.favorites }}</span>
              <span>💬 {{ recipe.comments }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import TopNav from '../components/TopNav.vue'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE = 'http://localhost:8000/api'

const searchKeyword = ref('')
const currentBanner = ref(0)


const banners = [
  {
    title: '热门菜谱',
    subtitle: '大家都在看的菜',
  },
  {
    title: '精选推荐',
    subtitle: '发现适合今天的美味灵感',
  },
  {
    title: '智能搜索',
    subtitle: '按菜名、食材、菜系快速查找',
  },
]

const hotKeywords = ['红烧肉', '西红柿炒鸡蛋', '清蒸鲈鱼', '宫保鸡丁', '麻婆豆腐', '糖醋排骨']

const categories = [
  { name: '川菜', icon: '🌶️' },
  { name: '粤菜', icon: '🥘' },
  { name: '鲁菜', icon: '🍖' },
  { name: '苏菜', icon: '🦐' },
  { name: '浙菜', icon: '🐟' },
  { name: '湘菜', icon: '🔥' },
  { name: '闽菜', icon: '🦀' },
  { name: '徽菜', icon: '🥬' },
  { name: '西餐', icon: '🍝' },
  { name: '家常菜', icon: '🍣' },
]

const goRecipeDetail = (id) => {
  router.push(`/recipe/${id}`)
}

const hotRecipes = ref([])

let bannerTimer = null

const getCookie = (name) => {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith(name + '='))

  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : ''
}

const requestJson = async (url, options = {}) => {
  const response = await fetch(`${API_BASE}${url}`, {
    credentials: 'include',
    ...options,
  })

  const text = await response.text()

  let data
  try {
    data = text ? JSON.parse(text) : {}
  } catch (error) {
    throw new Error(`接口返回的不是 JSON：${text.slice(0, 200)}`)
  }

  if (!response.ok) {
    throw new Error(data.message || `请求失败，状态码：${response.status}`)
  }

  return data
}

const handleSearch = () => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) return
  router.push(`/graph?dish=${encodeURIComponent(keyword)}`)
}

const quickSearch = (keyword) => {
  searchKeyword.value = keyword
  handleSearch()
}

const searchCategory = (category) => {
  router.push(`/graph?category=${encodeURIComponent(category)}`)
}

const loadHotRecipes = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/recipes/hot/')
    const data = await response.json()

    hotRecipes.value = Array.isArray(data)
      ? data
          .filter(item => item.title && item.title.trim())
          .map(item => ({
            id: item.id,
            title: item.title,
            desc: item.desc,
            time: item.time,
            level: item.level,
            levelClass:
              item.level === '简单'
                ? 'easy'
                : item.level === '中等'
                  ? 'medium'
                  : 'hard',
            tag: item.tag,
            views: item.views,
            favorites: item.favorites,
            comments: item.comments,
            image: item.image
              ? `http://127.0.0.1:8000${item.image}`
              : 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80',
          }))
      : []
  } catch (error) {
    console.error('加载热门菜谱失败：', error)
    hotRecipes.value = []
  }
}

const startBannerAutoPlay = () => {
  bannerTimer = setInterval(() => {
    currentBanner.value = (currentBanner.value + 1) % banners.length
  }, 3000)
}

onMounted(async () => {
  await loadHotRecipes()
  startBannerAutoPlay()
})

onBeforeUnmount(() => {
  if (bannerTimer) {
    clearInterval(bannerTimer)
    bannerTimer = null
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background:
    linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.94)),
    url('https://images.unsplash.com/photo-1495195134817-aeb325a55b65?auto=format&fit=crop&w=1600&q=80')
      center/cover fixed no-repeat;
  color: #1f2937;
}

.nav-item:hover,
.nav-item.active {
  background: #eaf3ff;
  color: #2490ff;
}

.dropdown-menu::before {
  content: '';
  position: absolute;
  top: -6px;
  right: 26px;
  width: 12px;
  height: 12px;
  background: white;
  border-left: 1px solid #e5e7eb;
  border-top: 1px solid #e5e7eb;
  transform: rotate(45deg);
}

.publish-btn,
.register-btn {
  text-decoration: none;
  padding: 8px 14px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 14px;
}

.publish-btn,
.login-btn {
  color: #2490ff;
  background: #eef6ff;
}

.hero-section,
.search-section,
.recommend-section,
.category-section {
  max-width: 1240px;
  margin: 0 auto;
  padding: 18px 20px 0;
}

.hero-banner {
  height: 330px;
  border-radius: 20px;
  background: linear-gradient(135deg, #5d7df7 0%, #8156d8 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 24px rgba(99, 102, 241, 0.14);
}

.hero-content {
  text-align: center;
  color: white;
}

.hero-content h1 {
  margin: 0 0 10px;
  font-size: 34px;
  font-weight: 800;
}

.hero-content p {
  margin: 0;
  font-size: 16px;
  opacity: 0.92;
}

.hero-dots {
  position: absolute;
  bottom: 22px;
  display: flex;
  gap: 10px;
}

.dot {
  width: 30px;
  height: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.35);
  cursor: pointer;
}

.dot.active {
  background: white;
}

.search-section {
  text-align: center;
}

.search-section h2 {
  margin: 20px 0 16px;
  font-size: 26px;
}

.search-box {
  max-width: 640px;
  margin: 0 auto;
  display: flex;
  background: white;
  border: 1px solid #dbe4ee;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.05);
}

.search-box input {
  flex: 1;
  padding: 14px 16px;
  border: none;
  outline: none;
  font-size: 15px;
}

.search-box button {
  border: none;
  padding: 0 22px;
  background: #f3f7fb;
  color: #4b5563;
  font-size: 15px;
  cursor: pointer;
}

.hot-search {
  margin-top: 16px;
  display: flex;
  gap: 10px;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}

.hot-label {
  font-weight: 700;
}

.hot-tag {
  padding: 6px 14px;
  border: 1px solid #93c5fd;
  color: #3b82f6;
  border-radius: 999px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.75);
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 34px 0 20px;
}

.section-title-row h2 {
  margin: 0;
  font-size: 28px;
}

.more-link {
  color: #2490ff;
  font-weight: 600;
  cursor: pointer;
}

.recipe-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 22px;
}

.recipe-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(226, 232, 240, 0.9);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.recipe-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.recipe-image-wrap {
  position: relative;
  height: 220px;
  overflow: hidden;
}

.recipe-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.recipe-tag {
  position: absolute;
  top: 14px;
  left: 14px;
  background: #4da3ff;
  color: white;
  font-size: 13px;
  font-weight: 700;
  padding: 5px 10px;
  border-radius: 8px;
}

.recipe-body {
  padding: 18px;
}

.recipe-body h3 {
  margin: 0 0 10px;
  font-size: 18px;
}

.recipe-body p {
  margin: 0 0 14px;
  color: #6b7280;
  line-height: 1.7;
  height: 52px;
  overflow: hidden;
}

.recipe-meta,
.recipe-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recipe-meta {
  margin-bottom: 12px;
  color: #4b5563;
}

.recipe-stats {
  color: #9ca3af;
  font-size: 14px;
}

.difficulty.easy {
  color: #65a30d;
  font-weight: 700;
}

.difficulty.medium {
  color: #f59e0b;
  font-weight: 700;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 18px;
}

.category-card {
  background: rgba(255, 255, 255, 0.78);
  border-radius: 18px;
  min-height: 130px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  cursor: pointer;
  transition: 0.2s ease;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.category-icon {
  font-size: 36px;
}

.category-name {
  font-size: 16px;
  font-weight: 600;
}

@media (max-width: 1200px) {
  .recipe-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .category-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .nav-inner {
    height: auto;
    padding-top: 14px;
    padding-bottom: 14px;
    flex-wrap: wrap;
  }

  .nav-menu {
    order: 3;
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .hero-content h1 {
    font-size: 42px;
  }

  .hero-content p {
    font-size: 22px;
  }

  .search-section h2 {
    font-size: 34px;
  }
}

@media (max-width: 768px) {
  .recipe-grid,
  .category-grid {
    grid-template-columns: 1fr;
  }

  .search-box {
    flex-direction: column;
  }

  .search-box button {
    padding: 16px;
  }
}
</style>