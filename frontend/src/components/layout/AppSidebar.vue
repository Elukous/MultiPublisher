<template>
  <aside class="app-sidebar">
    <div class="sidebar-section">
      <h3 class="section-title">选择发布平台</h3>
      <div class="platform-list">
        <div
          v-for="platform in platformStore.platforms"
          :key="platform.id"
          class="platform-item"
          :class="{ active: platformStore.isSelected(platform.id) }"
          @click="platformStore.togglePlatform(platform.id)"
        >
          <span class="platform-icon">{{ platform.icon }}</span>
          <span class="platform-name">{{ platform.display_name }}</span>
          <el-icon v-if="platformStore.isSelected(platform.id)" class="check-icon">
            <Check />
          </el-icon>
        </div>
      </div>
    </div>

    <div class="sidebar-bottom">
      <el-button
        type="primary"
        class="publish-btn"
        :loading="platformStore.isPublishing"
        :disabled="platformStore.selectedPlatforms.length === 0"
        @click="handlePublish"
      >
        🚀 一键发布 ({{ platformStore.selectedPlatforms.length }})
      </el-button>
      <el-button size="small" class="new-btn" @click="articleStore.newArticle()">
        新建文章
      </el-button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { Check } from '@element-plus/icons-vue'
import { useArticleStore } from '@/stores/article'
import { usePlatformStore } from '@/stores/platforms'

const articleStore = useArticleStore()
const platformStore = usePlatformStore()

function handlePublish() {
  platformStore.publish(articleStore.content, articleStore.title || '未命名文章')
}
</script>

<style scoped>
.app-sidebar {
  width: var(--sidebar-width);
  background: var(--color-sidebar);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 16px 12px;
  overflow-y: auto;
}

.section-title {
  font-size: 13px;
  color: #aaa;
  margin-bottom: 12px;
  padding-left: 4px;
}

.platform-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.platform-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
}

.platform-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.platform-item.active {
  background: var(--color-primary);
}

.platform-icon {
  font-size: 18px;
}

.platform-name {
  flex: 1;
}

.check-icon {
  font-size: 14px;
}

.sidebar-bottom {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.publish-btn {
  width: 100%;
  font-size: 15px;
  padding: 12px 0;
}

.new-btn {
  width: 100%;
}
</style>
