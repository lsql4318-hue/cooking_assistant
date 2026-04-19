<template>
  <header class="top-nav">
    <div class="nav-inner">
      <div class="brand" @click="goHome">
        <span class="brand-logo">🍳</span>
        <span class="brand-text">基于知识图谱的烹饪小助手</span>
      </div>

      <nav class="nav-menu">
        <router-link to="/" class="nav-item" :class="{ active: route.path === '/' }">首页</router-link>
        <router-link to="/recipes" class="nav-item" :class="{ active: route.path === '/recipes' }">菜谱</router-link>
        <router-link to="/graph" class="nav-item" :class="{ active: route.path === '/graph' }">知识图谱</router-link>
        <router-link to="/qa" class="nav-item" :class="{ active: route.path === '/qa' }">智能问答</router-link>
        <router-link to="/personal" class="nav-item" :class="{ active: route.path === '/personal' }">个性化服务
          <span v-if="hasSubmissionNotice" class="nav-dot"></span>
        </router-link>
      </nav>

      <div class="nav-user">
        <template v-if="isAuthenticated">
          <router-link to="/publish" class="publish-btn">发布菜谱</router-link>

          <div class="user-dropdown" ref="dropdownRef">
            <div class="user-trigger" @click.stop="toggleUserMenu">
              <span class="user-avatar">{{ username?.slice(0, 1) || 'U' }}</span>
              <span class="username">{{ username }}</span>
            </div>

            <div v-if="showUserMenu" class="dropdown-menu" @click.stop>
              <div class="dropdown-item" @click="goProfile">
                <span class="menu-icon">👤</span>
                <span>个人中心</span>
              </div>

              <div class="dropdown-item" @click="goFavorites">
                <span class="menu-icon">⭐</span>
                <span>我的收藏</span>
              </div>

              <div class="dropdown-item" @click="goHistory">
                <span class="menu-icon">🕘</span>
                <span>浏览历史</span>
              </div>

              <div class="dropdown-divider"></div>

              <div class="dropdown-item danger" @click="handleLogout">
                <span class="menu-icon">⏻</span>
                <span>退出登录</span>
              </div>
            </div>
          </div>
        </template>

        <template v-else>
          <router-link to="/login" class="login-btn">登录</router-link>
          <router-link to="/register" class="register-btn">注册</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getUserInfoApi, logoutApi } from '../api'

const router = useRouter()
const route = useRoute()

const isAuthenticated = ref(false)
const username = ref('')
const showUserMenu = ref(false)
const dropdownRef = ref(null)
const hasSubmissionNotice = ref(false)

const loadSubmissionNotice = async () => {
  if (!isAuthenticated.value) {
    hasSubmissionNotice.value = false
    return
  }

  try {
    const res = await fetch('http://localhost:8000/api/recipes/my-submissions/', {
      credentials: 'include'
    })
    const data = await res.json()
    hasSubmissionNotice.value = !!data.has_unread_rejection
  } catch (error) {
    hasSubmissionNotice.value = false
  }
}

const loadUserInfo = async () => {
  try {
    const data = await getUserInfoApi()
    if (data.success && data.is_authenticated) {
      isAuthenticated.value = true
      username.value = data.username
    } else {
      isAuthenticated.value = false
      username.value = ''
    }
  } catch (error) {
    isAuthenticated.value = false
    username.value = ''
  }
}

const goHome = () => {
  router.push('/')
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const goProfile = () => {
  showUserMenu.value = false
  router.push('/profile')
}

const goFavorites = () => {
  showUserMenu.value = false
  router.push('/profile?tab=favorites')
}

const goHistory = () => {
  showUserMenu.value = false
  router.push('/profile?tab=history')
}

const handleLogout = async () => {
  try {
    const data = await logoutApi()
    if (data.success) {
      showUserMenu.value = false
      isAuthenticated.value = false
      username.value = ''
      router.push('/login')
    }
  } catch (error) {
    console.error('退出登录失败：', error)
    alert(error.message || '退出登录失败')
  }
}

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

onMounted(async () => {
  await loadUserInfo()
  await loadSubmissionNotice()
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.nav-item {
  position: relative;
}

.nav-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 999px;
}

.top-nav {
  position: sticky;
  top: 0;
  z-index: 20;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.9);
}

.nav-inner {
  max-width: 1220px;
  margin: 0 auto;
  height: 68px;
  padding: 0 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.brand-logo {
  font-size: 24px;
}

.brand-text {
  font-size: 18px;
  font-weight: 800;
  color: #2490ff;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-item {
  text-decoration: none;
  color: #374151;
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
  transition: 0.2s ease;
}

.nav-item:hover,
.nav-item.active {
  background: #eaf3ff;
  color: #2490ff;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.publish-btn,
.login-btn,
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

.publish-btn:hover,
.login-btn:hover {
  background: #dbeafe;
}

.register-btn {
  color: white;
  background: #2490ff;
}

.user-dropdown {
  position: relative;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 12px;
  transition: 0.2s ease;
}

.user-trigger:hover {
  background: rgba(243, 247, 251, 0.9);
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  background: #9ca3af;
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
}

.username {
  font-weight: 600;
  color: #1f2937;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 180px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.12);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  z-index: 50;
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

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  cursor: pointer;
  color: #374151;
  font-size: 15px;
  transition: 0.2s ease;
  background: white;
}

.dropdown-item:hover {
  background: #f8fafc;
}

.dropdown-item.danger {
  color: #dc2626;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
}

.menu-icon {
  width: 18px;
  text-align: center;
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
}
</style>