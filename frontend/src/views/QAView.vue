<template>
  <div class="qa-page">
    <TopNav />

    <div class="qa-container">
      <div class="qa-header-card">
        <div class="header-badge">🤖 智能模块</div>
        <div class="header-main">
          <div>
            <h1>智能问答</h1>
            <p>围绕菜品、食材、菜系、口味、时间、难度进行智能问答，并联动知识图谱与菜谱页面查看结果。</p>
          </div>

          <div class="header-tags">
            <span class="header-tag">回车提问</span>
            <span class="header-tag">点击示例</span>
            <span class="header-tag">跳转图谱</span>
          </div>
        </div>
      </div>

      <div class="qa-chat-card">
        <div class="chat-toolbar">
          <div class="toolbar-left">
            <div class="toolbar-title">问答对话</div>
            <div class="toolbar-subtitle">你可以直接像聊天一样提问</div>
          </div>

          <div class="toolbar-right">
            <button
              v-if="historyQuestions.length"
              class="toolbar-btn"
              @click="clearHistory"
            >
              清空历史
            </button>
            <button
              class="toolbar-btn"
              :disabled="!chatMessages.length"
              @click="clearConversation"
            >
              清空对话
            </button>
          </div>
        </div>

        <div class="example-strip">
          <button class="example-chip" @click="useExample('西红柿炒鸡蛋有哪些食材')">
            🍲 西红柿炒鸡蛋有哪些食材
          </button>
          <button class="example-chip" @click="useExample('青椒可以做什么菜')">
            🥬 青椒可以做什么菜
          </button>
          <button class="example-chip" @click="useExample('家常菜有哪些菜')">
            🍳 家常菜有哪些菜
          </button>
          <button class="example-chip" @click="useExample('20分钟内能做什么菜')">
            ⏱️ 20分钟内能做什么菜
          </button>
          <button class="example-chip" @click="useExample('简单的家常菜有哪些')">
            🥘 简单的家常菜有哪些
          </button>
          <button class="example-chip" @click="useExample('家常菜里20分钟内的简单菜有哪些')">
            ✨ 家常菜里20分钟内的简单菜有哪些
          </button>
        </div>

        <div class="chat-panel" ref="chatPanelRef">
          <template v-if="chatMessages.length">
            <div
              v-for="(msg, index) in chatMessages"
              :key="index"
              class="message-row"
              :class="msg.role"
            >
              <div class="avatar" :class="{ ai: msg.role === 'assistant' }">
                <span v-if="msg.role === 'user'">你</span>
                <span v-else>AI</span>
              </div>

              <div class="bubble-wrap">
                <div class="bubble-meta">
                  <span>{{ msg.role === 'user' ? '你的提问' : '系统回答' }}</span>
                </div>

                <div class="bubble" :class="msg.role === 'user' ? 'user' : 'ai'">
                  <template v-if="msg.role === 'user'">
                    <div class="bubble-text">{{ msg.text }}</div>
                  </template>

                  <template v-else>
                    <div class="bubble-text">
                      {{ msg.answer || msg.message || '暂无结果' }}
                    </div>

                    <div v-if="msg.entity || msg.type" class="qa-meta-grid">
                      <div v-if="msg.entity" class="qa-meta-item">
                        <div class="meta-label">识别实体</div>
                        <div class="meta-value">{{ msg.entity }}</div>
                      </div>

                      <div v-if="msg.type" class="qa-meta-item">
                        <div class="meta-label">问答类型</div>
                        <div class="meta-value">{{ formatTypeLabel(msg.type) }}</div>
                      </div>
                    </div>

                    <div v-if="msg.data && msg.data.length" class="result-block">
                      <div class="block-title">结果列表</div>
                      <div class="result-tags">
                        <button
                          v-for="(item, itemIndex) in msg.data"
                          :key="itemIndex"
                          class="result-tag result-tag-btn"
                          @click="handleResultTagClick(msg, item)"
                        >
                          {{ item }}
                        </button>
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </template>

          <div v-else class="empty-chat">
            <div class="empty-icon">💬</div>
            <div class="empty-title">开始一次智能问答吧</div>
            <div class="empty-text">
              例如：输入“猪里脊可以做什么菜”“20分钟内能做什么菜”或“简单的家常菜有哪些”。
            </div>

            <div v-if="historyQuestions.length" class="recent-questions">
              <div class="recent-title">最近提问</div>
              <div class="recent-list">
                <button
                  v-for="(item, index) in historyQuestions"
                  :key="index"
                  class="recent-chip"
                  @click="useHistory(item)"
                >
                  {{ item }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="loading" class="thinking-row">
            <div class="avatar ai">
              <span>AI</span>
            </div>
            <div class="bubble-wrap">
              <div class="bubble-meta">
                <span>系统回答</span>
              </div>
              <div class="bubble ai thinking-bubble">
                <div class="thinking-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span class="thinking-text">正在分析你的问题...</span>
              </div>
            </div>
          </div>
        </div>

        <div class="input-panel">
          <textarea
            v-model="question"
            class="question-input"
            placeholder="请输入你的问题，例如：家常菜里20分钟内的简单菜有哪些"
            @keydown="handleKeydown"
          ></textarea>

          <div class="input-actions">
            <div class="left-actions">
              <button
                class="secondary-btn"
                :disabled="loading || !question.trim()"
                @click="clearQuestion"
              >
                清空输入
              </button>
              <span v-if="message" class="message-text">{{ message }}</span>
            </div>

            <button
              class="submit-btn"
              :disabled="loading"
              @click="submitQuestion"
            >
              {{ loading ? '思考中...' : '提问' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import TopNav from '../components/TopNav.vue'

const router = useRouter()

const question = ref('')
const result = ref(null)
const message = ref('')
const loading = ref(false)
const historyQuestions = ref([])
const chatMessages = ref([])
const chatPanelRef = ref(null)

const HISTORY_KEY = 'qa_history_questions'
const API_BASE = 'http://localhost:8000'

const loadHistory = () => {
  try {
    const raw = localStorage.getItem(HISTORY_KEY)
    historyQuestions.value = raw ? JSON.parse(raw) : []
  } catch (error) {
    historyQuestions.value = []
  }
}

const saveHistory = (q) => {
  const text = (q || '').trim()
  if (!text) return

  const list = historyQuestions.value.filter((item) => item !== text)
  list.unshift(text)
  historyQuestions.value = list.slice(0, 8)

  localStorage.setItem(HISTORY_KEY, JSON.stringify(historyQuestions.value))
}

const clearHistory = () => {
  historyQuestions.value = []
  localStorage.removeItem(HISTORY_KEY)
}

const clearQuestion = () => {
  question.value = ''
  message.value = ''
}

const clearConversation = () => {
  chatMessages.value = []
  result.value = null
  message.value = ''
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatPanelRef.value) {
    chatPanelRef.value.scrollTop = chatPanelRef.value.scrollHeight
  }
}

const handleKeydown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    submitQuestion()
  }
}

