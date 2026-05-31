import client from './client'
import type { PreviewResult } from '@/types/platform'

export async function generatePreview(
  platformId: string,
  content: string,
  title?: string,
  metadata?: Record<string, unknown>,
): Promise<PreviewResult> {
  const { data } = await client.post(`/preview/${platformId}`, {
    content,
    title,
    metadata: metadata || {},
  })
  return data
}

export async function generateBatchPreview(
  content: string,
  platforms: string[],
  title?: string,
  metadata?: Record<string, unknown>,
): Promise<PreviewResult[]> {
  const { data } = await client.post('/preview/batch', {
    content,
    platforms,
    title,
    metadata: metadata || {},
  })
  return data.previews
}
