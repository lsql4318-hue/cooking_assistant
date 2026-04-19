<template>
  <div class="graph-page">
    <TopNav />

    <div class="page">
      <div class="query-panel">
        <div class="query-card card">
          <div class="query-head">🍲 菜品查食材</div>
          <input
            v-model="dishName"
            placeholder="请输入菜名，例如：西湖牛肉羹"
            @keyup.enter="searchByDish"
          />
          <button class="primary-btn" @click="searchByDish">查询图谱</button>
        </div>

        <div class="query-card card">
          <div class="query-head">🥬 食材查菜品</div>
          <input
            v-model="ingredientName"
            placeholder="请输入食材，例如：香菜"
            @keyup.enter="searchByIngredient"
          />
          <button class="primary-btn" @click="searchByIngredient">查询图谱</button>
        </div>

        <div class="query-card card">
          <div class="query-head">🥘 菜系查菜品</div>
          <input
            v-model="categoryName"
            placeholder="请输入菜系，例如：川菜"
            @keyup.enter="searchByCategory"
          />
          <button class="primary-btn" @click="searchByCategory">查询图谱</button>
        </div>
      </div>

      <div class="action-bar">
        <button class="back-btn" @click="loadOverviewGraph">返回主视图</button>
      </div>

      <div v-if="message" class="message-box">
        {{ message }}
      </div>

      <div class="content-area">
        <div class="graph-area card">
          <div class="section-header">
            <h2>📍 知识图谱展示区</h2>
            <span class="mini-tag">可拖拽 / 可缩放 / 可点击节点</span>
          </div>

          <div class="graph-title" v-if="graphTitle">{{ graphTitle }}</div>
          <div class="empty-tip" v-if="!graphTitle">请先在上方输入条件并点击查询</div>
          <div ref="chartRef" class="graph-chart"></div>
        </div>

        <div class="detail-area card">
          <div class="section-header">
            <h2>📄 节点详情</h2>
          </div>

          <div class="detail-box">
            <template v-if="detailData">
              <div class="detail-line">
                <span class="label">类型</span>
                <span>{{ detailData.type || '-' }}</span>
              </div>

              <div class="detail-line">
                <span class="label">名称</span>
                <span>{{ detailData.name || '-' }}</span>
              </div>

              <template v-if="detailData.type === 'Dish'">
                <div
                  v-if="detailData.image"
                  class="node-image-wrap"
                >
                  <img
                    :src="getNodeImageUrl(detailData.image)"
                    :alt="detailData.name"
                    class="node-image"
                  />
                </div>

                <div class="detail-line">
                  <span class="label">难度</span>
                  <span>{{ detailData.difficulty || '-' }}</span>
                </div>

                <div class="detail-line">
                  <span class="label">烹饪时间</span>
                  <span>{{ detailData.cook_time || '-' }}</span>
                </div>

                <div
                  v-if="detailData.items && detailData.items.length"
                  class="list-block"
                >
                  <div class="sub-title">关联食材</div>
                  <ul>
                    <li v-for="(item, index) in detailData.items" :key="index">
                      {{ item }}
                    </li>
                  </ul>
                </div>

                <div class="detail-actions">
                  <button class="favorite-btn" @click="toggleFavoriteFromGraph">
                    ⭐ 收藏当前菜品
                  </button>

                  <button class="detail-btn" @click="goRecipeDetailFromGraph">
                    📖 查看菜谱详情
                  </button>
                </div>
              </template>

              <template
                v-if="
                  detailData.type === 'Ingredient' ||
                  detailData.type === 'Category' ||
                  detailData.type === 'Method'
                "
              >
                <div class="detail-line">
                  <span class="label">关联菜品数量</span>
                  <span>{{ detailData.dish_count || 0 }}</span>
                </div>

                <div
                  v-if="detailData.dishes && detailData.dishes.length"
                  class="list-block"
                >
                  <div class="sub-title">关联菜品</div>
                  <ul>
                    <li v-for="(item, index) in detailData.dishes" :key="index">
                      {{ item }}
                    </li>
                  </ul>
                </div>

                <div
                  v-else-if="detailData.items && detailData.items.length"
                  class="list-block"
                >
                  <div class="sub-title">关联菜品</div>
                  <ul>
                    <li v-for="(item, index) in detailData.items" :key="index">
                      {{ item }}
                    </li>
                  </ul>
                </div>
              </template>
            </template>

            <template v-else>
              <div class="empty-detail">点击图谱节点后，这里会显示节点详情</div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'
