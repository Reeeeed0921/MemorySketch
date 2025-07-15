# PGG传感器硬件接口使用说明

## 🎯 **接口概览**

PGG情感记忆生成系统已成功集成传感器硬件接口，支持多种传感器类型和数据格式，实现硬件与软件的无缝集成。

## 📋 **已实现的API接口**

### 1. 传感器数据管理
- **`POST /sensors/data`** - 接收单个传感器数据
- **`POST /sensors/data/batch`** - 批量接收传感器数据
- **`GET /sensors/history`** - 查询传感器历史数据
- **`GET /sensors/stream`** - 获取传感器数据流信息

### 2. 设备管理
- **`POST /sensors/devices/register`** - 注册传感器设备
- **`GET /sensors/status`** - 获取传感器状态
- **`GET /sensors/health`** - 获取传感器系统健康状态

### 3. 数据分析
- **`POST /sensors/analyze/emotion`** - 基于传感器数据分析情感
- **`POST /sensors/analyze/anomaly`** - 传感器数据异常检测
- **`GET /sensors/config`** - 获取传感器配置

## 🔧 **支持的传感器类型**

### 生理传感器
- **心率传感器** (heart_rate) - 30-220 bpm
- **体温传感器** (temperature) - 30.0-45.0°C
- **血压传感器** (blood_pressure) - 50-250 mmHg
- **血氧传感器** (spo2) - 70-100%
- **睡眠质量** (sleep_quality) - 0-100%
- **压力水平** (stress_level) - 0-100%

### 运动传感器
- **加速度传感器** (accelerometer) - -20.0 to 20.0 m/s²
- **陀螺仪传感器** (gyroscope) - -2000.0 to 2000.0 deg/s
- **磁力计传感器** (magnetometer) - -1000.0 to 1000.0 µT
- **步数传感器** (step_counter) - 0-100000 steps

### 环境传感器
- **环境温度** (ambient_temperature) - -40.0 to 80.0°C
- **湿度传感器** (humidity) - 0-100%
- **光照传感器** (light) - 0-100000 lux
- **噪音传感器** (noise) - 0-130 dB

## 🚀 **快速开始**

### 1. 启动服务器
```bash
# 启动PGG系统（包含传感器接口）
python start_server.py

# 或直接运行
python app.py
```

### 2. 设备注册
```bash
curl -X POST http://localhost:5000/sensors/devices/register \
  -H 'Content-Type: application/json' \
  -d '{
    "device_id": "smartwatch_001",
    "device_type": "wearable",
    "manufacturer": "TechCorp",
    "model": "SmartWatch Pro",
    "firmware_version": "1.2.3",
    "supported_sensors": ["heart_rate", "temperature", "accelerometer"]
  }'
```

**响应示例：**
```json
{
  "success": true,
  "message": "设备注册成功",
  "data": {
    "device_id": "smartwatch_001",
    "device_type": "wearable",
    "registered_at": "2024-01-01T12:00:00",
    "supported_sensors": ["heart_rate", "temperature", "accelerometer"]
  }
}
```

### 3. 发送传感器数据
```bash
curl -X POST http://localhost:5000/sensors/data \
  -H 'Content-Type: application/json' \
  -d '{
    "sensor_id": "hr_001",
    "sensor_type": "heart_rate",
    "device_id": "smartwatch_001",
    "user_id": "user_456",
    "timestamp": "2024-01-01T12:00:00Z",
    "data": {
      "value": 72,
      "unit": "bpm",
      "quality": "good",
      "raw_data": [70, 72, 74, 71, 73]
    },
    "metadata": {
      "battery_level": 85,
      "signal_strength": 90,
      "device_status": "normal"
    }
  }'
```

### 4. 批量发送数据
```bash
curl -X POST http://localhost:5000/sensors/data/batch \
  -H 'Content-Type: application/json' \
  -d '{
    "device_id": "smartwatch_001",
    "user_id": "user_456",
    "data_points": [
      {
        "sensor_id": "hr_001",
        "sensor_type": "heart_rate",
        "timestamp": "2024-01-01T12:00:00Z",
        "data": {"value": 72, "unit": "bpm"}
      },
      {
        "sensor_id": "temp_001",
        "sensor_type": "temperature",
        "timestamp": "2024-01-01T12:00:01Z",
        "data": {"value": 36.5, "unit": "celsius"}
      }
    ]
  }'
```

### 5. 查询历史数据
```bash
curl "http://localhost:5000/sensors/history?user_id=user_456&sensor_type=heart_rate&start_time=2024-01-01T00:00:00Z&end_time=2024-01-01T23:59:59Z&limit=100"
```

