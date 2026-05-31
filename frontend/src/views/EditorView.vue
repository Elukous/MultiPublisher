<template>
  <AppLayout>
    <MarkdownEditor v-model="articleStore.content" />
    <div class="preview-area">
      <PreviewGrid />
    </div>
    <PublishResultDialog />
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, watch, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import MarkdownEditor from '@/components/editor/MarkdownEditor.vue'
import PreviewGrid from '@/components/preview/PreviewGrid.vue'
import PublishResultDialog from '@/components/publish/PublishResultDialog.vue'
import { useArticleStore } from '@/stores/article'
import { usePlatformStore } from '@/stores/platforms'

const articleStore = useArticleStore()
const platformStore = usePlatformStore()
const route = useRoute()

// Debounce timer for preview refresh
let debounceTimer: ReturnType<typeof setTimeout> | null = null

function debouncedRefresh() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    platformStore.refreshPreviews(articleStore.content, articleStore.title)
  }, 600)
}

// Watch content changes and refresh previews
watch(
  () => articleStore.content,
  () => {
    if (articleStore.content.trim()) {
      debouncedRefresh()
    }
  },
)

// Watch platform selection changes
watch(
  () => platformStore.selectedPlatforms.length,
  () => {
    if (articleStore.content.trim()) {
      debouncedRefresh()
    }
  },
)

onMounted(async () => {
  await platformStore.loadPlatforms()

  // Load article if ID is provided in query
  const articleId = route.query.id as string
  if (articleId) {
    await articleStore.loadArticle(articleId)
  }

  // Initial preview if there's content
  if (articleStore.content.trim()) {
    debouncedRefresh()
  }
})
</script>

<style scoped>
.preview-area {
  width: 50%;
  min-width: 400px;
  height: 100%;
  overflow: hidden;
  border-left: 1px solid var(--color-border);
  background: var(--color-bg);
}
</style>