import TopNav from '../components/TopNav.vue'

const router = useRouter()
const route = useRoute()

const API_BASE = 'http://localhost:8000/api'
const MEDIA_BASE = 'http://localhost:8000'

const dishName = ref('')
const ingredientName = ref('')
const categoryName = ref('')
const message = ref('')

const graphTitle = ref('')
const detailData = ref(null)

const chartRef = ref(null)
let chartInstance = null

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

const getNodeImageUrl = (image) => {
  if (!image) return ''
  if (image.startsWith('http')) return image
  return `${MEDIA_BASE}${image}`
}

const goRecipeDetailFromGraph = () => {
  if (!detailData.value) return
  if (detailData.value.type !== 'Dish') return

  const recipeId = detailData.value.recipe_id
  const currentDishName = detailData.value.name

  if (recipeId) {
    router.push({
      path: `/recipe/${recipeId}`,
      query: {
        from: 'graph',
        name: currentDishName || ''
      }
    })
  } else {
    alert('当前菜品还没有关联到菜谱详情页')
  }
}

const requestJson = async (url, options = {}) => {
  const response = await fetch(url, {
    credentials: 'include',
    ...options,
  })

  const text = await response.text()

  let data = {}
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

const getCookie = (name) => {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith(name + '='))

  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : ''
}

const ensureCsrfCookie = async () => {
  await fetch(`${API_BASE}/csrf/`, {
    credentials: 'include'
  })
}

const toggleFavoriteFromGraph = async () => {
  if (!detailData.value || detailData.value.type !== 'Dish' || !detailData.value.recipe_id) {
    message.value = '当前菜品无法收藏'
    return
  }

  try {
    const csrftoken = getCookie('csrftoken')

    const data = await requestJson(`${API_BASE}/recipes/favorite/toggle/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({
        recipe_id: detailData.value.recipe_id,
      }),
    })

    message.value = data.message || '操作成功'
  } catch (error) {
    message.value = error.message || '收藏失败'
  }
}

const addHistory = async (currentDishName) => {
  try {
    await requestJson(`${API_BASE}/history/add/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        dish_name: currentDishName,
      }),
    })
  } catch (error) {
    console.error('记录浏览历史失败')
  }
}

const loadNodeDetail = async (nodeType, nodeName) => {
  try {
    const data = await requestJson(
      `${API_BASE}/node-detail/?type=${encodeURIComponent(nodeType)}&name=${encodeURIComponent(nodeName)}`
    )

    if (data.success) {
      detailData.value = data.detail
    }
  } catch (error) {
    message.value = '节点详情加载失败'
  }
}

const initChart = async () => {
  await nextTick()
  if (!chartRef.value) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
}

const renderGraph = async (nodes, links) => {
  await initChart()
  if (!chartInstance) return

  const option = {
    tooltip: {
      formatter(params) {
        if (params.dataType === 'node') {
          return `${params.data.category}<br/>${params.data.name}`
        }
        if (params.dataType === 'edge') {
          return params.data.relation || ''
        }
        return ''
      },
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        label: {
          show: true,
        },
        force: {
          repulsion: 250,
          edgeLength: 140,
        },
        data: nodes.map((node) => ({
          ...node,
          symbolSize:
            node.category === 'Dish'
              ? 72
              : node.category === 'Category'
                ? 64
                : node.category === 'Taste'
                  ? 60
                  : node.category === 'Method'
                    ? 58
                    : 54
        })),
        links,
        categories: [
          { name: 'Dish' },
          { name: 'Ingredient' },
          { name: 'Method' },
          { name: 'Category' },
        ],
        lineStyle: {
          width: 2,
        },
      },
    ],
  }

  chartInstance.clear()
  chartInstance.setOption(option)
  chartInstance.resize()

  chartInstance.off('click')
  chartInstance.on('click', async (params) => {
    if (params.dataType !== 'node') return

    await loadNodeDetail(params.data.category, params.data.name)

    if (params.data.category === 'Dish') {
      await addHistory(params.data.name)
    }
  })
}