### 6. 获取设备状态
```bash
curl "http://localhost:5000/sensors/status?device_id=smartwatch_001"
```

## 💻 **硬件集成示例**

### Arduino/ESP32 示例
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

void sendSensorData(float heartRate, float temperature) {
    HTTPClient http;
    http.begin("http://your-server:5000/sensors/data");
    http.addHeader("Content-Type", "application/json");
    
    StaticJsonDocument<300> doc;
    doc["sensor_id"] = "sensor_001";
    doc["sensor_type"] = "heart_rate";
    doc["device_id"] = "esp32_001";
    doc["user_id"] = "user_456";
    doc["timestamp"] = "2024-01-01T12:00:00Z";
    doc["data"]["value"] = heartRate;
    doc["data"]["unit"] = "bpm";
    doc["data"]["quality"] = "good";
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    int httpResponseCode = http.POST(jsonString);
    
    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println("Data sent successfully");
    }
    
    http.end();
}
```

### 树莓派 Python 示例
```python
import requests
import json
import time
from datetime import datetime

class SensorClient:
    def __init__(self, server_url, device_id):
        self.server_url = server_url
        self.device_id = device_id
        self.session = requests.Session()
    
    def send_sensor_data(self, sensor_id, sensor_type, value, unit, user_id):
        data = {
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "device_id": self.device_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "data": {
                "value": value,
                "unit": unit,
                "quality": "good"
            },
            "metadata": {
                "battery_level": 85,
                "signal_strength": 90
            }
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/sensors/data",
                json=data,
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"Error sending data: {e}")
            return None

# 使用示例
client = SensorClient("http://localhost:5000", "rpi_001")
result = client.send_sensor_data(
    sensor_id="heart_rate_01",
    sensor_type="heart_rate",
    value=72,
    unit="bpm",
    user_id="user_456"
)
```

### 移动端 JavaScript 示例
```javascript
class SensorManager {
    constructor(serverUrl, deviceId) {
        this.serverUrl = serverUrl;
        this.deviceId = deviceId;
    }
    
