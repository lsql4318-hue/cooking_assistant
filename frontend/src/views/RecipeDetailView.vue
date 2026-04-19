<template>
  <div class="detail-page">
    <TopNav />

    <div class="back-row">
      <button
        v-if="route.query.from === 'graph'"
        class="back-btn"
        @click="goBackToGraph"
      >
        ← 返回图谱展示区
      </button>

      <button
        v-else
        class="back-btn"
        @click="goBack"
      >
        ← 返回上一页
      </button>
    </div>

    <div class="detail-wrap" v-if="recipe">
      <div class="detail-header">
        <div class="image-box">
          <img :src="getImageUrl(recipe.image)" :alt="recipe.title" />
        </div>

        <div class="info-box">
          <h1>{{ recipe.title || '未命名菜谱' }}</h1>

          <div class="meta-line">
            <span class="tag">{{ recipe.tag || '家常菜' }}</span>
            <span class="level">{{ recipe.level || '未标注' }}</span>
            <span>🕒 {{ recipe.time || '未填写' }}</span>
            <span>👁 {{ recipe.views || 0 }}次浏览</span>
          </div>

          <p class="desc">{{ recipe.desc || '暂无简介' }}</p>

          <div class="action-row">
            <button class="action-btn" @click="toggleLike">
              👍 {{ recipe.is_liked ? '已点赞' : '点赞' }} ({{ recipe.likes || 0 }})
            </button>

            <button class="action-btn" @click="toggleFavorite">
              ⭐ {{ recipe.is_favorited ? '已收藏' : '收藏' }} ({{ recipe.favorites || 0 }})
            </button>
          </div>
        </div>
      </div>

      <div class="section-card">
        <h2>所需食材 <span class="sub-text">{{ recipe.servings || '2人份' }}</span></h2>
        <table class="ingredient-table">
          <thead>
            <tr>
              <th>食材</th>
              <th>用量</th>
              <th>单位</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in recipe.ingredients" :key="index">
              <td>{{ item.name }}</td>
              <td>{{ item.amount }}</td>
              <td>{{ item.unit }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section-card">
        <h2>烹饪步骤</h2>
        <div class="step-list">
          <div class="step-item" v-for="(step, index) in recipe.steps" :key="index">
            <div class="step-title">步骤 {{ index + 1 }}</div>
            <div class="step-card">
              <p>{{ step.content }}</p>
              <span class="step-time">{{ step.time }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="section-card comment-section">
        <h2>评论区</h2>

        <div class="comment-editor">
          <textarea
            v-model="commentText"
            placeholder="说说你对这道菜的看法吧..."
          ></textarea>
          <button @click="submitComment">发表评论</button>
        </div>

        <div v-if="comments.length" class="comment-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-main">
              <div class="comment-header">
                <span class="comment-user">{{ comment.username }}</span>
                <span class="comment-time">{{ comment.created_at }}</span>
              </div>

              <div class="comment-content">{{ comment.content }}</div>

              <div class="comment-actions">
                <button @click="startReply(comment.id)">回复</button>
                <button
                  v-if="comment.can_delete"
                  @click="deleteComment(comment.id)"
                >
                  删除
                </button>
              </div>
            </div>

            <div v-if="replyingTo === comment.id" class="reply-editor">
              <textarea
                v-model="replyText"
                placeholder="请输入回复内容"
              ></textarea>
              <div class="reply-actions">
                <button @click="submitReply(comment.id)">提交回复</button>
                <button @click="cancelReply">取消</button>
              </div>
            </div>

            <div
              v-if="comment.replies && comment.replies.length"
              class="reply-list"
            >
              <div
                v-for="reply in comment.replies"
                :key="reply.id"
                class="reply-item"
              >
                <div class="comment-header">
                  <span class="comment-user">{{ reply.username }}</span>
                  <span class="comment-time">{{ reply.created_at }}</span>
                </div>

                <div class="comment-content">{{ reply.content }}</div>

                <div class="comment-actions">
                  <button
                    v-if="reply.can_delete"
                    @click="deleteComment(reply.id)"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-comment">
          暂无评论，快来发表第一条评论吧～
        </div>
      </div>
    </div>

    <div v-else class="loading-box">加载中...</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TopNav from '../components/TopNav.vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const recipe = ref(null)
const recipeId = ref(route.params.id)

const comments = ref([])
const commentText = ref('')
const replyingTo = ref(null)
const replyText = ref('')

const API_BASE = 'http://localhost:8000'
const defaultImage =
  'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80'

const getCookie = (name) => {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith(name + '='))

  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : ''
}

const fetchRecipeDetail = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/recipes/${recipeId.value}/`, {
      credentials: 'include'
    })
    const data = await res.json()
    recipe.value = data
  } catch (error) {
    console.error('获取菜品详情失败：', error)
  }
}

const loadComments = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/recipes/${recipeId.value}/comments/`, {
      credentials: 'include'
    })
    const data = await res.json()
    comments.value = data.success ? data.comments : []
  } catch (error) {
    console.error('加载评论失败：', error)
    comments.value = []
  }
}