const loadOverviewGraph = async () => {
  message.value = ''
  detailData.value = null

  try {
    const data = await requestJson(`${API_BASE}/graph/overview/`)
    if (data.success) {
      graphTitle.value = '默认主图谱视图'
      await renderGraph(data.nodes, data.links)
    } else {
      message.value = '默认主图谱加载失败'
    }
  } catch (error) {
    message.value = '默认主图谱请求失败，请检查 Django 服务是否启动'
  }
}

const runGraphSearch = async ({
  keyword,
  apiPath,
  emptyMessage,
  titleBuilder,
  nameField,
  resultType,
  itemCategory,
  recordHistory = false,
}) => {
  message.value = ''
  detailData.value = null

  if (!keyword.trim()) {
    message.value = emptyMessage
    return
  }

  try {
    const data = await requestJson(
      `${API_BASE}${apiPath}${encodeURIComponent(keyword)}`
    )

    if (!data.success) {
      message.value = data.message || '查询失败'
      return
    }

    const currentName = data[nameField]
    graphTitle.value = titleBuilder(currentName)
    await renderGraph(data.nodes, data.links)

    if (recordHistory) {
      await addHistory(currentName)
    }

    const relatedNames = data.nodes
      .filter((node) => node.category === itemCategory)
      .map((node) => node.name)
      .filter((name) => name && String(name).trim() !== '')

    if (resultType === 'Category' || resultType === 'Ingredient') {
      detailData.value = {
        type: resultType,
        name: currentName,
        dish_count: relatedNames.length,
        dishes: relatedNames,
      }
    } else {
      detailData.value = {
        type: resultType,
        name: currentName,
        items: relatedNames,
      }
    }
  } catch (error) {
    message.value = '请求失败，请检查 Django 服务是否启动'
  }
}

const searchByDish = async () => {
  await runGraphSearch({
    keyword: dishName.value,
    apiPath: '/graph/dish/?name=',
    emptyMessage: '请输入菜名',
    titleBuilder: (name) => `当前查询：菜品「${name}」的知识图谱`,
    nameField: 'dish_name',
    resultType: 'Dish',
    itemCategory: 'Ingredient',
    recordHistory: true,
  })
}

const searchByIngredient = async () => {
  await runGraphSearch({
    keyword: ingredientName.value,
    apiPath: '/graph/ingredient/?name=',
    emptyMessage: '请输入食材名',
    titleBuilder: (name) => `当前查询：食材「${name}」关联的知识图谱`,
    nameField: 'ingredient_name',
    resultType: 'Ingredient',
    itemCategory: 'Dish',
  })
}

const searchByCategory = async () => {
  await runGraphSearch({
    keyword: categoryName.value,
    apiPath: '/graph/category/?name=',
    emptyMessage: '请输入菜系',
    titleBuilder: (name) => `当前查询：菜系「${name}」对应的知识图谱`,
    nameField: 'category_name',
    resultType: 'Category',
    itemCategory: 'Dish',
  })
}

