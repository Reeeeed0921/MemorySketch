# PGG系统传感器硬件接口设计文档

## 🔧 **传感器硬件接口架构**

PGG情感记忆生成系统为传感器硬件预留了完整的接口体系，支持多种传感器类型和数据格式，实现硬件与软件的无缝集成。

## 📊 **支持的传感器类型**

### 1. 生理传感器
- **心率传感器** (PPG/ECG)
- **血氧传感器** (SpO2)
- **体温传感器** (Body Temperature)
- **呼吸传感器** (Respiratory Rate)
- **血压传感器** (Blood Pressure)
- **脑电传感器** (EEG)
- **肌电传感器** (EMG)

### 2. 环境传感器
- **环境温度传感器** (Temperature)
- **湿度传感器** (Humidity)
- **光照传感器** (Light)
- **空气质量传感器** (Air Quality)
- **噪音传感器** (Noise Level)
- **气压传感器** (Atmospheric Pressure)

### 3. 运动传感器
- **加速度传感器** (Accelerometer)
- **陀螺仪传感器** (Gyroscope)
- **磁力计传感器** (Magnetometer)
- **步数传感器** (Step Counter)
- **位置传感器** (GPS)

### 4. 交互传感器
- **触摸传感器** (Touch)
- **压力传感器** (Pressure)
- **手势传感器** (Gesture)
- **眼动传感器** (Eye Tracking)
- **语音传感器** (Voice Activity Detection)

## 🚀 **传感器硬件API接口**

### 1. 传感器数据接收接口

#### 实时数据上传
```http
POST /sensors/data
Content-Type: application/json

{
    "sensor_id": "sensor_001",
    "sensor_type": "heart_rate",
    "device_id": "device_123",
    "user_id": "user_456",
    "timestamp": "2024-01-01T12:00:00Z",
    "data": {
        "value": 72,
        "unit": "bpm",
        "quality": "good",
        "raw_data": [72, 73, 71, 74, 72]
    },
    "metadata": {
        "battery_level": 85,
        "signal_strength": 90,
        "device_status": "normal"
    }
}
```

#### 批量数据上传
```http
POST /sensors/data/batch
Content-Type: application/json

{
    "device_id": "device_123",
    "user_id": "user_456",
    "data_points": [
        {
            "sensor_id": "sensor_001",
            "sensor_type": "heart_rate",
            "timestamp": "2024-01-01T12:00:00Z",
            "data": {"value": 72, "unit": "bpm"}
        },
        {
            "sensor_id": "sensor_002",
            "sensor_type": "temperature",
            "timestamp": "2024-01-01T12:00:01Z",
            "data": {"value": 36.5, "unit": "celsius"}
        }
    ]
}
```

### 2. 传感器状态监控接口

#### 获取传感器状态
```http
GET /sensors/status
GET /sensors/status?device_id=device_123
GET /sensors/status?sensor_type=heart_rate
```

**响应示例：**
```json
{
    "success": true,
    "data": {
        "total_sensors": 5,
        "active_sensors": 4,
        "sensors": [
            {
                "sensor_id": "sensor_001",
                "sensor_type": "heart_rate",
                "device_id": "device_123",
                "status": "active",
                "last_update": "2024-01-01T12:00:00Z",
                "battery_level": 85,
                "signal_strength": 90,
                "data_quality": "good"
            }
        ]
    }
}
```

#### 传感器健康检查
```http
GET /sensors/health
```

### 3. 传感器配置管理接口

#### 获取传感器配置
```http
GET /sensors/config
GET /sensors/config?sensor_id=sensor_001
```

#### 更新传感器配置
```http
PUT /sensors/config
Content-Type: application/json

{
    "sensor_id": "sensor_001",
    "config": {
        "sampling_rate": 100,
        "data_format": "json",
        "compression": true,
        "alerts": {
            "low_battery": true,
            "signal_loss": true,
            "abnormal_values": true
        },
        "thresholds": {
            "heart_rate_min": 60,
            "heart_rate_max": 100
        }
    }
}
```

### 4. 传感器数据查询接口

#### 获取历史数据
```http
GET /sensors/history
参数：
- sensor_id: 传感器ID
- sensor_type: 传感器类型
- device_id: 设备ID
- user_id: 用户ID
- start_time: 开始时间
- end_time: 结束时间
- page: 页码
- per_page: 每页数量
```

#### 获取实时数据流
```http
GET /sensors/stream
参数：
- sensor_id: 传感器ID
- format: 数据格式 (json/csv/binary)
```

### 5. 传感器数据分析接口

#### 情感分析集成
```http
POST /sensors/analyze/emotion
Content-Type: application/json

{
    "user_id": "user_456",
    "sensor_data": {
        "heart_rate": [72, 73, 71, 74, 72],
        "temperature": [36.5, 36.6, 36.4],
        "activity_level": "moderate"
    },
    "context": {
        "environment": "home",
        "activity": "resting",
        "time_of_day": "afternoon"
    }
}
```

