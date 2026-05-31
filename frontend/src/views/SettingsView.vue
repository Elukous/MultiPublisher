<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>🔌 平台管理</h1>
      <div class="header-actions">
        <el-button @click="activeTab = 'builtin'" :type="activeTab === 'builtin' ? 'primary' : 'default'">
          内置平台
        </el-button>
        <el-button @click="activeTab = 'custom'" :type="activeTab === 'custom' ? 'primary' : 'default'">
          自定义平台
        </el-button>
        <el-button @click="activeTab = 'docs'" :type="activeTab === 'docs' ? 'primary' : 'default'">
          开发文档
        </el-button>
        <el-button @click="handleReload" :loading="reloading" style="margin-left: 12px;">
          刷新平台列表
        </el-button>
      </div>
    </div>

    <!-- Built-in / plugin platforms -->
    <div v-if="activeTab === 'builtin'" class="tab-content">
      <div class="platform-grid">
        <div v-for="p in allPlatforms" :key="p.id" class="platform-card" :class="{ card_custom: p.id.startsWith('custom_'), card_plugin: p.id.startsWith('plugin_') }">
          <div class="card-icon">{{ p.icon }}</div>
          <div class="card-body">
            <h3>{{ p.display_name }}</h3>
            <p class="card-desc">{{ p.description }}</p>
            <el-tag size="small" :type="getPlatformType(p.id)">
              {{ p.id.startsWith('custom_') ? '自定义' : p.id.startsWith('plugin_') ? '插件' : '内置' }}
            </el-tag>
            <span class="card-id" v-if="p.content_limits">ID: {{ p.id }}</span>
          </div>
          <div class="card-limits">
            <div v-for="(v, k) in visibleLimits(p.content_limits)" :key="k" class="limit-item">
              <span class="limit-key">{{ limitLabel(k) }}:</span>
              <span class="limit-val">{{ v }}</span>
            </div>
            <el-button v-if="p.id.startsWith('custom_')" size="small" type="danger" plain
                       @click="handleDeleteCustom(p.id.replace('custom_', ''))">
              删除
            </el-button>
          </div>
        </div>
      </div>
      <div v-if="allPlatforms.length === 0" class="empty">
        暂无平台数据，请确保后端已启动
      </div>
    </div>

    <!-- Custom platform creator -->
    <div v-if="activeTab === 'custom'" class="tab-content">
      <el-card class="form-card">
        <template #header>
          <span>{{ editingPlatform ? '编辑自定义平台' : '添加自定义平台' }}</span>
          <el-button v-if="editingPlatform" size="small" @click="resetForm" style="float:right;">
            新建
          </el-button>
        </template>

        <el-form :model="form" label-width="100px" size="default">
          <el-form-item label="平台 ID" required>
            <el-input v-model="form.id" placeholder="例如: douyin" :disabled="!!editingPlatform" />
            <div class="form-tip">唯一标识符，只能包含字母、数字、下划线</div>
          </el-form-item>

          <el-form-item label="平台名称" required>
            <el-input v-model="form.name" placeholder="例如: 抖音" />
          </el-form-item>

          <el-form-item label="图标">
            <el-input v-model="form.icon" placeholder="例如: 🎵" maxlength="4" style="width:100px" />
            <div class="form-tip">一个 emoji 字符</div>
          </el-form-item>

          <el-form-item label="描述">
            <el-input v-model="form.description" placeholder="简短描述该平台" />
          </el-form-item>

          <el-form-item label="输出格式" required>
            <el-select v-model="form.format">
              <el-option label="HTML (富文本)" value="html" />
              <el-option label="Markdown" value="markdown" />
              <el-option label="纯文本" value="plain_text" />
              <el-option label="JSON" value="json" />
            </el-select>
          </el-form-item>

          <el-form-item label="样式预设">
            <el-select v-model="form.style_preset">
              <el-option label="桌面端 (720px)" value="desktop" />
              <el-option label="移动端 (375px)" value="mobile" />
              <el-option label="极简" value="minimal" />
            </el-select>
          </el-form-item>

          <el-form-item label="标题长度限制">
            <el-input-number v-model="contentLimits.max_title_length" :min="0" :max="500" />
            <div class="form-tip">0 表示不限制</div>
          </el-form-item>

          <el-form-item label="正文长度限制">
            <el-input-number v-model="contentLimits.max_body_length" :min="0" :max="100000" :step="1000" />
            <div class="form-tip">0 表示不限制</div>
          </el-form-item>

          <el-form-item label="头部模板">
            <el-input v-model="form.header_template" placeholder="例如: {title} - 内容开始" />
            <div class="form-tip">可使用 {title} 占位符</div>
          </el-form-item>

          <el-form-item label="尾部模板">
            <el-input v-model="form.footer_template" placeholder="例如: --- 全文结束 ---" />
          </el-form-item>

          <el-form-item label="预处理器">
            <el-checkbox v-model="form.preprocessor.add_tags">自动追加标签</el-checkbox>
            <el-checkbox v-model="form.preprocessor.emoji_prefix" style="margin-left:12px;">添加 Emoji 前缀</el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSaveCustom" :loading="saving">
              {{ editingPlatform ? '更新平台' : '创建平台' }}
            </el-button>
            <el-button v-if="editingPlatform" @click="resetForm">取消编辑</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- Existing custom platforms list -->
      <el-card class="existing-card" style="margin-top: 16px;">
        <template #header>
          <span>已创建的自定义平台</span>
        </template>
        <div v-if="customPlatforms.length === 0" class="empty">
          还没有自定义平台，使用上方表单创建一个
        </div>
        <div v-else class="custom-list">
          <div v-for="p in customPlatforms" :key="p.id" class="custom-item">
            <span>{{ p.icon }} <strong>{{ p.name }}</strong> ({{ p.format }})</span>
            <div>
              <el-button size="small" @click="editPlatform(p)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="handleDeleteCustom(p.id)">删除</el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Dev docs -->
    <div v-if="activeTab === 'docs'" class="tab-content docs-content">
      <h2>📖 三种扩展方式</h2>

      <div class="doc-section">
        <h3>方式一：插件文件（推荐开发者）</h3>
        <p>在 <code>backend/plugins/</code> 目录下创建 <code>.py</code> 文件，参考 <code>example_plugin.py</code>。</p>
        <p>系统启动时自动发现并注册，无需修改任何现有代码。</p>
        <el-button type="primary" plain @click="openPluginExample">查看示例代码</el-button>
      </div>

      <div class="doc-section">
        <h3>方式二：Config 自定义（无需写代码）</h3>
        <p>使用上方的"自定义平台"表单，填写平台信息。支持 HTML/Markdown/纯文本/JSON 格式。</p>
        <p>配置保存在 <code>backend/data/custom_platforms.json</code>，可随时编辑。</p>
      </div>

      <div class="doc-section">
        <h3>方式三：完整适配器（高级）</h3>
        <p>在 <code>backend/app/platforms/</code> 中创建完整的 <code>PlatformAdapter</code> 子类，</p>
        <p>在 <code>backend/app/transformers/renderers/</code> 中创建专用渲染器。</p>
        <p>适合需要深度定制格式的平台。</p>
        <a :href="addPlatformsDocUrl" target="_blank">
          <el-button plain>查看完整文档</el-button>
        </a>
      </div>

      <h2 style="margin-top:32px;">🗂️ 项目文件结构</h2>
      <pre class="file-tree">
