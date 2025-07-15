# PGG系统CSV文档接口完整使用说明

## 🎯 **功能概述**

PGG情感记忆生成系统现已完整集成CSV文档处理功能，提供了**13个专业化CSV处理接口**，支持CSV文件的导入、导出、分析、转换、合并、拆分、验证等全方位操作。

## 📊 **支持的CSV数据格式**

### 1. 回忆记录格式 (memories)
```csv
id,user_id,user_input,memory_text,image_url,primary_emotion,confidence,emotion_scores,created_at
memory_001,user_123,今天天气很好,今天天气很好让我想起了春天,image1.jpg,happy,0.85,"{""happy"": 0.85}",2024-01-01T12:00:00
```

### 2. 情感数据格式 (emotions)
```csv
id,user_id,text,primary_emotion,confidence,emotion_scores,valence,arousal,dominance,created_at
emotion_001,user_123,今天心情很好,happy,0.90,"{""happy"": 0.90}",0.8,0.6,0.7,2024-01-01T12:00:00
```

### 3. 老人数据格式 (elderly_data)
```csv
id,user_id,text,primary_emotion,confidence,age,gender,age_group,keywords_matched,keyword_count,elderly_specific_health,elderly_specific_family,elderly_specific_loneliness,elderly_specific_nostalgia,ai_suggestions,created_at,updated_at
elderly_001,user_123,想念孙子,nostalgia,0.85,70,女,senior,"孙子,想念",2,0,1,1,1,"多与家人联系",2024-01-01T12:00:00,2024-01-01T12:00:00
```

### 4. 传感器数据格式 (sensor_data)
```csv
sensor_id,sensor_type,device_id,user_id,value,unit,timestamp,quality,metadata
sensor_001,heart_rate,device_123,user_456,72,bpm,2024-01-01T12:00:00,good,"{""battery_level"": 85}"
```

### 5. 用户统计格式 (user_statistics)
```csv
user_id,total_memories,emotion_distribution,most_common_emotion,first_memory_date,last_memory_date,emotional_trend,updated_at
user_123,50,"{""happy"": 30, ""sad"": 20}",happy,2024-01-01T12:00:00,2024-01-10T12:00:00,"{""trend"": ""positive""}",2024-01-01T12:00:00
```

### 6. 关键词分析格式 (keywords)
```csv
keyword,frequency,category,emotional_correlation,usage_context,first_appearance,last_appearance,trend
孙子,15,家庭关系,"{""happy"": 12, ""nostalgia"": 3}",家庭情感,2024-01-01T12:00:00,2024-01-10T12:00:00,0.2
血压,8,健康关键词,"{""worry"": 6, ""neutral"": 2}",健康状况,2024-01-02T12:00:00,2024-01-09T12:00:00,-0.1
广场舞,5,社交活动,"{""happy"": 4, ""social"": 1}",社交娱乐,2024-01-03T12:00:00,2024-01-08T12:00:00,0.1
```

## 🚀 **完整API接口清单**

### 1. 数据导出接口
- **`POST /csv/export`** - 导出数据为CSV格式
- **`GET /csv/download/<filename>`** - 下载CSV文件

### 2. 数据导入接口
- **`POST /csv/import`** - 导入CSV文件数据

### 3. 文件分析接口
- **`POST /csv/analyze`** - 分析CSV文件结构
- **`POST /csv/statistics`** - 获取CSV文件统计信息
- **`POST /csv/validate`** - 验证CSV文件数据

### 4. 文件处理接口
- **`POST /csv/convert`** - 转换CSV格式
- **`POST /csv/merge`** - 合并多个CSV文件
- **`POST /csv/split`** - 拆分CSV文件

### 5. 模板管理接口
- **`POST /csv/template`** - 创建CSV模板
- **`GET /csv/formats`** - 获取支持的CSV格式

### 6. 关键词分析接口
- **`POST /csv/keywords/analyze`** - 分析CSV数据中的关键词
- **`POST /csv/keywords/export`** - 导出关键词分析结果为CSV
- **`GET /csv/keywords/config`** - 获取关键词配置

## 📋 **详细接口说明**

### 1. CSV数据导出 - POST /csv/export

