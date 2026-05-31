# 添加新平台指南

MultiPublisher 提供 **三种层次** 的平台扩展机制，用户可根据自身能力选择最适合的方式。

---

## 方式一：插件文件（推荐开发者，无需改现有代码）

> 难度：★☆☆ — 需要会写基础 Python
> 结果：文件放到 `backend/plugins/` 目录，重启即生效

### 使用脚手架工具（最快方法）

```bash
cd backend
python scaffold_plugin.py douyin "抖音" 🎵
```

这会生成 `backend/plugins/douyin.py` 文件，包含完整的 `PlatformAdapter` 模板。你可以编辑其中的 `transform()` 方法来自定义格式转换逻辑。

重启后端后，新平台自动出现：

```bash
uvicorn app.main:app --reload
```

### 手动创建

1. 在 `backend/plugins/` 下创建 `.py` 文件，参考 `example_plugin.py`
2. 创建一个继承 `PlatformAdapter` 的类，实现所有抽象方法
3. 文件底部调用 `registry.register(YourPlatform())`
4. 重启后端

**示例：** `plugins/example_plugin.py` 中有完整注释的模板代码。

---

## 方式二：Config 自定义（无需写代码）

> 难度：★☆☆ — 通过 UI 表单填写
> 结果：配置保存在 `backend/data/custom_platforms.json`

### 通过 UI 创建（推荐非开发者）

1. 打开前端页面，点击右上角 🔌 按钮进入**设置页**
2. 切换到 **自定义平台** 标签
3. 填写表单：
   - **平台 ID**：唯一标识（例如 `douyin`）
   - **平台名称**：显示名称（例如 `抖音`）
   - **图标**：一个 emoji 字符
   - **输出格式**：HTML / Markdown / 纯文本 / JSON
   - **样式预设**：移动端 / 桌面端 / 极简
   - **其他选项**：标题/正文长度限制、头部/尾部模板等
4. 点击 **创建平台**，配置保存并立即生效

### 配置文件结构

如果你更喜欢直接编辑 JSON 文件：

```json
[
  {
    "id": "douyin",
    "name": "抖音",
    "icon": "🎵",
    "description": "抖音图文内容",
    "format": "html",
    "style_preset": "mobile",
    "header_template": "{title}",
    "footer_template": "--- 全文结束 ---",
    "preprocessor": {
      "add_tags": true,
      "emoji_prefix": false,
      "max_heading_depth": 3
    },
    "content_limits": {
      "max_title_length": 30,
      "max_body_length": 2000
    }
  }
]
```

配置保存在 `backend/data/custom_platforms.json`，保存后自动生效（无需重启）。

### 支持的输出格式

| 格式 | 说明 | 预览效果 |
|------|------|---------|
| `html` | 富文本 HTML，带样式 | 渲染为网页 |
| `markdown` | 清洁 Markdown | 渲染为 HTML |
| `plain_text` | 纯文本 | 以 `<pre>` 显示 |
| `json` | JSON 格式输出 | 以 `<pre>` 显示 |

### 预处理器选项

| 选项 | 说明 |
|------|------|
| `add_tags` | 自动在文末追加标签 |
| `emoji_prefix` | 在开头添加 Emoji |
| `max_heading_depth` | 限制标题最大层级（如 3 = 最多用 ###） |

### 模板变量

在 `header_template` 和 `footer_template` 中可使用 `{title}` 占位符，例如：

```
header_template: "📢 {title}"
footer_template: "---\n原创内容，欢迎转发"
```

---

## 方式三：完整适配器（高级）

> 难度：★★★ — 需要深入理解 Pipeline
> 结果：完全自定义格式转换

适合需要深度定制格式的平台，在 `backend/app/platforms/` 中创建完整适配器：

### 步骤

1. **创建渲染器** — `backend/app/transformers/renderers/{name}_renderer.py`

```python
from app.transformers.base_renderer import BaseRenderer

class MyRenderer(BaseRenderer):
    def render(self, ast, metadata=None):
        # 实现自定义格式转换
        ...
```

2. **创建适配器** — `backend/app/platforms/{name}.py`

```python
from app.platforms.base import PlatformAdapter

class MyPlatform(PlatformAdapter):
    @property
    def platform_id(self): return 'my_platform'
    @property
    def display_name(self): return '我的平台'
    @property
    def icon(self): return '🌟'

    # 实现 transform(), generate_preview_html(), validate(), simulate_publish()
    ...

from app.platforms.registry import registry
registry.register(MyPlatform())
```

3. **注册** — 在 `registry.py` 的 `auto_register_platforms()` 中添加import

---

## 架构原理

```
用户 Markdown
      │
      ▼
  mistune AST 解析器 (parser.py)
      │
      ▼
  ContentAST (intermediate.py)   ← 所有渲染器基于此
      │
      ├──▶ 内置渲染器 + 适配器 (platforms/, transformers/renderers/)
      │       ├── wechat.py    → 全内联样式 HTML
      │       ├── zhihu.py     → 清洁 Markdown
      │       ├── xiaohongshu.py → 短文本 + Emoji
      │       └── bilibili.py  → Bilibili HTML
      │
      ├──▶ 插件渲染器 (plugins/)     ← 自动发现，无需注册
      │       └── example_plugin.py
      │
      └──▶ 自定义平台 (custom_platforms.json)  ← 无需代码
                └── CustomPlatformAdapter  + ContentRenderer
```

### 平台注册流程

```
                ┌──────────────────┐
                │  auto_register_  │
                │  platforms()     │  ← 应用启动时调用
                └───────┬──────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
  内置平台 import   插件发现扫描    自定义JSON加载
  (platforms/)     (plugins/)    (custom_platforms.json)
          │             │             │
          └─────────────┼─────────────┘
                        ▼
              PlatformRegistry
              (registry.py)
                        │
                        ▼
               API / Frontend
```

---

## 常见问题

**Q: 自定义平台能否覆盖内置平台的 ID？**
A: 不能。自定义平台 ID 会自动添加 `custom_` 前缀，插件平台添加 `plugin_` 前缀，避免与内置平台冲突。

**Q: 如何调试插件？**
A: 后端日志会输出插件加载信息。运行 `uvicorn app.main:app --reload` 并在日志中搜索 "Loaded plugin"。

**Q: 自定义平台支持图片吗？**
A: 取决于你选择的格式。HTML 格式会保留 Markdown 中的 `<img>` 标签，纯文本格式则不会。

**Q: 插件目录为什么不在 Python 包里？**
A: `plugins/` 目录在 Python 包结构之外，不需要 `__init__.py`，用户可以自由增删文件而不影响包结构。
