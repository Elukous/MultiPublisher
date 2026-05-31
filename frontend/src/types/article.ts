export interface Article {
  id: string
  title: string
  content: string
  tags: string[]
  cover_image: string | null
  word_count: number
  created_at: string
  updated_at: string
}

export interface ArticleListItem {
  id: string
  title: string
  tags: string[]
  word_count: number
  created_at: string
  updated_at: string
}

export interface ArticleCreate {
  title: string
  content: string
  tags?: string[]
  cover_image?: string | null
}

export interface ArticleUpdate {
  title?: string
  content?: string
  tags?: string[]
  cover_image?: string | null
}
