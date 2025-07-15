# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 配置管理模块
管理所有API密钥、模型路径、系统参数等配置项
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """系统配置类"""
    
    # Flask应用配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'pgg-memory-system-2024')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')  # 支持局域网访问
    PORT = int(os.getenv('PORT', 5000))
    
    # 数据库配置
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'pgg_memory_db')
    
    # 本地存储配置（作为MongoDB的备选方案）
    LOCAL_STORAGE_PATH = os.getenv('LOCAL_STORAGE_PATH', './storage/')
    USE_LOCAL_STORAGE = os.getenv('USE_LOCAL_STORAGE', 'True').lower() == 'true'
    
    # 语音识别API配置
    # 科大讯飞API配置
    IFLYTEK_APP_ID = os.getenv('IFLYTEK_APP_ID', '')
    IFLYTEK_API_SECRET = os.getenv('IFLYTEK_API_SECRET', '')
    IFLYTEK_API_KEY = os.getenv('IFLYTEK_API_KEY', '')
    
    # Whisper API配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    WHISPER_MODEL_PATH = os.getenv('WHISPER_MODEL_PATH', './models/whisper/')
    
    # DeepSeek API配置（用于高精度情感分析）
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-79b0e5d5aee647e59319e78a94bffab9')
    DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')  # 或 deepseek-reasoner
    DEEPSEEK_MAX_TOKENS = int(os.getenv('DEEPSEEK_MAX_TOKENS', 1000))
    DEEPSEEK_TEMPERATURE = float(os.getenv('DEEPSEEK_TEMPERATURE', 0.7))
    
    # 情绪识别模型配置
    WAV2VEC2_MODEL_PATH = os.getenv('WAV2VEC2_MODEL_PATH', './models/wav2vec2/')
    ECAPA_MODEL_PATH = os.getenv('ECAPA_MODEL_PATH', './models/ecapa/')
    
    # 图像生成API配置
    # Stable Diffusion配置
    SD_MODEL_PATH = os.getenv('SD_MODEL_PATH', './models/stable_diffusion/')
    SD_API_URL = os.getenv('SD_API_URL', 'http://localhost:7860')
    
    # MidJourney API配置
    MJ_API_KEY = os.getenv('MJ_API_KEY', '')
    MJ_API_URL = os.getenv('MJ_API_URL', 'https://api.midjourney.com/')
    
    # 科大讯飞图片生成API配置
    IFLYTEK_IMAGE_API_ID = os.getenv('IFLYTEK_IMAGE_API_ID', 'e5bc8a2a')
    IFLYTEK_IMAGE_API_KEY = os.getenv('IFLYTEK_IMAGE_API_KEY', '956565afe6a1ddc7f269e627b7cfee32')
    IFLYTEK_IMAGE_API_SECRET = os.getenv('IFLYTEK_IMAGE_API_SECRET', 'ZGJkOGM5Mjc0NWVhZDlhYzllZDdiMjY3')
    IFLYTEK_IMAGE_API_URL = os.getenv('IFLYTEK_IMAGE_API_URL', 'https://spark-api.cn-huabei-1.xf-yun.com/v2.1/tti')
    
    # 科大讯飞性别年龄识别API配置
    IFLYTEK_GENDER_AGE_API_ID = os.getenv('IFLYTEK_GENDER_AGE_API_ID', 'e5bc8a2a')
    IFLYTEK_GENDER_AGE_API_KEY = os.getenv('IFLYTEK_GENDER_AGE_API_KEY', '956565afe6a1ddc7f269e627b7cfee32')
    IFLYTEK_GENDER_AGE_API_SECRET = os.getenv('IFLYTEK_GENDER_AGE_API_SECRET', 'ZGJkOGM5Mjc0NWVhZDlhYzllZDdiMjY3')
    IFLYTEK_GENDER_AGE_API_URL = os.getenv('IFLYTEK_GENDER_AGE_API_URL', 'https://api.xfyun.cn/v1/service/v1/ise')
    
    # 音频处理配置
    AUDIO_SAMPLE_RATE = int(os.getenv('AUDIO_SAMPLE_RATE', 16000))
    AUDIO_CHANNELS = int(os.getenv('AUDIO_CHANNELS', 1))
    AUDIO_FORMAT = os.getenv('AUDIO_FORMAT', 'wav')
    MAX_AUDIO_LENGTH = int(os.getenv('MAX_AUDIO_LENGTH', 300))  # 秒
    
    # 系统资源配置（适配边缘设备）
    MAX_MEMORY_USAGE = os.getenv('MAX_MEMORY_USAGE', '512MB')
    USE_CPU_ONLY = os.getenv('USE_CPU_ONLY', 'True').lower() == 'true'
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 1))  # 小批次处理
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', './logs/pgg_system.log')
    
    # 安全配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB最大上传大小
    ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a'}
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv'}
    
    # 服务优先级配置（准确率优先）
    PRIORITIZE_ACCURACY = os.getenv('PRIORITIZE_ACCURACY', 'True').lower() == 'true'
    
    # ========== 扩展API配置 ==========
    
    # 搜索服务API配置
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
    ELASTICSEARCH_API_KEY = os.getenv('ELASTICSEARCH_API_KEY', '')
    ELASTICSEARCH_API_SECRET = os.getenv('ELASTICSEARCH_API_SECRET', '')
    
    # 第三方搜索服务
    ALGOLIA_APP_ID = os.getenv('ALGOLIA_APP_ID', '')
    ALGOLIA_API_KEY = os.getenv('ALGOLIA_API_KEY', '')
    ALGOLIA_API_SECRET = os.getenv('ALGOLIA_API_SECRET', '')
    
    # 数据分析服务API配置
    GOOGLE_ANALYTICS_API_KEY = os.getenv('GOOGLE_ANALYTICS_API_KEY', '')
    GOOGLE_ANALYTICS_API_SECRET = os.getenv('GOOGLE_ANALYTICS_API_SECRET', '')
    GOOGLE_ANALYTICS_VIEW_ID = os.getenv('GOOGLE_ANALYTICS_VIEW_ID', '')
    
    # 百度统计API配置
    BAIDU_TONGJI_API_KEY = os.getenv('BAIDU_TONGJI_API_KEY', '')
    BAIDU_TONGJI_API_SECRET = os.getenv('BAIDU_TONGJI_API_SECRET', '')
    BAIDU_TONGJI_SITE_ID = os.getenv('BAIDU_TONGJI_SITE_ID', '')
    
    # 文件存储服务API配置
    # 阿里云OSS
    ALIYUN_OSS_ACCESS_KEY_ID = os.getenv('ALIYUN_OSS_ACCESS_KEY_ID', '')
    ALIYUN_OSS_ACCESS_KEY_SECRET = os.getenv('ALIYUN_OSS_ACCESS_KEY_SECRET', '')
    ALIYUN_OSS_BUCKET_NAME = os.getenv('ALIYUN_OSS_BUCKET_NAME', '')
    ALIYUN_OSS_ENDPOINT = os.getenv('ALIYUN_OSS_ENDPOINT', '')
    
    # 腾讯云COS
    TENCENT_COS_SECRET_ID = os.getenv('TENCENT_COS_SECRET_ID', '')
    TENCENT_COS_SECRET_KEY = os.getenv('TENCENT_COS_SECRET_KEY', '')
    TENCENT_COS_BUCKET_NAME = os.getenv('TENCENT_COS_BUCKET_NAME', '')
    TENCENT_COS_REGION = os.getenv('TENCENT_COS_REGION', '')
    
    # AWS S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME', '')
    AWS_S3_REGION = os.getenv('AWS_S3_REGION', '')
    
    # 消息队列服务API配置
    RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
    RABBITMQ_API_KEY = os.getenv('RABBITMQ_API_KEY', '')
    RABBITMQ_API_SECRET = os.getenv('RABBITMQ_API_SECRET', '')
    
    # Redis缓存服务配置
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_API_KEY = os.getenv('REDIS_API_KEY', '')
    
    # 实时通信服务API配置
    WEBSOCKET_SECRET_KEY = os.getenv('WEBSOCKET_SECRET_KEY', 'ws-secret-key-2024')
    SOCKETIO_API_KEY = os.getenv('SOCKETIO_API_KEY', '')
    
    # 推送服务API配置
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', '')
    FIREBASE_API_SECRET = os.getenv('FIREBASE_API_SECRET', '')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
    
    # 极光推送
    JPUSH_APP_KEY = os.getenv('JPUSH_APP_KEY', '')
    JPUSH_APP_SECRET = os.getenv('JPUSH_APP_SECRET', '')
    JPUSH_MASTER_SECRET = os.getenv('JPUSH_MASTER_SECRET', '')
    
    # 邮件服务API配置
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
    SENDGRID_API_SECRET = os.getenv('SENDGRID_API_SECRET', '')
    
    # 阿里云邮件推送
    ALIYUN_EMAIL_ACCESS_KEY_ID = os.getenv('ALIYUN_EMAIL_ACCESS_KEY_ID', '')
    ALIYUN_EMAIL_ACCESS_KEY_SECRET = os.getenv('ALIYUN_EMAIL_ACCESS_KEY_SECRET', '')
    
    # 监控服务API配置
    PROMETHEUS_URL = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
    PROMETHEUS_API_KEY = os.getenv('PROMETHEUS_API_KEY', '')
    
    # Grafana API配置
    GRAFANA_URL = os.getenv('GRAFANA_URL', 'http://localhost:3000')
    GRAFANA_API_KEY = os.getenv('GRAFANA_API_KEY', '')
    GRAFANA_API_SECRET = os.getenv('GRAFANA_API_SECRET', '')
    
    # 第三方监控服务
    DATADOG_API_KEY = os.getenv('DATADOG_API_KEY', '')
    DATADOG_APP_KEY = os.getenv('DATADOG_APP_KEY', '')
    
    # 日志服务API配置
    LOGSTASH_URL = os.getenv('LOGSTASH_URL', 'http://localhost:5044')
    LOGSTASH_API_KEY = os.getenv('LOGSTASH_API_KEY', '')
    
    # 阿里云日志服务
    ALIYUN_LOG_ACCESS_KEY_ID = os.getenv('ALIYUN_LOG_ACCESS_KEY_ID', '')
    ALIYUN_LOG_ACCESS_KEY_SECRET = os.getenv('ALIYUN_LOG_ACCESS_KEY_SECRET', '')
    ALIYUN_LOG_PROJECT = os.getenv('ALIYUN_LOG_PROJECT', '')
    ALIYUN_LOG_STORE = os.getenv('ALIYUN_LOG_STORE', '')
    
    # 翻译服务API配置
    GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY', '')
    GOOGLE_TRANSLATE_API_SECRET = os.getenv('GOOGLE_TRANSLATE_API_SECRET', '')
    
    # 百度翻译API
    BAIDU_TRANSLATE_APP_ID = os.getenv('BAIDU_TRANSLATE_APP_ID', '')
    BAIDU_TRANSLATE_API_KEY = os.getenv('BAIDU_TRANSLATE_API_KEY', '')
    BAIDU_TRANSLATE_API_SECRET = os.getenv('BAIDU_TRANSLATE_API_SECRET', '')
    
    # 腾讯翻译API
    TENCENT_TRANSLATE_SECRET_ID = os.getenv('TENCENT_TRANSLATE_SECRET_ID', '')
    TENCENT_TRANSLATE_SECRET_KEY = os.getenv('TENCENT_TRANSLATE_SECRET_KEY', '')
    
    # ========== 老人相关数据配置 ==========
    
    # 老人关键词检测配置（扩展版98个关键词）
    ELDERLY_KEYWORDS = [
        # 基础关键词
        '孙子', '孙女', '退休', '养老', '老伴', '儿媳', '女婿', '看病', '体检',
        
        # 家庭关系
        '重孙', '重孙女', '外孙', '外孙女', '曾孙', '曾孙女', '孙媳妇', '孙女婿',
        '大儿子', '小儿子', '大女儿', '小女儿', '长子', '次子', '长女', '次女',
        
        # 生活相关
        '老花镜', '拐杖', '血压', '血糖', '服药', '吃药', '医院', '诊所', '住院',
        '保健品', '营养品', '钙片', '维生素', '降压药', '降糖药', '心脏病', '高血压',
        '糖尿病', '关节炎', '骨质疏松', '老年痴呆', '健忘', '记忆力', '老花眼',
        
        # 社交与活动
        '广场舞', '太极', '晨练', '散步', '下棋', '打牌', '唱戏', '看戏', '听戏',
        '老年大学', '老年活动', '社区活动', '邻居', '老朋友', '老同事', '老战友',
        
        # 情感状态
        '孤独', '寂寞', '想念', '怀念', '回忆', '过去', '当年', '年轻时', '以前',
        '操心', '担心', '放心不下', '牵挂', '惦记', '想家', '想儿子', '想女儿',
        
        # 生活状态
        '独居', '空巢', '照顾', '陪伴', '探望', '看望', '回家', '养老院', '敬老院',
        '老人院', '护理院', '社区服务', '上门服务', '送餐', '代购', '家政',
        
        # 补充的健康关键词
        '心脏', '头晕', '失眠', '关节', '骨头', '药物', '医生', '身体', '健康',
        '疼痛', '不舒服', '生病', '复查', '治疗', '康复', '手术', '住院',
        
        # 补充的家庭关键词
        '孩子', '子女', '儿子', '女儿', '老公', '老婆', '家人', '家里', '团聚',
        '思念', '亲人', '孙辈', '晚辈', '后代', '家族',
        
        # 补充的社交关键词
        '朋友', '同伴', '聊天', '说话', '交流', '沟通', '相伴', '聚会', '聚餐',
        '热闹', '安静', '冷静', '无聊', '空虚', '冷清', '一个人', '没人', '独自'
    ]
    
    # 传感器硬件配置
    SENSOR_DATA_STORAGE = os.getenv('SENSOR_DATA_STORAGE', 'local')  # local/database
    SENSOR_DATA_RETENTION_DAYS = int(os.getenv('SENSOR_DATA_RETENTION_DAYS', 30))
    SENSOR_BATCH_SIZE = int(os.getenv('SENSOR_BATCH_SIZE', 100))
    SENSOR_SAMPLING_RATE = int(os.getenv('SENSOR_SAMPLING_RATE', 10))  # Hz
    
    # 支持的传感器类型
    SUPPORTED_SENSOR_TYPES = [
        'heart_rate', 'temperature', 'blood_pressure', 'spo2',
        'accelerometer', 'gyroscope', 'magnetometer',
        'ambient_temperature', 'humidity', 'light', 'noise',
        'step_counter', 'sleep_quality', 'stress_level'
    ]
    
    # 传感器数据验证范围
    SENSOR_VALUE_RANGES = {
        'heart_rate': {'min': 30, 'max': 220, 'unit': 'bpm'},
        'temperature': {'min': 30.0, 'max': 45.0, 'unit': 'celsius'},
        'blood_pressure': {'min': 50, 'max': 250, 'unit': 'mmHg'},
        'spo2': {'min': 70, 'max': 100, 'unit': '%'},
        'accelerometer': {'min': -20.0, 'max': 20.0, 'unit': 'm/s²'},
        'gyroscope': {'min': -2000.0, 'max': 2000.0, 'unit': 'deg/s'},
        'magnetometer': {'min': -1000.0, 'max': 1000.0, 'unit': 'µT'},
        'ambient_temperature': {'min': -40.0, 'max': 80.0, 'unit': 'celsius'},
        'humidity': {'min': 0.0, 'max': 100.0, 'unit': '%'},
        'light': {'min': 0.0, 'max': 100000.0, 'unit': 'lux'},
        'noise': {'min': 0.0, 'max': 130.0, 'unit': 'dB'},
        'step_counter': {'min': 0, 'max': 100000, 'unit': 'steps'},
        'sleep_quality': {'min': 0.0, 'max': 100.0, 'unit': '%'},
        'stress_level': {'min': 0.0, 'max': 100.0, 'unit': '%'}
    }
    
    # 传感器警报配置
    SENSOR_ALERTS_ENABLED = os.getenv('SENSOR_ALERTS_ENABLED', 'True').lower() == 'true'
    SENSOR_ALERT_THRESHOLDS = {
        'heart_rate': {'critical_low': 50, 'critical_high': 120, 'warning_low': 60, 'warning_high': 100},
        'temperature': {'critical_low': 35.0, 'critical_high': 38.5, 'warning_low': 36.0, 'warning_high': 37.5},
        'blood_pressure': {'critical_low': 70, 'critical_high': 180, 'warning_low': 90, 'warning_high': 140},
        'spo2': {'critical_low': 85, 'critical_high': 100, 'warning_low': 90, 'warning_high': 99}
    }
    
    # 传感器设备配置
    SENSOR_DEVICE_TIMEOUT = int(os.getenv('SENSOR_DEVICE_TIMEOUT', 300))  # 5分钟
    SENSOR_MAX_DEVICES_PER_USER = int(os.getenv('SENSOR_MAX_DEVICES_PER_USER', 10))
    SENSOR_DATA_ENCRYPTION = os.getenv('SENSOR_DATA_ENCRYPTION', 'True').lower() == 'true'
    
    # 传感器数据流配置
    SENSOR_STREAM_ENABLED = os.getenv('SENSOR_STREAM_ENABLED', 'True').lower() == 'true'
    SENSOR_STREAM_MAX_CONNECTIONS = int(os.getenv('SENSOR_STREAM_MAX_CONNECTIONS', 100))
    SENSOR_STREAM_BUFFER_SIZE = int(os.getenv('SENSOR_STREAM_BUFFER_SIZE', 1000))
    SENSOR_STREAM_HEARTBEAT_INTERVAL = int(os.getenv('SENSOR_STREAM_HEARTBEAT_INTERVAL', 30))
    
    # 传感器情感分析配置
    SENSOR_EMOTION_ANALYSIS_ENABLED = os.getenv('SENSOR_EMOTION_ANALYSIS_ENABLED', 'True').lower() == 'true'
    SENSOR_EMOTION_CONFIDENCE_THRESHOLD = float(os.getenv('SENSOR_EMOTION_CONFIDENCE_THRESHOLD', 0.6))
    SENSOR_EMOTION_ANALYSIS_WINDOW = int(os.getenv('SENSOR_EMOTION_ANALYSIS_WINDOW', 60))  # 60秒窗口
    
    # 传感器异常检测配置
    SENSOR_ANOMALY_DETECTION_ENABLED = os.getenv('SENSOR_ANOMALY_DETECTION_ENABLED', 'True').lower() == 'true'
    SENSOR_ANOMALY_DETECTION_ALGORITHM = os.getenv('SENSOR_ANOMALY_DETECTION_ALGORITHM', 'statistical')  # statistical/ml
    SENSOR_ANOMALY_SENSITIVITY = os.getenv('SENSOR_ANOMALY_SENSITIVITY', 'medium')  # low/medium/high
    
    # 老人数据存储配置
    ELDERLY_DATA_STORAGE_TYPE = os.getenv('ELDERLY_DATA_STORAGE_TYPE', 'CSV')  # CSV, MONGODB
    ELDERLY_CSV_PATH = os.getenv('ELDERLY_CSV_PATH', './storage/elderly_data.csv')
    ELDERLY_MONGODB_COLLECTION = os.getenv('ELDERLY_MONGODB_COLLECTION', 'elderly_emotions')
    
    # 老人数据分析配置
    ELDERLY_MIN_AGE = int(os.getenv('ELDERLY_MIN_AGE', 60))  # 最小年龄阈值
    ELDERLY_KEYWORD_THRESHOLD = int(os.getenv('ELDERLY_KEYWORD_THRESHOLD', 2))  # 关键词匹配阈值
    ELDERLY_EXPORT_ENABLED = os.getenv('ELDERLY_EXPORT_ENABLED', 'True').lower() == 'true'
    
    # 内容审核服务API配置
    ALIYUN_CONTENT_SECURITY_ACCESS_KEY_ID = os.getenv('ALIYUN_CONTENT_SECURITY_ACCESS_KEY_ID', '')
    ALIYUN_CONTENT_SECURITY_ACCESS_KEY_SECRET = os.getenv('ALIYUN_CONTENT_SECURITY_ACCESS_KEY_SECRET', '')
    
    # 腾讯内容安全
    TENCENT_CMS_SECRET_ID = os.getenv('TENCENT_CMS_SECRET_ID', '')
    TENCENT_CMS_SECRET_KEY = os.getenv('TENCENT_CMS_SECRET_KEY', '')
    
    # 系统配置
    ENABLE_SEARCH = os.getenv('ENABLE_SEARCH', 'True').lower() == 'true'
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true'
    ENABLE_BATCH_PROCESSING = os.getenv('ENABLE_BATCH_PROCESSING', 'True').lower() == 'true'
    ENABLE_REALTIME = os.getenv('ENABLE_REALTIME', 'True').lower() == 'true'
    ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'True').lower() == 'true'
    ENABLE_MONITORING = os.getenv('ENABLE_MONITORING', 'True').lower() == 'true'
    
    # 批量处理配置
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10))
    MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', 100))
    BATCH_TIMEOUT = int(os.getenv('BATCH_TIMEOUT', 300))  # 5分钟
    
    # 缓存配置
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1小时
    CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 1000))
    
    # 搜索配置
    SEARCH_RESULTS_PER_PAGE = int(os.getenv('SEARCH_RESULTS_PER_PAGE', 20))
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 1000))
    
    # 文件上传配置
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 100 * 1024 * 1024))  # 100MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './storage/uploads/')
    TEMP_FOLDER = os.getenv('TEMP_FOLDER', './storage/temp/')
    
    # 导出配置
    EXPORT_FORMATS = ['json', 'csv', 'xlsx', 'pdf']
    MAX_EXPORT_RECORDS = int(os.getenv('MAX_EXPORT_RECORDS', 10000))
    
    @classmethod
    def get_storage_config(cls):
        """获取存储配置"""
        return {
            'use_local': cls.USE_LOCAL_STORAGE,
            'local_path': cls.LOCAL_STORAGE_PATH,
            'mongodb_uri': cls.MONGODB_URI,
            'database_name': cls.DATABASE_NAME
        }
    
    @classmethod
    def get_api_priority(cls):
        """获取API优先级配置"""
        # 检查是否为占位符值
        def is_valid_key(key):
            if not key:
                return False
            # 排除常见的占位符
            placeholder_patterns = [
                'your_', 'test_', 'placeholder_', 'example_', 'demo_',
                'fake_', 'dummy_', 'sample_', 'mock_'
            ]
            return not any(key.lower().startswith(pattern) for pattern in placeholder_patterns)
        
        return {
            'prioritize_accuracy': cls.PRIORITIZE_ACCURACY,
            'has_openai_key': is_valid_key(cls.OPENAI_API_KEY),
            'has_midjourney_key': is_valid_key(cls.MJ_API_KEY),
            'has_iflytek_speech_key': is_valid_key(cls.IFLYTEK_API_KEY),
            'has_iflytek_image_key': is_valid_key(cls.IFLYTEK_IMAGE_API_KEY),
            'has_iflytek_gender_age_key': is_valid_key(cls.IFLYTEK_GENDER_AGE_API_KEY)
        }
    
    @classmethod
    def get_model_paths(cls):
        """获取所有模型路径配置"""
        return {
            'whisper': cls.WHISPER_MODEL_PATH,
            'wav2vec2': cls.WAV2VEC2_MODEL_PATH,
            'ecapa': cls.ECAPA_MODEL_PATH,
            'stable_diffusion': cls.SD_MODEL_PATH
        }
    
    @classmethod
    def validate_config(cls):
        """验证关键配置项是否存在"""
        required_dirs = [cls.LOCAL_STORAGE_PATH, './logs/', './models/']
        for dir_path in required_dirs:
            os.makedirs(dir_path, exist_ok=True)
        
        print("✅ PGG系统配置验证完成")
        print(f"   - 存储模式: {'本地存储' if cls.USE_LOCAL_STORAGE else 'MongoDB'}")
        print(f"   - CPU模式: {cls.USE_CPU_ONLY}")
        print(f"   - 调试模式: {cls.DEBUG}")
        print(f"   - 准确率优先: {cls.PRIORITIZE_ACCURACY}")
        
        # 显示API可用性
        api_info = cls.get_api_priority()
        print(f"   - API状态:")
        print(f"     * OpenAI: {'✅' if api_info['has_openai_key'] else '❌'}")
        print(f"     * MidJourney: {'✅' if api_info['has_midjourney_key'] else '❌'}")
        print(f"     * 科大讯飞语音: {'✅' if api_info['has_iflytek_speech_key'] else '❌'}")
        print(f"     * 科大讯飞图像: {'✅' if api_info['has_iflytek_image_key'] else '❌'}")
        print(f"     * 科大讯飞性别年龄: {'✅' if api_info['has_iflytek_gender_age_key'] else '❌'}")
    
    @classmethod
    def get_search_config(cls):
        """获取搜索配置"""
        return {
            'enabled': cls.ENABLE_SEARCH,
            'elasticsearch_url': cls.ELASTICSEARCH_URL,
            'elasticsearch_api_key': cls.ELASTICSEARCH_API_KEY,
            'algolia_app_id': cls.ALGOLIA_APP_ID,
            'algolia_api_key': cls.ALGOLIA_API_KEY,
            'results_per_page': cls.SEARCH_RESULTS_PER_PAGE,
            'max_results': cls.MAX_SEARCH_RESULTS
        }
    
    @classmethod
    def get_analytics_config(cls):
        """获取分析配置"""
        return {
            'enabled': cls.ENABLE_ANALYTICS,
            'google_analytics_api_key': cls.GOOGLE_ANALYTICS_API_KEY,
            'baidu_tongji_api_key': cls.BAIDU_TONGJI_API_KEY,
            'baidu_tongji_site_id': cls.BAIDU_TONGJI_SITE_ID
        }
    
    @classmethod
    def get_file_storage_config(cls):
        """获取文件存储配置"""
        return {
            'aliyun_oss_access_key_id': cls.ALIYUN_OSS_ACCESS_KEY_ID,
            'aliyun_oss_access_key_secret': cls.ALIYUN_OSS_ACCESS_KEY_SECRET,
            'aliyun_oss_bucket_name': cls.ALIYUN_OSS_BUCKET_NAME,
            'tencent_cos_secret_id': cls.TENCENT_COS_SECRET_ID,
            'tencent_cos_secret_key': cls.TENCENT_COS_SECRET_KEY,
            'aws_access_key_id': cls.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': cls.AWS_SECRET_ACCESS_KEY,
            'upload_folder': cls.UPLOAD_FOLDER,
            'temp_folder': cls.TEMP_FOLDER,
            'max_file_size': cls.MAX_FILE_SIZE
        }
    
    @classmethod
    def get_cache_config(cls):
        """获取缓存配置"""
        return {
            'enabled': cls.ENABLE_CACHE,
            'redis_url': cls.REDIS_URL,
            'redis_password': cls.REDIS_PASSWORD,
            'cache_ttl': cls.CACHE_TTL,
            'max_size': cls.CACHE_MAX_SIZE
        }
    
    @classmethod
    def get_monitoring_config(cls):
        """获取监控配置"""
        return {
            'enabled': cls.ENABLE_MONITORING,
            'prometheus_url': cls.PROMETHEUS_URL,
            'prometheus_api_key': cls.PROMETHEUS_API_KEY,
            'grafana_url': cls.GRAFANA_URL,
            'grafana_api_key': cls.GRAFANA_API_KEY,
            'datadog_api_key': cls.DATADOG_API_KEY,
            'datadog_app_key': cls.DATADOG_APP_KEY
        }
    
    @classmethod
    def get_batch_config(cls):
        """获取批量处理配置"""
        return {
            'enabled': cls.ENABLE_BATCH_PROCESSING,
            'batch_size': cls.BATCH_SIZE,
            'max_batch_size': cls.MAX_BATCH_SIZE,
            'batch_timeout': cls.BATCH_TIMEOUT
        }
    
    @classmethod
    def get_realtime_config(cls):
        """获取实时通信配置"""
        return {
            'enabled': cls.ENABLE_REALTIME,
            'websocket_secret_key': cls.WEBSOCKET_SECRET_KEY,
            'socketio_api_key': cls.SOCKETIO_API_KEY,
            'firebase_api_key': cls.FIREBASE_API_KEY,
            'firebase_project_id': cls.FIREBASE_PROJECT_ID,
            'jpush_app_key': cls.JPUSH_APP_KEY,
            'jpush_app_secret': cls.JPUSH_APP_SECRET
        }

# 创建全局配置实例
config = Config()

# 系统启动时验证配置
if __name__ == "__main__":
    config.validate_config() 