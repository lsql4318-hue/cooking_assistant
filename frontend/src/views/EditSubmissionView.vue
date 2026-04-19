<template>
  <div class="edit-page">
    <TopNav />

    <div class="edit-wrap">
      <div class="page-header">
        <h1>修改投稿并重新提交</h1>
        <p>根据管理员审核意见修改后，可重新提交审核。</p>
      </div>

      <div class="form-card">
        <div class="section-title">基础信息</div>

        <div class="form-grid">
          <div class="form-item full">
            <label>菜谱名称</label>
            <input v-model="title" type="text" placeholder="请输入菜谱名称" />
          </div>

          <div class="form-item full">
            <label>菜谱简介</label>
            <textarea v-model="description" placeholder="请输入菜谱简介"></textarea>
          </div>

          <div class="form-item">
            <label>菜系</label>
            <input v-model="category" type="text" placeholder="例如：家常菜 / 川菜" />
          </div>

          <div class="form-item">
            <label>难度</label>
            <input v-model="difficulty" type="text" placeholder="例如：简单 / 中等" />
          </div>

          <div class="form-item">
            <label>耗时</label>
            <input v-model="cookTime" type="text" placeholder="例如：15分钟" />
          </div>

          <div class="form-item">
            <label>份量</label>
            <input v-model="servings" type="text" placeholder="例如：2人份" />
          </div>

          <div class="form-item full">
            <label>更换菜品图片</label>
            <input type="file" @change="handleImageChange" />
            <div v-if="currentImage" class="preview-wrap">
              <div class="preview-label">当前图片</div>
              <img :src="getImageUrl(currentImage)" alt="当前菜品图片" class="preview-image" />
            </div>
          </div>
        </div>
      </div>

      <div class="form-card">
        <div class="section-header">
          <div class="section-title">食材</div>
          <button class="small-add-btn" @click="addIngredient">新增食材</button>
        </div>

        <div
          v-for="(item, index) in ingredients"
          :key="index"
          class="dynamic-card"
        >
          <div class="dynamic-head">
            <span>食材 {{ index + 1 }}</span>
            <button
              v-if="ingredients.length > 1"
              class="remove-btn"
              @click="removeIngredient(index)"
            >
              删除
            </button>
          </div>

          <div class="dynamic-grid ingredient-grid">
            <div class="form-item">
              <label>食材名</label>
              <input v-model="item.name" type="text" placeholder="例如：猪里脊" />
            </div>

            <div class="form-item">
              <label>用量</label>
              <input v-model="item.amount" type="text" placeholder="例如：200" />
            </div>

            <div class="form-item">
              <label>单位</label>
              <input v-model="item.unit" type="text" placeholder="例如：克" />
            </div>
          </div>
        </div>
      </div>

      <div class="form-card">
        <div class="section-header">
          <div class="section-title">步骤</div>
          <button class="small-add-btn" @click="addStep">新增步骤</button>
        </div>

        <div
          v-for="(item, index) in steps"
          :key="index"
          class="dynamic-card"
        >
          <div class="dynamic-head">
            <span>步骤 {{ index + 1 }}</span>
            <button
              v-if="steps.length > 1"
              class="remove-btn"
              @click="removeStep(index)"
            >
              删除
            </button>
          </div>

          <div class="dynamic-grid step-grid">
            <div class="form-item step-content">
              <label>步骤内容</label>
              <textarea
                v-model="item.content"
                placeholder="请输入该步骤的详细内容"
              ></textarea>
            </div>

            <div class="form-item step-time">
              <label>耗时说明</label>
              <input v-model="item.time" type="text" placeholder="例如：约5分钟" />
            </div>
          </div>
        </div>
      </div>

      <div class="submit-row">
        <button class="submit-btn" @click="resubmitRecipe">重新提交审核</button>
      </div>

      <p v-if="message" class="submit-message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopNav from '../components/TopNav.vue'

const API_BASE = 'http://localhost:8000'
const route = useRoute()
const router = useRouter()

const title = ref('')
const description = ref('')
const category = ref('')
const difficulty = ref('')
const cookTime = ref('')
const servings = ref('2人份')
const currentImage = ref('')
const imageFile = ref(null)
const message = ref('')

const ingredients = ref([{ name: '', amount: '', unit: '' }])
const steps = ref([{ content: '', time: '' }])

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${API_BASE}${url}`
}

const handleImageChange = (e) => {
  imageFile.value = e.target.files[0] || null
}

const addIngredient = () => {
  ingredients.value.push({ name: '', amount: '', unit: '' })
}

const removeIngredient = (index) => {
  ingredients.value.splice(index, 1)
}

const addStep = () => {
  steps.value.push({ content: '', time: '' })
}

const removeStep = (index) => {
  steps.value.splice(index, 1)
}

const loadDetail = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/recipes/my-submissions/${route.params.id}/`, {
      credentials: 'include'
    })
    const data = await res.json()

    if (!data.success) {
      message.value = data.message || '加载失败'
      return
    }

    const d = data.detail
    title.value = d.title || ''
    description.value = d.description || ''
    category.value = d.category || ''
    difficulty.value = d.difficulty || ''
    cookTime.value = d.cook_time || ''
    servings.value = d.servings || '2人份'
    currentImage.value = d.image || ''
    ingredients.value = d.ingredients?.length
      ? d.ingredients
      : [{ name: '', amount: '', unit: '' }]
    steps.value = d.steps?.length
      ? d.steps
      : [{ content: '', time: '' }]
  } catch (error) {
    message.value = '加载投稿详情失败'
  }
}

