import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PlatformInfo, PreviewResult, PublishResult } from '@/types/platform'
import { fetchPlatforms } from '@/api/platforms'
import { generateBatchPreview } from '@/api/preview'
import { simulatePublish } from '@/api/publish'

export const usePlatformStore = defineStore('platforms', () => {
  // State
  const platforms = ref<PlatformInfo[]>([])
  const selectedPlatforms = ref<string[]>([])
  const previews = ref<Record<string, PreviewResult>>({})
  const publishResults = ref<PublishResult[]>([])
  const isLoadingPreview = ref(false)
  const isPublishing = ref(false)
  const showPublishDialog = ref(false)

  // Actions
  async function loadPlatforms() {
    platforms.value = await fetchPlatforms()
    // Default: select all platforms
    if (selectedPlatforms.value.length === 0) {
      selectedPlatforms.value = platforms.value.map((p) => p.id)
    }
  }

  function togglePlatform(id: string) {
    const idx = selectedPlatforms.value.indexOf(id)
    if (idx >= 0) {
      selectedPlatforms.value.splice(idx, 1)
    } else {
      selectedPlatforms.value.push(id)
    }
  }

  function isSelected(id: string): boolean {
    return selectedPlatforms.value.includes(id)
  }

  async function refreshPreviews(content: string, title?: string) {
    if (selectedPlatforms.value.length === 0 || !content.trim()) return

    isLoadingPreview.value = true
    try {
      const results = await generateBatchPreview(
        content,
        selectedPlatforms.value,
        title,
      )
      const map: Record<string, PreviewResult> = {}
      for (const r of results) {
        map[r.platform_id] = r
      }
      previews.value = map
    } catch (e) {
      console.error('Preview generation failed:', e)
    } finally {
      isLoadingPreview.value = false
    }
  }

  async function publish(content: string, title: string) {
    if (selectedPlatforms.value.length === 0) return

    isPublishing.value = true
    try {
      const response = await simulatePublish(content, title, selectedPlatforms.value)
      publishResults.value = response.results
      showPublishDialog.value = true
    } catch (e) {
      console.error('Publish failed:', e)
    } finally {
      isPublishing.value = false
    }
  }

  return {
    platforms,
    selectedPlatforms,
    previews,
    publishResults,
    isLoadingPreview,
    isPublishing,
    showPublishDialog,
    loadPlatforms,
    togglePlatform,
    isSelected,
    refreshPreviews,
    publish,
  }
})