onMounted(async () => {
  await ensureCsrfCookie()

  const dish = route.query.dish
  const ingredient = route.query.ingredient
  const category = route.query.category

  if (dish) {
    dishName.value = dish
    await searchByDish()
  } else if (ingredient) {
    ingredientName.value = ingredient
    await searchByIngredient()
  } else if (category) {
    categoryName.value = category
    await searchByCategory()
  } else {
    await loadOverviewGraph()
  }

  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)

  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.graph-page {
  min-height: 100vh;
  background: #f5f7fb;
}

.page {
  width: 100%;
  font-family: Arial, sans-serif;
  padding: 24px 20px 40px;
  box-sizing: border-box;
  max-width: 1220px;
  margin: 0 auto;
}

.card {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 26px rgba(15, 23, 42, 0.06);
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding: 22px 24px;
  margin-bottom: 22px;
}

.page-title-wrap h1 {
  margin: 10px 0 8px 0;
  font-size: 34px;
}

.page-badge {
  display: inline-block;
  background: #eef9f3;
  color: #1f8f5f;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
}

.page-subtitle {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.query-panel {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 20px;
}

.query-card {
  padding: 20px;
}

.query-head {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 14px;
}

.query-card input {
  width: 100%;
  padding: 12px 14px;
  font-size: 15px;
  border: 1px solid #dbe4ee;
  border-radius: 10px;
  margin-bottom: 12px;
  outline: none;
  box-sizing: border-box;
}

.query-card input:focus {
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.12);
}

.primary-btn,
.favorite-btn,
.back-btn {
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: 0.2s ease;
}

.primary-btn {
  width: 100%;
  background: #42b983;
  color: white;
  padding: 12px;
  font-size: 15px;
  font-weight: 700;
}

.favorite-btn {
  margin-top: 14px;
  background: #f59e0b;
  color: white;
  padding: 10px 14px;
  font-size: 15px;
}

.back-btn {
  background: #2563eb;
  color: white;
  padding: 10px 18px;
  font-size: 15px;
  font-weight: 700;
}

.action-bar {
  text-align: center;
  margin-bottom: 18px;
}

.message-box {
  background: #fff7ed;
  color: #c2410c;
  border: 1px solid #fed7aa;
  padding: 12px 14px;
  border-radius: 12px;
  margin-bottom: 18px;
}

.content-area {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(320px, 1.2fr);
  gap: 20px;
  align-items: start;
}

.graph-area {
  padding: 18px;
  min-width: 0;
}

.detail-area {
  padding: 18px;
  min-width: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.section-header h2 {
  margin: 0;
  font-size: 24px;
}

.mini-tag {
  font-size: 12px;
  color: #64748b;
  background: #f8fafc;
  padding: 6px 10px;
  border-radius: 999px;
}

.graph-title {
  text-align: center;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 700;
}

.empty-tip {
  text-align: center;
  color: #94a3b8;
  margin: 8px 0 12px;
}

.graph-chart {
  width: 100%;
  height: 530px;
}

.detail-box {
  min-height: 600px;
  background: #f8fafc;
  border-radius: 14px;
  padding: 18px;
  box-sizing: border-box;
}

.detail-line {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 9px 0;
  border-bottom: 1px solid #e5edf5;
}

.label {
  color: #64748b;
  font-weight: 700;
}

.node-image-wrap {
  margin: 14px 0 18px;
  border-radius: 14px;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid #e5edf5;
}

.node-image {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  display: block;
}

.detail-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.detail-btn {
  border: none;
  background: #3b82f6;
  color: #fff;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.detail-btn:hover {
  background: #2563eb;
}

.sub-title {
  margin-top: 14px;
  font-weight: 700;
}

.list-block ul,
.detail-box ul {
  padding-left: 20px;
  line-height: 1.8;
}

.empty-detail {
  color: #94a3b8;
  padding-top: 10px;
}

@media (max-width: 1100px) {
  .query-panel {
    grid-template-columns: 1fr;
  }

  .content-area {
    grid-template-columns: 1fr;
  }

  .detail-box {
    min-height: auto;
  }
}

@media (max-width: 768px) {
  .page {
    padding: 14px 14px 28px;
  }

  .top-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .page-title-wrap h1 {
    font-size: 28px;
  }

  .graph-chart {
    height: 460px;
  }
}
</style>