const formatTypeLabel = (type) => {
  const typeMap = {
    dish_ingredients: '菜品查食材',
    ingredient_dishes: '食材查菜品',
    taste_dishes: '口味查菜品',
    category_dishes: '菜系查菜品',
    time_dishes: '时间筛选',
    difficulty_dishes: '难度筛选',
    time_difficulty_dishes: '时间 + 难度筛选',
    category_time_dishes: '菜系 + 时间筛选',
    category_difficulty_dishes: '菜系 + 难度筛选',
    category_time_difficulty_dishes: '菜系 + 时间 + 难度筛选',
    unknown: '未识别问题',
  }
  return typeMap[type] || type || '问答结果'
}

const submitQuestion = async () => {
  message.value = ''
  result.value = null

  const q = question.value.trim()
  if (!q) {
    message.value = '请输入问题'
    return
  }

  chatMessages.value.push({
    role: 'user',
    text: q,
  })
  await scrollToBottom()

  loading.value = true

  try {
    const response = await fetch(
      `${API_BASE}/api/qa/?question=${encodeURIComponent(q)}`,
      {
        credentials: 'include',
      }
    )

    const text = await response.text()

    let data = {}
    try {
      data = text ? JSON.parse(text) : {}
    } catch (error) {
      throw new Error(`接口返回的不是 JSON：${text.slice(0, 200)}`)
    }

    if (!response.ok) {
      message.value = data.message || `请求失败，状态码：${response.status}`
      chatMessages.value.push({
        role: 'assistant',
        question: q,
        answer: data.message || `请求失败，状态码：${response.status}`,
        message: data.message || '',
        entity: '',
        category: '',
        type: 'unknown',
        data: [],
      })
      await scrollToBottom()
      return
    }

    result.value = data
    saveHistory(q)

    chatMessages.value.push({
      role: 'assistant',
      question: data.question || q,
      answer: data.answer || data.message || '暂无结果',
      message: data.message || '',
      entity: data.entity || '',
      category: data.category || '',
      type: data.type || 'unknown',
      data: data.data || [],
      success: data.success,
    })

    question.value = ''

    if (!data.success) {
      message.value = data.message || '未识别该问题'
    }

    await scrollToBottom()
  } catch (error) {
    console.error('问答请求失败：', error)
    const errMsg = error.message || '问答请求失败，请检查 Django 服务'
    message.value = errMsg

    chatMessages.value.push({
      role: 'assistant',
      question: q,
      answer: errMsg,
      message: errMsg,
      entity: '',
      category: '',
      type: 'unknown',
      data: [],
    })
    await scrollToBottom()
  } finally {
    loading.value = false
  }
}