**功能**: 将数据导出为CSV格式文件

**请求格式**:
```bash
POST http://localhost:5000/csv/export
Content-Type: application/json

{
  "data": [
    {
      "id": "memory_001",
      "user_id": "user_123",
      "user_input": "今天天气很好",
      "memory_text": "今天天气很好，让我想起了春天",
      "primary_emotion": "happy",
      "confidence": 0.85
    }
  ],
  "type": "memories",
  "filename": "memories_export.csv",
  "options": {
    "include_headers": true,
    "encoding": "utf-8",
    "delimiter": ",",
    "custom_fields": ["id", "user_id", "user_input", "primary_emotion"]
  }
}
```

**请求参数**:
- `data`: 要导出的数据数组（必填）
- `type`: 数据类型，支持: memories, emotions, elderly_data, sensor_data, user_statistics, general
- `filename`: 自定义文件名（可选）
- `options`: 导出选项
  - `include_headers`: 是否包含表头（默认true）
  - `encoding`: 文件编码（默认utf-8）
  - `delimiter`: 字段分隔符（默认逗号）
  - `custom_fields`: 自定义字段列表

**响应示例**:
```json
{
  "success": true,
  "message": "CSV导出成功",
  "data": {
    "file_path": "/path/to/memories_export_20240101_120000.csv",
    "filename": "memories_export_20240101_120000.csv",
    "file_size": 1024,
    "record_count": 1,
    "fields": ["id", "user_id", "user_input", "primary_emotion"],
    "export_type": "memories",
    "encoding": "utf-8",
    "delimiter": ",",
    "created_at": "2024-01-01T12:00:00"
  }
}
```

### 2. CSV数据导入 - POST /csv/import

**功能**: 从CSV文件导入数据

**请求格式**:
```bash
POST http://localhost:5000/csv/import
Content-Type: multipart/form-data

# 表单数据
file: [CSV文件]
type: memories
encoding: utf-8
delimiter: ,
skip_header: true
validate_data: true
```

**请求参数**:
- `file`: 要导入的CSV文件（必填）
- `type`: 数据类型（默认general）
- `encoding`: 文件编码（默认utf-8）
- `delimiter`: 字段分隔符（默认逗号）
- `skip_header`: 是否跳过表头（默认true）
- `validate_data`: 是否验证数据（默认true）

**响应示例**:
```json
{
  "success": true,
  "message": "CSV导入成功",
  "data": {
    "data": [
      {
        "id": "memory_001",
        "user_id": "user_123",
        "user_input": "今天天气很好",
        "primary_emotion": "happy"
      }
    ],
    "total_rows": 1,
    "success_count": 1,
    "error_count": 0,
    "errors": [],
    "file_size": 1024,
    "import_type": "memories",
    "encoding": "utf-8",
    "delimiter": ",",
    "processed_at": "2024-01-01T12:00:00"
  }
}
```

### 3. CSV文件结构分析 - POST /csv/analyze

**功能**: 分析CSV文件的结构和字段类型

**请求格式**:
```bash
POST http://localhost:5000/csv/analyze
Content-Type: multipart/form-data

# 表单数据
file: [CSV文件]
encoding: utf-8
delimiter: ,
sample_size: 100
```

**响应示例**:
```json
{
  "success": true,
  "message": "CSV文件分析成功",
  "data": {
    "file_size": 1024,
    "total_rows": 100,
    "headers": ["id", "user_id", "text", "emotion"],
    "field_count": 4,
    "field_analysis": {
      "id": {
        "type": "string",
        "null_count": 0,
        "unique_values": 100,
        "sample_values": ["memory_001", "memory_002"]
      },
      "confidence": {
        "type": "float",
        "null_count": 5,
        "unique_values": 50,
        "sample_values": [0.85, 0.92, 0.78]
      }
    },
    "sample_data": [
      {"id": "memory_001", "user_id": "user_123", "text": "今天很开心", "emotion": "happy"}
    ],
    "analyzed_at": "2024-01-01T12:00:00"
  }
}
```

### 4. CSV模板创建 - POST /csv/template

**功能**: 创建CSV模板文件

