# PGG老人数据系统说明文档

## 概述

PGG情感记忆生成系统已成功集成老人数据专用管理功能，能够根据扩展的老人相关关键词自动识别老人群体，并将相关数据存储到CSV或MongoDB中。

## 功能特性

### 1. 老人群体智能识别

**识别条件**（满足任一条件即可识别为老人群体）：
- **年龄判断**：年龄 ≥ 60岁
- **年龄组判断**：age_group 为 "senior"、"elderly"、"老年"、"老人"
- **关键词判断**：文本中包含 ≥ 2个老人相关关键词

**扩展关键词列表**（98个）：
```
# 基础关键词
孙子、孙女、退休、养老、老伴、儿媳、女婿、看病、体检

# 家庭关系
重孙、重孙女、外孙、外孙女、曾孙、曾孙女、孙媳妇、孙女婿
大儿子、小儿子、大女儿、小女儿、长子、次子、长女、次女

# 生活相关
老花镜、拐杖、血压、血糖、服药、吃药、医院、诊所、住院
保健品、营养品、钙片、维生素、降压药、降糖药、心脏病、高血压
糖尿病、关节炎、骨质疏松、老年痴呆、健忘、记忆力、老花眼

# 社交与活动
广场舞、太极、晨练、散步、下棋、打牌、唱戏、看戏、听戏
老年大学、老年活动、社区活动、邻居、老朋友、老同事、老战友

# 情感状态
孤独、寂寞、想念、怀念、回忆、过去、当年、年轻时、以前
操心、担心、放心不下、牵挂、惦记、想家、想儿子、想女儿

# 生活状态
独居、空巢、照顾、陪伴、探望、看望、回家、养老院、敬老院
老人院、护理院、社区服务、上门服务、送餐、代购、家政
```

### 2. 双重存储支持

**CSV存储模式**：
- 默认存储路径：`./storage/elderly_data.csv`
- 支持所有标准查询、过滤、分页功能
- 包含完整的老人特有数据字段

**MongoDB存储模式**：
- 集合名称：`elderly_emotions`
- 自动创建专用索引优化查询性能
- 支持聚合查询和复杂统计分析

**数据结构**：
```csv
id,user_id,text,primary_emotion,confidence,age,gender,age_group,
keywords_matched,keyword_count,elderly_specific_health,
elderly_specific_family,elderly_specific_loneliness,
elderly_specific_nostalgia,ai_suggestions,created_at,updated_at
```

### 3. API接口

#### 查询老人情感数据
```http
GET /elderly/emotions
参数：
- user_id: 用户ID（可选）
- page: 页码（默认1）
- per_page: 每页数量（默认20）
- emotion_filter: 情感过滤（可选）
- age_filter: 年龄过滤（可选）
```

#### 获取统计数据
```http
GET /elderly/statistics
参数：
- user_id: 用户ID（可选）
```

#### 导出数据
```http
POST /elderly/export
Body: {
  "format": "csv|json",
  "user_id": "用户ID（可选）"
}
```

#### 获取关键词配置
```http
GET /elderly/keywords
```

#### 测试老人群体检测
```http
POST /elderly/test
Body: {
  "text": "测试文本",
  "user_context": {
    "age": 70,
    "gender": "女",
    "age_group": "senior"
  }
}
```

## 配置说明

### 环境变量配置

```bash
# 老人数据存储配置
ELDERLY_DATA_STORAGE_TYPE=CSV          # CSV 或 MONGODB
ELDERLY_CSV_PATH=./storage/elderly_data.csv
ELDERLY_MONGODB_COLLECTION=elderly_emotions

# 老人数据分析配置
ELDERLY_MIN_AGE=60                     # 最小年龄阈值
ELDERLY_KEYWORD_THRESHOLD=2            # 关键词匹配阈值
ELDERLY_EXPORT_ENABLED=True            # 是否启用导出功能
```

### 切换存储模式

1. **使用CSV存储**（默认）：
   ```bash
   ELDERLY_DATA_STORAGE_TYPE=CSV
   ```

2. **使用MongoDB存储**：
   ```bash
   ELDERLY_DATA_STORAGE_TYPE=MONGODB
   MONGODB_URI=mongodb://localhost:27017/
   DATABASE_NAME=pgg_memory_db
   ```

## 使用示例

### 1. 老人情感分析示例

```python
from services.emotion_analysis import emotion_analyzer

# 老人用户上下文
user_context = {
    "user_id": "elderly_001",
    "age": 70,
    "gender": "女",
    "age_group": "senior"
}

# 分析文本
text = "今天孙子来看我了，真的很开心，但是他走了以后又觉得有点孤单"
result = emotion_analyzer.analyze_text(text, user_context)

# 系统会自动识别为老人群体并保存专用数据
print(f"是否为老人群体: {result.get('is_elderly')}")
print(f"匹配关键词: {result.get('keywords_matched')}")
print(f"老人特有指标: {result.get('elderly_specific')}")
```

### 2. 直接使用老人数据管理器

```python
from utils.elderly_storage import elderly_data_manager

# 检测老人群体
is_elderly = elderly_data_manager.is_elderly_context(user_context, text)

# 获取匹配的关键词
keywords = elderly_data_manager.get_matched_keywords(text)

# 查询老人情感数据
emotions = elderly_data_manager.get_elderly_emotions(
    user_id="elderly_001",
    page=1,
    per_page=20
)

# 获取统计数据
stats = elderly_data_manager.get_elderly_statistics()
```

## 测试

### 运行系统测试
```bash
python test_elderly_system.py
```

### 运行API测试
```bash
# 先启动服务器
python app.py

# 然后在另一个终端运行API测试
python test_elderly_api.py
```

## 数据分析功能

### 老人特有指标

系统为老人群体提供专门的情感分析指标：

- **health_concern**: 健康相关程度 (0-1)
- **family_relation**: 家庭关系相关程度 (0-1)
- **loneliness**: 孤独感程度 (0-1)
- **nostalgia**: 怀念程度 (0-1)

### 统计分析

- 总记录数和平均年龄
- 情感分布和年龄分布
- 关键词频率统计
- 最常见情感识别

### AI建议

系统为老人群体提供针对性的心理健康建议：

- **孤独情感**: "建议参加社区活动，增加社交机会"
- **担忧情感**: "适当的担心是正常的，但不要过度焦虑"
- **怀旧情感**: "美好的回忆是珍贵的财富"
- **健康相关**: "注意身体健康，定期体检很重要"

## 注意事项

1. **数据隐私**: 老人数据包含敏感信息，请确保数据安全
2. **存储性能**: MongoDB适合大量数据，CSV适合小规模测试
3. **关键词更新**: 可通过修改`config.py`中的`ELDERLY_KEYWORDS`列表添加新关键词
4. **备份重要**: 建议定期备份老人情感数据
5. **监控分析**: 建议定期分析老人情感趋势，提供及时关怀

## 技术架构

```
老人数据系统架构：

输入文本 + 用户上下文
        ↓
   老人群体识别
   (年龄/关键词/组别)
        ↓
     情感分析
   (DeepSeek优化)
        ↓
    老人特有处理
   (指标/建议/后处理)
        ↓
     数据存储
   (CSV/MongoDB)
        ↓
   查询统计API
```

## 更新日志

### v1.0.0 (2025-07-06)
- ✅ 扩展老人关键词列表到98个
- ✅ 实现CSV和MongoDB双重存储
- ✅ 集成老人群体智能识别
- ✅ 添加老人数据管理API
- ✅ 提供完整的测试套件
- ✅ 支持老人特有情感分析 