const useExample = async (text) => {
  question.value = text
  await submitQuestion()
}

const useHistory = async (text) => {
  question.value = text
  await submitQuestion()
}

const goToDishGraph = (dishName) => {
  router.push(`/graph?dish=${encodeURIComponent(dishName)}`)
}

const goToIngredientGraph = (ingredientName) => {
  router.push(`/graph?ingredient=${encodeURIComponent(ingredientName)}`)
}

const handleResultTagClick = (msg, item) => {
  if (!msg || !item) return

  // 菜品查食材：结果列表是食材，点食材跳食材图谱
  if (msg.type === 'dish_ingredients') {
    goToIngredientGraph(item)
    return
  }

  // 食材查菜品：结果列表是菜品，点菜品跳菜品图谱
  if (msg.type === 'ingredient_dishes') {
    goToDishGraph(item)
    return
  }

  // 口味查菜品：结果列表是菜品，点菜品跳菜品图谱
  if (msg.type === 'taste_dishes') {
    goToDishGraph(item)
    return
  }

  // 菜系 / 时间 / 难度相关筛选：结果列表都是菜品，点菜品跳菜品图谱
  if (
    [
      'category_dishes',
      'time_dishes',
      'difficulty_dishes',
      'time_difficulty_dishes',
      'category_time_dishes',
      'category_difficulty_dishes',
      'category_time_difficulty_dishes'
    ].includes(msg.type)
  ) {
    goToDishGraph(item)
    return
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.result-tag-btn {
  border: none;
  cursor: pointer;
  transition: 0.2s ease;
}

.result-tag-btn:hover {
  background: #dbeafe;
  color: #1d4ed8;
  transform: translateY(-1px);
}

.qa-page {
  min-height: 100vh;
  background:
    linear-gradient(rgba(245, 247, 251, 0.96), rgba(245, 247, 251, 0.98)),
    url('https://images.unsplash.com/photo-1495195134817-aeb325a55b65?auto=format&fit=crop&w=1600&q=80')
      center/cover fixed no-repeat;
}

.qa-container {
  max-width: 1220px;
  margin: 0 auto;
  padding: 24px 20px 40px;
  box-sizing: border-box;
}

.qa-header-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 22px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
  padding: 28px 30px;
  margin-bottom: 22px;
  border: 1px solid rgba(226, 232, 240, 0.9);
}

.header-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: #eef9f3;
  color: #1f8f5f;
  font-size: 13px;
  font-weight: 800;
  margin-bottom: 16px;
}