**请求格式**:
```bash
POST http://localhost:5000/csv/template
Content-Type: application/json

{
  "type": "memories",
  "include_examples": true,
  "custom_fields": ["id", "user_id", "text", "emotion"]
}
```

**请求参数**:
- `type`: 模板类型（必填）
- `include_examples`: 是否包含示例数据（默认true）
- `custom_fields`: 自定义字段列表（可选）

**响应示例**:
```json
{
  "success": true,
  "message": "CSV模板创建成功",
  "data": {
    "file_path": "/path/to/memories_template_20240101_120000.csv",
    "filename": "memories_template_20240101_120000.csv",
    "template_type": "memories",
    "fields": ["id", "user_id", "user_input", "memory_text", "primary_emotion"],
    "field_count": 5,
    "include_examples": true,
    "example_count": 1,
    "created_at": "2024-01-01T12:00:00"
  }
}
```

### 5. CSV格式转换 - POST /csv/convert

**功能**: 转换CSV数据格式

**请求格式**:
```bash
POST http://localhost:5000/csv/convert
Content-Type: multipart/form-data

# 表单数据
file: [CSV文件]
from_type: general
to_type: memories
mapping_rules: {"target_field": "source_field"}
```

**请求参数**:
- `file`: 要转换的CSV文件（必填）
- `from_type`: 源数据类型（必填）
- `to_type`: 目标数据类型（必填）
- `mapping_rules`: 字段映射规则（可选，JSON格式）

**响应示例**:
```json
{
  "success": true,
  "message": "CSV格式转换成功",
  "data": {
    "input_file": "/path/to/input.csv",
    "output_file": "/path/to/converted_input.csv",
    "from_type": "general",
    "to_type": "memories",
    "converted_records": 100,
    "export_info": {
      "filename": "converted_input.csv",
      "file_size": 2048,
      "record_count": 100
    }
  }
}
```

### 6. CSV文件合并 - POST /csv/merge

**功能**: 合并多个CSV文件

**请求格式**:
```bash
POST http://localhost:5000/csv/merge
Content-Type: multipart/form-data

# 表单数据
files: [CSV文件1, CSV文件2, ...]
merge_type: union
remove_duplicates: true
key_fields: ["id", "user_id"]
```

**请求参数**:
- `files`: 要合并的CSV文件列表（必填，至少2个）
- `merge_type`: 合并类型（union, intersection, left_join, inner_join）
- `remove_duplicates`: 是否移除重复行（默认true）
- `key_fields`: 合并关键字段（JSON数组格式）

**响应示例**:
```json
{
  "success": true,
  "message": "CSV文件合并成功",
  "data": {
    "input_files": ["/path/to/file1.csv", "/path/to/file2.csv"],
    "output_file": "/path/to/merged_20240101_120000.csv",
    "merge_type": "union",
    "total_input_records": 200,
    "merged_records": 180,
    "file_info": [
      {"file_path": "/path/to/file1.csv", "record_count": 100, "errors": 0},
      {"file_path": "/path/to/file2.csv", "record_count": 100, "errors": 0}
    ]
  }
}
```

### 7. CSV文件拆分 - POST /csv/split

**功能**: 拆分CSV文件

**请求格式**:
```bash
POST http://localhost:5000/csv/split
Content-Type: multipart/form-data

# 表单数据
file: [CSV文件]
split_by: rows
split_size: 1000
split_field: user_id
```

**请求参数**:
- `file`: 要拆分的CSV文件（必填）
- `split_by`: 拆分方式（rows, field, size）
- `split_size`: 拆分大小（默认1000）
- `split_field`: 拆分字段（当split_by为field时）

**响应示例**:
```json
{
  "success": true,
  "message": "CSV文件拆分成功",
  "data": {
    "input_file": "/path/to/input.csv",
    "output_dir": "/path/to/split_20240101_120000/",
    "split_by": "rows",
    "split_size": 1000,
    "total_records": 5000,
    "split_files": [
      {
        "file_path": "/path/to/split_20240101_120000/chunk_1.csv",
        "filename": "chunk_1.csv",
        "record_count": 1000
      },
      {
        "file_path": "/path/to/split_20240101_120000/chunk_2.csv",
        "filename": "chunk_2.csv",
        "record_count": 1000
      }
    ],
    "file_count": 5
  }
}
```