    async sendSensorData(sensorData) {
        try {
            const response = await fetch(`${this.serverUrl}/sensors/data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sensor_id: sensorData.sensorId,
                    sensor_type: sensorData.type,
                    device_id: this.deviceId,
                    user_id: sensorData.userId,
                    timestamp: new Date().toISOString(),
                    data: {
                        value: sensorData.value,
                        unit: sensorData.unit,
                        quality: 'good'
                    }
                })
            });
            
            return await response.json();
        } catch (error) {
            console.error('Error sending sensor data:', error);
            return null;
        }
    }
}

// 使用示例
const sensorManager = new SensorManager('http://localhost:5000', 'mobile_001');
sensorManager.sendSensorData({
    sensorId: 'mobile_accel_01',
    type: 'accelerometer',
    value: 9.81,
    unit: 'm/s²',
    userId: 'user_456'
});
```

## 🧠 **情感分析集成**

### 基于传感器数据的情感分析
```bash
curl -X POST http://localhost:5000/sensors/analyze/emotion \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "user_456",
    "sensor_data": {
      "heart_rate": [72, 75, 78, 82, 85],
      "temperature": [36.5, 36.6, 36.7],
      "activity_level": "high"
    },
    "context": {
      "environment": "home",
      "activity": "exercising",
      "time_of_day": "morning"
    }
  }'
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "emotion_analysis": {
      "primary_emotion": "excited",
      "confidence": 0.78,
      "emotion_scores": {
        "excited": 3,
        "neutral": 1,
        "stressed": 1
      },
      "sensor_indicators": {
        "heart_rate": {
          "average": 78.4,
          "variability": 5.2,
          "analysis": {
            "emotion_indicators": ["active_or_anxious"]
          }
        },
        "temperature": {
          "average": 36.6,
          "analysis": {
            "emotion_indicators": ["normal_state"]
          }
        }
      }
    }
  }
}
```

## 🔍 **异常检测**

### 传感器数据异常检测
```bash
curl -X POST http://localhost:5000/sensors/analyze/anomaly \
  -H 'Content-Type: application/json' \
  -d '{
    "sensor_data": {
      "sensor_id": "hr_001",
      "values": [72, 73, 71, 74, 72, 105, 110, 108, 75, 73],
      "timestamps": ["2024-01-01T12:00:00Z", "2024-01-01T12:00:01Z", "..."]
    },
    "detection_config": {
      "algorithm": "statistical",
      "sensitivity": "medium"
    }
  }'
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "anomaly_detection": {
      "sensor_id": "hr_001",
      "anomalies": [
        {
          "index": 5,
          "value": 105,
          "expected_range": [64.4, 81.6],
          "deviation": 23.4,
          "severity": "high"
        },
        {
          "index": 6,
          "value": 110,
          "expected_range": [64.4, 81.6],
          "deviation": 28.4,
          "severity": "high"
        }
      ],
      "total_anomalies": 2,
      "anomaly_rate": 0.2
    }
  }
}
```

## 📊 **监控和状态**

### 系统健康检查
```bash
curl http://localhost:5000/sensors/health
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00",
    "storage_type": "local",
    "supported_sensors": 13,
    "sensor_types": ["heart_rate", "temperature", "..."],
    "storage_status": "healthy"
  }
}
```

### 传感器配置查询
```bash
curl http://localhost:5000/sensors/config
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "supported_sensor_types": ["heart_rate", "temperature", "..."],
    "sensor_value_ranges": {
      "heart_rate": {"min": 30, "max": 220, "unit": "bpm"},
      "temperature": {"min": 30.0, "max": 45.0, "unit": "celsius"}
    },
    "system_config": {
      "storage_type": "local",
      "data_retention_days": 30,
      "batch_size": 100,
      "sampling_rate": 10
    }
  }
}
```

## ⚙️ **配置选项**

### 环境变量配置
```bash
# 传感器数据存储
SENSOR_DATA_STORAGE=local
SENSOR_DATA_RETENTION_DAYS=30
SENSOR_BATCH_SIZE=100
SENSOR_SAMPLING_RATE=10

# 传感器警报
SENSOR_ALERTS_ENABLED=True
SENSOR_DEVICE_TIMEOUT=300
SENSOR_MAX_DEVICES_PER_USER=10

# 传感器数据流
SENSOR_STREAM_ENABLED=True
SENSOR_STREAM_MAX_CONNECTIONS=100
SENSOR_STREAM_BUFFER_SIZE=1000

# 传感器情感分析
SENSOR_EMOTION_ANALYSIS_ENABLED=True
SENSOR_EMOTION_CONFIDENCE_THRESHOLD=0.6
SENSOR_EMOTION_ANALYSIS_WINDOW=60

# 传感器异常检测
SENSOR_ANOMALY_DETECTION_ENABLED=True
SENSOR_ANOMALY_DETECTION_ALGORITHM=statistical
SENSOR_ANOMALY_SENSITIVITY=medium
```

## 📈 **数据存储**

### 本地存储（默认）
- **传感器数据**: `storage/sensor_data.json`
- **设备信息**: `storage/sensor_devices.json`
- **传感器配置**: `storage/sensor_config.json`

### 数据格式
```json
{
  "sensor_id": "hr_001",
  "sensor_type": "heart_rate",
  "device_id": "smartwatch_001",
  "user_id": "user_456",
  "value": 72,
  "unit": "bpm",
  "timestamp": "2024-01-01T12:00:00",
  "quality": "good",
  "raw_data": [70, 72, 74, 71, 73],
  "metadata": {
    "battery_level": 85,
    "signal_strength": 90
  }
}
```

## 🔒 **安全考虑**

### 数据验证
- 传感器数据范围验证
- 数据类型验证
- 时间戳验证
- 设备认证

### 数据加密
- 可选的数据加密传输
- 敏感数据本地加密存储
- 设备认证令牌

## 🎯 **使用场景**

### 1. 智能健康监测
- 实时心率监测
- 体温异常检测
- 睡眠质量分析
- 运动状态跟踪

### 2. 情感状态分析
- 生理指标情感分析
- 环境因素情感影响
- 长期情感趋势分析
- 异常情感状态报警

### 3. 老年人健康关怀
- 生理指标监测
- 异常状态预警
- 生活习惯分析
- 健康趋势报告

## 📞 **技术支持**

### 常见问题
1. **数据未保存**: 检查传感器数据格式和数值范围
2. **设备离线**: 检查设备连接和心跳间隔
3. **异常检测误报**: 调整异常检测敏感度
4. **情感分析不准确**: 提供更多上下文信息

### 调试工具
```bash
# 检查传感器系统状态
curl http://localhost:5000/sensors/health

# 查看最近的传感器数据
curl "http://localhost:5000/sensors/history?limit=10"

# 检查设备状态
curl "http://localhost:5000/sensors/status"
```

## 🚀 **未来扩展**

### 计划功能
- WebSocket 实时数据流
- 机器学习异常检测
- 更多传感器类型支持
- 云端数据同步
- 移动端SDK

### 自定义扩展
- 自定义传感器类型
- 自定义情感分析算法
- 自定义异常检测规则
- 自定义数据存储后端

---

🎉 **PGG传感器硬件接口已完整实现，支持多种传感器类型，提供完整的数据管理、分析和监控功能！** 