const submitComment = async () => {
  if (!commentText.value.trim()) {
    alert('请输入评论内容')
    return
  }

  try {
    const csrftoken = getCookie('csrftoken')

    const res = await fetch(`${API_BASE}/api/recipes/${recipeId.value}/comments/add/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({
        content: commentText.value
      })
    })

    const data = await res.json()

    if (data.success) {
      commentText.value = ''
      await loadComments()
    } else {
      alert(data.message || '评论失败')
    }
  } catch (error) {
    console.error('评论失败：', error)
    alert('评论失败')
  }
}

const startReply = (commentId) => {
  replyingTo.value = commentId
  replyText.value = ''
}

const cancelReply = () => {
  replyingTo.value = null
  replyText.value = ''
}

const submitReply = async (commentId) => {
  if (!replyText.value.trim()) {
    alert('请输入回复内容')
    return
  }

  try {
    const csrftoken = getCookie('csrftoken')

    const res = await fetch(`${API_BASE}/api/recipes/${recipeId.value}/comments/add/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({
        content: replyText.value,
        parent_id: commentId
      })
    })

    const data = await res.json()

    if (data.success) {
      replyingTo.value = null
      replyText.value = ''
      await loadComments()
    } else {
      alert(data.message || '回复失败')
    }
  } catch (error) {
    console.error('回复失败：', error)
    alert('回复失败')
  }
}

const deleteComment = async (commentId) => {
  if (!confirm('确定删除这条评论吗？')) return

  try {
    const csrftoken = getCookie('csrftoken')

    const res = await fetch(`${API_BASE}/api/recipes/comments/${commentId}/delete/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRFToken': csrftoken
      }
    })

    const data = await res.json()

    if (data.success) {
      await loadComments()
    } else {
      alert(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除失败：', error)
    alert('删除失败')
  }
}

const getImageUrl = (image) => {
  if (!image) return defaultImage
  if (image.startsWith('http')) return image
  return `${API_BASE}${image}`
}

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/recipes')
  }
}

const goBackToGraph = () => {
  const dishName = route.query.name || ''

  if (dishName) {
    router.push({
      path: '/graph',
      query: {
        dish: dishName
      }
    })
  } else {
    router.push('/graph')
  }
}

const toggleFavorite = async () => {
  try {
    const csrftoken = getCookie('csrftoken')

    const res = await fetch(`${API_BASE}/api/recipes/favorite/toggle/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({
        recipe_id: recipeId.value
      })
    })

    const data = await res.json()

    if (res.status === 401) {
      alert('请先登录后再收藏')
      return
    }

    if (!res.ok) {
      alert(data.message || '收藏操作失败')
      return
    }

    if (data.success && recipe.value) {
      recipe.value.is_favorited = data.action === 'favorite'
      recipe.value.favorites = data.favorites
    } else {
      alert(data.message || '收藏操作失败')
    }
  } catch (error) {
    console.error('收藏失败：', error)
    alert('收藏操作失败')
  }
}

const toggleLike = async () => {
  try {
    const csrftoken = getCookie('csrftoken')

    const res = await fetch(`${API_BASE}/api/recipes/like/toggle/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({
        recipe_id: recipeId.value
      })
    })

    const data = await res.json()

    if (res.status === 401) {
      alert('请先登录后再点赞')
      return
    }

    if (!res.ok) {
      alert(data.message || '点赞操作失败')
      return
    }

    if (data.success && recipe.value) {
      recipe.value.is_liked = data.action === 'like'
      recipe.value.likes = data.likes
    } else {
      alert(data.message || '点赞操作失败')
    }
  } catch (error) {
    console.error('点赞失败：', error)
    alert('点赞操作失败')
  }
}

const ensureCsrfCookie = async () => {
  await fetch(`${API_BASE}/api/csrf/`, {
    credentials: 'include'
  })
}

const addHistory = async () => {
  try {
    await fetch(`${API_BASE}/api/history/add/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        dish_name: recipe.value?.title || ''
      })
    })
  } catch (error) {
    console.error('记录浏览历史失败：', error)
  }
}

