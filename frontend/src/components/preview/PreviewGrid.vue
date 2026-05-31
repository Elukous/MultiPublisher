<template>
  <div class="preview-grid">
    <PreviewPanel
      v-for="platform in selectedPlatforms"
      :key="platform.id"
      :platform="platform"
      :html-content="previews[platform.id]?.html || ''"
      :warnings="previews[platform.id]?.warnings || []"
      :loading="isLoadingPreview"
    />
    <div v-if="selectedPlatforms.length === 0" class="empty-hint">
      <p>请在左侧选择至少一个平台</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import PreviewPanel from './PreviewPanel.vue'
import { usePlatformStore } from '@/stores/platforms'

const platformStore = usePlatformStore()

const selectedPlatforms = computed(() =>
  platformStore.platforms.filter((p) => platformStore.isSelected(p.id)),
)

const previews = computed(() => platformStore.previews)
const isLoadingPreview = computed(() => platformStore.isLoadingPreview)
</script>

<style scoped>
.preview-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 12px;
  height: 100%;
  overflow-y: auto;
  align-content: start;
}

.empty-hint {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  font-size: 14px;
  min-height: 200px;
}
</style>
