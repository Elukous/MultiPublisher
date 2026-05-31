import client from './client'
import type { Article, ArticleListItem, ArticleCreate, ArticleUpdate } from '@/types/article'

export async function listArticles(): Promise<ArticleListItem[]> {
  const { data } = await client.get('/articles')
  return data
}

export async function getArticle(id: string): Promise<Article> {
  const { data } = await client.get(`/articles/${id}`)
  return data
}

export async function createArticle(input: ArticleCreate): Promise<Article> {
  const { data } = await client.post('/articles', input)
  return data
}

export async function updateArticle(id: string, input: ArticleUpdate): Promise<Article> {
  const { data } = await client.put(`/articles/${id}`, input)
  return data
}

export async function deleteArticle(id: string): Promise<void> {
  await client.delete(`/articles/${id}`)
}
