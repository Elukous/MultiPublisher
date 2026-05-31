<template>
  <header class="app-header">
    <div class="header-left">
      <span class="logo">📝 MultiPublisher</span>
      <el-input
        v-model="articleStore.title"
        placeholder="输入文章标题..."
        class="title-input"
        size="default"
        @input="articleStore.isDirty = true"
      />
      <el-tag size="small" type="info">{{ articleStore.wordCount }} 字</el-tag>
    </div>
    <div class="header-right">
      <el-button
        size="default"
        :disabled="!articleStore.isDirty"
        :loading="articleStore.isSaving"
        @click="articleStore.saveArticle()"
      >
        保存
      </el-button>
      <el-button size="default" @click="router.push('/articles')">
        文章列表
      </el-button>
      <el-button size="default" circle @click="router.push('/settings')" title="平台管理">
        🔌
      </el-button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useArticleStore } from '@/stores/article'
import { useRouter } from 'vue-router'

const articleStore = useArticleStore()
const router = useRouter()
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  background: #fff;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: var(--color-primary);
  white-space: nowrap;
}

.title-input {
  width: 320px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
