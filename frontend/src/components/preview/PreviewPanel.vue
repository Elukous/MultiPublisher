<template>
  <div class="preview-panel">
    <div class="preview-header">
      <span class="platform-badge">{{ platform.icon }} {{ platform.display_name }}</span>
      <el-tag
        v-for="warn in warnings"
        :key="warn.message"
        :type="warn.level === 'error' ? 'danger' : 'warning'"
        size="small"
      >
        {{ warn.message }}
      </el-tag>
    </div>
    <div class="preview-body">
      <div v-if="loading" class="preview-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>生成预览中...</span>
      </div>
      <iframe
        v-else
        :srcdoc="htmlContent"
        class="preview-iframe"
        sandbox="allow-same-origin"
        referrerpolicy="no-referrer"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'
import type { PlatformInfo, PlatformWarning } from '@/types/platform'

defineProps<{
  platform: PlatformInfo
  htmlContent: string
  warnings: PlatformWarning[]
  loading: boolean
}>()
</script>

<style scoped>
.preview-panel {
  background: #fff;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.preview-header {
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  background: #fafafa;
}

.platform-badge {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}

.preview-body {
  flex: 1;
  position: relative;
  min-height: 200px;
}

.preview-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--color-text-secondary);
}

.preview-iframe {
  width: 100%;
  height: 100%;
  min-height: 400px;
  border: none;
  background: #fff;
}
</style>
