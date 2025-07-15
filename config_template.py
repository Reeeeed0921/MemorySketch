# ========== API配置文件模板 ==========
# 复制此文件为 config_local.py 并填入您的真实API配置

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class APIConfig:
    """扩展API配置"""
    
    # ========== 基础配置 ==========
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # ========== 1. 搜索服务API配置 ==========
    ENABLE_SEARCH = os.getenv('ENABLE_SEARCH', 'True').lower() == 'true'
    SEARCH_RESULTS_PER_PAGE = int(os.getenv('SEARCH_RESULTS_PER_PAGE', 20))
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 1000))
    
    # Elasticsearch配置
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
    ELASTICSEARCH_API_KEY = os.getenv('ELASTICSEARCH_API_KEY', '')
    ELASTICSEARCH_API_SECRET = os.getenv('ELASTICSEARCH_API_SECRET', '')
    
    # Algolia配置
    ALGOLIA_APP_ID = os.getenv('ALGOLIA_APP_ID', '')
    ALGOLIA_API_KEY = os.getenv('ALGOLIA_API_KEY', '')
    ALGOLIA_API_SECRET = os.getenv('ALGOLIA_API_SECRET', '')
    
    # ========== 2. 数据分析服务API配置 ==========
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true'
    ANALYTICS_CACHE_TTL = int(os.getenv('ANALYTICS_CACHE_TTL', 3600))
    
    # Google Analytics配置
    GOOGLE_ANALYTICS_API_KEY = os.getenv('GOOGLE_ANALYTICS_API_KEY', '')
    GOOGLE_ANALYTICS_API_SECRET = os.getenv('GOOGLE_ANALYTICS_API_SECRET', '')
    GOOGLE_ANALYTICS_VIEW_ID = os.getenv('GOOGLE_ANALYTICS_VIEW_ID', '')
    
    # 百度统计配置
    BAIDU_TONGJI_API_KEY = os.getenv('BAIDU_TONGJI_API_KEY', '')
    BAIDU_TONGJI_API_SECRET = os.getenv('BAIDU_TONGJI_API_SECRET', '')
    BAIDU_TONGJI_SITE_ID = os.getenv('BAIDU_TONGJI_SITE_ID', '')
    
    # ========== 3. 文件存储服务API配置 ==========
    ENABLE_FILE_STORAGE = os.getenv('ENABLE_FILE_STORAGE', 'True').lower() == 'true'
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 100 * 1024 * 1024))  # 100MB
    
    # 阿里云OSS配置
    ALIYUN_OSS_ACCESS_KEY_ID = os.getenv('ALIYUN_OSS_ACCESS_KEY_ID', '')
    ALIYUN_OSS_ACCESS_KEY_SECRET = os.getenv('ALIYUN_OSS_ACCESS_KEY_SECRET', '')
    ALIYUN_OSS_BUCKET_NAME = os.getenv('ALIYUN_OSS_BUCKET_NAME', '')
    ALIYUN_OSS_ENDPOINT = os.getenv('ALIYUN_OSS_ENDPOINT', '')
    
    # 腾讯云COS配置
    TENCENT_COS_SECRET_ID = os.getenv('TENCENT_COS_SECRET_ID', '')
    TENCENT_COS_SECRET_KEY = os.getenv('TENCENT_COS_SECRET_KEY', '')
    TENCENT_COS_BUCKET_NAME = os.getenv('TENCENT_COS_BUCKET_NAME', '')
    TENCENT_COS_REGION = os.getenv('TENCENT_COS_REGION', '')
    
    # AWS S3配置
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME', '')
    AWS_S3_REGION = os.getenv('AWS_S3_REGION', '')
    
    # ========== 4. 实时通信服务API配置 ==========
    ENABLE_REALTIME = os.getenv('ENABLE_REALTIME', 'True').lower() == 'true'
    WEBSOCKET_SECRET_KEY = os.getenv('WEBSOCKET_SECRET_KEY', 'ws-secret-key-2024')
    SOCKETIO_API_KEY = os.getenv('SOCKETIO_API_KEY', '')
    
    # Firebase推送配置
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', '')
    FIREBASE_API_SECRET = os.getenv('FIREBASE_API_SECRET', '')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
    
    # 极光推送配置
    JPUSH_APP_KEY = os.getenv('JPUSH_APP_KEY', '')
    JPUSH_APP_SECRET = os.getenv('JPUSH_APP_SECRET', '')
    JPUSH_MASTER_SECRET = os.getenv('JPUSH_MASTER_SECRET', '')
    
    # ========== 5. 监控服务API配置 ==========
    ENABLE_MONITORING = os.getenv('ENABLE_MONITORING', 'True').lower() == 'true'
    MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', 60))  # 监控间隔（秒）
    
    # Prometheus配置
    PROMETHEUS_URL = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
    PROMETHEUS_API_KEY = os.getenv('PROMETHEUS_API_KEY', '')
    
    # Grafana配置
    GRAFANA_URL = os.getenv('GRAFANA_URL', 'http://localhost:3000')
    GRAFANA_API_KEY = os.getenv('GRAFANA_API_KEY', '')
    GRAFANA_API_SECRET = os.getenv('GRAFANA_API_SECRET', '')
    
    # DataDog配置
    DATADOG_API_KEY = os.getenv('DATADOG_API_KEY', '')
    DATADOG_APP_KEY = os.getenv('DATADOG_APP_KEY', '')
    
    # ========== 6. 缓存服务API配置 ==========
    ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'True').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 默认缓存过期时间（秒）
    CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 1000))  # 最大缓存条目数
    
    # Redis配置
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_API_KEY = os.getenv('REDIS_API_KEY', '')
    
    # ========== 7. 日志服务API配置 ==========
    ENABLE_LOGGING = os.getenv('ENABLE_LOGGING', 'True').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # LogStash配置
    LOGSTASH_URL = os.getenv('LOGSTASH_URL', 'http://localhost:5044')
    LOGSTASH_API_KEY = os.getenv('LOGSTASH_API_KEY', '')
    
    # 阿里云日志服务配置
    ALIYUN_LOG_ACCESS_KEY_ID = os.getenv('ALIYUN_LOG_ACCESS_KEY_ID', '')
    ALIYUN_LOG_ACCESS_KEY_SECRET = os.getenv('ALIYUN_LOG_ACCESS_KEY_SECRET', '')
    ALIYUN_LOG_PROJECT = os.getenv('ALIYUN_LOG_PROJECT', '')
    ALIYUN_LOG_STORE = os.getenv('ALIYUN_LOG_STORE', '')
    
    # ========== 8. 翻译服务API配置 ==========
    ENABLE_TRANSLATION = os.getenv('ENABLE_TRANSLATION', 'True').lower() == 'true'
    DEFAULT_TRANSLATE_LANGUAGE = os.getenv('DEFAULT_TRANSLATE_LANGUAGE', 'zh-CN')
    
    # Google翻译配置
    GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY', '')
    GOOGLE_TRANSLATE_API_SECRET = os.getenv('GOOGLE_TRANSLATE_API_SECRET', '')
    
    # 百度翻译配置
    BAIDU_TRANSLATE_APP_ID = os.getenv('BAIDU_TRANSLATE_APP_ID', '')
    BAIDU_TRANSLATE_API_KEY = os.getenv('BAIDU_TRANSLATE_API_KEY', '')
    BAIDU_TRANSLATE_API_SECRET = os.getenv('BAIDU_TRANSLATE_API_SECRET', '')
    
    # 腾讯翻译配置
    TENCENT_TRANSLATE_SECRET_ID = os.getenv('TENCENT_TRANSLATE_SECRET_ID', '')
    TENCENT_TRANSLATE_SECRET_KEY = os.getenv('TENCENT_TRANSLATE_SECRET_KEY', '')
    
    # ========== 9. 内容审核服务API配置 ==========
    ENABLE_CONTENT_MODERATION = os.getenv('ENABLE_CONTENT_MODERATION', 'True').lower() == 'true'
    MODERATION_THRESHOLD = float(os.getenv('MODERATION_THRESHOLD', 0.8))  # 审核阈值
    
    # 阿里云内容安全配置
    ALIYUN_CONTENT_SECURITY_ACCESS_KEY_ID = os.getenv('ALIYUN_CONTENT_SECURITY_ACCESS_KEY_ID', '')
    ALIYUN_CONTENT_SECURITY_ACCESS_KEY_SECRET = os.getenv('ALIYUN_CONTENT_SECURITY_ACCESS_KEY_SECRET', '')
    
    # 腾讯内容安全配置
    TENCENT_CMS_SECRET_ID = os.getenv('TENCENT_CMS_SECRET_ID', '')
    TENCENT_CMS_SECRET_KEY = os.getenv('TENCENT_CMS_SECRET_KEY', '')
    
    # ========== 10. 邮件服务API配置 ==========
    ENABLE_EMAIL = os.getenv('ENABLE_EMAIL', 'True').lower() == 'true'
    EMAIL_RATE_LIMIT = int(os.getenv('EMAIL_RATE_LIMIT', 100))  # 每小时邮件发送限制
    
    # SendGrid配置
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
    SENDGRID_API_SECRET = os.getenv('SENDGRID_API_SECRET', '')
    
    # 阿里云邮件推送配置
    ALIYUN_EMAIL_ACCESS_KEY_ID = os.getenv('ALIYUN_EMAIL_ACCESS_KEY_ID', '')
    ALIYUN_EMAIL_ACCESS_KEY_SECRET = os.getenv('ALIYUN_EMAIL_ACCESS_KEY_SECRET', '')
    
    # ========== 批量处理配置 ==========
    ENABLE_BATCH_PROCESSING = os.getenv('ENABLE_BATCH_PROCESSING', 'True').lower() == 'true'
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10))
    MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', 100))
    BATCH_TIMEOUT = int(os.getenv('BATCH_TIMEOUT', 300))  # 批量处理超时时间（秒）
    
    # ========== 音频处理配置 ==========
    AUDIO_SAMPLE_RATE = int(os.getenv('AUDIO_SAMPLE_RATE', 16000))
    AUDIO_CHANNELS = int(os.getenv('AUDIO_CHANNELS', 1))
    AUDIO_FORMAT = os.getenv('AUDIO_FORMAT', 'wav')
    
    # ========== 配置验证方法 ==========
    
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
            'google_analytics_view_id': cls.GOOGLE_ANALYTICS_VIEW_ID,
            'baidu_tongji_api_key': cls.BAIDU_TONGJI_API_KEY,
            'baidu_tongji_site_id': cls.BAIDU_TONGJI_SITE_ID,
            'cache_ttl': cls.ANALYTICS_CACHE_TTL
        }
    
    @classmethod
    def get_file_storage_config(cls):
        """获取文件存储配置"""
        return {
            'enabled': cls.ENABLE_FILE_STORAGE,
            'max_file_size': cls.MAX_FILE_SIZE,
            'aliyun_oss_bucket': cls.ALIYUN_OSS_BUCKET_NAME,
            'tencent_cos_bucket': cls.TENCENT_COS_BUCKET_NAME,
            'aws_s3_bucket': cls.AWS_S3_BUCKET_NAME
        }
    
    @classmethod
    def get_realtime_config(cls):
        """获取实时通信配置"""
        return {
            'enabled': cls.ENABLE_REALTIME,
            'websocket_secret_key': cls.WEBSOCKET_SECRET_KEY,
            'firebase_project_id': cls.FIREBASE_PROJECT_ID,
            'jpush_app_key': cls.JPUSH_APP_KEY
        }
    
    @classmethod
    def get_monitoring_config(cls):
        """获取监控配置"""
        return {
            'enabled': cls.ENABLE_MONITORING,
            'interval': cls.MONITORING_INTERVAL,
            'prometheus_url': cls.PROMETHEUS_URL,
            'grafana_url': cls.GRAFANA_URL,
            'datadog_api_key': cls.DATADOG_API_KEY
        }
    
    @classmethod
    def get_cache_config(cls):
        """获取缓存配置"""
        return {
            'enabled': cls.ENABLE_CACHE,
            'cache_ttl': cls.CACHE_TTL,
            'max_size': cls.CACHE_MAX_SIZE,
            'redis_url': cls.REDIS_URL
        }
    
    @classmethod
    def validate_api_configs(cls):
        """验证API配置"""
        validation_results = {}
        
        # 验证搜索配置
        if cls.ENABLE_SEARCH:
            validation_results['search'] = {
                'elasticsearch_configured': bool(cls.ELASTICSEARCH_API_KEY),
                'algolia_configured': bool(cls.ALGOLIA_API_KEY)
            }
        
        # 验证分析配置
        if cls.ENABLE_ANALYTICS:
            validation_results['analytics'] = {
                'google_analytics_configured': bool(cls.GOOGLE_ANALYTICS_API_KEY),
                'baidu_tongji_configured': bool(cls.BAIDU_TONGJI_API_KEY)
            }
        
        # 验证文件存储配置
        if cls.ENABLE_FILE_STORAGE:
            validation_results['file_storage'] = {
                'aliyun_oss_configured': bool(cls.ALIYUN_OSS_ACCESS_KEY_ID),
                'tencent_cos_configured': bool(cls.TENCENT_COS_SECRET_ID),
                'aws_s3_configured': bool(cls.AWS_ACCESS_KEY_ID)
            }
        
        # 验证实时通信配置
        if cls.ENABLE_REALTIME:
            validation_results['realtime'] = {
                'firebase_configured': bool(cls.FIREBASE_API_KEY),
                'jpush_configured': bool(cls.JPUSH_APP_KEY)
            }
        
        # 验证监控配置
        if cls.ENABLE_MONITORING:
            validation_results['monitoring'] = {
                'prometheus_configured': bool(cls.PROMETHEUS_URL),
                'grafana_configured': bool(cls.GRAFANA_API_KEY),
                'datadog_configured': bool(cls.DATADOG_API_KEY)
            }
        
        # 验证缓存配置
        if cls.ENABLE_CACHE:
            validation_results['cache'] = {
                'redis_configured': bool(cls.REDIS_URL)
            }
        
        return validation_results
    
    @classmethod
    def get_api_service_status(cls):
        """获取API服务状态"""
        return {
            'search_enabled': cls.ENABLE_SEARCH,
            'analytics_enabled': cls.ENABLE_ANALYTICS,
            'file_storage_enabled': cls.ENABLE_FILE_STORAGE,
            'realtime_enabled': cls.ENABLE_REALTIME,
            'monitoring_enabled': cls.ENABLE_MONITORING,
            'cache_enabled': cls.ENABLE_CACHE,
            'translation_enabled': cls.ENABLE_TRANSLATION,
            'content_moderation_enabled': cls.ENABLE_CONTENT_MODERATION,
            'email_enabled': cls.ENABLE_EMAIL,
            'batch_processing_enabled': cls.ENABLE_BATCH_PROCESSING
        }


# ========== 使用示例 ==========

if __name__ == "__main__":
    # 验证配置
    config = APIConfig()
    
    print("=== API配置验证 ===")
    validation_results = config.validate_api_configs()
    
    for service, status in validation_results.items():
        print(f"\n{service.upper()}:")
        for key, value in status.items():
            status_text = "✅ 已配置" if value else "❌ 未配置"
            print(f"  {key}: {status_text}")
    
    print("\n=== 服务状态 ===")
    service_status = config.get_api_service_status()
    for service, enabled in service_status.items():
        status_text = "✅ 启用" if enabled else "❌ 禁用"
        print(f"{service}: {status_text}") 