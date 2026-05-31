export interface PlatformInfo {
  id: string
  display_name: string
  icon: string
  description: string
  supports_preview: boolean
  content_limits: Record<string, unknown>
}

export interface PlatformWarning {
  level: 'warning' | 'error'
  message: string
  field?: string
}

export interface PreviewResult {
  platform_id: string
  html: string
  raw_content: string
  warnings: PlatformWarning[]
  metadata: Record<string, unknown>
}

export interface PublishResult {
  platform_id: string
  success: boolean
  message: string
  simulated_url?: string
  content_to_copy: string
  timestamp: string
  platform_tip?: string
}