#### 异常检测
```http
POST /sensors/analyze/anomaly
Content-Type: application/json

{
    "sensor_data": {
        "sensor_id": "sensor_001",
        "values": [72, 73, 71, 74, 72, 105, 110, 108],
        "timestamps": ["2024-01-01T12:00:00Z", "..."]
    },
    "detection_config": {
        "algorithm": "statistical",
        "sensitivity": "medium"
    }
}
```

### 6. 传感器设备管理接口

#### 设备注册
```http
POST /sensors/devices/register
Content-Type: application/json

{
    "device_id": "device_123",
    "device_type": "wearable",
    "manufacturer": "TechCorp",
    "model": "SmartWatch Pro",
    "firmware_version": "1.2.3",
    "supported_sensors": [
        "heart_rate",
        "temperature",
        "accelerometer",
        "gyroscope"
    ],
    "communication_protocol": "bluetooth",
    "encryption": "AES256"
}
```

#### 设备认证
```http
POST /sensors/devices/auth
Content-Type: application/json

{
    "device_id": "device_123",
    "auth_token": "eyJhbGciOiJIUzI1NiIs...",
    "user_id": "user_456"
}
```

## 💾 **传感器数据存储设计**

### 数据表结构

#### 传感器数据表 (sensor_data)
```sql
CREATE TABLE sensor_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    device_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    value DECIMAL(10,4) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    quality VARCHAR(20) DEFAULT 'good',
    raw_data TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_time (sensor_id, timestamp),
    INDEX idx_user_sensor (user_id, sensor_type),
    INDEX idx_device_time (device_id, timestamp)
);
```

#### 传感器配置表 (sensor_config)
```sql
CREATE TABLE sensor_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) UNIQUE NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    device_id VARCHAR(50) NOT NULL,
    config JSON NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 设备信息表 (devices)
```sql
CREATE TABLE devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(50) UNIQUE NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    firmware_version VARCHAR(50),
    user_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔌 **硬件集成示例**

