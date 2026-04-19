<template>
  <div class="recipe-list-page">
    <TopNav />

    <div class="page-wrap">
      <div class="page-header">
        <div>
          <div class="page-badge"> 菜谱中心</div>
          <p>浏览当前数据库中的所有菜谱，点击卡片查看详情</p>
        </div>
      </div>

      <div v-if="loading" class="loading-box">加载中...</div>

      <div v-else-if="recipes.length === 0" class="empty-box">
        暂无菜谱数据
      </div>

      <div v-else class="recipe-grid">
        <div
          v-for="recipe in recipes"
          :key="recipe.id"
          class="recipe-card"
          @click="goDetail(recipe.id)"
        >
          <div class="image-wrap">
            <img
              :src="getImageUrl(recipe.image)"
              :alt="recipe.title"
              class="recipe-image"
            />
            <span class="tag">{{ recipe.tag || '家常菜' }}</span>
          </div>

          <div class="card-body">
            <h3>{{ recipe.title || '未命名菜谱' }}</h3>
            <p class="desc">{{ recipe.desc || '暂无简介' }}</p>

            <div class="meta-row">
              <span>🕒 {{ recipe.time || '未填写' }}</span>
              <span :class="['level', getLevelClass(recipe.level)]">
                {{ recipe.level || '未标注' }}
              </span>
            </div>

            <div class="stat-row">
              <span>👁 {{ recipe.views || 0 }}</span>
              <span>⭐ {{ recipe.favorites || 0 }}</span>
              <span>💬 {{ recipe.comments || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopNav from '../components/TopNav.vue'

const router = useRouter()
const recipes = ref([])
const loading = ref(true)

const defaultImage =
  'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80'

const getLevelClass = (level) => {
  if (level === '简单') return 'easy'
  if (level === '中等') return 'medium'
  if (level === '较难') return 'hard'
  return 'normal'
}

const getImageUrl = (image) => {
  if (!image) return defaultImage
  if (image.startsWith('http')) return image
  return `http://127.0.0.1:8000${image}`
}

const loadRecipes = async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/recipes/all/')
    const data = await res.json()
    recipes.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('获取全部菜谱失败：', error)
    recipes.value = []
  } finally {
    loading.value = false
  }
}

const goDetail = (id) => {
  router.push(`/recipe/${id}`)
}

onMounted(() => {
  loadRecipes()
})
</script>

<style scoped>
.recipe-list-page {
  min-height: 100vh;
  background:
    linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.95)),
    url('https://images.unsplash.com/photo-1495195134817-aeb325a55b65?auto=format&fit=crop&w=1600&q=80')
      center/cover fixed no-repeat;
}

.page-wrap {
  max-width: 1320px;
  margin: 0 auto;
  padding: 36px 24px 60px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.page-badge {
  display: inline-block;
  padding: 8px 14px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0284c7;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 14px;
}

.page-header h1 {
  font-size: 42px;
  color: #1f2937;
  margin-bottom: 10px;
}

.page-header p {
  color: #6b7280;
  font-size: 18px;
}

.loading-box,
.empty-box {
  text-align: center;
  padding: 80px 0;
  font-size: 20px;
  color: #6b7280;
}

.recipe-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 28px;
}

.recipe-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 22px;
  overflow: hidden;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
  cursor: pointer;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.recipe-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.14);
}

.image-wrap {
  position: relative;
  height: 260px;
  overflow: hidden;
}

.recipe-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.tag {
  position: absolute;
  top: 16px;
  left: 16px;
  background: #60a5fa;
  color: #fff;
  padding: 6px 12px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
}

.card-body {
  padding: 22px;
}

.card-body h3 {
  font-size: 30px;
  font-weight: 800;
  color: #1f2937;
  margin-bottom: 12px;
}

.desc {
  color: #6b7280;
  line-height: 1.8;
  min-height: 88px;
  font-size: 18px;
}

.meta-row,
.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 18px;
  color: #6b7280;
  font-size: 16px;
}

.level {
  font-weight: 700;
}

.level.easy {
  color: #16a34a;
}

.level.medium {
  color: #f59e0b;
}

.level.hard {
  color: #ef4444;
}

.level.normal {
  color: #6b7280;
}

@media (max-width: 1200px) {
  .recipe-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .recipe-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-header h1 {
    font-size: 32px;
  }
}

@media (max-width: 640px) {
  .recipe-grid {
    grid-template-columns: 1fr;
  }
}
</style>