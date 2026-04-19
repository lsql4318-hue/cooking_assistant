<template>
  <div class="publish-page">
    <TopNav />
    <div class="publish-wrap">
      <h1>发布菜谱</h1>

      <input v-model="title" placeholder="菜谱名称" />
      <textarea v-model="description" placeholder="菜谱简介"></textarea>
      <input v-model="category" placeholder="菜系，例如：川菜" />
      <input v-model="difficulty" placeholder="难度，例如：简单" />
      <input v-model="cookTime" placeholder="耗时，例如：20分钟" />
      <input v-model="servings" placeholder="份量，例如：2人份" />

      <input type="file" @change="handleImageChange" />

      <h3>食材</h3>
      <div v-for="(item, index) in ingredients" :key="index" class="row">
        <input v-model="item.name" placeholder="食材名" />
        <input v-model="item.amount" placeholder="用量" />
        <input v-model="item.unit" placeholder="单位" />
      </div>
      <button @click="addIngredient">新增食材</button>

      <h3>步骤</h3>
      <div v-for="(item, index) in steps" :key="index" class="row">
        <input v-model="item.content" placeholder="步骤内容" />
        <input v-model="item.time" placeholder="耗时说明" />
      </div>
      <button @click="addStep">新增步骤</button>

      <div class="submit-row">
        <button class="submit-btn" @click="submitRecipe">提交审核</button>
      </div>

      <p v-if="message" class="submit-message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TopNav from '../components/TopNav.vue'

const API_BASE = 'http://localhost:8000'

const title = ref('')
const description = ref('')
const category = ref('')
const difficulty = ref('')
const cookTime = ref('')
const servings = ref('2人份')
const imageFile = ref(null)
const message = ref('')

const ingredients = ref([{ name: '', amount: '', unit: '' }])
const steps = ref([{ content: '', time: '' }])

const getCookie = (name) => {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith(name + '='))

  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : ''
}

const handleImageChange = (e) => {
  imageFile.value = e.target.files[0] || null
}

const addIngredient = () => {
  ingredients.value.push({ name: '', amount: '', unit: '' })
}

const addStep = () => {
  steps.value.push({ content: '', time: '' })
}

const submitRecipe = async () => {
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

    const res = await fetch(`${API_BASE}/api/recipes/submit/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRFToken': csrftoken
      },
      body: formData
    })

    const data = await res.json()
    message.value = data.message || '提交完成'

    if (data.success) {
      title.value = ''
      description.value = ''
      category.value = ''
      difficulty.value = ''
      cookTime.value = ''
      servings.value = '2人份'
      imageFile.value = null
      ingredients.value = [{ name: '', amount: '', unit: '' }]
      steps.value = [{ content: '', time: '' }]
    }
  } catch (error) {
    message.value = '提交失败，请稍后重试'
  }
}
</script>

<style scoped>
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
  border: none;
  padding: 14px 32px;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
}

.submit-message {
  text-align: center;
  margin-top: 10px;
  color: #1f2937;
}

.publish-wrap {
  max-width: 900px;
  margin: 30px auto;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
}
input, textarea {
  width: 100%;
  margin-bottom: 12px;
  padding: 12px;
  border: 1px solid #dbe4ee;
  border-radius: 10px;
  box-sizing: border-box;
}
.row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
}
.submit-btn {
  margin-top: 16px;
  background: #2490ff;
  color: #fff;
  border: none;
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}
</style>