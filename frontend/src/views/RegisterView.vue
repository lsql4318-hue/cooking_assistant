<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-icon">📝</div>
        <h1>创建账号</h1>
        <p>注册后即可使用知识图谱查询、智能问答与个性化服务</p>
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

      <div class="form-group">
        <label>确认密码</label>
        <input v-model="confirmPassword" type="password" placeholder="请再次输入密码" />
      </div>

      <button class="primary-btn" @click="handleRegister">立即注册</button>

      <div class="bottom-text">
        已有账号？
        <router-link to="/login">去登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const message = ref('')
const router = useRouter()

const handleRegister = async () => {
  message.value = ''

  if (!username.value.trim() || !password.value.trim() || !confirmPassword.value.trim()) {
    message.value = '所有字段都不能为空'
    return
  }

  if (password.value !== confirmPassword.value) {
    message.value = '两次输入的密码不一致'
    return
  }

  try {
    const response = await fetch('http://localhost:8000/api/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        username: username.value,
        password: password.value,
        confirm_password: confirmPassword.value,
      }),
    })

    const data = await response.json()

    if (data.success) {
      message.value = '注册成功，正在跳转到登录页...'
      setTimeout(() => {
        router.push('/login')
      }, 1000)
    } else {
      message.value = data.message || '注册失败'
    }
  } catch (error) {
    message.value = '请求失败，请检查 Django 服务是否启动'
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
  width: 460px;
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