<template>
  <div class="personal-page">
    <TopNav />
    <div class="page-wrap">
      <div class="page-header">
        <h1>个性化服务</h1>
        <p>查看你的投稿状态、驳回原因，并可修改后重新提交审核。</p>
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
})
</script>

<style scoped>
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