const getCookie = (name) => {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith(name + '='))

  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : ''
}

const resubmitRecipe = async () => {
  try {
    const csrftoken = getCookie('csrftoken')
    const formData = new FormData()

    formData.append('title', title.value)
    formData.append('description', description.value)
    formData.append('category', category.value)
    formData.append('difficulty', difficulty.value)
    formData.append('cook_time', cookTime.value)
    formData.append('servings', servings.value)
    formData.append('ingredients_json', JSON.stringify(ingredients.value))
    formData.append('steps_json', JSON.stringify(steps.value))

    if (imageFile.value) {
      formData.append('image', imageFile.value)
    }

    const res = await fetch(
      `${API_BASE}/api/recipes/my-submissions/${route.params.id}/resubmit/`,
      {
        method: 'POST',
        credentials: 'include',
        headers: {
          'X-CSRFToken': csrftoken
        },
        body: formData
      }
    )

    const data = await res.json()
    message.value = data.message || '提交完成'

    if (data.success) {
      setTimeout(() => {
        router.push('/personal')
      }, 800)
    }
  } catch (error) {
    message.value = '重新提交失败'
  }
}

onMounted(async () => {
  await loadDetail()
})
</script>

<style scoped>
.edit-page {
  min-height: 100vh;
  background: #f5f7fb;
}

.edit-wrap {
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px 20px 50px;
}

.page-header {
  margin-bottom: 22px;
}

.page-header h1 {
  margin: 0 0 8px;
  font-size: 36px;
  font-weight: 800;
  color: #1f2937;
}

.page-header p {
  margin: 0;
  color: #64748b;
  font-size: 15px;
}

.form-card {
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 8px 26px rgba(15, 23, 42, 0.06);
  padding: 24px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 24px;
  font-weight: 800;
  color: #1f2937;
  margin-bottom: 18px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.form-item {
  display: flex;
  flex-direction: column;
}

.form-item.full {
  grid-column: 1 / -1;
}

.form-item label {
  margin-bottom: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #374151;
}

.form-item input,
.form-item textarea {
  width: 100%;
  padding: 13px 14px;
  border: 1px solid #dbe4ee;
  border-radius: 12px;
  font-size: 15px;
  box-sizing: border-box;
  background: #fff;
  outline: none;
  transition: 0.2s ease;
}

.form-item input:focus,
.form-item textarea:focus {
  border-color: #2490ff;
  box-shadow: 0 0 0 3px rgba(36, 144, 255, 0.1);
}

.form-item textarea {
  min-height: 120px;
  resize: vertical;
}

.preview-wrap {
  margin-top: 12px;
}

.preview-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
}

.preview-image {
  width: 220px;
  max-width: 100%;
  border-radius: 12px;
  border: 1px solid #e5edf5;
  display: block;
}

.dynamic-card {
  border: 1px solid #e5edf5;
  border-radius: 16px;
  background: #f8fafc;
  padding: 18px;
  margin-bottom: 14px;
}

.dynamic-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  font-weight: 700;
  color: #1f2937;
}

.dynamic-grid {
  display: grid;
  gap: 14px;
}

.ingredient-grid {
  grid-template-columns: 1.3fr 1fr 1fr;
}

.step-grid {
  grid-template-columns: 2fr 1fr;
  align-items: start;
}

.step-content textarea {
  min-height: 100px;
}

.small-add-btn,
.remove-btn,
.submit-btn {
  border: none;
  cursor: pointer;
  transition: 0.2s ease;
}

.small-add-btn {
  background: #eef6ff;
  color: #2490ff;
  padding: 10px 16px;
  border-radius: 10px;
  font-weight: 700;
}

.small-add-btn:hover {
  background: #dbeafe;
}

.remove-btn {
  background: #fff1f2;
  color: #e11d48;
  padding: 8px 14px;
  border-radius: 10px;
  font-weight: 700;
}

.remove-btn:hover {
  background: #ffe4e6;
}

.submit-row {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-top: 28px;
  margin-bottom: 12px;
}

.submit-btn {
  background: #2490ff;
  color: #fff;
  padding: 14px 34px;
  border-radius: 14px;
  font-size: 18px;
  font-weight: 800;
}

.submit-btn:hover {
  background: #1d7fe0;
}

.submit-message {
  text-align: center;
  font-size: 16px;
  color: #1f2937;
  margin-top: 10px;
}

@media (max-width: 900px) {
  .form-grid,
  .ingredient-grid,
  .step-grid {
    grid-template-columns: 1fr;
  }

  .page-header h1 {
    font-size: 30px;
  }
}

@media (max-width: 768px) {
  .edit-wrap {
    padding: 18px 14px 36px;
  }

  .form-card {
    padding: 18px;
  }

  .section-header {
    align-items: flex-start;
  }

  .dynamic-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>