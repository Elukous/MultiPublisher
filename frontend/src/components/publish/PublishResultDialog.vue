<template>
  <el-dialog
    v-model="platformStore.showPublishDialog"
    title="发布结果"
    width="680px"
    :close-on-click-modal="true"
  >
    <div class="publish-summary">
      <el-tag type="success" size="large">
        成功: {{ successCount }}
      </el-tag>
      <el-tag v-if="failCount > 0" type="danger" size="large">
        失败: {{ failCount }}
      </el-tag>
    </div>

    <div class="result-list">
      <div
        v-for="result in platformStore.publishResults"
        :key="result.platform_id"
        class="result-item"
      >
        <div class="result-header">
          <el-tag :type="result.success ? 'success' : 'danger'" size="small">
            {{ result.success ? '✅' : '❌' }}
          </el-tag>
          <span class="result-platform">{{ getPlatformName(result.platform_id) }}</span>
        </div>
        <p class="result-message">{{ result.message }}</p>
        <p v-if="result.platform_tip" class="result-tip">💡 {{ result.platform_tip }}</p>
        <el-button
          size="small"
          type="primary"
          plain
          @click="copyContent(result.content_to_copy)"
        >
          复制内容到剪贴板
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { usePlatformStore } from '@/stores/platforms'

const platformStore = usePlatformStore()

const successCount = computed(() =>
  platformStore.publishResults.filter((r) => r.success).length,
)
const failCount = computed(() =>
  platformStore.publishResults.filter((r) => !r.success).length,
)

function getPlatformName(id: string): string {
  const p = platformStore.platforms.find((p) => p.id === id)
  return p ? `${p.icon} ${p.display_name}` : id
}

async function copyContent(content: string) {
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}
</script>

<style scoped>
.publish-summary {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: #fafafa;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.result-platform {
  font-weight: 600;
}

.result-message {
  font-size: 14px;
  color: var(--color-text);
  margin-bottom: 4px;
}

.result-tip {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}
</style>
