# AI竞争力诊断问卷App

一个基于FastAPI和Vanilla JavaScript的现代化问卷应用，帮助用户诊断自己的AI协作能力和"构建者"潜力。

## 功能特性

- 📝 10个精心设计的诊断问题，涵盖"用户 vs. 构建者"心智模型和AI协作五阶段框架
- 🤖 基于AI Builder API的个性化分析报告生成
- 🎨 现代化、简约大方的用户界面
- 📱 响应式设计，支持移动端访问
- 🚀 单进程单端口部署，符合AI Builder平台要求

## 技术栈

- **后端**: Python 3.12+, FastAPI
- **前端**: HTML5, CSS3, Vanilla JavaScript
- **LLM**: AI Builder API (grok-4-fast模型)
- **Markdown渲染**: marked.js

## 快速开始

### 1. 环境要求

- Python 3.12+
- uv (用于虚拟环境管理)

### 2. 安装依赖

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
uv pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件（已添加到.gitignore）：

```env
AI_BUILDER_TOKEN=your_token_here
PORT=8000
```

### 4. 运行应用

```bash
# 激活虚拟环境后
python app.py
```

或者使用uvicorn直接运行：

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

应用将在 `http://localhost:8000` 启动。

## 项目结构

```
demo_survey/
├── app.py                 # FastAPI后端主文件
├── requirements.txt       # Python依赖
├── .env                   # 环境变量（不提交到git）
├── .gitignore            # Git忽略文件
├── static/               # 静态文件目录
│   ├── index.html       # 前端HTML
│   ├── style.css        # 样式文件
│   └── app.js           # 前端JavaScript
└── outline.md           # 问卷设计文档
```

## API端点

- `GET /` - 返回前端页面
- `GET /api/questions` - 获取问卷问题列表
- `POST /api/analyze` - 提交答案并生成分析报告

## 部署

本项目符合AI Builder平台的部署要求：

- ✅ 单进程单端口（FastAPI + Uvicorn）
- ✅ 支持PORT环境变量
- ✅ 静态文件和API在同一服务器
- ✅ 使用AI_BUILDER_TOKEN环境变量

部署时，`AI_BUILDER_TOKEN` 会自动注入到环境中。

## 开发说明

### 问卷设计

问卷基于以下核心理论框架：

1. **身份认同模型 (Yuzheng)**: 用户 vs. 构建者
2. **协作成熟度模型 (Yan)**: 五阶段框架（黑箱 → 实习生 → 队友 → 项目经理 → 共创者）

详细设计思路见 `outline.md`。

### 前端交互流程

1. 用户访问首页，加载问卷问题
2. 逐题回答，支持前进/后退
3. 提交后调用后端API生成报告
4. 使用marked.js渲染Markdown报告
5. 显示课程CTA链接

## License

MIT