### 8. CSV文件验证 - POST /csv/validate

**功能**: 验证CSV文件数据

**请求格式**:
```bash
POST http://localhost:5000/csv/validate
Content-Type: multipart/form-data

# 表单数据
file: [CSV文件]
validation_type: memories
custom_rules: {"field": "rule"}
```

**请求参数**:
- `file`: 要验证的CSV文件（必填）
- `validation_type`: 验证类型（默认general）
- `custom_rules`: 自定义验证规则（可选，JSON格式）

**响应示例**:
```json
{
  "success": true,
  "message": "CSV文件验证完成",
  "data": {
    "file_path": "/path/to/input.csv",
    "validation_type": "memories",
    "total_rows": 1000,
    "valid_rows": 950,
    "invalid_rows": 50,
    "validation_rate": 0.95,
    "errors": [
      {
        "row": 25,
        "error": "缺少必填字段: user_id",
        "data": {"id": "memory_025", "text": "今天很开心"}
      }
    ],
    "validated_at": "2024-01-01T12:00:00"
  }
}
```

### 9. CSV文件统计 - POST /csv/statistics

**功能**: 获取CSV文件统计信息

**请求格式**:
```bash
POST http://localhost:5000/csv/statistics
Content-Type: multipart/form-data

# 表单数据
file: [CSV文件]
```

**响应示例**:
```json
{
  "success": true,
  "message": "CSV文件统计分析完成",
  "data": {
    "file_path": "/path/to/input.csv",
    "file_size": 10240,
    "row_count": 1000,
    "column_count": 5,
    "columns": ["id", "user_id", "text", "emotion", "confidence"],
    "data_types": {
      "id": "object",
      "user_id": "object",
      "text": "object",
      "emotion": "object",
      "confidence": "float64"
    },
    "memory_usage": 50000,
    "null_counts": {
      "id": 0,
      "user_id": 0,
      "text": 5,
      "emotion": 10,
      "confidence": 20
    },
    "describe": {
      "confidence": {
        "count": 980,
        "mean": 0.85,
        "std": 0.12,
        "min": 0.45,
        "max": 0.98
      }
    },
    "analyzed_at": "2024-01-01T12:00:00"
  }
}
```

### 10. 获取支持格式 - GET /csv/formats

**功能**: 获取系统支持的CSV格式

**请求格式**:
```bash
GET http://localhost:5000/csv/formats
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "supported_formats": ["memories", "emotions", "elderly_data", "sensor_data", "user_statistics"],
    "format_details": {
      "memories": {
        "fields": ["id", "user_id", "user_input", "memory_text", "image_url", "primary_emotion", "confidence", "emotion_scores", "created_at"],
        "required": ["user_id", "user_input", "memory_text"],
        "types": {
          "confidence": "float",
          "created_at": "datetime",
          "emotion_scores": "dict"
        }
      }
    }
  },
  "message": "成功获取支持的CSV格式"
}
```

### 11. 文件下载 - GET /csv/download/<filename>

**功能**: 下载CSV文件

**请求格式**:
```bash
GET http://localhost:5000/csv/download/memories_export_20240101_120000.csv
```

**响应**: 直接返回CSV文件内容

### 12. 关键词分析 - POST /csv/keywords/analyze

**功能**: 分析CSV数据中的关键词

**请求格式**:
```json
{
  "data": [
    {
      "text": "今天孙子来看我了，很开心",
      "user_id": "user_123",
      "primary_emotion": "happy"
    }
  ],
  "format": "general"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "keyword_analysis": {
      "total_keywords": 98,
      "most_common_keywords": {"孙子": 5, "开心": 3},
      "matched_records": 1,
      "unmatched_records": 0,
      "average_keywords_per_record": 2.0
    },
    "text_analysis": {
      "total_records": 1,
      "records_with_keywords": 1,
      "keyword_density": 100.0
    },
    "elderly_specific_insights": {
      "family_keywords": {"孙子": 5},
      "health_keywords": {},
      "loneliness_keywords": {},
      "social_keywords": {}
    }
  },
  "message": "关键词分析完成，共分析1条记录，发现2个不同关键词"
}
```

### 13. 关键词导出 - POST /csv/keywords/export