.header-main {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.qa-header-card h1 {
  margin: 0 0 12px;
  font-size: 38px;
  color: #1f2937;
  font-weight: 900;
}

.qa-header-card p {
  margin: 0;
  color: #64748b;
  font-size: 16px;
  line-height: 1.9;
  max-width: 760px;
}

.header-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.header-tag {
  padding: 8px 12px;
  border-radius: 999px;
  background: #f8fafc;
  color: #475569;
  font-size: 13px;
  font-weight: 700;
}

.qa-chat-card {
  background: rgba(255, 255, 255, 0.94);
  border-radius: 22px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(226, 232, 240, 0.9);
  overflow: hidden;
}

.chat-toolbar {
  padding: 22px 24px 16px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  border-bottom: 1px solid #edf2f7;
}

.toolbar-title {
  font-size: 22px;
  font-weight: 900;
  color: #1f2937;
}

.toolbar-subtitle {
  margin-top: 4px;
  font-size: 14px;
  color: #94a3b8;
}

.toolbar-right {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.toolbar-btn {
  border: none;
  background: #f1f5f9;
  color: #334155;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.toolbar-btn:hover {
  background: #e2e8f0;
}

.example-strip {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  padding: 0 24px 18px;
  border-bottom: 1px solid #edf2f7;
}

.example-chip {
  border: none;
  background: #f8fafc;
  color: #334155;
  padding: 10px 14px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  transition: 0.2s ease;
}

.example-chip:hover {
  background: #eaf3ff;
  color: #2490ff;
}

.chat-panel {
  min-height: 430px;
  max-height: 640px;
  overflow-y: auto;
  padding: 22px 24px;
  background: linear-gradient(180deg, #fcfdff 0%, #f8fafc 100%);
}

.message-row,
.thinking-row {
  display: flex;
  gap: 14px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-row.user .bubble-wrap {
  align-items: flex-end;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 999px;
  flex-shrink: 0;
  background: #dbeafe;
  color: #1d4ed8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
}

.avatar.ai {
  background: #dcfce7;
  color: #15803d;
}

.bubble-wrap {
  display: flex;
  flex-direction: column;
  max-width: min(780px, 78%);
}

.bubble-meta {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 8px;
  font-weight: 700;
}

.bubble {
  border-radius: 18px;
  padding: 16px 18px;
  border: 1px solid #e5edf5;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.03);
}

.bubble.user {
  background: #eaf3ff;
  color: #1e3a8a;
  border-color: #cfe2ff;
}

.bubble.ai {
  background: #ffffff;
  color: #1f2937;
}

.bubble-text {
  font-size: 16px;
  line-height: 1.85;
  word-break: break-word;
}

.qa-meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.qa-meta-item {
  background: #f8fafc;
  border: 1px solid #e5edf5;
  border-radius: 14px;
  padding: 12px 14px;
}

.meta-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 800;
  margin-bottom: 6px;
}

.meta-value {
  font-size: 15px;
  color: #1f2937;
  font-weight: 700;
}

.result-block {
  margin-top: 14px;
}

.block-title {
  font-size: 14px;
  font-weight: 800;
  color: #334155;
  margin-bottom: 10px;
}

.result-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.result-tag {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 999px;
  background: #eef6ff;
  color: #2563eb;
  font-size: 14px;
  font-weight: 700;
}

.action-links {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.action-btn {
  border: none;
  padding: 11px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: 0.2s ease;
}

.action-btn.primary {
  background: #2563eb;
  color: #fff;
}

.action-btn.primary:hover {
  background: #1d4ed8;
}

.action-btn.secondary {
  background: #eef2f7;
  color: #334155;
}

.action-btn.secondary:hover {
  background: #e2e8f0;
}

.empty-chat {
  min-height: 360px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #64748b;
  text-align: center;
  padding: 20px;
}

.empty-icon {
  font-size: 42px;
  margin-bottom: 14px;
}

.empty-title {
  font-size: 24px;
  font-weight: 900;
  color: #1f2937;
  margin-bottom: 8px;
}

.empty-text {
  font-size: 15px;
  line-height: 1.8;
  max-width: 520px;
}

.recent-questions {
  margin-top: 22px;
  width: 100%;
  max-width: 760px;
}

.recent-title {
  font-size: 14px;
  font-weight: 800;
  color: #475569;
  margin-bottom: 10px;
}

.recent-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.recent-chip {
  border: none;
  background: #eef6ff;
  color: #2563eb;
  padding: 9px 14px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.thinking-bubble {
  display: flex;
  align-items: center;
  gap: 12px;
}

.thinking-dots {
  display: inline-flex;
  gap: 6px;
}

.thinking-dots span {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #42b983;
  animation: blink 1.2s infinite ease-in-out;
}

.thinking-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.thinking-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

.thinking-text {
  color: #475569;
  font-size: 15px;
  font-weight: 700;
}

@keyframes blink {
  0%, 80%, 100% {
    opacity: 0.35;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-2px);
  }
}

.input-panel {
  border-top: 1px solid #edf2f7;
  background: #ffffff;
  padding: 18px 24px 22px;
}

.question-input {
  width: 100%;
  min-height: 120px;
  resize: vertical;
  border: 1px solid #dbe4ee;
  border-radius: 16px;
  padding: 16px 18px;
  font-size: 17px;
  line-height: 1.8;
  outline: none;
  box-sizing: border-box;
  transition: 0.2s ease;
  background: #fbfdff;
}

.question-input:focus {
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.12);
  background: #fff;
}

.input-actions {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  flex-wrap: wrap;
}

.left-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.secondary-btn,
.submit-btn {
  border: none;
  cursor: pointer;
  transition: 0.2s ease;
}

.secondary-btn {
  background: #eef2f7;
  color: #475569;
  padding: 12px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 800;
}

.secondary-btn:hover {
  background: #e2e8f0;
}

.secondary-btn:disabled,
.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.submit-btn {
  background: #42b983;
  color: white;
  padding: 12px 24px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 900;
}

.submit-btn:hover {
  background: #36a673;
}

.message-text {
  color: #e11d48;
  font-size: 14px;
  font-weight: 700;
}

@media (max-width: 900px) {
  .qa-meta-grid {
    grid-template-columns: 1fr;
  }

  .bubble-wrap {
    max-width: 100%;
  }

  .chat-panel {
    max-height: none;
  }
}

@media (max-width: 768px) {
  .qa-container {
    padding: 14px 14px 28px;
  }

  .qa-header-card,
  .qa-chat-card {
    border-radius: 18px;
  }

  .qa-header-card {
    padding: 22px 18px;
  }

  .qa-header-card h1 {
    font-size: 30px;
  }

  .chat-toolbar,
  .example-strip,
  .chat-panel,
  .input-panel {
    padding-left: 16px;
    padding-right: 16px;
  }

  .message-row,
  .thinking-row {
    gap: 10px;
  }

  .avatar {
    width: 36px;
    height: 36px;
    font-size: 12px;
  }

  .bubble {
    padding: 14px 15px;
  }

  .bubble-text {
    font-size: 15px;
  }

  .question-input {
    min-height: 100px;
    font-size: 16px;
  }

  .input-actions {
    align-items: stretch;
  }
}
</style>