backend/
├── platforms/          # 内置平台适配器
│   ├── base.py         # PlatformAdapter 抽象基类
│   ├── registry.py     # 注册表 + 插件发现 + 自定义平台加载
│   ├── wechat.py       # 内置：微信公众号
│   ├── zhihu.py        # 内置：知乎
│   ├── xiaohongshu.py  # 内置：小红书
│   └── bilibili.py     # 内置：B站
├── plugins/            # 👈 插件目录：放入 .py 文件即可注册
│   └── example_plugin.py
├── transformers/
│   └── renderers/      # 平台渲染器
├── data/
│   └── custom_platforms.json  # 👈 用户自定义平台配置
└── tests/
      </pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fetchPlatforms, fetchCustomPlatforms, saveCustomPlatform, deleteCustomPlatform, reloadPlatforms } from '@/api/platforms'
import type { PlatformInfo, CustomPlatformDef } from '@/api/platforms'

const activeTab = ref('builtin')
const allPlatforms = ref<PlatformInfo[]>([])
const customPlatforms = ref<CustomPlatformDef[]>([])
const reloading = ref(false)
const saving = ref(false)
const editingPlatform = ref<CustomPlatformDef | null>(null)

const addPlatformsDocUrl = '/docs/adding-platforms.md'

const form = reactive({
  id: '',
  name: '',
  icon: '🔌',
  description: '',
  format: 'html' as const,
  style_preset: 'desktop' as const,
  header_template: '',
  footer_template: '',
  preprocessor: { add_tags: false, emoji_prefix: false } as Record<string, unknown>,
})

const contentLimits = reactive({
  max_title_length: 0,
  max_body_length: 0,
})