### 1. Arduino/ESP32 集成示例

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// 传感器数据发送
void sendSensorData(float heartRate, float temperature) {
    HTTPClient http;
    http.begin("http://pgg-server:5000/sensors/data");
    http.addHeader("Content-Type", "application/json");
    
    StaticJsonDocument<200> doc;
    doc["sensor_id"] = "sensor_001";
    doc["sensor_type"] = "heart_rate";
    doc["device_id"] = "esp32_001";
    doc["user_id"] = "user_456";
    doc["timestamp"] = "2024-01-01T12:00:00Z";
    doc["data"]["value"] = heartRate;
    doc["data"]["unit"] = "bpm";
    
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

### 2. 树莓派 Python 集成示例

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
        """发送传感器数据"""
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
    
    def get_sensor_config(self, sensor_id):
        """获取传感器配置"""
        try:
            response = self.session.get(
                f"{self.server_url}/sensors/config",
                params={"sensor_id": sensor_id}
            )
            return response.json()
        except Exception as e:
            print(f"Error getting config: {e}")
            return None

# 使用示例
if __name__ == "__main__":
    client = SensorClient("http://localhost:5000", "rpi_001")
    
    # 模拟传感器数据
    while True:
        # 发送心率数据
        client.send_sensor_data(
            sensor_id="heart_rate_01",
            sensor_type="heart_rate",
            value=72,
            unit="bpm",
            user_id="user_456"
        )
        
        # 发送温度数据
        client.send_sensor_data(
            sensor_id="temp_01",
            sensor_type="temperature",
            value=36.5,
            unit="celsius",
            user_id="user_456"
        )
        
        time.sleep(1)  # 每秒发送一次
```

### 3. 移动端集成示例 (React Native)

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
                    },
                    metadata: {
                        app_version: '1.0.0',
                        os_version: Platform.Version
                    }
                })
            });
            
            return await response.json();
        } catch (error) {
            console.error('Error sending sensor data:', error);
            return null;
        }
    }
    
    async startSensorStream(sensorType, callback) {
        const ws = new WebSocket(`${this.serverUrl}/sensors/stream?sensor_type=${sensorType}`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            callback(data);
        };
        
        return ws;
    }
}

// 使用示例
const sensorManager = new SensorManager('http://localhost:5000', 'mobile_001');

// 发送传感器数据
sensorManager.sendSensorData({
    sensorId: 'mobile_accel_01',
    type: 'accelerometer',
    value: 9.81,
    unit: 'm/s²',
    userId: 'user_456'
});
```

## 🔧 **传感器接口实现**

现在让我为您在现有的Flask应用中添加传感器硬件接口：

### 传感器数据模型
```python
from datetime import datetime
from typing import Dict, Any, Optional
import json

class SensorData:
    def __init__(self, sensor_id: str, sensor_type: str, device_id: str, 
                 user_id: str, value: float, unit: str, timestamp: datetime = None):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.device_id = device_id
        self.user_id = user_id
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.now()
        self.quality = "good"
        self.raw_data = []
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type,
            'device_id': self.device_id,
            'user_id': self.user_id,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'quality': self.quality,
            'raw_data': self.raw_data,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SensorData':
        sensor_data = cls(
            sensor_id=data['sensor_id'],
            sensor_type=data['sensor_type'],
            device_id=data['device_id'],
            user_id=data['user_id'],
            value=data['value'],
            unit=data['unit'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        )
        sensor_data.quality = data.get('quality', 'good')
        sensor_data.raw_data = data.get('raw_data', [])
        sensor_data.metadata = data.get('metadata', {})
        return sensor_data

class SensorDevice:
    def __init__(self, device_id: str, device_type: str, manufacturer: str = "",
                 model: str = "", firmware_version: str = ""):
        self.device_id = device_id
        self.device_type = device_type
        self.manufacturer = manufacturer
        self.model = model
        self.firmware_version = firmware_version
        self.supported_sensors = []
        self.status = "active"
        self.last_seen = datetime.now()
        self.user_id = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'firmware_version': self.firmware_version,
            'supported_sensors': self.supported_sensors,
            'status': self.status,
            'last_seen': self.last_seen.isoformat(),
            'user_id': self.user_id
        }
```

## 🎯 **配置文件扩展**

在 `config.py` 中添加传感器相关配置：

```python
# 传感器硬件配置
SENSOR_DATA_STORAGE = os.getenv('SENSOR_DATA_STORAGE', 'database')  # database/file
SENSOR_DATA_RETENTION_DAYS = int(os.getenv('SENSOR_DATA_RETENTION_DAYS', 30))
SENSOR_BATCH_SIZE = int(os.getenv('SENSOR_BATCH_SIZE', 100))
SENSOR_SAMPLING_RATE = int(os.getenv('SENSOR_SAMPLING_RATE', 10))  # Hz

# 支持的传感器类型
SUPPORTED_SENSOR_TYPES = [
    'heart_rate', 'temperature', 'blood_pressure', 'spo2',
    'accelerometer', 'gyroscope', 'magnetometer',
    'ambient_temperature', 'humidity', 'light', 'noise'
]

# 传感器数据验证配置
SENSOR_VALUE_RANGES = {
    'heart_rate': {'min': 30, 'max': 220, 'unit': 'bpm'},
    'temperature': {'min': 30.0, 'max': 45.0, 'unit': 'celsius'},
    'blood_pressure': {'min': 50, 'max': 250, 'unit': 'mmHg'},
    'spo2': {'min': 70, 'max': 100, 'unit': '%'},
}

# 传感器警报配置
SENSOR_ALERTS_ENABLED = os.getenv('SENSOR_ALERTS_ENABLED', 'True').lower() == 'true'
SENSOR_ALERT_THRESHOLDS = {
    'heart_rate': {'critical_low': 50, 'critical_high': 120},
    'temperature': {'critical_low': 35.0, 'critical_high': 38.5},
}
```

## 🚀 **使用示例**

### 1. 设备注册和配置
```bash
# 注册新设备
curl -X POST http://localhost:5000/sensors/devices/register \
  -H 'Content-Type: application/json' \
  -d '{
    "device_id": "smartwatch_001",
    "device_type": "wearable",
    "manufacturer": "TechCorp",
    "model": "SmartWatch Pro",
    "supported_sensors": ["heart_rate", "temperature", "accelerometer"]
  }'
```

### 2. 发送传感器数据
```bash
# 发送心率数据
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
      "quality": "good"
    }
  }'
```

### 3. 查询传感器数据
```bash
# 获取用户心率历史
curl "http://localhost:5000/sensors/history?user_id=user_456&sensor_type=heart_rate&start_time=2024-01-01T00:00:00Z&end_time=2024-01-01T23:59:59Z"

# 获取设备状态
curl "http://localhost:5000/sensors/status?device_id=smartwatch_001"
```

## 📈 **监控和分析**

### 传感器数据与情感分析集成
```bash
# 基于传感器数据进行情感分析
curl -X POST http://localhost:5000/sensors/analyze/emotion \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "user_456",
    "sensor_data": {
      "heart_rate": [72, 75, 78, 82, 85],
      "temperature": [36.5, 36.6, 36.7],
      "activity_level": "high"
    },
    "text_input": "今天参加了朋友的聚会，感觉很开心"
  }'
```

这个传感器硬件接口设计提供了：

1. **完整的API体系** - 涵盖数据接收、状态监控、配置管理等
2. **多种传感器支持** - 生理、环境、运动、交互传感器
3. **灵活的数据格式** - 支持JSON、CSV、二进制等格式
4. **硬件适配性** - 支持Arduino、树莓派、移动设备等
5. **实时处理能力** - 流式数据处理和实时分析
6. **安全认证机制** - 设备认证和数据加密
7. **情感分析集成** - 与现有情感分析系统无缝集成

您可以基于这个设计，根据具体的传感器硬件类型和需求进行定制化开发。 