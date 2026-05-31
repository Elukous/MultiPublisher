import client from './client'
import type { PlatformInfo } from '@/types/platform'

export async function fetchPlatforms(): Promise<PlatformInfo[]> {
  const { data } = await client.get('/platforms')
  return data
}

export interface CustomPlatformDef {
  id: string
  name: string
  icon: string
  description: string
  format: 'html' | 'markdown' | 'plain_text' | 'json'
  style_preset: 'mobile' | 'desktop' | 'minimal'
  header_template?: string
  footer_template?: string
  preprocessor?: Record<string, unknown>
  content_limits?: Record<string, number>
}

export async function fetchCustomPlatforms(): Promise<CustomPlatformDef[]> {
  const { data } = await client.get('/platforms/custom')
  return data
}

export async function saveCustomPlatform(def: CustomPlatformDef): Promise<PlatformInfo[]> {
  const { data } = await client.post('/platforms/custom', def)
  return data
}

export async function deleteCustomPlatform(platformId: string): Promise<PlatformInfo[]> {
  const { data } = await client.delete(`/platforms/custom/${platformId}`)
  return data
}

export async function reloadPlatforms(): Promise<PlatformInfo[]> {
  const { data } = await client.post('/platforms/reload')
  return data
}
