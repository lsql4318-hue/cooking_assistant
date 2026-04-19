<template>
  <div class="page-box">
    <div class="header-card card">
      <div>
        <div class="badge">💬 社区模块</div>
        <h1>社区讨论</h1>
        <p>这里将用于用户交流做菜经验、分享食谱心得与互动讨论。</p>
      </div>
    </div>

    <div class="card content-card">
      <div class="placeholder-box">
        <div class="placeholder-icon">🧑‍🍳</div>
        <h2>社区功能开发中</h2>
        <p>后续将支持发帖、评论、经验分享、互动交流等内容。</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-box {
  padding: 0;
  font-family: Arial, sans-serif;
}

.card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 26px rgba(15, 23, 42, 0.06);
}

.header-card {
  padding: 24px;
  margin-bottom: 20px;
}

.badge {
  display: inline-block;
  background: #eef9f3;
  color: #1f8f5f;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 10px;
}

.header-card h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
}

.header-card p {
  margin: 0;
  color: #64748b;
}

.content-card {
  padding: 30px;
}

.placeholder-box {
  min-height: 360px;
  border-radius: 16px;
  background: linear-gradient(180deg, #f8fbff 0%, #f2f5f9 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #64748b;
  text-align: center;
}

.placeholder-icon {
  font-size: 54px;
  margin-bottom: 16px;
}

.placeholder-box h2 {
  margin: 0 0 10px 0;
  color: #1f2937;
}

.placeholder-box p {
  margin: 0;
}
</style>