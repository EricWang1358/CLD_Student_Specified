# PDF AI Assistant

基于 Flask 和 Claude API 构建的 PDF 智能处理助手，支持 PDF 文本提取、智能分析和交互式对话。

## 核心功能

### 1. PDF 处理

- PDF 文件上传和文本提取
- 分页处理和进度跟踪
- 支持预览和跳过页面
- 批量处理功能
- 处理结果保存为 Markdown 格式

### 2. AI 对话

- 基于 Claude API 的智能对话
- 支持自定义提示词
- 聊天历史记录
- 对话导出功能

### 3. 提示词管理

- 内置多种处理提示模板
- 支持自定义和切换提示词
- 针对不同场景的专业提示

## 技术架构

### 后端 (Flask)

- `app/routes/`: API 路由处理
  - `pdf.py`: PDF 相关接口
  - `chat.py`: 对话相关接口
- `app/services/`: 核心服务
  - `pdf_processor.py`: PDF 处理服务
  - `ai_processor.py`: AI 处理服务
- `app/utils/`: 工具类
  - `file_handler.py`: 文件处理
  - `prompt_manager.py`: 提示词管理

### 前端

- 单页面应用
- 响应式设计
- 实时处理状态显示
- Markdown 渲染

## 环境要求

- Python 3.8+
- Flask 3.0.0
- PyMuPDF 1.23.8
- 其他依赖见 requirements.txt

## 快速开始

1. 克隆项目

```bash
git clone [repository_url]
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置环境

- 复制 `.env.example` 为 `.env`
- 配置你的 API key

4. 运行项目

```bash
python run.py
```

## 使用说明

### PDF 处理

1. 上传 PDF 文件
2. 选择处理提示
3. 开始处理
4. 查看和导出结果

### AI 对话

1. 选择对话模式
2. 输入问题
3. 获取 AI 回复
4. 保存对话记录

## 项目特点

1. 模块化设计
2. 完整的错误处理
3. 详细的日志记录
4. 灵活的提示词系统
5. 友好的用户界面

## 注意事项

- API key 安全存储
- 大文件处理注意内存使用
- 保持日志文件大小合理

## 贡献指南

欢迎提交 Issue 和 Pull Request

## 许可证

MIT License
