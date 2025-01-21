# PDF Notes Assistant

一个基于 Claude API 的 PDF 笔记处理和 AI 对话助手系统。采用模块化设计，支持逐页处理和实时对话。

## 系统架构

### 模块化设计
- `app/routes/`: HTTP 路由处理
  - `chat.py`: 处理聊天相关请求
  - `pdf.py`: 处理 PDF 文件相关请求
  - `token.py`: 处理 token 计数和状态
- `app/services/`: 核心业务逻辑
  - `ai_processor.py`: AI 请求处理服务
  - `pdf_processor.py`: PDF 文件处理服务
- `app/models/`: 数据模型
  - `session.py`: 会话状态管理
- `app/utils/`: 工具函数
  - `file_handler.py`: 文件处理工具

## 主要功能

### 1. AI对话功能
- 实时与AI助手对话
- 支持上下文理解
- 对话历史保存功能（支持导出为Markdown）
- Token使用量实时监控
- 自动保存对话记录

### 2. PDF处理功能
- 本地逐页处理PDF文档
- 实时预览PDF内容
- 自定义处理提示
- 自动/手动处理控制
- 实时保存处理结果
- 支持处理进度显示
- 详细的处理日志

### 3. 文件管理
- 自动文件命名和组织
- 按日期分类存储
- 支持同文件追加处理
- 清晰的保存路径提示

### 4. 界面特性
- VSCode风格深色主题
- 响应式设计
- 实时状态反馈
- 友好的错误提示
- 平滑的动画效果

## 安装和使用

1. 克隆仓库
```bash
git clone https://github.com/EricWang1358/CLD_Student_Specified.git
cd CLD_Student_Specified
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置API密钥
创建 .env 文件并添加您的API密钥：
```
API_KEY=your-api-key-here
```

4. 运行应用
```bash
python run.py
```

5. 访问应用
打开浏览器访问 http://localhost:5000

## 项目结构
```
CLD_Student_Specified/
├── app/                    # 应用主目录
│   ├── __init__.py        # 应用初始化
│   ├── routes/            # 路由处理
│   │   ├── chat.py        # 聊天路由
│   │   ├── pdf.py         # PDF处理路由
│   │   └── token.py       # Token管理路由
│   ├── services/          # 核心服务
│   │   ├── ai_processor.py    # AI处理服务
│   │   └── pdf_processor.py   # PDF处理服务
│   ├── models/            # 数据模型
│   │   └── session.py     # 会话管理
│   ├── utils/             # 工具函数
│   │   └── file_handler.py    # 文件处理
│   └── templates/         # 前端模板
│       └── index.html     # 主页面
├── uploads/               # PDF上传目录
├── outputs/               # 处理结果输出目录
├── config.py             # 配置文件
├── requirements.txt      # 项目依赖
└── README.md             # 项目文档
```

## 注意事项
- 确保有足够的API额度
- PDF文件大小限制为16MB
- 建议使用现代浏览器访问
- 处理大文件时请耐心等待

## 开发计划
- [ ] 增加更多文件格式支持
- [ ] 优化Token使用效率
- [ ] 添加批量处理功能
- [ ] 增加导出格式选项
- [ ] 添加处理模板选择

## 贡献
欢迎提交Issue和Pull Request！

## 许可
MIT License