onMounted(async () => {
  await ensureCsrfCookie()
  await fetchRecipeDetail()
  await addHistory()
  await loadComments()
})
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background:
    linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.95)),
    url('https://images.unsplash.com/photo-1495195134817-aeb325a55b65?auto=format&fit=crop&w=1600&q=80')
      center/cover fixed no-repeat;
}

.detail-wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 36px 20px 60px;
}

.detail-header {
  display: flex;
  gap: 28px;
  align-items: flex-start;
}

.image-box {
  width: 520px;
  flex-shrink: 0;
}

.back-row {
  max-width: 1200px;
  margin: 20px auto 0;
  padding: 0 20px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.back-btn {
  border: none;
  background: #eef6ff;
  color: #2563eb;
  padding: 10px 16px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.back-btn:hover {
  background: #dbeafe;
}

.image-box img {
  width: 100%;
  border-radius: 18px;
  display: block;
  object-fit: cover;
}

.info-box {
  flex: 1;
}

.info-box h1 {
  font-size: 46px;
  margin-bottom: 18px;
  color: #1f2937;
}

.meta-line {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
  color: #6b7280;
  margin-bottom: 18px;
}

.tag {
  background: #dbeafe;
  color: #3b82f6;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 14px;
}

.level {
  background: #dcfce7;
  color: #16a34a;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 14px;
}

.desc {
  font-size: 18px;
  line-height: 1.9;
  color: #4b5563;
  margin-bottom: 20px;
}

.action-row {
  display: flex;
  gap: 14px;
}

.action-btn {
  border: 1px solid #d1d5db;
  background: #fff;
  padding: 10px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: 0.2s ease;
}

.action-btn:hover {
  background: #f8fafc;
  border-color: #93c5fd;
}

.section-card {
  margin-top: 36px;
  background: rgba(255, 255, 255, 0.82);
  border-radius: 18px;
  padding: 24px;
}

.section-card h2 {
  font-size: 30px;
  margin-bottom: 18px;
}

.sub-text {
  font-size: 14px;
  color: #3b82f6;
  margin-left: 10px;
}

.ingredient-table {
  width: 100%;
  border-collapse: collapse;
}

.ingredient-table th,
.ingredient-table td {
  text-align: left;
  padding: 14px 12px;
  border-bottom: 1px solid #e5e7eb;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.step-title {
  margin-bottom: 8px;
  color: #94a3b8;
  font-weight: 700;
}

.step-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}

.step-time {
  display: inline-block;
  margin-top: 10px;
  background: #f3f4f6;
  color: #9ca3af;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 13px;
}

.comment-section {
  margin-top: 40px;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
}

.comment-section h2 {
  margin: 0 0 20px;
  font-size: 30px;
  color: #1f2937;
}

.comment-editor textarea,
.reply-editor textarea {
  width: 100%;
  min-height: 100px;
  border: 1px solid #dbe4ee;
  border-radius: 14px;
  padding: 14px 16px;
  font-size: 15px;
  resize: vertical;
  box-sizing: border-box;
  outline: none;
}

.comment-editor button,
.reply-actions button,
.comment-actions button {
  border: none;
  cursor: pointer;
  transition: 0.2s ease;
}

.comment-editor button,
.reply-actions button:first-child {
  margin-top: 12px;
  background: #2490ff;
  color: #fff;
  padding: 10px 18px;
  border-radius: 10px;
  font-weight: 700;
}

.reply-actions button:last-child {
  margin-top: 12px;
  margin-left: 10px;
  background: #eef2f7;
  color: #475569;
  padding: 10px 18px;
  border-radius: 10px;
  font-weight: 700;
}

.comment-list {
  margin-top: 24px;
}

.comment-item {
  padding: 18px 0;
  border-bottom: 1px solid #e5edf5;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-user {
  font-weight: 800;
  color: #1f2937;
}

.comment-time {
  color: #94a3b8;
  font-size: 13px;
}

.comment-content {
  color: #334155;
  line-height: 1.8;
  font-size: 15px;
}

.comment-actions {
  display: flex;
  gap: 12px;
  margin-top: 10px;
}

.comment-actions button {
  background: transparent;
  color: #2490ff;
  font-size: 14px;
  font-weight: 700;
}

.reply-editor {
  margin-top: 14px;
  padding: 14px;
  background: #f8fafc;
  border-radius: 14px;
}

.reply-list {
  margin-top: 14px;
  margin-left: 24px;
  padding-left: 14px;
  border-left: 3px solid #e5edf5;
}

.reply-item {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 10px;
}

.empty-comment {
  margin-top: 20px;
  color: #94a3b8;
  font-size: 15px;
}

.loading-box {
  text-align: center;
  padding: 80px 0;
  font-size: 20px;
  color: #6b7280;
}
</style>