function getPlatformType(id: string): string {
  if (id.startsWith('custom_')) return 'warning'
  if (id.startsWith('plugin_')) return 'success'
  return 'primary'
}

function visibleLimits(limits: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {}
  for (const [k, v] of Object.entries(limits)) {
    if (typeof v === 'number' && v > 0) out[k] = v
  }
  return out
}

function limitLabel(key: string): string {
  const map: Record<string, string> = {
    max_title_length: '标题上限',
    max_body_length: '正文上限',
    min_images: '最少图片',
    max_images: '最多图片',
  }
  return map[key] || key
}

function resetForm() {
  editingPlatform.value = null
  form.id = ''
  form.name = ''
  form.icon = '🔌'
  form.description = ''
  form.format = 'html'
  form.style_preset = 'desktop'
  form.header_template = ''
  form.footer_template = ''
  form.preprocessor = { add_tags: false, emoji_prefix: false }
  contentLimits.max_title_length = 0
  contentLimits.max_body_length = 0
}

function editPlatform(p: CustomPlatformDef) {
  editingPlatform.value = p
  form.id = p.id
  form.name = p.name
  form.icon = p.icon
  form.description = p.description
  form.format = p.format
  form.style_preset = p.style_preset
  form.header_template = p.header_template || ''
  form.footer_template = p.footer_template || ''
  form.preprocessor = p.preprocessor || {}
  contentLimits.max_title_length = p.content_limits?.max_title_length || 0
  contentLimits.max_body_length = p.content_limits?.max_body_length || 0
  activeTab.value = 'custom'
}

async function loadData() {
  allPlatforms.value = await fetchPlatforms()
  customPlatforms.value = await fetchCustomPlatforms()
}

async function handleSaveCustom() {
  if (!form.id || !form.name) {
    ElMessage.warning('请填写平台 ID 和名称')
    return
  }
  saving.value = true
  try {
    await saveCustomPlatform({
      id: form.id,
      name: form.name,
      icon: form.icon || '🔌',
      description: form.description,
      format: form.format,
      style_preset: form.style_preset,
      header_template: form.header_template,
      footer_template: form.footer_template,
      preprocessor: form.preprocessor,
      content_limits: {
        max_title_length: contentLimits.max_title_length || 0,
        max_body_length: contentLimits.max_body_length || 0,
      },
    })
    ElMessage.success('自定义平台已保存')
    resetForm()
    await loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDeleteCustom(id: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个自定义平台吗？', '确认删除')
  } catch {
    return
  }
  try {
    await deleteCustomPlatform(id)
    ElMessage.success('已删除')
    // If editing this one, reset
    if (editingPlatform.value?.id === id) resetForm()
    await loadData()
  } catch {
    ElMessage.error('删除失败')
  }
}

async function handleReload() {
  reloading.value = true
  try {
    await reloadPlatforms()
    await loadData()
    ElMessage.success('平台列表已刷新')
  } catch {
    ElMessage.error('刷新失败')
  } finally {
    reloading.value = false
  }
}

function openPluginExample() {
  window.open('/example_plugin.py', '_blank')
}

onMounted(loadData)
</script>

<style scoped>
.settings-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 22px;
  margin-bottom: 16px;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.platform-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.platform-card {
  display: flex;
  gap: 16px;
  padding: 16px 20px;
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  align-items: center;
}

.card-icon {
  font-size: 36px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 12px;
}

.card-body {
  flex: 1;
}

.card-body h3 {
  font-size: 16px;
  margin-bottom: 4px;
}

.card-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.card-id {
  font-size: 12px;
  color: #bbb;
  margin-left: 8px;
}

.card-limits {
  text-align: right;
  font-size: 13px;
  flex-shrink: 0;
}

.limit-item {
  margin: 2px 0;
}

.limit-key {
  color: var(--color-text-secondary);
}

.limit-val {
  font-weight: 600;
  margin-left: 4px;
}

.card_custom {
  border-left: 3px solid #e6a23c;
}

.card_plugin {
  border-left: 3px solid #67c23a;
}

.form-card {
  max-width: 640px;
}

.form-tip {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.custom-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.custom-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: var(--color-text-secondary);
}

.docs-content {
  max-width: 720px;
}

.doc-section {
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px 20px;
  margin: 12px 0;
}

.doc-section h3 {
  margin-bottom: 8px;
}

.doc-section p {
  font-size: 14px;
  color: var(--color-text);
  margin: 4px 0;
}

.doc-section code {
  background: #f0f0f0;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 13px;
}

.file-tree {
  background: #2c3e50;
  color: #e0e0e0;
  padding: 16px 20px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.8;
  overflow-x: auto;
}
</style>
