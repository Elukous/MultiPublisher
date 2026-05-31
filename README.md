# MultiPublisher 📝 多平台内容发布工具

一次编写，多平台发布。用 Markdown 编写内容，自动适配微信公众号、知乎、小红书、B站专栏等平台的格式和风格。

## ✨ 功能特性

- **Markdown 编辑器** — 实时编写，支持完整 Markdown 语法
- **四平台适配** — 自动转换内容格式：
  - 💬 **微信公众号** — 全内联样式 HTML，适配移动端阅读
  - 🔍 **知乎** — 清洁 Markdown，中英文间距优化
  - 📕 **小红书** — 短文本 + Emoji 建议 + 标签提取
  - 📺 **B站专栏** — 兼容 Bilibili 编辑器的 HTML
- **实时预览** — 编辑同时查看各平台渲染效果
- **模拟发布** — 一键生成各平台格式内容，复制粘贴即可使用
- **插件式架构** — 3 步添加新平台，无需改动现有代码

## 🏗️ 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.12 + FastAPI |
| 内容解析 | mistune 3.x (Markdown → AST) |
| 前端 | Vue 3 + TypeScript + Vite |
| 编辑器 | md-editor-v3 |
| UI 组件 | Element Plus |
| 状态管理 | Pinia |

## 🚀 快速开始

### 前置条件

- Python 3.10+
- Node.js 18+

### 启动后端

```bash
cd backend
pip install -r requirements.txt   # 或 pip install fastapi uvicorn "mistune>=3.0" pydantic-settings premailer python-multipart
uvicorn app.main:app --reload --port 8000
```

后端运行在 http://127.0.0.1:8000

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173，API 请求自动代理到后端。

### 同时启动（推荐）

```bash
# 终端 1 - 后端
cd backend && uvicorn app.main:app --reload

# 终端 2 - 前端
cd frontend && npm run dev
```

打开浏览器访问 http://localhost:5173 即可使用。

## 📁 项目结构

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── platforms/           # 平台适配器（插件式）
│   │   ├── transformers/        # Markdown → AST → 平台格式
│   │   ├── services/            # 业务逻辑层
│   │   ├── api/                 # REST API 路由
│   │   └── schemas/             # 数据模型
│   └── tests/                   # 47 个测试用例
├── frontend/
│   └── src/
│       ├── components/          # Vue 组件
│       │   ├── editor/          # Markdown 编辑器
│       │   ├── preview/         # 平台预览面板
│       │   ├── publish/         # 发布功能
│       │   └── layout/          # 布局组件
│       ├── stores/              # Pinia 状态管理
│       ├── api/                 # HTTP 客户端
│       └── views/               # 页面视图
└── docs/
    └── adding-platforms.md      # 扩展新平台指南
```

## 🔌 API 接口

| Method | Endpoint | 说明 |
|--------|----------|------|
| GET | `/api/v1/platforms` | 列出所有平台 |
| POST | `/api/v1/preview/{platform_id}` | 单平台预览 |
| POST | `/api/v1/preview/batch` | 批量预览 |
| POST | `/api/v1/publish` | 模拟发布 |
| GET/POST/PUT/DELETE | `/api/v1/articles` | 文章 CRUD |

## 🧪 运行测试

```bash
cd backend
pip install pytest httpx
python -m pytest tests/ -v
```

## 📖 扩展新平台

详见 [adding-platforms.md](docs/adding-platforms.md)，只需 3 步：

1. 创建渲染器 (`transformers/renderers/`)
2. 创建适配器 (`platforms/`)
3. 在 `registry.py` 中添加 import

新平台自动出现在前端，无需修改前端代码。

