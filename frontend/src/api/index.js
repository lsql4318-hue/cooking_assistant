const API_BASE = 'http://localhost:8000/api'

export async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
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

export function loginApi(username, password) {
  return requestJson('/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  })
}

export function logoutApi() {
  return requestJson('/logout/', {
    method: 'POST',
  })
}

export function getUserInfoApi() {
  return requestJson('/user-info/')
}

export function getFavoritesApi() {
  return requestJson('/favorites/')
}

export function getHistoryApi() {
  return requestJson('/history/')
}