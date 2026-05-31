<template>
  <div class="articles-page">
    <div class="page-header">
      <h1>📁 文章列表</h1>
      <el-button type="primary" @click="goEditor()">新建文章</el-button>
    </div>

    <div v-if="loading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      加载中...
    </div>

    <div v-else-if="articles.length === 0" class="empty">
      <p>还没有文章，点击"新建文章"开始创作吧！</p>
      <el-button type="primary" @click="goEditor()">新建文章</el-button>
    </div>

    <div v-else class="article-list">
      <div v-for="article in articles" :key="article.id" class="article-card">
        <div class="card-main" @click="goEditor(article.id)">
          <h3 class="card-title">{{ article.title }}</h3>
          <div class="card-meta">
            <span>{{ article.word_count }} 字</span>
            <span>{{ formatDate(article.updated_at) }}</span>
          </div>
          <div class="card-tags">
            <el-tag v-for="tag in article.tags" :key="tag" size="small" type="info">
              {{ tag }}
            </el-tag>
          </div>
        </div>
        <div class="card-actions">
          <el-button size="small" type="primary" plain @click="goEditor(article.id)">
            编辑
          </el-button>
          <el-popconfirm
            title="确定要删除这篇文章吗？"
            @confirm="handleDelete(article.id)"
          >
            <template #reference>
              <el-button size="small" type="danger" plain>删除</el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { ArticleListItem } from '@/types/article'
import { listArticles, deleteArticle } from '@/api/articles'

const router = useRouter()
const articles = ref<ArticleListItem[]>([])
const loading = ref(true)

function goEditor(id?: string) {
  const query = id ? { id } : {}
  router.push({ path: '/', query })
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString('zh-CN')
  } catch {
    return iso
  }
}

async function handleDelete(id: string) {
  await deleteArticle(id)
  articles.value = articles.value.filter((a) => a.id !== id)
  ElMessage.success('文章已删除')
}

onMounted(async () => {
  try {
    articles.value = await listArticles()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.articles-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 22px;
  color: var(--color-text);
}

.loading, .empty {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-text-secondary);
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.article-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  transition: box-shadow 0.2s;
}

.article-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-main {
  cursor: pointer;
  flex: 1;
}

.card-title {
  font-size: 16px;
  margin-bottom: 6px;
  color: var(--color-text);
}

.card-meta {
  font-size: 13px;
  color: var(--color-text-secondary);
  display: flex;
  gap: 16px;
  margin-bottom: 6px;
}

.card-tags {
  display: flex;
  gap: 4px;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  margin-left: 16px;
}
</style>
