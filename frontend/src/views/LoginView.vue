<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-icon">🔐</div>
        <h1>欢迎登录</h1>
        <p>登录后继续使用烹饪知识图谱小助手</p>
      </div>

      <div v-if="message" class="message-box">{{ message }}</div>

      <div class="form-group">
        <label>用户名</label>
        <input v-model="username" type="text" placeholder="请输入用户名" />
      </div>

      <div class="form-group">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="请输入密码" />
      </div>

      <button class="primary-btn" @click="handleLogin">立即登录</button>

      <div class="bottom-text">
        还没有账号？
        <router-link to="/register">去注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginApi } from '../api'

const router = useRouter()

const username = ref('')
const password = ref('')
const message = ref('')
const loading = ref(false)

const handleLogin = async () => {
  message.value = ''

  if (!username.value.trim() || !password.value.trim()) {
    message.value = '用户名和密码不能为空'
    return
  }

  loading.value = true
  try {
    const data = await loginApi(username.value, password.value)

    if (data.success) {
      router.push('/')
    } else {
      message.value = data.message || '登录失败'
    }
  } catch (error) {
    console.error('登录失败：', error)
    message.value = error.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 56px);
  display: flex;
  justify-content: center;
  align-items: center;
}

.auth-card {
  width: 430px;
  background: white;
  border-radius: 18px;
  box-shadow: 0 14px 35px rgba(15, 23, 42, 0.08);
  padding: 34px;
}

.auth-header {
  text-align: center;
  margin-bottom: 24px;
}

.auth-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 14px;
  border-radius: 18px;
  background: #eef9f3;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.auth-header h1 {
  margin: 0 0 8px 0;
  font-size: 30px;
}

.auth-header p {
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

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 700;
  color: #334155;
}

input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid #dbe4ee;
  font-size: 15px;
  outline: none;
}

input:focus {
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.12);
}

.primary-btn {
  width: 100%;
  margin-top: 8px;
  border: none;
  border-radius: 12px;
  background: #42b983;
  color: white;
  padding: 13px 16px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.bottom-text {
  margin-top: 18px;
  text-align: center;
  color: #64748b;
}

.bottom-text a {
  color: #1f8f5f;
  text-decoration: none;
  font-weight: 700;
}
</style>