**功能**: 导出关键词分析结果为CSV文件

**请求格式**:
```json
{
  "data": [
    {
      "text": "今天孙子来看我了，很开心",
      "user_id": "user_123",
      "primary_emotion": "happy"
    }
  ],
  "format": "general",
  "filename": "keywords_analysis_20240101.csv"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "file_path": "./storage/keywords_analysis_20240101.csv",
    "filename": "keywords_analysis_20240101.csv",
    "processed_records": 1,
    "keywords_found": 2,
    "download_url": "/csv/download/keywords_analysis_20240101.csv"
  },
  "message": "关键词分析结果导出成功"
}
```

### 14. 关键词配置 - GET /csv/keywords/config

**功能**: 获取关键词配置信息

**请求格式**:
```bash
GET http://localhost:5000/csv/keywords/config
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "keywords": ["孙子", "孙女", "退休", "养老", "老伴", "..."],
    "total_keywords": 98,
    "keyword_threshold": 2,
    "min_age": 60,
    "categories": {
      "基础关键词": ["孙子", "孙女", "退休", "养老", "老伴", "儿媳", "女婿", "看病", "体检"],
      "家庭关系": ["重孙", "重孙女", "外孙", "..."],
      "生活相关": ["老花镜", "拐杖", "血压", "..."],
      "社交与活动": ["广场舞", "太极", "晨练", "..."],
      "情感状态": ["孤独", "寂寞", "想念", "..."],
      "生活状态": ["独居", "空巢", "照顾", "..."]
    }
  },
  "message": "关键词配置获取成功，共98个关键词"
}
```

## 🎯 **实际使用示例**

### 1. Python客户端示例

```python
import requests
import json

class CSVAPIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def export_data(self, data, export_type="general", filename=None, options=None):
        """导出数据为CSV"""
        url = f"{self.base_url}/csv/export"
        payload = {
            "data": data,
            "type": export_type,
            "filename": filename,
            "options": options or {}
        }
        
        response = self.session.post(url, json=payload)
        return response.json()
    
    def import_csv(self, file_path, import_type="general", encoding="utf-8"):
        """导入CSV文件"""
        url = f"{self.base_url}/csv/import"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'type': import_type,
                'encoding': encoding,
                'skip_header': 'true',
                'validate_data': 'true'
            }
            
            response = self.session.post(url, files=files, data=data)
            return response.json()
    
    def analyze_csv(self, file_path, encoding="utf-8", sample_size=100):
        """分析CSV文件结构"""
        url = f"{self.base_url}/csv/analyze"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'encoding': encoding,
                'sample_size': str(sample_size)
            }
            
            response = self.session.post(url, files=files, data=data)
            return response.json()
    
    def create_template(self, template_type, include_examples=True, custom_fields=None):
        """创建CSV模板"""
        url = f"{self.base_url}/csv/template"
        payload = {
            "type": template_type,
            "include_examples": include_examples,
            "custom_fields": custom_fields
        }
        
        response = self.session.post(url, json=payload)
        return response.json()
    
    def download_file(self, filename, save_path=None):
        """下载CSV文件"""
        url = f"{self.base_url}/csv/download/{filename}"
        response = self.session.get(url)
        
        if response.status_code == 200:
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return save_path
            else:
                return response.content
        else:
            return response.json()

# 使用示例
if __name__ == "__main__":
    client = CSVAPIClient()
    
    # 1. 导出数据
    sample_data = [
        {
            "id": "memory_001",
            "user_id": "user_123",
            "user_input": "今天天气很好",
            "memory_text": "今天天气很好，让我想起了春天",
            "primary_emotion": "happy",
            "confidence": 0.85
        }
    ]
    
    export_result = client.export_data(
        data=sample_data,
        export_type="memories",
        filename="test_export.csv"
    )
    print("导出结果:", export_result)
    
    # 2. 创建模板
    template_result = client.create_template(
        template_type="memories",
        include_examples=True
    )
    print("模板创建结果:", template_result)
    
    # 3. 分析CSV文件
    if template_result['success']:
        template_filename = template_result['data']['filename']
        # 下载模板文件
        client.download_file(template_filename, "template.csv")
        
        # 分析模板文件
        analysis_result = client.analyze_csv("template.csv")
        print("分析结果:", analysis_result)
    
    # 4. 导入CSV文件
    import_result = client.import_csv("template.csv", "memories")
    print("导入结果:", import_result)
```

