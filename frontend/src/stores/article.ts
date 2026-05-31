import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Article } from '@/types/article'
import * as articlesApi from '@/api/articles'

export const useArticleStore = defineStore('article', () => {
  // State
  const currentArticle = ref<Article | null>(null)
  const title = ref('')
  const content = ref('')
  const tags = ref<string[]>([])
  const isDirty = ref(false)
  const isSaving = ref(false)
  const articles = ref<Article[]>([])

  // Getters
  const wordCount = computed(() => {
    const chinese = (content.value.match(/[一-鿿]/g) || []).length
    const english = (content.value.match(/[a-zA-Z]+/g) || []).length
    return chinese + english
  })

  // Actions
  function newArticle() {
    currentArticle.value = null
    title.value = ''
    content.value = ''
    tags.value = []
    isDirty.value = false
  }

  async function saveArticle() {
    isSaving.value = true
    try {
      if (currentArticle.value) {
        const updated = await articlesApi.updateArticle(currentArticle.value.id, {
          title: title.value,
          content: content.value,
          tags: tags.value,
        })
        currentArticle.value = updated
      } else {
        const created = await articlesApi.createArticle({
          title: title.value || '未命名文章',
          content: content.value,
          tags: tags.value,
        })
        currentArticle.value = created
      }
      isDirty.value = false
    } finally {
      isSaving.value = false
    }
  }

  async function loadArticle(id: string) {
    const article = await articlesApi.getArticle(id)
    currentArticle.value = article
    title.value = article.title
    content.value = article.content
    tags.value = article.tags
    isDirty.value = false
  }

  async function fetchArticles() {
    const list = await articlesApi.listArticles()
    articles.value = list as unknown as Article[]
  }

  async function removeArticle(id: string) {
    await articlesApi.deleteArticle(id)
    if (currentArticle.value?.id === id) {
      newArticle()
    }
    await fetchArticles()
  }

  function setContent(value: string) {
    content.value = value
    isDirty.value = true
  }

  function setTitle(value: string) {
    title.value = value
    isDirty.value = true
  }

  return {
    currentArticle,
    title,
    content,
    tags,
    isDirty,
    isSaving,
    articles,
    wordCount,
    newArticle,
    saveArticle,
    loadArticle,
    fetchArticles,
    removeArticle,
    setContent,
    setTitle,
  }
})
