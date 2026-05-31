import client from './client'
import type { PublishResult } from '@/types/platform'

export interface PublishResponse {
  results: PublishResult[]
  total_platforms: number
  successful: number
  failed: number
}

export async function simulatePublish(
  content: string,
  title: string,
  platforms: string[],
  metadata?: Record<string, unknown>,
): Promise<PublishResponse> {
  const { data } = await client.post('/publish', {
    content,
    title,
    platforms,
    metadata: metadata || {},
  })
  return data
}
