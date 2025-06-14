# 通用智能学习系统

## 系统简介

通用智能学习系统是一个基于Flask和Ollama AI的现代化Web学习平台，支持多种学科的智能化学习。系统采用响应式设计，支持跨平台访问，集成了知识学习、考试生成和试卷审批三大功能，通过本地AI模型提供智能辅导。

## 功能特点

### 🎓 智能学习
- 按章节浏览各学科概念和知识点
- AI生成详细讲解，包含定义、示例和代码
- 学习进度跟踪和个性化推荐
- 知识点搜索功能

### 📝 智能考试
- 根据选定章节自动生成考试试卷
- 支持多种题型：选择题、简答题、设计题等
- AI生成题目，质量可控
- 试卷下载和历史记录

### ✅ 智能审批
- 上传试卷文件进行AI批改
- 智能分析答题情况
- 生成详细学习建议
- 识别薄弱知识点

## 技术架构

- **后端**: Flask + SQLAlchemy + SQLite
- **前端**: Bootstrap 5 + jQuery + 响应式设计
- **AI服务**: Ollama本地API
- **数据存储**: JSON知识库 + SQLite用户数据 + 多课程支持

## 系统要求

- Python 3.8+
- 本地运行的Ollama服务（支持chat API）
- 推荐使用qwen3:14b、gemma2:27b等模型（或其他兼容模型）
- 现代浏览器（Chrome、Firefox、Safari、Edge）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动系统

```bash
python run.py
```

或者直接运行：

```bash
python app.py
```

### 3. 访问系统

在浏览器中访问：http://127.0.0.1:5000

## 详细使用指南

### 🎓 学习功能

1. **选择章节**: 在左侧章节列表中点击要学习的章节
2. **浏览内容**: 中间区域显示该章节的概念和知识点
3. **获取讲解**: 点击任意概念或知识点，AI将生成详细讲解
4. **搜索功能**: 使用搜索按钮快速查找特定知识点

### 📝 考试功能

1. **选择章节**: 勾选要考查的章节（支持多选）
2. **选择题型**: 选择需要的题型（选择题、简答题等）
3. **AI生成**: 开启AI生成获得高质量题目
4. **生成试卷**: 点击"生成试卷"按钮
5. **下载试卷**: 生成完成后可下载TXT格式试卷

### ✅ 审批功能

1. **上传试卷**: 选择并上传试卷文件（支持TXT、PDF、DOC等）
2. **预览内容**: 系统自动解析并预览试卷内容
3. **开始审批**: 点击"开始审批"，AI将分析答题情况
4. **查看结果**: 获得详细的批改结果和学习建议

## 配置说明

### Ollama配置

在 `config.py` 中可以修改以下配置：

```python
# Ollama API配置
OLLAMA_API_URL = 'http://127.0.0.1:11434/api/chat'
OLLAMA_MODEL = 'gemma2:27b'  # 可改为其他模型
```

### 数据文件

- `kownlgebase.json`: 数据库课程知识库
- `testmodel.json`: 考试题型配置
- `data/database.db`: SQLite数据库（自动创建）

## 项目结构

```
database_learn_system/
├── app.py                 # Flask应用主入口
├── run.py                 # 启动脚本
├── config.py             # 配置文件
├── routes.py             # 路由定义
├── requirements.txt      # Python依赖
├── models/               # 数据模型
├── services/             # 业务逻辑
├── templates/            # HTML模板
├── static/               # 静态资源
├── utils/                # 工具类
└── data/                 # 数据目录
```

## 开发说明

### 本地开发

```bash
# 克隆项目
git clone <repository-url>
cd database_learn_system

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python run.py
```

### 生产部署

```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 故障排除

### 常见问题

1. **AI服务连接失败 ("获取讲解失败: 抱歉，AI服务暂时不可用")**

   **原因**: Ollama服务未运行或模型配置错误

   **解决步骤**:
   ```bash
   # 1. 检查Ollama是否运行
   ollama serve

   # 2. 检查已安装的模型
   ollama list

   # 3. 如果没有gemma3:27b模型，下载它
   ollama pull gemma3:27b

   # 4. 或者修改config.py使用其他已安装的模型
   # 例如改为: OLLAMA_MODEL = 'qwen3:14b'
   ```

   **验证修复**:
   ```bash
   # 测试API连接
   curl -X POST http://127.0.0.1:11434/api/chat \
        -H "Content-Type: application/json" \
        -d '{"model":"gemma3:27b","messages":[{"role":"user","content":"Hello"}],"stream":false}'
   ```

2. **数据库错误**
   - 检查data目录权限
   - 删除database.db重新初始化

3. **文件上传失败**
   - 检查文件大小（限制16MB）
   - 确认文件格式支持

4. **模型响应慢**
   - 首次使用时模型需要加载，请耐心等待
   - 可以考虑使用更小的模型如gemma3:12b

### 日志查看

应用运行时会在控制台显示详细日志，包括：
- API请求状态
- 数据库操作
- AI服务调用
- 错误信息

## 版本信息

当前版本已完成以下优化：
- ✅ 移除所有测试代码和调试文件
- ✅ 完善的.gitignore配置
- ✅ 修复Mermaid图表渲染问题
- ✅ 优化AI内容生成和显示
- ✅ 完整的错误处理机制

## 注意事项

- 🔒 **隐私安全**: 所有数据本地存储，不会上传到外部服务器
- ⚡ **性能优化**: AI生成内容会缓存，避免重复请求
- 🌐 **浏览器兼容**: 建议使用现代浏览器以获得最佳体验
- 📱 **移动端**: 支持响应式设计，可在手机和平板上使用
- 🧹 **代码整洁**: 项目已清理所有测试代码，适合生产使用

## 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发起 Pull Request
- 邮件联系项目维护者