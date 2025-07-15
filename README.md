# PGG情感记忆生成系统

## 🎨 项目简介

PGG情感记忆生成系统是一个基于Flask的后端服务，通过情感分析和AI图像生成技术，将用户的文本输入转化为带有情感色彩的视觉化回忆。系统支持多种情感分析模型和图像生成服务，适用于边缘设备部署。

## ✨ 核心功能

- **情感分析**: 支持文本和音频的情感识别
- **图像生成**: 基于情感和文本生成个性化图像
- **回忆管理**: 存储和检索用户的历史回忆数据
- **多存储支持**: 支持MongoDB和本地存储
- **API接口**: 提供RESTful API便于集成

## 🏗️ 系统架构

```
PGG情感记忆生成系统/
├── app.py                      # Flask主应用
├── config.py                   # 配置管理
├── models.py                   # 数据模型
├── start_server.py             # 启动脚本
├── requirements.txt            # 依赖包
├── environment_config.template # 环境变量模板
├── utils/                      # 工具模块
│   ├── __init__.py
│   └── database.py            # 数据库管理
├── services/                   # 服务模块
│   ├── __init__.py
│   ├── emotion_analysis.py    # 情感分析服务
│   └── image_generation.py    # 图像生成服务
├── storage/                   # 本地存储目录
│   ├── images/               # 生成的图像
│   ├── memories.json         # 回忆数据
│   └── user_stats.json       # 用户统计
├── logs/                     # 日志文件
└── models/                   # AI模型文件
    ├── whisper/
    ├── wav2vec2/
    ├── ecapa/
    └── stable_diffusion/
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
cp environment_config.template .env
# 编辑.env文件，填入相应的API密钥和配置
```

### 2. 启动服务

```bash
# 使用启动脚本（推荐）
python start_server.py

# 或直接运行Flask应用
python app.py
```

### 3. 验证服务

```bash
# 健康检查
curl http://localhost:5000/health

# 生成回忆示例
curl -X POST http://localhost:5000/generate \
     -H 'Content-Type: application/json' \
     -d '{"text":"今天是美好的一天", "user_id":"user123"}'
```

## 📋 API接口文档

### 健康检查
```
GET /health
```
**响应示例:**
```json
{
  "success": true,
  "message": "PGG情感记忆生成系统运行正常",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

### 生成回忆
```
POST /generate
```
**请求参数:**
```json
{
  "text": "用户输入文本",
  "user_id": "用户ID（可选）",
  "audio_file": "音频文件路径（可选）"
}
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "id": "回忆记录ID",
    "memory_text": "生成的回忆文本",
    "image_url": "生成的图像URL",
    "emotion": {
      "primary_emotion": "happy",
      "confidence": 0.85,
      "emotion_scores": {"happy": 0.85, "sad": 0.15}
    },
    "user_input": "用户输入文本",
    "created_at": "2024-01-01T12:00:00"
  },
  "message": "回忆生成成功"
}
```

### 获取历史回忆
```
GET /history?user_id=用户ID&page=1&per_page=20&emotion=情感过滤
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "memories": [
      {
        "id": "回忆ID",
        "user_input": "用户输入",
        "memory_text": "回忆文本",
        "image_url": "图像URL",
        "emotion": {"primary_emotion": "happy"},
        "created_at": "2024-01-01T12:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "pages": 5
    }
  },
  "message": "成功获取20条回忆记录"
}
```

### 获取回忆详情
```
GET /memory/<memory_id>
```

### 获取用户统计
```
GET /stats?user_id=用户ID
```

## ⚙️ 配置说明

### 环境变量配置

系统支持通过环境变量进行配置，主要配置项包括：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Flask密钥 | `pgg-memory-system-2024` |
| `DEBUG` | 调试模式 | `True` |
| `HOST` | 服务主机 | `0.0.0.0` |
| `PORT` | 服务端口 | `5000` |
| `MONGODB_URI` | MongoDB连接字符串 | `mongodb://localhost:27017/` |
| `USE_LOCAL_STORAGE` | 是否使用本地存储 | `True` |
| `OPENAI_API_KEY` | OpenAI API密钥 | - |
| `SD_API_URL` | Stable Diffusion API地址 | `http://localhost:7860` |

### 存储配置

系统支持两种存储方式：

1. **MongoDB存储**: 适合生产环境，支持分布式部署
2. **本地存储**: 适合开发和边缘设备，无需额外服务

### AI模型配置

系统预留了多种AI模型的集成接口：

- **情感分析**: Wav2Vec2, ECAPA-TDNN, BERT等
- **图像生成**: Stable Diffusion, MidJourney, DALL-E等
- **语音识别**: Whisper, 科大讯飞API等

## 🔧 开发指南

### 添加新的情感分析模型

1. 在`services/emotion_analysis.py`中实现新的分析方法
2. 在`_init_text_analyzer()`或`_init_audio_analyzer()`中加载模型
3. 更新`analyze_text()`或`analyze_audio()`方法

### 添加新的图像生成服务

1. 在`services/image_generation.py`中实现新的生成方法
2. 在`_init_api_services()`中添加服务初始化
3. 更新`generate_image()`方法中的服务选择逻辑

### 自定义数据模型

1. 在`models.py`中定义新的数据模型
2. 实现`to_dict()`和`from_dict()`方法
3. 在`utils/database.py`中添加相应的数据库操作

## 🧪 测试

### 单元测试

```bash
# 运行基础功能测试
python -m pytest tests/

# 运行API接口测试
python -m pytest tests/test_api.py
```

### 手动测试

```bash
# 测试情感分析
python -c "
from services.emotion_analysis import EmotionAnalyzer
analyzer = EmotionAnalyzer()
result = analyzer.analyze_text('今天心情很好')
print(result)
"

# 测试图像生成
python -c "
from services.image_generation import ImageGenerator
generator = ImageGenerator()
url = generator.generate_image('美好的一天', {'primary_emotion': 'happy'})
print(url)
"
```

## 📊 性能优化

### 边缘设备优化

- 启用CPU模式: `USE_CPU_ONLY=True`
- 减少批次大小: `BATCH_SIZE=1`
- 限制内存使用: `MAX_MEMORY_USAGE=512MB`

### 生产环境优化

- 使用MongoDB存储: `USE_LOCAL_STORAGE=False`
- 配置负载均衡和反向代理
- 启用缓存机制

## 🛠️ 故障排除

### 常见问题

1. **依赖包安装失败**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **MongoDB连接失败**
   - 检查MongoDB服务是否运行
   - 验证连接字符串配置
   - 系统会自动切换到本地存储模式

3. **API接口调用失败**
   - 检查API密钥配置
   - 验证网络连接
   - 查看日志文件获取详细错误信息

### 日志查看

```bash
# 查看系统日志
tail -f logs/pgg_system.log

# 查看Flask日志
# 日志会同时输出到控制台和文件
```

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 📞 联系我们

- 项目主页: [GitHub Repository]
- 技术支持: [Support Email]
- 文档Wiki: [Documentation Wiki]

---

**注意**: 本系统在开发阶段使用模拟数据进行测试，生产环境请配置真实的API密钥和模型文件。 