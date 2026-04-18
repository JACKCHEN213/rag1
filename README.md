# RAG 系统

一个功能强大的检索增强生成（RAG）系统，支持多格式文档处理、精美Web界面、智能检索和记忆管理等高级功能。

## 功能特性

✨ **精美的Web界面**
- 现代化设计，支持深色/浅色主题
- 对话框架式管理
- 实时状态显示

📄 **多格式文档支持**
- PDF (文本和扫描版)
- Word (.docx/.doc)
- Excel (.xlsx/.xls)
- PowerPoint
- Markdown
- 图片OCR

🔍 **智能检索**
- 混合检索（密集+稀疏）
- BGE-Reranker重排
- 基于语义的分块

🧠 **记忆管理**
- 短期记忆（Redis）
- 长期记忆（MySQL 8.0）
- 重要性评分机制

⚙️ **灵活配置**
- 支持多种LLM连接
- 可自定义提示词
- 可配置检索参数

## 技术栈

### 前端
- React 18 + TypeScript
- Ant Design
- Zustand状态管理
- Axios

### 后端
- FastAPI
- Python 3.10+
- SQLModel
- Celery

### 数据库
- Milvus 2.x (向量)
- MySQL 8.0 (关系)
- Redis (缓存)

### AI模型
- BGE-M3 (嵌入)
- BGE-Reranker
- 支持OpenAI API兼容

## 快速开始

### 前提条件

- Docker & Docker Compose
- Node.js 16+
- Python 3.10+

### 部署步骤

1. 复制环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填写相关配置
```

2. 启动服务：
```bash
docker-compose up -d mysql milvus redis
```

3. 安装后端依赖：
```bash
cd backend
poetry install
poetry shell
```

4. 运行后端：
```bash
python -m app.main
```

5. 安装前端依赖：
```bash
cd frontend
pnpm install
```

6. 运行前端：
```bash
pnpm dev
```

7. 访问 `http://localhost:3000`

## 文档

详细文档请查看 [docs/](docs/) 目录。

## 贡献

我们欢迎社区贡献！请先阅读我们的 [CONTRIBUTING.md](CONTRIBUTING.md) 指南。

## 许可证

本项目基于 MIT 许可证开源。
