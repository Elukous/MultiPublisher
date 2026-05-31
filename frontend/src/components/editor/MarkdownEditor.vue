<template>
  <div class="markdown-editor-wrap">
    <MdEditor
      :model-value="modelValue"
      @update:model-value="$emit('update:modelValue', $event)"
      :preview="false"
      :style="{ height: '100%' }"
      language="zh-CN"
      placeholder="在这里输入 Markdown 内容..."
      @onSave="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

defineProps<{
  modelValue: string
}>()

defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

function handleSave() {
  // Trigger save via keyboard shortcut
  const event = new KeyboardEvent('keydown', { key: 's', ctrlKey: true })
  document.dispatchEvent(event)
}
</script>

<style scoped>
.markdown-editor-wrap {
  flex: 1;
  height: 100%;
  overflow: hidden;
}

.markdown-editor-wrap :deep(.md-editor) {
  border: none;
  border-radius: 0;
}
</style>
