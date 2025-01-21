# PDF Notes Assistant

一个基于Claude API的PDF笔记处理和AI对话助手系统。

## 主要功能

### 1. AI对话功能

- 实时与AI助手对话
- 支持上下文理解
- 对话历史保存功能
- Token使用量单次粗测监控
- 支持将对话导出为Markdown格式

### 2. PDF处理功能

- 逐页处理PDF文档
- 实时预览PDF转文字后内容
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

- 深色主题
- 响应式设计
- 实时状态反馈
- 友好的错误提示
- 平滑的动画效果

## 安装和使用

**1. 克隆仓库**

bash

```
git clone https://github.com/EricWang1358/CLD\_Student\_Specified.git

cd CLD\_Student\_Specified
```

**2. 安装依赖**

bash

```
pip install -r requirements.txt
```

**3. 配置API密钥**

**创建 .env 文件并添加您的API密钥：**

API\_KEY=your-api-key-here

**4. 运行应用**

bash

```
python main.py
```

**5. 访问应用**

**打开浏览器访问 http://localhost:5000**

**## 项目结构**

CLD\_Student\_Specified/

├── main.py # 主应用程序

├── templates/ # 前端模板

│ └── index.html # 主页面

├── uploads/ # PDF上传目录

├── outputs/ # 输出文件目录

├── requirements.txt # 项目依赖

└── README.md # 项目文档

**## 注意事项**

**- 确保有足够的API额度**

**- PDF文件大小限制为16MB**

**- 建议使用现代浏览器访问**

**- 处理大文件时请耐心等待**

**## 开发计划**

**- [ ] 增加更多文件格式支持**

**- [ ] 优化Token使用效率**

**- [ ] 添加批量处理功能**

**- [ ] 增加导出格式选项**

**## 贡献**

**欢迎提交Issue和Pull Request！**

**## 许可**

**MIT License**

现在，您可以按以下步骤