### 2. JavaScript客户端示例

```javascript
class CSVAPIClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }
    
    async exportData(data, exportType = 'general', filename = null, options = {}) {
        const response = await fetch(`${this.baseUrl}/csv/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: data,
                type: exportType,
                filename: filename,
                options: options
            })
        });
        
        return await response.json();
    }
    
    async importCSV(file, importType = 'general', encoding = 'utf-8') {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', importType);
        formData.append('encoding', encoding);
        formData.append('skip_header', 'true');
        formData.append('validate_data', 'true');
        
        const response = await fetch(`${this.baseUrl}/csv/import`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    }
    
    async analyzeCSV(file, encoding = 'utf-8', sampleSize = 100) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('encoding', encoding);
        formData.append('sample_size', sampleSize.toString());
        
        const response = await fetch(`${this.baseUrl}/csv/analyze`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    }
    
    async createTemplate(templateType, includeExamples = true, customFields = null) {
        const response = await fetch(`${this.baseUrl}/csv/template`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: templateType,
                include_examples: includeExamples,
                custom_fields: customFields
            })
        });
        
        return await response.json();
    }
    
    async downloadFile(filename) {
        const response = await fetch(`${this.baseUrl}/csv/download/${filename}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            return true;
        } else {
            return await response.json();
        }
    }
    
    async getSupportedFormats() {
        const response = await fetch(`${this.baseUrl}/csv/formats`);
        return await response.json();
    }
}

// 使用示例
const client = new CSVAPIClient();

// 导出数据示例
const sampleData = [
    {
        id: 'memory_001',
        user_id: 'user_123',
        user_input: '今天天气很好',
        memory_text: '今天天气很好，让我想起了春天',
        primary_emotion: 'happy',
        confidence: 0.85
    }
];

client.exportData(sampleData, 'memories', 'test_export.csv')
    .then(result => console.log('导出结果:', result))
    .catch(error => console.error('导出错误:', error));

// 文件上传处理示例
document.getElementById('fileInput').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.csv')) {
        try {
            const analysisResult = await client.analyzeCSV(file);
            console.log('分析结果:', analysisResult);
            
            const importResult = await client.importCSV(file, 'memories');
            console.log('导入结果:', importResult);
        } catch (error) {
            console.error('处理错误:', error);
        }
    }
});
```

### 3. 命令行工具示例

```bash
#!/bin/bash

# CSV API 命令行工具
CSV_API_BASE="http://localhost:5000"

# 导出数据
export_csv() {
    local data_file=$1
    local export_type=$2
    local filename=$3
    
    curl -X POST "${CSV_API_BASE}/csv/export" \
        -H "Content-Type: application/json" \
        -d @"$data_file" \
        -o "export_result.json"
    
    echo "导出结果已保存到 export_result.json"
}

# 导入CSV文件
import_csv() {
    local file_path=$1
    local import_type=$2
    
    curl -X POST "${CSV_API_BASE}/csv/import" \
        -F "file=@$file_path" \
        -F "type=$import_type" \
        -F "encoding=utf-8" \
        -F "skip_header=true" \
        -F "validate_data=true" \
        -o "import_result.json"
    
    echo "导入结果已保存到 import_result.json"
}

# 分析CSV文件
analyze_csv() {
    local file_path=$1
    
    curl -X POST "${CSV_API_BASE}/csv/analyze" \
        -F "file=@$file_path" \
        -F "encoding=utf-8" \
        -F "sample_size=100" \
        -o "analysis_result.json"
    
    echo "分析结果已保存到 analysis_result.json"
}

# 创建模板
create_template() {
    local template_type=$1
    
    curl -X POST "${CSV_API_BASE}/csv/template" \
        -H "Content-Type: application/json" \
        -d "{\"type\": \"$template_type\", \"include_examples\": true}" \
        -o "template_result.json"
    
    echo "模板创建结果已保存到 template_result.json"
}

# 下载文件
download_csv() {
    local filename=$1
    local save_path=${2:-$filename}
    
    curl -X GET "${CSV_API_BASE}/csv/download/$filename" \
        -o "$save_path"
    
    echo "文件已下载到 $save_path"
}

# 使用示例
case $1 in
    "export")
        export_csv "$2" "$3" "$4"
        ;;
    "import")
        import_csv "$2" "$3"
        ;;
    "analyze")
        analyze_csv "$2"
        ;;
    "template")
        create_template "$2"
        ;;
    "download")
        download_csv "$2" "$3"
        ;;
    *)
        echo "使用方法:"
        echo "  $0 export <data_file> <type> <filename>"
        echo "  $0 import <csv_file> <type>"
        echo "  $0 analyze <csv_file>"
        echo "  $0 template <type>"
        echo "  $0 download <filename> [save_path]"
        ;;
esac
```

## 🔧 **高级功能**

### 1. 批量处理工作流

```python
def batch_process_workflow(file_list, output_dir):
    """批量处理CSV文件工作流"""
    client = CSVAPIClient()
    
    # 1. 分析所有文件
    analysis_results = []
    for file_path in file_list:
        result = client.analyze_csv(file_path)
        analysis_results.append(result)
    
    # 2. 验证文件格式
    valid_files = []
    for i, result in enumerate(analysis_results):
        if result['success'] and result['data']['field_count'] > 0:
            valid_files.append(file_list[i])
    
    # 3. 合并文件
    if len(valid_files) > 1:
        # 使用API合并文件
        merge_result = merge_csv_files(valid_files)
        print(f"合并结果: {merge_result}")
    
    # 4. 拆分大文件
    for file_path in valid_files:
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            split_result = split_csv_file(file_path, 1000)
            print(f"拆分结果: {split_result}")
    
    return True
```

### 2. 数据质量检查

```python
def data_quality_check(file_path):
    """数据质量检查"""
    client = CSVAPIClient()
    
    # 1. 分析文件结构
    analysis = client.analyze_csv(file_path)
    
    # 2. 统计分析
    statistics = client.get_statistics(file_path)
    
    # 3. 验证数据
    validation = client.validate_csv(file_path)
    
    # 4. 质量报告
    quality_report = {
        'file_path': file_path,
        'total_rows': analysis['data']['total_rows'],
        'valid_rows': validation['data']['valid_rows'],
        'data_quality_score': validation['data']['validation_rate'],
        'null_percentage': sum(statistics['data']['null_counts'].values()) / (analysis['data']['total_rows'] * analysis['data']['field_count']),
        'recommendations': []
    }
    
    # 5. 生成建议
    if quality_report['data_quality_score'] < 0.8:
        quality_report['recommendations'].append("数据质量较低，建议进行数据清洗")
    
    if quality_report['null_percentage'] > 0.1:
        quality_report['recommendations'].append("空值较多，建议检查数据完整性")
    
    return quality_report
```

## 🎯 **最佳实践**

### 1. 大文件处理
- 使用分块处理避免内存溢出
- 优先使用文件拆分功能处理大文件
- 设置合适的sample_size进行分析

### 2. 数据验证
- 始终开启数据验证
- 为不同数据类型设置合适的验证规则
- 处理验证错误并提供用户友好的错误信息

### 3. 性能优化
- 使用合适的编码格式（UTF-8推荐）
- 选择适当的分隔符
- 批量处理时控制并发数量

### 4. 错误处理
- 检查API响应状态
- 处理文件格式错误
- 提供回退机制

## 📞 **技术支持**

### 常见问题
1. **文件编码问题**: 确保使用UTF-8编码
2. **内存不足**: 对大文件使用拆分功能
3. **数据格式不匹配**: 使用格式转换功能
4. **验证失败**: 检查必填字段和数据类型

### 调试工具
```bash
# 检查支持的格式
curl http://localhost:5000/csv/formats

# 创建测试模板
curl -X POST http://localhost:5000/csv/template \
  -H 'Content-Type: application/json' \
  -d '{"type": "memories", "include_examples": true}'
```

---

🎉 **PGG系统CSV文档接口已完整实现，提供了专业级的CSV文件处理能力，支持企业级数据管理需求！** 