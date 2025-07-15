# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 传感器管理服务
负责传感器数据的接收、处理、存储和分析
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import math
import statistics
from dataclasses import dataclass

from config import config

logger = logging.getLogger(__name__)

@dataclass
class SensorData:
    """传感器数据模型"""
    sensor_id: str
    sensor_type: str
    device_id: str
    user_id: str
    value: float
    unit: str
    timestamp: datetime
    quality: str = "good"
    raw_data: List[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.raw_data is None:
            self.raw_data = []
        if self.metadata is None:
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
        return cls(
            sensor_id=data['sensor_id'],
            sensor_type=data['sensor_type'],
            device_id=data['device_id'],
            user_id=data['user_id'],
            value=data['value'],
            unit=data['unit'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
            quality=data.get('quality', 'good'),
            raw_data=data.get('raw_data', []),
            metadata=data.get('metadata', {})
        )

@dataclass
class SensorDevice:
    """传感器设备模型"""
    device_id: str
    device_type: str
    manufacturer: str = ""
    model: str = ""
    firmware_version: str = ""
    supported_sensors: List[str] = None
    status: str = "active"
    last_seen: datetime = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        if self.supported_sensors is None:
            self.supported_sensors = []
        if self.last_seen is None:
            self.last_seen = datetime.now()
    
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SensorDevice':
        return cls(
            device_id=data['device_id'],
            device_type=data['device_type'],
            manufacturer=data.get('manufacturer', ''),
            model=data.get('model', ''),
            firmware_version=data.get('firmware_version', ''),
            supported_sensors=data.get('supported_sensors', []),
            status=data.get('status', 'active'),
            last_seen=datetime.fromisoformat(data['last_seen'].replace('Z', '+00:00')),
            user_id=data.get('user_id')
        )

class SensorManager:
    """传感器管理器"""
    
    def __init__(self):
        """初始化传感器管理器"""
        self.use_local_storage = config.USE_LOCAL_STORAGE
        self.local_storage_path = config.LOCAL_STORAGE_PATH
        
        # 传感器配置
        self.supported_sensor_types = getattr(config, 'SUPPORTED_SENSOR_TYPES', [
            'heart_rate', 'temperature', 'blood_pressure', 'spo2',
            'accelerometer', 'gyroscope', 'magnetometer',
            'ambient_temperature', 'humidity', 'light', 'noise'
        ])
        
        self.sensor_value_ranges = getattr(config, 'SENSOR_VALUE_RANGES', {
            'heart_rate': {'min': 30, 'max': 220, 'unit': 'bpm'},
            'temperature': {'min': 30.0, 'max': 45.0, 'unit': 'celsius'},
            'blood_pressure': {'min': 50, 'max': 250, 'unit': 'mmHg'},
            'spo2': {'min': 70, 'max': 100, 'unit': '%'},
        })
        
        # 初始化存储
        if self.use_local_storage:
            self._init_local_storage()
    
    def _init_local_storage(self):
        """初始化本地存储"""
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        # 创建传感器数据文件
        self.sensor_data_file = os.path.join(self.local_storage_path, 'sensor_data.json')
        self.sensor_devices_file = os.path.join(self.local_storage_path, 'sensor_devices.json')
        self.sensor_config_file = os.path.join(self.local_storage_path, 'sensor_config.json')
        
        # 初始化文件
        for file_path in [self.sensor_data_file, self.sensor_devices_file, self.sensor_config_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def validate_sensor_data(self, sensor_data: SensorData) -> Tuple[bool, str]:
        """验证传感器数据"""
        try:
            # 检查传感器类型
            if sensor_data.sensor_type not in self.supported_sensor_types:
                return False, f"不支持的传感器类型: {sensor_data.sensor_type}"
            
            # 检查数值范围
            if sensor_data.sensor_type in self.sensor_value_ranges:
                range_config = self.sensor_value_ranges[sensor_data.sensor_type]
                if sensor_data.value < range_config['min'] or sensor_data.value > range_config['max']:
                    return False, f"传感器数值超出范围: {range_config['min']}-{range_config['max']}"
            
            # 检查必填字段
            required_fields = ['sensor_id', 'sensor_type', 'device_id', 'user_id', 'value', 'unit']
            for field in required_fields:
                if not getattr(sensor_data, field):
                    return False, f"缺少必填字段: {field}"
            
            return True, "数据验证通过"
            
        except Exception as e:
            logger.error(f"传感器数据验证失败: {str(e)}")
            return False, f"数据验证失败: {str(e)}"
    
    def save_sensor_data(self, sensor_data: SensorData) -> bool:
        """保存传感器数据"""
        try:
            # 验证数据
            is_valid, message = self.validate_sensor_data(sensor_data)
            if not is_valid:
                logger.warning(f"传感器数据验证失败: {message}")
                return False
            
            if self.use_local_storage:
                return self._save_sensor_data_local(sensor_data)
            else:
                return self._save_sensor_data_database(sensor_data)
                
        except Exception as e:
            logger.error(f"保存传感器数据失败: {str(e)}")
            return False
    
    def _save_sensor_data_local(self, sensor_data: SensorData) -> bool:
        """本地存储保存传感器数据"""
        try:
            # 读取现有数据
            with open(self.sensor_data_file, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
            
            # 添加新数据
            data_list.append(sensor_data.to_dict())
            
            # 数据清理 - 只保留最近30天的数据
            cutoff_time = datetime.now() - timedelta(days=30)
            data_list = [
                d for d in data_list 
                if datetime.fromisoformat(d['timestamp'].replace('Z', '+00:00')) > cutoff_time
            ]
            
            # 保存到文件
            with open(self.sensor_data_file, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2)
            
            logger.info(f"本地保存传感器数据成功: {sensor_data.sensor_id}")
            return True
            
        except Exception as e:
            logger.error(f"本地保存传感器数据失败: {str(e)}")
            return False
    
    def _save_sensor_data_database(self, sensor_data: SensorData) -> bool:
        """数据库保存传感器数据"""
        # TODO: 实现数据库存储
        logger.info("数据库存储功能待实现")
        return True
    
    def get_sensor_data(self, user_id: str = None, sensor_type: str = None, 
                       device_id: str = None, start_time: datetime = None, 
                       end_time: datetime = None, limit: int = 100) -> List[SensorData]:
        """获取传感器数据"""
        try:
            if self.use_local_storage:
                return self._get_sensor_data_local(user_id, sensor_type, device_id, start_time, end_time, limit)
            else:
                return self._get_sensor_data_database(user_id, sensor_type, device_id, start_time, end_time, limit)
                
        except Exception as e:
            logger.error(f"获取传感器数据失败: {str(e)}")
            return []
    
    def _get_sensor_data_local(self, user_id: str, sensor_type: str, device_id: str,
                              start_time: datetime, end_time: datetime, limit: int) -> List[SensorData]:
        """本地存储获取传感器数据"""
        try:
            with open(self.sensor_data_file, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
            
            # 过滤数据
            filtered_data = []
            for data in data_list:
                # 用户ID过滤
                if user_id and data.get('user_id') != user_id:
                    continue
                
                # 传感器类型过滤
                if sensor_type and data.get('sensor_type') != sensor_type:
                    continue
                
                # 设备ID过滤
                if device_id and data.get('device_id') != device_id:
                    continue
                
                # 时间范围过滤
                data_time = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                if start_time and data_time < start_time:
                    continue
                if end_time and data_time > end_time:
                    continue
                
                filtered_data.append(SensorData.from_dict(data))
            
            # 按时间排序（最新的在前）
            filtered_data.sort(key=lambda x: x.timestamp, reverse=True)
            
            # 限制返回数量
            return filtered_data[:limit]
            
        except Exception as e:
            logger.error(f"本地获取传感器数据失败: {str(e)}")
            return []
    
    def _get_sensor_data_database(self, user_id: str, sensor_type: str, device_id: str,
                                 start_time: datetime, end_time: datetime, limit: int) -> List[SensorData]:
        """数据库获取传感器数据"""
        # TODO: 实现数据库查询
        logger.info("数据库查询功能待实现")
        return []
    
    def register_device(self, device: SensorDevice) -> bool:
        """注册传感器设备"""
        try:
            if self.use_local_storage:
                return self._register_device_local(device)
            else:
                return self._register_device_database(device)
                
        except Exception as e:
            logger.error(f"注册设备失败: {str(e)}")
            return False
    
    def _register_device_local(self, device: SensorDevice) -> bool:
        """本地存储注册设备"""
        try:
            # 读取现有设备
            with open(self.sensor_devices_file, 'r', encoding='utf-8') as f:
                devices = json.load(f)
            
            # 检查设备是否已存在
            for i, existing_device in enumerate(devices):
                if existing_device.get('device_id') == device.device_id:
                    devices[i] = device.to_dict()  # 更新现有设备
                    break
            else:
                devices.append(device.to_dict())  # 添加新设备
            
            # 保存到文件
            with open(self.sensor_devices_file, 'w', encoding='utf-8') as f:
                json.dump(devices, f, ensure_ascii=False, indent=2)
            
            logger.info(f"本地注册设备成功: {device.device_id}")
            return True
            
        except Exception as e:
            logger.error(f"本地注册设备失败: {str(e)}")
            return False
    
    def _register_device_database(self, device: SensorDevice) -> bool:
        """数据库注册设备"""
        # TODO: 实现数据库存储
        logger.info("数据库存储功能待实现")
        return True
    
    def get_device_status(self, device_id: str = None) -> Dict[str, Any]:
        """获取设备状态"""
        try:
            if self.use_local_storage:
                return self._get_device_status_local(device_id)
            else:
                return self._get_device_status_database(device_id)
                
        except Exception as e:
            logger.error(f"获取设备状态失败: {str(e)}")
            return {}
    
    def _get_device_status_local(self, device_id: str) -> Dict[str, Any]:
        """本地存储获取设备状态"""
        try:
            with open(self.sensor_devices_file, 'r', encoding='utf-8') as f:
                devices = json.load(f)
            
            if device_id:
                # 获取指定设备
                for device_data in devices:
                    if device_data.get('device_id') == device_id:
                        return {
                            'device': device_data,
                            'online': self._is_device_online(device_data),
                            'last_data_time': self._get_last_data_time(device_id)
                        }
                return {}
            else:
                # 获取所有设备状态
                device_statuses = []
                for device_data in devices:
                    device_statuses.append({
                        'device': device_data,
                        'online': self._is_device_online(device_data),
                        'last_data_time': self._get_last_data_time(device_data['device_id'])
                    })
                
                return {
                    'total_devices': len(devices),
                    'online_devices': sum(1 for status in device_statuses if status['online']),
                    'devices': device_statuses
                }
                
        except Exception as e:
            logger.error(f"本地获取设备状态失败: {str(e)}")
            return {}
    
    def _get_device_status_database(self, device_id: str) -> Dict[str, Any]:
        """数据库获取设备状态"""
        # TODO: 实现数据库查询
        logger.info("数据库查询功能待实现")
        return {}
    
    def _is_device_online(self, device_data: Dict[str, Any]) -> bool:
        """检查设备是否在线"""
        try:
            last_seen = datetime.fromisoformat(device_data['last_seen'].replace('Z', '+00:00'))
            return (datetime.now() - last_seen).total_seconds() < 300  # 5分钟内视为在线
        except:
            return False
    
    def _get_last_data_time(self, device_id: str) -> Optional[str]:
        """获取设备最后数据时间"""
        try:
            with open(self.sensor_data_file, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
            
            device_data = [d for d in data_list if d.get('device_id') == device_id]
            if device_data:
                latest_data = max(device_data, key=lambda x: x['timestamp'])
                return latest_data['timestamp']
            return None
            
        except Exception as e:
            logger.error(f"获取最后数据时间失败: {str(e)}")
            return None
    
    def analyze_sensor_emotion(self, user_id: str, sensor_data: Dict[str, Any], 
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """基于传感器数据分析情感"""
        try:
            emotion_result = {
                'primary_emotion': 'neutral',
                'confidence': 0.5,
                'emotion_scores': {},
                'analysis_source': 'sensor_data',
                'sensor_indicators': {}
            }
            
            # 心率分析
            if 'heart_rate' in sensor_data:
                hr_values = sensor_data['heart_rate']
                if isinstance(hr_values, list) and hr_values:
                    avg_hr = statistics.mean(hr_values)
                    hr_variability = statistics.stdev(hr_values) if len(hr_values) > 1 else 0
                    
                    emotion_result['sensor_indicators']['heart_rate'] = {
                        'average': avg_hr,
                        'variability': hr_variability,
                        'analysis': self._analyze_heart_rate_emotion(avg_hr, hr_variability)
                    }
            
            # 温度分析
            if 'temperature' in sensor_data:
                temp_values = sensor_data['temperature']
                if isinstance(temp_values, list) and temp_values:
                    avg_temp = statistics.mean(temp_values)
                    emotion_result['sensor_indicators']['temperature'] = {
                        'average': avg_temp,
                        'analysis': self._analyze_temperature_emotion(avg_temp)
                    }
            
            # 活动水平分析
            if 'activity_level' in sensor_data:
                activity = sensor_data['activity_level']
                emotion_result['sensor_indicators']['activity'] = {
                    'level': activity,
                    'analysis': self._analyze_activity_emotion(activity)
                }
            
            # 综合分析
            emotion_result.update(self._combine_sensor_emotion_analysis(emotion_result['sensor_indicators']))
            
            return emotion_result
            
        except Exception as e:
            logger.error(f"传感器情感分析失败: {str(e)}")
            return {
                'primary_emotion': 'neutral',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _analyze_heart_rate_emotion(self, avg_hr: float, hr_variability: float) -> Dict[str, Any]:
        """分析心率情感指标"""
        analysis = {'emotion_indicators': []}
        
        # 基于平均心率判断
        if avg_hr > 100:
            analysis['emotion_indicators'].append('excited_or_stressed')
        elif avg_hr > 80:
            analysis['emotion_indicators'].append('active_or_anxious')
        elif avg_hr < 60:
            analysis['emotion_indicators'].append('relaxed_or_calm')
        else:
            analysis['emotion_indicators'].append('normal_state')
        
        # 基于心率变异性判断
        if hr_variability > 10:
            analysis['emotion_indicators'].append('emotional_instability')
        elif hr_variability < 3:
            analysis['emotion_indicators'].append('stable_state')
        
        return analysis
    
    def _analyze_temperature_emotion(self, avg_temp: float) -> Dict[str, Any]:
        """分析体温情感指标"""
        analysis = {'emotion_indicators': []}
        
        if avg_temp > 37.0:
            analysis['emotion_indicators'].append('stressed_or_excited')
        elif avg_temp < 36.0:
            analysis['emotion_indicators'].append('calm_or_tired')
        else:
            analysis['emotion_indicators'].append('normal_state')
        
        return analysis
    
    def _analyze_activity_emotion(self, activity_level: str) -> Dict[str, Any]:
        """分析活动水平情感指标"""
        analysis = {'emotion_indicators': []}
        
        if activity_level == 'high':
            analysis['emotion_indicators'].append('energetic_or_excited')
        elif activity_level == 'low':
            analysis['emotion_indicators'].append('calm_or_sad')
        else:
            analysis['emotion_indicators'].append('normal_state')
        
        return analysis
    
    def _combine_sensor_emotion_analysis(self, sensor_indicators: Dict[str, Any]) -> Dict[str, Any]:
        """综合传感器情感分析"""
        # 简单的规则基础情感判断
        all_indicators = []
        for sensor_type, data in sensor_indicators.items():
            if 'analysis' in data and 'emotion_indicators' in data['analysis']:
                all_indicators.extend(data['analysis']['emotion_indicators'])
        
        # 统计情感指标
        emotion_counts = {}
        for indicator in all_indicators:
            if 'excited' in indicator or 'energetic' in indicator:
                emotion_counts['excited'] = emotion_counts.get('excited', 0) + 1
            elif 'stressed' in indicator or 'anxious' in indicator:
                emotion_counts['stressed'] = emotion_counts.get('stressed', 0) + 1
            elif 'calm' in indicator or 'relaxed' in indicator:
                emotion_counts['calm'] = emotion_counts.get('calm', 0) + 1
            elif 'sad' in indicator or 'tired' in indicator:
                emotion_counts['sad'] = emotion_counts.get('sad', 0) + 1
            else:
                emotion_counts['neutral'] = emotion_counts.get('neutral', 0) + 1
        
        # 确定主要情感
        if emotion_counts:
            primary_emotion = max(emotion_counts, key=emotion_counts.get)
            confidence = emotion_counts[primary_emotion] / sum(emotion_counts.values())
        else:
            primary_emotion = 'neutral'
            confidence = 0.5
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': confidence,
            'emotion_scores': emotion_counts
        }
    
    def detect_anomalies(self, sensor_data: Dict[str, Any], 
                        detection_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """检测传感器数据异常"""
        try:
            anomalies = []
            
            if detection_config is None:
                detection_config = {'algorithm': 'statistical', 'sensitivity': 'medium'}
            
            sensor_id = sensor_data.get('sensor_id')
            values = sensor_data.get('values', [])
            
            if not values:
                return {'anomalies': [], 'message': '没有数据可分析'}
            
            # 统计分析方法
            if detection_config.get('algorithm') == 'statistical':
                mean_val = statistics.mean(values)
                std_val = statistics.stdev(values) if len(values) > 1 else 0
                
                # 根据敏感度设置阈值
                sensitivity_multiplier = {
                    'low': 3.0,
                    'medium': 2.0,
                    'high': 1.5
                }.get(detection_config.get('sensitivity', 'medium'), 2.0)
                
                threshold = std_val * sensitivity_multiplier
                
                for i, value in enumerate(values):
                    if abs(value - mean_val) > threshold:
                        anomalies.append({
                            'index': i,
                            'value': value,
                            'expected_range': [mean_val - threshold, mean_val + threshold],
                            'deviation': abs(value - mean_val),
                            'severity': 'high' if abs(value - mean_val) > threshold * 1.5 else 'medium'
                        })
            
            return {
                'sensor_id': sensor_id,
                'anomalies': anomalies,
                'total_anomalies': len(anomalies),
                'anomaly_rate': len(anomalies) / len(values) if values else 0,
                'analysis_method': detection_config.get('algorithm', 'statistical')
            }
            
        except Exception as e:
            logger.error(f"异常检测失败: {str(e)}")
            return {
                'anomalies': [],
                'error': str(e)
            }
    
    def get_health_check(self) -> Dict[str, Any]:
        """获取传感器系统健康状态"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'storage_type': 'local' if self.use_local_storage else 'database',
                'supported_sensors': len(self.supported_sensor_types),
                'sensor_types': self.supported_sensor_types
            }
            
            # 检查存储系统
            if self.use_local_storage:
                # 检查本地文件
                storage_status = all(
                    os.path.exists(f) for f in [
                        self.sensor_data_file,
                        self.sensor_devices_file,
                        self.sensor_config_file
                    ]
                )
                health_status['storage_status'] = 'healthy' if storage_status else 'error'
            else:
                # TODO: 检查数据库连接
                health_status['storage_status'] = 'not_implemented'
            
            return health_status
            
        except Exception as e:
            logger.error(f"获取健康状态失败: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            } 