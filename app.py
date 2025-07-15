# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - Flask主应用
提供API接口用于生成和查询用户回忆数据
"""

from flask import Flask, request, jsonify, g, render_template, send_file
from flask_cors import CORS
import logging
import json
import traceback
from datetime import datetime
import os
import platform
import psutil

# 导入配置和工具模块
from config import config
from utils.database import DatabaseManager
from services.emotion_analysis import EmotionAnalyzer
from services.image_generation import ImageGenerator
from services.speech_to_text import SpeechToTextService
from models import MemoryRecord, get_emotion_description
from utils.elderly_storage import elderly_data_manager

# 导入传感器管理模块
from services.sensor_manager import SensorManager, SensorData, SensorDevice

# 导入CSV管理模块
from services.csv_manager import CSVManager

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(config)

# 启用CORS支持
CORS(app)

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE_PATH, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 初始化服务组件
db_manager = DatabaseManager()
emotion_analyzer = EmotionAnalyzer()
image_generator = ImageGenerator()
speech_service = SpeechToTextService()

# 初始化传感器管理器
sensor_manager = SensorManager()

# 初始化CSV管理器
csv_manager = CSVManager()

@app.before_request
def before_request():
    """请求前处理"""
    g.request_start_time = datetime.now()
    logger.info(f"收到请求: {request.method} {request.path}")

@app.after_request
def after_request(response):
    """请求后处理"""
    if hasattr(g, 'request_start_time'):
        duration = (datetime.now() - g.request_start_time).total_seconds()
        logger.info(f"请求完成: {request.method} {request.path} - 状态码: {response.status_code} - 耗时: {duration:.2f}秒")
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    """全局异常处理"""
    logger.error(f"未处理的异常: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        'success': False,
        'error': '服务器内部错误',
        'message': str(e) if config.DEBUG else '请联系管理员'
    }), 500

@app.route('/', methods=['GET'])
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'message': 'PGG情感记忆生成系统运行正常',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/generate', methods=['POST'])
def generate_memory():
    """
    生成回忆接口
    接收用户输入，调用情感分析和图像生成服务，返回生成的回忆数据
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供有效的JSON数据'
            }), 400
        
        # 验证必要字段
        user_input = data.get('text', '').strip()
        if not user_input:
            return jsonify({
                'success': False,
                'error': '用户输入为空',
                'message': '请提供要分析的文本内容'
            }), 400
        
        # 可选参数
        user_id = data.get('user_id', 'anonymous')
        audio_file = data.get('audio_file')  # 未来可能支持音频输入
        
        logger.info(f"开始处理用户输入: {user_input[:50]}...")
        
        # 1. 情感分析
        logger.info("开始情感分析...")
        emotion_result = emotion_analyzer.analyze_text(user_input)
        
        # 2. 生成回忆文本（基于用户输入和情感分析结果）
        logger.info("生成回忆文本...")
        memory_text = emotion_analyzer.generate_memory_text(user_input, emotion_result)
        
        # 3. 生成图像
        logger.info("开始图像生成...")
        image_url = image_generator.generate_image(memory_text, emotion_result)
        
        # 4. 创建回忆记录
        memory_record = MemoryRecord(
            user_id=user_id,
            user_input=user_input,
            memory_text=memory_text,
            image_url=image_url,
            emotion_result=emotion_result,
            created_at=datetime.now()
        )
        
        # 5. 保存到数据库
        logger.info("保存回忆记录到数据库...")
        record_id = db_manager.save_memory(memory_record)
        
        # 6. 返回结果
        response_data = {
            'success': True,
            'id': record_id,
            'text': user_input,
            'memory_text': memory_text,
            'image_url': image_url,
            'emotion': emotion_result,
            'user_id': user_id,
            'created_at': memory_record.created_at.isoformat(),
            'message': '回忆生成成功'
        }
        
        logger.info(f"回忆生成完成，记录ID: {record_id}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"生成回忆时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': '生成回忆失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/history', methods=['GET'])
def get_history():
    """
    获取历史回忆接口
    返回用户的历史回忆数据
    """
    try:
        # 获取查询参数
        user_id = request.args.get('user_id', 'anonymous')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        emotion_filter = request.args.get('emotion')  # 可选的情感过滤
        
        # 验证参数
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        logger.info(f"获取历史回忆: user_id={user_id}, page={page}, per_page={per_page}")
        
        # 从数据库获取历史记录
        history_data = db_manager.get_memories(
            user_id=user_id,
            page=page,
            per_page=per_page,
            emotion_filter=emotion_filter
        )
        
        # 格式化返回数据
        memories = []
        for memory in history_data['memories']:
            memories.append({
                'id': memory.id,
                'text': memory.user_input,
                'user_id': memory.user_id,
                'memory_text': memory.memory_text,
                'image_url': memory.image_url,
                'emotion': memory.emotion_result,
                'created_at': memory.created_at.isoformat()
            })
        
        response_data = {
            'success': True,
            'memories': memories,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': history_data['total'],
                'pages': history_data['pages']
            },
            'message': f'成功获取{len(memories)}条回忆记录'
        }
        
        logger.info(f"历史回忆查询完成，返回{len(memories)}条记录")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"获取历史回忆时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': '获取历史回忆失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/memory/<memory_id>', methods=['GET'])
def get_memory_detail(memory_id):
    """
    获取单个回忆详情
    """
    try:
        logger.info(f"获取回忆详情: {memory_id}")
        
        # 从数据库获取回忆记录
        memory = db_manager.get_memory_by_id(memory_id)
        
        if not memory:
            return jsonify({
                'success': False,
                'error': '回忆记录不存在',
                'message': f'未找到ID为{memory_id}的回忆记录'
            }), 404
        
        response_data = {
            'success': True,
            'data': {
                'id': memory.id,
                'user_id': memory.user_id,
                'user_input': memory.user_input,
                'memory_text': memory.memory_text,
                'image_url': memory.image_url,
                'emotion': memory.emotion_result,
                'created_at': memory.created_at.isoformat()
            },
            'message': '成功获取回忆详情'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"获取回忆详情时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': '获取回忆详情失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/stats', methods=['GET'])
def get_statistics():
    """
    获取用户统计信息
    """
    try:
        user_id = request.args.get('user_id', 'anonymous')
        
        logger.info(f"获取用户统计信息: {user_id}")
        
        # 从数据库获取统计数据
        stats = db_manager.get_user_statistics(user_id)
        
        response_data = {
            'success': True,
            'total_memories': stats.get('total_memories', 0),
            'total_users': stats.get('total_users', 0),
            'avg_emotion_score': stats.get('avg_emotion_score', 0.0),
            'api_calls': stats.get('api_calls', 0),
            'message': '成功获取统计信息'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"获取统计信息时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': '获取统计信息失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    """
    语音转文本接口
    支持音频文件上传和语音识别
    """
    try:
        # 检查文件是否存在
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传音频文件',
                'message': '请上传音频文件'
            }), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空',
                'message': '请选择有效的音频文件'
            }), 400
        
        # 获取可选参数
        language = request.form.get('language', 'zh-CN')
        include_gender_age = request.form.get('include_gender_age', 'false').lower() == 'true'
        
        # 保存临时文件
        temp_filename = f"temp_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        temp_filepath = os.path.join(config.UPLOAD_FOLDER, temp_filename)
        
        # 确保上传目录存在
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        
        # 保存上传的文件
        audio_file.save(temp_filepath)
        
        logger.info(f"开始语音转文本处理: {temp_filepath}")
        
        # 调用语音转文本服务
        result = speech_service.transcribe_audio(temp_filepath, language, include_gender_age)
        
        # 清理临时文件
        try:
            os.remove(temp_filepath)
        except:
            pass
        
            response_data = {
                'success': True,
            'data': {
                'text': result['text'],
                'confidence': result['confidence'],
                'language': result['language'],
                'duration': result.get('duration', 0),
                'segments': result.get('segments', [])
            },
                'message': '语音转文本成功'
            }
        
        # 如果包含性别年龄识别结果
        if include_gender_age and 'gender_age' in result:
            response_data['data']['gender_age'] = result['gender_age']
        
        logger.info(f"语音转文本完成: {result['text'][:50]}...")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"语音转文本时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        
        # 清理临时文件
        try:
            if 'temp_filepath' in locals():
                os.remove(temp_filepath)
        except:
            pass
        
        return jsonify({
                'success': False,
                'error': '语音转文本失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 情绪识别API接口
@app.route('/emotion/analyze-text', methods=['POST'])
def analyze_text_emotion():
    """
    文本情绪识别API
    分析输入文本的情绪状态
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供有效的JSON数据'
            }), 400
        
        # 验证文本输入
        text = data.get('text', '').strip()
        if not text:
            return jsonify({
                'success': False,
                'error': '文本为空',
                'message': '请提供要分析的文本内容'
            }), 400
        
        # 可选参数
        user_id = data.get('user_id', 'anonymous')
        include_suggestions = data.get('include_suggestions', True)
        
        logger.info(f"开始文本情绪分析: {text[:50]}...")
        
        # 执行情绪分析
        emotion_result = emotion_analyzer.analyze_text(text)
        
        # 构建响应数据
        response_data = {
            'success': True,
            'data': {
                'text': text,
                'emotion': {
                    'primary_emotion': emotion_result['primary_emotion'],
                    'confidence': emotion_result['confidence'],
                    'emotion_scores': emotion_result['emotion_scores'],
                    'dimensions': {
                        'valence': emotion_result['valence'],
                        'arousal': emotion_result['arousal'],
                        'dominance': emotion_result['dominance']
                    },
                    'analysis_model': emotion_result['analysis_model'],
                    'description': get_emotion_description(emotion_result['primary_emotion'])
                }
            },
            'message': '文本情绪分析成功'
        }
        
        # 添加建议（如果需要）
        if include_suggestions:
            suggestions = emotion_analyzer.get_emotion_suggestions(emotion_result)
            response_data['data']['suggestions'] = suggestions
        
        logger.info(f"文本情绪分析完成: {emotion_result['primary_emotion']} (置信度: {emotion_result['confidence']:.2f})")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"文本情绪分析时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': '文本情绪分析失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/emotion/analyze-audio', methods=['POST'])
def analyze_audio_emotion():
    """
    音频情绪识别API
    分析音频文件的情绪状态
    """
    try:
        # 检查文件是否存在
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传音频文件',
                'message': '请上传音频文件'
            }), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空',
                'message': '请选择有效的音频文件'
            }), 400
        
        # 获取可选参数
        user_id = request.form.get('user_id', 'anonymous')
        include_suggestions = request.form.get('include_suggestions', 'true').lower() == 'true'
        
        # 保存临时文件
        temp_filename = f"temp_emotion_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        temp_filepath = os.path.join(config.UPLOAD_FOLDER, temp_filename)
        
        # 确保上传目录存在
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        
        # 保存上传的文件
        audio_file.save(temp_filepath)
        
        logger.info(f"开始音频情绪分析: {temp_filepath}")
        
        # 执行情绪分析
        emotion_result = emotion_analyzer.analyze_audio(temp_filepath)
        
        # 清理临时文件
        try:
            os.remove(temp_filepath)
        except:
            pass
        
        # 构建响应数据
        response_data = {
            'success': True,
            'data': {
                'filename': audio_file.filename,
                'emotion': {
                    'primary_emotion': emotion_result['primary_emotion'],
                    'confidence': emotion_result['confidence'],
                    'emotion_scores': emotion_result['emotion_scores'],
                    'dimensions': {
                        'valence': emotion_result['valence'],
                        'arousal': emotion_result['arousal'],
                        'dominance': emotion_result['dominance']
                    },
                    'analysis_model': emotion_result['analysis_model'],
                    'description': get_emotion_description(emotion_result['primary_emotion'])
                }
            },
            'message': '音频情绪分析成功'
        }
        
        # 添加建议（如果需要）
        if include_suggestions:
            suggestions = emotion_analyzer.get_emotion_suggestions(emotion_result)
            response_data['data']['suggestions'] = suggestions
        
        logger.info(f"音频情绪分析完成: {emotion_result['primary_emotion']} (置信度: {emotion_result['confidence']:.2f})")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"音频情绪分析时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        
        # 清理临时文件
        try:
            if 'temp_filepath' in locals():
                os.remove(temp_filepath)
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': '音频情绪分析失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/emotion/batch-analyze', methods=['POST'])
def batch_analyze_emotions():
    """
    批量情绪分析API
    一次性分析多个文本的情绪状态
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供有效的JSON数据'
            }), 400
        
        # 验证文本列表
        texts = data.get('texts', [])
        if not texts or not isinstance(texts, list):
            return jsonify({
                'success': False,
                'error': '文本列表为空或格式错误',
                'message': '请提供有效的文本列表'
            }), 400
        
        # 限制批量处理数量
        max_batch_size = 50
        if len(texts) > max_batch_size:
            return jsonify({
                'success': False,
                'error': f'批量处理数量超限',
                'message': f'最多支持{max_batch_size}个文本同时分析'
            }), 400
        
        # 可选参数
        user_id = data.get('user_id', 'anonymous')
        include_suggestions = data.get('include_suggestions', False)
        
        logger.info(f"开始批量文本情绪分析: {len(texts)}个文本")
        
        # 执行批量分析
        results = emotion_analyzer.batch_analyze_texts(texts)
        
        # 构建响应数据
        analyzed_results = []
        for i, (text, emotion_result) in enumerate(zip(texts, results)):
            result_data = {
                'index': i,
                'text': text,
                'emotion': {
                    'primary_emotion': emotion_result['primary_emotion'],
                    'confidence': emotion_result['confidence'],
                    'emotion_scores': emotion_result['emotion_scores'],
                    'dimensions': {
                        'valence': emotion_result['valence'],
                        'arousal': emotion_result['arousal'],
                        'dominance': emotion_result['dominance']
                    },
                    'analysis_model': emotion_result['analysis_model'],
                    'description': get_emotion_description(emotion_result['primary_emotion'])
                }
            }
            
            # 添加建议（如果需要）
            if include_suggestions:
                suggestions = emotion_analyzer.get_emotion_suggestions(emotion_result)
                result_data['suggestions'] = suggestions
            
            analyzed_results.append(result_data)
        
        # 统计信息
        emotion_counts = {}
        for result in results:
            emotion = result['primary_emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        response_data = {
            'success': True,
            'data': {
                'results': analyzed_results,
                'summary': {
                    'total_texts': len(texts),
                    'emotion_distribution': emotion_counts,
                    'most_common_emotion': max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
                }
            },
            'message': f'批量情绪分析成功，共分析{len(texts)}个文本'
        }
        
        logger.info(f"批量文本情绪分析完成: {len(texts)}个文本")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"批量情绪分析时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': '批量情绪分析失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/emotion/status', methods=['GET'])
def get_emotion_service_status():
    """
    获取情绪识别服务状态
    """
    try:
        # 检查情绪分析器状态
        emotion_status = {
            'service_available': True,  # 情绪分析始终可用（有保底方案）
            'models_loaded': emotion_analyzer.models_loaded,
            'supported_emotions': list(emotion_analyzer.emotion_keywords.keys()),
            'supported_languages': ['zh-CN', 'en-US'],  # 支持的语言
            'analysis_methods': [
                'OpenAI API' if config.OPENAI_API_KEY else None,
                'Local AI Model' if emotion_analyzer.models_loaded else None,
                'Rule-based Analysis'  # 始终可用
            ]
        }
        
        # 过滤空值
        emotion_status['analysis_methods'] = [method for method in emotion_status['analysis_methods'] if method]
        
        # API配置状态
        api_statuses = {
            'openai': bool(config.OPENAI_API_KEY and not config.OPENAI_API_KEY.startswith('your_')),
            'deepseek': bool(config.DEEPSEEK_API_KEY and not config.DEEPSEEK_API_KEY.startswith('your_')),
            'iflytek_speech': bool(config.IFLYTEK_API_KEY and not config.IFLYTEK_API_KEY.startswith('your_')),
            'iflytek_image': bool(config.IFLYTEK_IMAGE_API_KEY and not config.IFLYTEK_IMAGE_API_KEY.startswith('your_')),
            'iflytek_gender_age': bool(config.IFLYTEK_GENDER_AGE_API_KEY and not config.IFLYTEK_GENDER_AGE_API_KEY.startswith('your_')),
            'midjourney': bool(getattr(config, 'MJ_API_KEY', '') and not getattr(config, 'MJ_API_KEY', '').startswith('your_')),
            'azure_speech': bool(getattr(config, 'AZURE_SPEECH_KEY', '') and not getattr(config, 'AZURE_SPEECH_KEY', '').startswith('your_')),
            'google_speech': bool(getattr(config, 'GOOGLE_SPEECH_KEY', '') and not getattr(config, 'GOOGLE_SPEECH_KEY', '').startswith('your_')),
            'baidu_speech': bool(getattr(config, 'BAIDU_SPEECH_API_KEY', '') and not getattr(config, 'BAIDU_SPEECH_API_KEY', '').startswith('your_')),
            'tencent_speech': bool(getattr(config, 'TENCENT_SPEECH_SECRET_ID', '') and not getattr(config, 'TENCENT_SPEECH_SECRET_ID', '').startswith('your_')),
            'alibaba_speech': bool(getattr(config, 'ALIBABA_SPEECH_ACCESS_KEY', '') and not getattr(config, 'ALIBABA_SPEECH_ACCESS_KEY', '').startswith('your_'))
        }
        
        response_data = {
            'success': True,
            'data': {
                'service_status': emotion_status,
                'api_availability': api_statuses,
                'endpoints': {
                    'text_analysis': '/emotion/analyze-text',
                    'audio_analysis': '/emotion/analyze-audio',
                    'batch_analysis': '/emotion/batch-analyze',
                    'status': '/emotion/status'
                }
            },
            'message': '成功获取情绪识别服务状态'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"获取情绪识别服务状态时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': '获取情绪识别服务状态失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/speech-to-text/status', methods=['GET'])
def get_speech_service_status():
    """
    获取语音转文本服务状态
    """
    try:
        status = speech_service.get_service_status()
        
        response_data = {
            'success': True,
            'available': status.get('available', False),
            'data': {
                'api_available': status.get('api_available', {}),
                'models_loaded': status.get('models_loaded', False),
                'supported_languages': status.get('supported_languages', []),
                'supported_formats': status.get('supported_formats', []),
                'priority_order': status.get('priority_order', []),
                'has_api': status.get('has_api', False),
                'has_models': status.get('has_models', False)
            },
            'message': '成功获取服务状态'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"获取语音服务状态时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': '获取服务状态失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# ========== 扩展API接口 ==========

# 1. 回忆管理接口
@app.route('/memory/<memory_id>', methods=['DELETE'])
def delete_memory(memory_id):
    """删除回忆记录"""
    try:
        logger.info(f"删除回忆记录: {memory_id}")
        
        # 验证回忆记录是否存在
        memory = db_manager.get_memory_by_id(memory_id)
        if not memory:
            return jsonify({
                'success': False,
                'error': '回忆记录不存在',
                'message': f'未找到ID为{memory_id}的回忆记录'
            }), 404
        
        # 删除回忆记录
        result = db_manager.delete_memory(memory_id)
        
        if result:
            return jsonify({
                'success': True,
                'message': '回忆记录删除成功',
                'deleted_id': memory_id
            })
        else:
            return jsonify({
                'success': False,
                'error': '删除失败',
                'message': '回忆记录删除失败'
            }), 500
        
    except Exception as e:
        logger.error(f"删除回忆记录时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除回忆记录失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/memory/<memory_id>', methods=['PUT'])
def update_memory(memory_id):
    """更新回忆记录"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供要更新的数据'
            }), 400
        
        logger.info(f"更新回忆记录: {memory_id}")
        
        # 验证回忆记录是否存在
        memory = db_manager.get_memory_by_id(memory_id)
        if not memory:
            return jsonify({
                'success': False,
                'error': '回忆记录不存在',
                'message': f'未找到ID为{memory_id}的回忆记录'
            }), 404
        
        # 更新回忆记录
        updated_memory = db_manager.update_memory(memory_id, data)
        
        if updated_memory:
            return jsonify({
                'success': True,
                'message': '回忆记录更新成功',
                'data': {
                    'id': updated_memory.id,
                    'user_id': updated_memory.user_id,
                    'user_input': updated_memory.user_input,
                    'memory_text': updated_memory.memory_text,
                    'image_url': updated_memory.image_url,
                    'emotion': updated_memory.emotion_result,
                    'created_at': updated_memory.created_at.isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '更新失败',
                'message': '回忆记录更新失败'
            }), 500
        
    except Exception as e:
        logger.error(f"更新回忆记录时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新回忆记录失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/memories', methods=['DELETE'])
def delete_memories():
    """批量删除回忆记录"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供要删除的回忆记录ID列表'
            }), 400
        
        memory_ids = data.get('memory_ids', [])
        user_id = data.get('user_id')
        
        if not memory_ids and not user_id:
            return jsonify({
                'success': False,
                'error': '参数错误',
                'message': '请提供要删除的回忆记录ID列表或用户ID'
            }), 400
        
        logger.info(f"批量删除回忆记录: {memory_ids if memory_ids else f'用户: {user_id}'}")
        
        # 批量删除回忆记录
        result = db_manager.delete_memories_batch(memory_ids, user_id)
        
        return jsonify({
            'success': True,
            'message': f'成功删除{result["deleted_count"]}条回忆记录',
            'deleted_count': result['deleted_count'],
            'failed_ids': result.get('failed_ids', [])
        })
        
    except Exception as e:
        logger.error(f"批量删除回忆记录时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '批量删除回忆记录失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/export/memories', methods=['GET'])
def export_memories():
    """导出回忆记录"""
    try:
        # 获取查询参数
        user_id = request.args.get('user_id')
        format_type = request.args.get('format', 'json')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        emotion_filter = request.args.get('emotion')
        
        if format_type not in config.EXPORT_FORMATS:
            return jsonify({
                'success': False,
                'error': '不支持的导出格式',
                'message': f'支持的格式: {", ".join(config.EXPORT_FORMATS)}'
            }), 400
        
        logger.info(f"导出回忆记录: user_id={user_id}, format={format_type}")
        
        # 导出回忆记录
        export_result = db_manager.export_memories(
            user_id=user_id,
            format_type=format_type,
            start_date=start_date,
            end_date=end_date,
            emotion_filter=emotion_filter
        )
        
        if export_result['success']:
            return jsonify({
                'success': True,
                'message': '回忆记录导出成功',
                'data': {
                    'file_url': export_result['file_url'],
                    'file_name': export_result['file_name'],
                    'file_size': export_result['file_size'],
                    'record_count': export_result['record_count'],
                    'export_time': datetime.now().isoformat()
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '导出失败',
                'message': export_result.get('message', '导出回忆记录失败')
            }), 500
        
    except Exception as e:
        logger.error(f"导出回忆记录时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '导出回忆记录失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 2. 用户管理接口
@app.route('/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search', '')
        
        logger.info(f"获取用户列表: page={page}, per_page={per_page}")
        
        # 获取用户列表
        users_data = db_manager.get_users(page=page, per_page=per_page, search=search)
        
        return jsonify({
            'success': True,
            'data': {
                'users': users_data['users'],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': users_data['total'],
                    'pages': users_data['pages']
                }
            },
            'message': f'成功获取{len(users_data["users"])}个用户'
        })
        
    except Exception as e:
        logger.error(f"获取用户列表时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取用户列表失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/user/<user_id>', methods=['GET'])
def get_user_detail(user_id):
    """获取用户详情"""
    try:
        logger.info(f"获取用户详情: {user_id}")
        
        # 获取用户详情
        user_data = db_manager.get_user_detail(user_id)
        
        if user_data:
            return jsonify({
                'success': True,
                'data': user_data,
                'message': '成功获取用户详情'
            })
        else:
            return jsonify({
                'success': False,
                'error': '用户不存在',
                'message': f'未找到ID为{user_id}的用户'
            }), 404
        
    except Exception as e:
        logger.error(f"获取用户详情时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取用户详情失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户及其数据"""
    try:
        logger.info(f"删除用户: {user_id}")
        
        # 验证用户是否存在
        user_data = db_manager.get_user_detail(user_id)
        if not user_data:
            return jsonify({
                'success': False,
                'error': '用户不存在',
                'message': f'未找到ID为{user_id}的用户'
            }), 404
        
        # 删除用户及其数据
        result = db_manager.delete_user(user_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': '用户删除成功',
                'data': {
                    'deleted_user_id': user_id,
                    'deleted_memories': result['deleted_memories'],
                    'deleted_stats': result['deleted_stats']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '删除失败',
                'message': result.get('message', '用户删除失败')
            }), 500
        
    except Exception as e:
        logger.error(f"删除用户时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除用户失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供要更新的用户信息'
            }), 400
        
        logger.info(f"更新用户信息: {user_id}")
        
        # 验证用户是否存在
        user_data = db_manager.get_user_detail(user_id)
        if not user_data:
            return jsonify({
                'success': False,
                'error': '用户不存在',
                'message': f'未找到ID为{user_id}的用户'
            }), 404
        
        # 更新用户信息
        updated_user = db_manager.update_user(user_id, data)
        
        if updated_user:
            return jsonify({
                'success': True,
                'message': '用户信息更新成功',
                'data': updated_user
            })
        else:
            return jsonify({
                'success': False,
                'error': '更新失败',
                'message': '用户信息更新失败'
            }), 500
        
    except Exception as e:
        logger.error(f"更新用户信息时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新用户信息失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 3. 高级搜索接口
@app.route('/search/memories', methods=['GET'])
def search_memories():
    """搜索回忆记录"""
    try:
        # 获取查询参数
        query = request.args.get('q', '')
        user_id = request.args.get('user_id')
        emotion = request.args.get('emotion')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        if not query:
            return jsonify({
                'success': False,
                'error': '搜索关键词为空',
                'message': '请提供搜索关键词'
            }), 400
        
        logger.info(f"搜索回忆记录: {query}")
        
        # 执行搜索
        search_result = db_manager.search_memories(
            query=query,
            user_id=user_id,
            emotion=emotion,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': {
                'memories': search_result['memories'],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': search_result['total'],
                    'pages': search_result['pages']
                },
                'search_info': {
                    'query': query,
                    'filters': {
                        'user_id': user_id,
                        'emotion': emotion,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                }
            },
            'message': f'找到{search_result["total"]}条匹配的回忆记录'
        })
        
    except Exception as e:
        logger.error(f"搜索回忆记录时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '搜索回忆记录失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/search/emotions', methods=['GET'])
def search_by_emotion():
    """按情感搜索"""
    try:
        # 获取查询参数
        emotion = request.args.get('emotion')
        user_id = request.args.get('user_id')
        confidence_min = float(request.args.get('confidence_min', 0.0))
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        if not emotion:
            return jsonify({
                'success': False,
                'error': '情感参数为空',
                'message': '请提供要搜索的情感类型'
            }), 400
        
        logger.info(f"按情感搜索: {emotion}")
        
        # 执行搜索
        search_result = db_manager.search_by_emotion(
            emotion=emotion,
            user_id=user_id,
            confidence_min=confidence_min,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': {
                'memories': search_result['memories'],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': search_result['total'],
                    'pages': search_result['pages']
                },
                'emotion_stats': search_result.get('emotion_stats', {})
            },
            'message': f'找到{search_result["total"]}条{emotion}情感的回忆记录'
        })
        
    except Exception as e:
        logger.error(f"按情感搜索时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '按情感搜索失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/search/timeline', methods=['GET'])
def search_timeline():
    """按时间线搜索"""
    try:
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        user_id = request.args.get('user_id')
        granularity = request.args.get('granularity', 'day')  # day, week, month, year
        
        if not start_date or not end_date:
            return jsonify({
                'success': False,
                'error': '时间参数不完整',
                'message': '请提供开始和结束时间'
            }), 400
        
        logger.info(f"按时间线搜索: {start_date} - {end_date}")
        
        # 执行搜索
        timeline_result = db_manager.search_timeline(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            granularity=granularity
        )
        
        return jsonify({
            'success': True,
            'data': {
                'timeline': timeline_result['timeline'],
                'summary': timeline_result['summary'],
                'emotion_trends': timeline_result.get('emotion_trends', {}),
                'period_stats': timeline_result.get('period_stats', {})
            },
            'message': f'成功获取{start_date}至{end_date}的时间线数据'
        })
        
    except Exception as e:
        logger.error(f"按时间线搜索时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '按时间线搜索失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/search/keywords', methods=['GET'])
def search_keywords():
    """按关键词搜索"""
    try:
        # 获取查询参数
        keywords = request.args.get('keywords', '').split(',')
        user_id = request.args.get('user_id')
        match_type = request.args.get('match_type', 'any')  # any, all
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        keywords = [k.strip() for k in keywords if k.strip()]
        
        if not keywords:
            return jsonify({
                'success': False,
                'error': '关键词为空',
                'message': '请提供要搜索的关键词'
            }), 400
        
        logger.info(f"按关键词搜索: {keywords}")
        
        # 执行搜索
        search_result = db_manager.search_keywords(
            keywords=keywords,
            user_id=user_id,
            match_type=match_type,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': {
                'memories': search_result['memories'],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': search_result['total'],
                    'pages': search_result['pages']
                },
                'keyword_stats': search_result.get('keyword_stats', {}),
                'search_info': {
                    'keywords': keywords,
                    'match_type': match_type
                }
            },
            'message': f'找到{search_result["total"]}条匹配的回忆记录'
        })
        
    except Exception as e:
        logger.error(f"按关键词搜索时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '按关键词搜索失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 4. 数据分析接口
@app.route('/analytics/emotion-trends', methods=['GET'])
def get_emotion_trends():
    """获取情感趋势分析"""
    try:
        # 获取查询参数
        user_id = request.args.get('user_id')
        period = request.args.get('period', '30d')  # 30d, 7d, 1y
        granularity = request.args.get('granularity', 'day')  # day, week, month
        
        logger.info(f"获取情感趋势分析: user_id={user_id}, period={period}")
        
        # 获取情感趋势数据
        trends_data = db_manager.get_emotion_trends(
            user_id=user_id,
            period=period,
            granularity=granularity
        )
        
        return jsonify({
            'success': True,
            'data': {
                'trends': trends_data['trends'],
                'summary': trends_data['summary'],
                'top_emotions': trends_data.get('top_emotions', []),
                'emotion_changes': trends_data.get('emotion_changes', {}),
                'period_info': {
                    'period': period,
                    'granularity': granularity,
                    'data_points': len(trends_data['trends'])
                }
            },
            'message': '成功获取情感趋势分析'
        })
        
    except Exception as e:
        logger.error(f"获取情感趋势分析时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取情感趋势分析失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/analytics/word-frequency', methods=['GET'])
def get_word_frequency():
    """获取词频分析"""
    try:
        # 获取查询参数
        user_id = request.args.get('user_id')
        top_n = int(request.args.get('top_n', 50))
        min_length = int(request.args.get('min_length', 2))
        exclude_common = request.args.get('exclude_common', 'true').lower() == 'true'
        
        logger.info(f"获取词频分析: user_id={user_id}, top_n={top_n}")
        
        # 获取词频数据
        word_freq_data = db_manager.get_word_frequency(
            user_id=user_id,
            top_n=top_n,
            min_length=min_length,
            exclude_common=exclude_common
        )
        
        return jsonify({
            'success': True,
            'data': {
                'word_frequency': word_freq_data['word_frequency'],
                'word_cloud_data': word_freq_data.get('word_cloud_data', []),
                'statistics': {
                    'total_words': word_freq_data.get('total_words', 0),
                    'unique_words': word_freq_data.get('unique_words', 0),
                    'average_frequency': word_freq_data.get('average_frequency', 0.0)
                },
                'analysis_params': {
                    'top_n': top_n,
                    'min_length': min_length,
                    'exclude_common': exclude_common
                }
            },
            'message': '成功获取词频分析'
        })
        
    except Exception as e:
        logger.error(f"获取词频分析时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取词频分析失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/analytics/user-activity', methods=['GET'])
def get_user_activity():
    """获取用户活跃度分析"""
    try:
        # 获取查询参数
        user_id = request.args.get('user_id')
        period = request.args.get('period', '30d')
        
        logger.info(f"获取用户活跃度分析: user_id={user_id}, period={period}")
        
        # 获取用户活跃度数据
        activity_data = db_manager.get_user_activity(
            user_id=user_id,
            period=period
        )
        
        return jsonify({
            'success': True,
            'data': {
                'activity_timeline': activity_data['activity_timeline'],
                'peak_hours': activity_data.get('peak_hours', []),
                'active_days': activity_data.get('active_days', []),
                'statistics': {
                    'total_sessions': activity_data.get('total_sessions', 0),
                    'average_session_length': activity_data.get('average_session_length', 0.0),
                    'most_active_day': activity_data.get('most_active_day', ''),
                    'activity_score': activity_data.get('activity_score', 0.0)
                }
            },
            'message': '成功获取用户活跃度分析'
        })
        
    except Exception as e:
        logger.error(f"获取用户活跃度分析时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取用户活跃度分析失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/analytics/system-usage', methods=['GET'])
def get_system_usage():
    """获取系统使用统计"""
    try:
        # 获取查询参数
        period = request.args.get('period', '30d')
        
        logger.info(f"获取系统使用统计: period={period}")
        
        # 获取系统使用数据
        usage_data = db_manager.get_system_usage(period=period)
        
        return jsonify({
            'success': True,
            'data': {
                'usage_metrics': usage_data['usage_metrics'],
                'api_statistics': usage_data.get('api_statistics', {}),
                'user_metrics': usage_data.get('user_metrics', {}),
                'performance_metrics': usage_data.get('performance_metrics', {}),
                'error_statistics': usage_data.get('error_statistics', {}),
                'period_info': {
                    'period': period,
                    'start_date': usage_data.get('start_date'),
                    'end_date': usage_data.get('end_date')
                }
            },
            'message': '成功获取系统使用统计'
        })
        
    except Exception as e:
        logger.error(f"获取系统使用统计时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取系统使用统计失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 5. 批量处理接口
@app.route('/generate/batch', methods=['POST'])
def generate_batch():
    """批量生成回忆"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供批量处理的数据'
            }), 400
        
        texts = data.get('texts', [])
        user_id = data.get('user_id', 'anonymous')
        batch_options = data.get('options', {})
        
        if not texts or len(texts) > config.MAX_BATCH_SIZE:
            return jsonify({
                'success': False,
                'error': '批量数据无效',
                'message': f'请提供1-{config.MAX_BATCH_SIZE}条文本数据'
            }), 400
        
        logger.info(f"批量生成回忆: {len(texts)}条数据")
        
        # 创建批量任务
        batch_task = db_manager.create_batch_task(
            task_type='generate',
            data=texts,
            user_id=user_id,
            options=batch_options
        )
        
        # 异步处理批量任务
        batch_result = db_manager.process_batch_generate(
            batch_task_id=batch_task['id'],
            texts=texts,
            user_id=user_id,
            options=batch_options
        )
        
        return jsonify({
            'success': True,
            'data': {
                'batch_id': batch_task['id'],
                'status': batch_result['status'],
                'total_items': len(texts),
                'processed_items': batch_result.get('processed_items', 0),
                'successful_items': batch_result.get('successful_items', 0),
                'failed_items': batch_result.get('failed_items', 0),
                'results': batch_result.get('results', []),
                'estimated_completion': batch_result.get('estimated_completion')
            },
            'message': f'批量生成任务已创建，任务ID: {batch_task["id"]}'
        })
        
    except Exception as e:
        logger.error(f"批量生成回忆时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '批量生成回忆失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/speech-to-text/batch', methods=['POST'])
def speech_to_text_batch():
    """批量语音转文本"""
    try:
        # 检查是否有文件上传
        if 'audio_files' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到音频文件',
                'message': '请上传音频文件'
            }), 400
        
        audio_files = request.files.getlist('audio_files')
        language = request.form.get('language', 'zh-CN')
        
        if len(audio_files) > config.MAX_BATCH_SIZE:
            return jsonify({
                'success': False,
                'error': '文件数量超限',
                'message': f'最多支持{config.MAX_BATCH_SIZE}个文件'
            }), 400
        
        logger.info(f"批量语音转文本: {len(audio_files)}个文件")
        
        # 创建批量任务
        batch_task = db_manager.create_batch_task(
            task_type='speech_to_text',
            data=[f.filename for f in audio_files],
            user_id=request.form.get('user_id', 'anonymous'),
            options={'language': language}
        )
        
        # 处理批量音频文件
        batch_result = db_manager.process_batch_speech_to_text(
            batch_task_id=batch_task['id'],
            audio_files=audio_files,
            language=language
        )
        
        return jsonify({
            'success': True,
            'data': {
                'batch_id': batch_task['id'],
                'status': batch_result['status'],
                'total_files': len(audio_files),
                'processed_files': batch_result.get('processed_files', 0),
                'successful_files': batch_result.get('successful_files', 0),
                'failed_files': batch_result.get('failed_files', 0),
                'results': batch_result.get('results', [])
            },
            'message': f'批量语音转文本任务已创建，任务ID: {batch_task["id"]}'
        })
        
    except Exception as e:
        logger.error(f"批量语音转文本时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '批量语音转文本失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/import/memories', methods=['POST'])
def import_memories():
    """批量导入回忆数据"""
    try:
        # 检查是否有文件上传
        if 'import_file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到导入文件',
                'message': '请上传要导入的文件'
            }), 400
        
        import_file = request.files['import_file']
        format_type = request.form.get('format', 'json')
        user_id = request.form.get('user_id', 'anonymous')
        merge_option = request.form.get('merge_option', 'skip')  # skip, overwrite, merge
        
        if format_type not in ['json', 'csv', 'xlsx']:
            return jsonify({
                'success': False,
                'error': '不支持的文件格式',
                'message': '支持的格式: json, csv, xlsx'
            }), 400
        
        logger.info(f"批量导入回忆数据: {import_file.filename}, 格式: {format_type}")
        
        # 创建导入任务
        import_task = db_manager.create_import_task(
            file=import_file,
            format_type=format_type,
            user_id=user_id,
            merge_option=merge_option
        )
        
        # 处理导入任务
        import_result = db_manager.process_import_memories(
            import_task_id=import_task['id'],
            file_path=import_task['file_path'],
            format_type=format_type,
            user_id=user_id,
            merge_option=merge_option
        )
        
        return jsonify({
            'success': True,
            'data': {
                'import_id': import_task['id'],
                'status': import_result['status'],
                'total_records': import_result.get('total_records', 0),
                'imported_records': import_result.get('imported_records', 0),
                'skipped_records': import_result.get('skipped_records', 0),
                'failed_records': import_result.get('failed_records', 0),
                'errors': import_result.get('errors', [])
            },
            'message': f'数据导入完成，导入ID: {import_task["id"]}'
        })
        
    except Exception as e:
        logger.error(f"批量导入回忆数据时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '批量导入回忆数据失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/batch/status/<task_id>', methods=['GET'])
def get_batch_status(task_id):
    """获取批量处理任务状态"""
    try:
        logger.info(f"获取批量任务状态: {task_id}")
        
        # 获取任务状态
        task_status = db_manager.get_batch_task_status(task_id)
        
        if not task_status:
            return jsonify({
                'success': False,
                'error': '任务不存在',
                'message': f'未找到ID为{task_id}的批量任务'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'status': task_status['status'],
                'progress': task_status.get('progress', 0),
                'total_items': task_status.get('total_items', 0),
                'processed_items': task_status.get('processed_items', 0),
                'successful_items': task_status.get('successful_items', 0),
                'failed_items': task_status.get('failed_items', 0),
                'created_at': task_status.get('created_at'),
                'started_at': task_status.get('started_at'),
                'completed_at': task_status.get('completed_at'),
                'estimated_completion': task_status.get('estimated_completion'),
                'errors': task_status.get('errors', [])
            },
            'message': '成功获取批量任务状态'
        })
        
    except Exception as e:
        logger.error(f"获取批量任务状态时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取批量任务状态失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 6. 配置管理接口
@app.route('/config', methods=['GET'])
def get_config():
    """获取系统配置"""
    try:
        logger.info("获取系统配置")
        
        # 获取系统配置（排除敏感信息）
        system_config = {
            'system_info': {
                'version': '1.0.0',
                'debug_mode': config.DEBUG,
                'host': config.HOST,
                'port': config.PORT
            },
            'features': {
                'search_enabled': config.ENABLE_SEARCH,
                'analytics_enabled': config.ENABLE_ANALYTICS,
                'batch_processing_enabled': config.ENABLE_BATCH_PROCESSING,
                'realtime_enabled': config.ENABLE_REALTIME,
                'cache_enabled': config.ENABLE_CACHE,
                'monitoring_enabled': config.ENABLE_MONITORING
            },
            'storage': {
                'use_local_storage': config.USE_LOCAL_STORAGE,
                'local_storage_path': config.LOCAL_STORAGE_PATH
            },
            'processing': {
                'batch_size': config.BATCH_SIZE,
                'max_batch_size': config.MAX_BATCH_SIZE,
                'prioritize_accuracy': config.PRIORITIZE_ACCURACY
            },
            'file_limits': {
                'max_content_length': config.MAX_CONTENT_LENGTH,
                'max_file_size': config.MAX_FILE_SIZE,
                'allowed_audio_extensions': list(config.ALLOWED_AUDIO_EXTENSIONS),
                'allowed_image_extensions': list(config.ALLOWED_IMAGE_EXTENSIONS)
            }
        }
        
        return jsonify({
            'success': True,
            'data': system_config,
            'message': '成功获取系统配置'
        })
        
    except Exception as e:
        logger.error(f"获取系统配置时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取系统配置失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/config', methods=['PUT'])
def update_config():
    """更新系统配置"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供要更新的配置项'
            }), 400
        
        logger.info("更新系统配置")
        
        # 更新配置（这里应该谨慎处理，只允许更新特定配置项）
        updatable_configs = [
            'ENABLE_SEARCH', 'ENABLE_ANALYTICS', 'ENABLE_BATCH_PROCESSING',
            'ENABLE_REALTIME', 'ENABLE_CACHE', 'ENABLE_MONITORING',
            'BATCH_SIZE', 'PRIORITIZE_ACCURACY'
        ]
        
        updated_configs = {}
        for key, value in data.items():
            config_key = key.upper()
            if config_key in updatable_configs:
                # 验证并更新配置
                if hasattr(config, config_key):
                    setattr(config, config_key, value)
                    updated_configs[key] = value
        
        # 保存配置更改
        config_result = db_manager.save_config_changes(updated_configs)
        
        return jsonify({
            'success': True,
            'data': {
                'updated_configs': updated_configs,
                'total_updated': len(updated_configs)
            },
            'message': '系统配置更新成功'
        })
        
    except Exception as e:
        logger.error(f"更新系统配置时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新系统配置失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/config/reset', methods=['POST'])
def reset_config():
    """重置系统配置"""
    try:
        logger.info("重置系统配置")
        
        # 重置配置到默认值
        reset_result = db_manager.reset_config_to_defaults()
        
        return jsonify({
            'success': True,
            'data': {
                'reset_items': reset_result.get('reset_items', []),
                'total_reset': reset_result.get('total_reset', 0)
            },
            'message': '系统配置已重置为默认值'
        })
        
    except Exception as e:
        logger.error(f"重置系统配置时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '重置系统配置失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/models/status', methods=['GET'])
def get_models_status():
    """获取模型状态"""
    try:
        logger.info("获取模型状态")
        
        # 获取各个模型的状态
        models_status = {
            'emotion_analyzer': {
                'loaded': hasattr(emotion_analyzer, 'models_loaded') and emotion_analyzer.models_loaded,
                'models': emotion_analyzer.get_available_models() if hasattr(emotion_analyzer, 'get_available_models') else []
            },
            'image_generator': {
                'loaded': hasattr(image_generator, 'models_loaded') and image_generator.models_loaded,
                'models': image_generator.get_available_models() if hasattr(image_generator, 'get_available_models') else []
            },
            'speech_service': {
                'loaded': hasattr(speech_service, 'models_loaded') and speech_service.models_loaded,
                'services': speech_service.get_service_status().get('services', {}) if hasattr(speech_service, 'get_service_status') else {}
            }
        }
        
        return jsonify({
            'success': True,
            'data': models_status,
            'message': '成功获取模型状态'
        })
        
    except Exception as e:
        logger.error(f"获取模型状态时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取模型状态失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 7. 文件管理接口
@app.route('/upload', methods=['POST'])
def upload_file():
    """文件上传"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到文件',
                'message': '请选择要上传的文件'
            }), 400
        
        file = request.files['file']
        file_type = request.form.get('type', 'general')  # audio, image, video, document, general
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空',
                'message': '请选择有效的文件'
            }), 400
        
        # 验证文件类型和大小
        if file_type == 'audio' and not any(file.filename.lower().endswith(ext) for ext in config.ALLOWED_AUDIO_EXTENSIONS):
            return jsonify({
                'success': False,
                'error': '不支持的音频文件格式',
                'message': f'支持的格式: {", ".join(config.ALLOWED_AUDIO_EXTENSIONS)}'
            }), 400
        
        if file_type == 'image' and not any(file.filename.lower().endswith(ext) for ext in config.ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({
                'success': False,
                'error': '不支持的图像文件格式',
                'message': f'支持的格式: {", ".join(config.ALLOWED_IMAGE_EXTENSIONS)}'
            }), 400
        
        logger.info(f"上传文件: {file.filename}, 类型: {file_type}")
        
        # 保存文件
        upload_result = db_manager.save_uploaded_file(
            file=file,
            file_type=file_type,
            user_id=request.form.get('user_id', 'anonymous')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'file_id': upload_result['file_id'],
                'file_name': upload_result['file_name'],
                'file_size': upload_result['file_size'],
                'file_type': file_type,
                'file_url': upload_result['file_url'],
                'upload_time': upload_result['upload_time']
            },
            'message': '文件上传成功'
        })
        
    except Exception as e:
        logger.error(f"文件上传时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '文件上传失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/files/<file_id>', methods=['GET'])
def get_file_info(file_id):
    """获取文件信息"""
    try:
        logger.info(f"获取文件信息: {file_id}")
        
        # 获取文件信息
        file_info = db_manager.get_file_info(file_id)
        
        if not file_info:
            return jsonify({
                'success': False,
                'error': '文件不存在',
                'message': f'未找到ID为{file_id}的文件'
            }), 404
        
        return jsonify({
            'success': True,
            'data': file_info,
            'message': '成功获取文件信息'
        })
        
    except Exception as e:
        logger.error(f"获取文件信息时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取文件信息失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """删除文件"""
    try:
        logger.info(f"删除文件: {file_id}")
        
        # 验证文件是否存在
        file_info = db_manager.get_file_info(file_id)
        if not file_info:
            return jsonify({
                'success': False,
                'error': '文件不存在',
                'message': f'未找到ID为{file_id}的文件'
            }), 404
        
        # 删除文件
        delete_result = db_manager.delete_file(file_id)
        
        if delete_result['success']:
            return jsonify({
                'success': True,
                'message': '文件删除成功',
                'data': {
                    'deleted_file_id': file_id,
                    'deleted_file_name': delete_result.get('file_name'),
                    'freed_space': delete_result.get('freed_space', 0)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '删除失败',
                'message': delete_result.get('message', '文件删除失败')
            }), 500
        
    except Exception as e:
        logger.error(f"删除文件时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除文件失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/files/<file_id>/preview', methods=['GET'])
def preview_file(file_id):
    """文件预览"""
    try:
        logger.info(f"预览文件: {file_id}")
        
        # 获取文件信息
        file_info = db_manager.get_file_info(file_id)
        if not file_info:
            return jsonify({
                'success': False,
                'error': '文件不存在',
                'message': f'未找到ID为{file_id}的文件'
            }), 404
        
        # 生成预览
        preview_result = db_manager.generate_file_preview(file_id, file_info)
        
        return jsonify({
            'success': True,
            'data': {
                'file_id': file_id,
                'preview_type': preview_result.get('preview_type', 'none'),
                'preview_url': preview_result.get('preview_url'),
                'thumbnail_url': preview_result.get('thumbnail_url'),
                'metadata': preview_result.get('metadata', {}),
                'can_preview': preview_result.get('can_preview', False)
            },
            'message': '成功生成文件预览'
        })
        
    except Exception as e:
        logger.error(f"预览文件时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '预览文件失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 8. 实时通信接口
@app.route('/ws', methods=['GET'])
def websocket_info():
    """WebSocket连接信息"""
    try:
        ws_config = config.get_realtime_config()
        
        return jsonify({
            'success': True,
            'data': {
                'websocket_enabled': ws_config['enabled'],
                'websocket_url': f"ws://{config.HOST}:{config.PORT}/ws",
                'supported_events': [
                    'memory_generated',
                    'speech_converted',
                    'batch_progress',
                    'system_notification'
                ],
                'connection_info': {
                    'max_connections': 100,
                    'heartbeat_interval': 30,
                    'reconnect_interval': 5
                }
            },
            'message': '成功获取WebSocket连接信息'
        })
        
    except Exception as e:
        logger.error(f"获取WebSocket信息时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取WebSocket信息失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/events', methods=['GET'])
def get_events():
    """获取服务器推送事件"""
    try:
        # 获取查询参数
        user_id = request.args.get('user_id')
        event_type = request.args.get('type')
        since = request.args.get('since')
        limit = int(request.args.get('limit', 50))
        
        logger.info(f"获取服务器事件: user_id={user_id}, type={event_type}")
        
        # 获取事件列表
        events = db_manager.get_events(
            user_id=user_id,
            event_type=event_type,
            since=since,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': {
                'events': events['events'],
                'total': events['total'],
                'unread_count': events.get('unread_count', 0),
                'last_event_time': events.get('last_event_time')
            },
            'message': f'成功获取{len(events["events"])}个事件'
        })
        
    except Exception as e:
        logger.error(f"获取服务器事件时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取服务器事件失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/ws/speech-realtime', methods=['GET'])
def realtime_speech_info():
    """实时语音转文本连接信息"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'realtime_speech_enabled': config.ENABLE_REALTIME,
                'websocket_url': f"ws://{config.HOST}:{config.PORT}/ws/speech-realtime",
                'supported_languages': ['zh-CN', 'en-US', 'ja-JP', 'ko-KR'],
                'audio_config': {
                    'sample_rate': config.AUDIO_SAMPLE_RATE,
                    'channels': config.AUDIO_CHANNELS,
                    'format': config.AUDIO_FORMAT,
                    'chunk_size': 1024
                }
            },
            'message': '成功获取实时语音转文本连接信息'
        })
        
    except Exception as e:
        logger.error(f"获取实时语音转文本信息时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取实时语音转文本信息失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 9. 缓存管理接口
@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """清空缓存"""
    try:
        # 获取请求参数
        data = request.get_json() or {}
        cache_type = data.get('type', 'all')  # all, memory, file, database
        pattern = data.get('pattern', '*')  # 缓存键模式
        
        logger.info(f"清空缓存: type={cache_type}, pattern={pattern}")
        
        # 清空缓存
        cache_result = db_manager.clear_cache(
            cache_type=cache_type,
            pattern=pattern
        )
        
        return jsonify({
            'success': True,
            'data': {
                'cleared_items': cache_result.get('cleared_items', 0),
                'freed_memory': cache_result.get('freed_memory', 0),
                'cache_types_cleared': cache_result.get('cache_types_cleared', []),
                'clear_time': datetime.now().isoformat()
            },
            'message': f'成功清空{cache_result.get("cleared_items", 0)}个缓存项'
        })
        
    except Exception as e:
        logger.error(f"清空缓存时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '清空缓存失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/cache/status', methods=['GET'])
def get_cache_status():
    """获取缓存状态"""
    try:
        logger.info("获取缓存状态")
        
        # 获取缓存状态
        cache_status = db_manager.get_cache_status()
        cache_config = config.get_cache_config()
        
        return jsonify({
            'success': True,
            'data': {
                'cache_enabled': cache_config['enabled'],
                'cache_statistics': {
                    'total_items': cache_status.get('total_items', 0),
                    'memory_usage': cache_status.get('memory_usage', 0),
                    'hit_rate': cache_status.get('hit_rate', 0.0),
                    'miss_rate': cache_status.get('miss_rate', 0.0),
                    'eviction_count': cache_status.get('eviction_count', 0)
                },
                'cache_types': {
                    'memory_cache': cache_status.get('memory_cache', {}),
                    'file_cache': cache_status.get('file_cache', {}),
                    'database_cache': cache_status.get('database_cache', {}),
                    'redis_cache': cache_status.get('redis_cache', {})
                },
                'configuration': {
                    'max_size': cache_config['max_size'],
                    'ttl': cache_config['cache_ttl'],
                    'redis_url': cache_config['redis_url'] if cache_config['redis_url'] else None
                }
            },
            'message': '成功获取缓存状态'
        })
        
    except Exception as e:
        logger.error(f"获取缓存状态时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取缓存状态失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/cache/warm', methods=['POST'])
def warm_cache():
    """预热缓存"""
    try:
        # 获取请求参数
        data = request.get_json() or {}
        warm_type = data.get('type', 'all')  # all, memories, users, analytics
        user_id = data.get('user_id')
        
        logger.info(f"预热缓存: type={warm_type}, user_id={user_id}")
        
        # 预热缓存
        warm_result = db_manager.warm_cache(
            warm_type=warm_type,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'warmed_items': warm_result.get('warmed_items', 0),
                'warm_types': warm_result.get('warm_types', []),
                'estimated_time': warm_result.get('estimated_time', 0),
                'cache_hit_improvement': warm_result.get('cache_hit_improvement', 0.0),
                'warm_time': datetime.now().isoformat()
            },
            'message': f'成功预热{warm_result.get("warmed_items", 0)}个缓存项'
        })
        
    except Exception as e:
        logger.error(f"预热缓存时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '预热缓存失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 10. 日志和监控接口
@app.route('/logs', methods=['GET'])
def get_logs():
    """获取系统日志"""
    try:
        # 获取查询参数
        level = request.args.get('level', 'INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        search = request.args.get('search', '')
        
        logger.info(f"获取系统日志: level={level}, limit={limit}")
        
        # 获取日志记录
        logs_result = db_manager.get_system_logs(
            level=level,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
            search=search
        )
        
        return jsonify({
            'success': True,
            'data': {
                'logs': logs_result['logs'],
                'total': logs_result['total'],
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'has_more': logs_result.get('has_more', False)
                },
                'log_statistics': {
                    'error_count': logs_result.get('error_count', 0),
                    'warning_count': logs_result.get('warning_count', 0),
                    'info_count': logs_result.get('info_count', 0)
                }
            },
            'message': f'成功获取{len(logs_result["logs"])}条日志记录'
        })
        
    except Exception as e:
        logger.error(f"获取系统日志时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取系统日志失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/logs/errors', methods=['GET'])
def get_error_logs():
    """获取错误日志"""
    try:
        # 获取查询参数
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = int(request.args.get('limit', 50))
        error_type = request.args.get('error_type')  # exception, api_error, validation_error
        
        logger.info(f"获取错误日志: limit={limit}, error_type={error_type}")
        
        # 获取错误日志
        error_logs = db_manager.get_error_logs(
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            error_type=error_type
        )
        
        return jsonify({
            'success': True,
            'data': {
                'error_logs': error_logs['logs'],
                'total_errors': error_logs['total'],
                'error_summary': {
                    'most_common_errors': error_logs.get('most_common_errors', []),
                    'error_rate': error_logs.get('error_rate', 0.0),
                    'critical_errors': error_logs.get('critical_errors', 0),
                    'resolved_errors': error_logs.get('resolved_errors', 0)
                },
                'error_trends': error_logs.get('error_trends', [])
            },
            'message': f'成功获取{len(error_logs["logs"])}条错误日志'
        })
        
    except Exception as e:
        logger.error(f"获取错误日志时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取错误日志失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """获取性能指标"""
    try:
        # 获取查询参数
        metric_type = request.args.get('type', 'all')  # all, performance, resource, api
        period = request.args.get('period', '1h')  # 1h, 6h, 24h, 7d, 30d
        
        logger.info(f"获取性能指标: type={metric_type}, period={period}")
        
        # 获取性能指标
        metrics_data = db_manager.get_system_metrics(
            metric_type=metric_type,
            period=period
        )
        
        return jsonify({
            'success': True,
            'data': {
                'performance_metrics': {
                    'response_time': metrics_data.get('response_time', {}),
                    'throughput': metrics_data.get('throughput', {}),
                    'error_rate': metrics_data.get('error_rate', {}),
                    'cpu_usage': metrics_data.get('cpu_usage', {}),
                    'memory_usage': metrics_data.get('memory_usage', {})
                },
                'api_metrics': {
                    'total_requests': metrics_data.get('total_requests', 0),
                    'successful_requests': metrics_data.get('successful_requests', 0),
                    'failed_requests': metrics_data.get('failed_requests', 0),
                    'avg_response_time': metrics_data.get('avg_response_time', 0.0),
                    'requests_per_minute': metrics_data.get('requests_per_minute', 0.0)
                },
                'resource_metrics': {
                    'disk_usage': metrics_data.get('disk_usage', {}),
                    'network_io': metrics_data.get('network_io', {}),
                    'database_connections': metrics_data.get('database_connections', {}),
                    'cache_performance': metrics_data.get('cache_performance', {})
                },
                'period_info': {
                    'period': period,
                    'start_time': metrics_data.get('start_time'),
                    'end_time': metrics_data.get('end_time'),
                    'data_points': metrics_data.get('data_points', 0)
                }
            },
            'message': '成功获取性能指标'
        })
        
    except Exception as e:
        logger.error(f"获取性能指标时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取性能指标失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/monitoring', methods=['GET'])
def get_monitoring_status():
    """获取系统监控状态"""
    try:
        logger.info("获取系统监控状态")
        
        # 获取监控状态
        monitoring_config = config.get_monitoring_config()
        monitoring_status = db_manager.get_monitoring_status()
        
        return jsonify({
            'success': True,
            'data': {
                'monitoring_enabled': monitoring_config['enabled'],
                'system_health': {
                    'overall_status': monitoring_status.get('overall_status', 'unknown'),
                    'uptime': monitoring_status.get('uptime', 0),
                    'last_check': monitoring_status.get('last_check'),
                    'health_score': monitoring_status.get('health_score', 0.0)
                },
                'service_status': {
                    'database': monitoring_status.get('database_status', 'unknown'),
                    'cache': monitoring_status.get('cache_status', 'unknown'),
                    'file_system': monitoring_status.get('file_system_status', 'unknown'),
                    'external_apis': monitoring_status.get('external_apis_status', {})
                },
                'alerts': {
                    'active_alerts': monitoring_status.get('active_alerts', []),
                    'resolved_alerts': monitoring_status.get('resolved_alerts', []),
                    'alert_rules': monitoring_status.get('alert_rules', [])
                },
                'monitoring_services': {
                    'prometheus_enabled': bool(monitoring_config.get('prometheus_url')),
                    'grafana_enabled': bool(monitoring_config.get('grafana_url')),
                    'datadog_enabled': bool(monitoring_config.get('datadog_api_key'))
                }
            },
            'message': '成功获取系统监控状态'
        })
        
    except Exception as e:
        logger.error(f"获取系统监控状态时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取系统监控状态失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 科大讯飞图片生成测试接口
@app.route('/test/iflytek-image', methods=['POST'])
def test_iflytek_image_generation():
    """测试科大讯飞图片生成"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供测试提示词'
            }), 400
        
        prompt = data.get('prompt', '美丽的风景画')
        style = data.get('style', 'realistic')
        size = data.get('size', '512x512')
        
        logger.info(f"测试科大讯飞图片生成: {prompt}")
        
        # 检查讯飞配置
        if not config.IFLYTEK_IMAGE_API_KEY:
            return jsonify({
                'success': False,
                'error': '科大讯飞图片生成API未配置',
                'message': '请先配置IFLYTEK_IMAGE_API_KEY等参数'
            }), 400
        
        # 模拟情感分析结果
        mock_emotion_result = {
            'dominant_emotion': 'peaceful',
            'confidence': 0.8,
            'emotions': {
                'peaceful': 0.8,
                'happy': 0.2
            }
        }
        
        # 生成图片
        image_url = image_generator.generate_image(
            memory_text=prompt,
            emotion_result=mock_emotion_result,
            style=style,
            size=size
        )
        
        # 检查配置状态
        api_info = config.get_api_priority()
        available_models = image_generator.get_available_models()
        
        return jsonify({
            'success': True,
            'data': {
                'image_url': image_url,
                'prompt': prompt,
                'style': style,
                'size': size,
                'generated_by': '科大讯飞图片生成API',
                'api_status': {
                    'iflytek_image_configured': api_info.get('has_iflytek_image_key', False),
                    'api_id': config.IFLYTEK_IMAGE_API_ID,
                    'api_url': config.IFLYTEK_IMAGE_API_URL
                },
                'available_models': available_models
            },
            'message': f'科大讯飞图片生成测试完成'
        })
        
    except Exception as e:
        logger.error(f"测试科大讯飞图片生成时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '科大讯飞图片生成测试失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# 科大讯飞性别年龄识别测试接口
@app.route('/test/iflytek-gender-age', methods=['POST'])
def test_iflytek_gender_age():
    """测试科大讯飞性别年龄识别"""
    try:
        # 检查是否有上传的音频文件
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': '请上传音频文件',
                'message': '请在表单中包含名为"audio"的音频文件'
            }), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': '未选择音频文件',
                'message': '请选择一个音频文件'
            }), 400
        
        # 保存上传的音频文件
        filename = f"gender_age_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        audio_path = os.path.join(config.LOCAL_STORAGE_PATH, 'uploads', filename)
        
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        audio_file.save(audio_path)
        
        logger.info(f"测试科大讯飞性别年龄识别: {filename}")
        
        # 检查讯飞配置
        if not config.IFLYTEK_GENDER_AGE_API_KEY:
            return jsonify({
                'success': False,
                'error': '科大讯飞性别年龄识别API未配置',
                'message': '请先配置IFLYTEK_GENDER_AGE_API_KEY等参数'
            }), 400
        
        # 调用语音转文字服务（包含性别年龄识别）
        result = speech_service.convert_audio_to_text(
            audio_path,
            language="zh-CN"
        )
        
        # 检查配置状态
        api_info = config.get_api_priority()
        
        response_data = {
            'success': True,
            'data': {
                'filename': filename,
                'speech_result': {
                    'text': result.get('text', ''),
                    'confidence': result.get('confidence', 0.0),
                    'language': result.get('language', 'zh-CN'),
                    'service': result.get('service', 'unknown')
                },
                'gender_age_result': result.get('gender_age', {}),
                'api_status': {
                    'iflytek_speech_configured': api_info.get('has_iflytek_speech_key', False),
                    'iflytek_gender_age_configured': api_info.get('has_iflytek_gender_age_key', False),
                    'api_id': config.IFLYTEK_GENDER_AGE_API_ID,
                    'api_url': config.IFLYTEK_GENDER_AGE_API_URL
                }
            },
            'message': '科大讯飞性别年龄识别测试完成'
        }
        
        # 清理临时文件
        try:
            os.remove(audio_path)
        except:
            pass
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"测试科大讯飞性别年龄识别时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': '科大讯飞性别年龄识别测试失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/test/deepseek-emotion', methods=['POST'])
def test_deepseek_emotion_analysis():
    """测试DeepSeek情感分析功能（针对老人群体优化）"""
    try:
        logger.info("开始测试DeepSeek情感分析功能")
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供要分析的文本和用户上下文'
            }), 400
        
        text = data.get('text', '')
        user_context = data.get('user_context', {})
        
        if not text:
            return jsonify({
                'success': False,
                'error': '文本为空',
                'message': '请提供要分析的文本内容'
            }), 400
        
        logger.info(f"测试文本: {text[:50]}...")
        logger.info(f"用户上下文: {user_context}")
        
        # 检查DeepSeek配置
        if not config.DEEPSEEK_API_KEY or config.DEEPSEEK_API_KEY.startswith('your_'):
            # 如果没有配置DeepSeek，使用模拟测试
            result = {
                'primary_emotion': 'happy',
                'confidence': 0.85,
                'emotion_scores': {'happy': 0.85, 'peaceful': 0.3},
                'analysis_model': 'Simulation_Mode',
                'elderly_specific': {
                    'health_concern': 0.2,
                    'family_relation': 0.8,
                    'loneliness': 0.1,
                    'nostalgia': 0.3
                } if user_context.get('age', 0) >= 65 else {},
                'ai_suggestions': [
                    '继续保持积极乐观的心态',
                    '分享快乐能让幸福感加倍'
                ] if user_context.get('age', 0) >= 65 else [
                    '保持积极心态',
                    '适当运动有助于心情'
                ],
                'message': 'DeepSeek API未配置，使用模拟分析'
            }
        else:
            # 调用真实的DeepSeek情感分析
            result = emotion_analyzer.analyze_text(text, user_context)
        
        # 获取配置状态
        api_configured = bool(config.DEEPSEEK_API_KEY and not config.DEEPSEEK_API_KEY.startswith('your_'))
        
        response_data = {
            'success': True,
            'data': {
                'input': {
                    'text': text,
                    'user_context': user_context,
                    'is_elderly': user_context.get('age', 0) >= 65 or user_context.get('age_group') in ['senior', 'elderly']
                },
                'emotion_result': result,
                'api_status': {
                    'deepseek_configured': api_configured,
                    'api_url': config.DEEPSEEK_API_URL,
                    'model': config.DEEPSEEK_MODEL,
                    'max_tokens': config.DEEPSEEK_MAX_TOKENS,
                    'temperature': config.DEEPSEEK_TEMPERATURE
                },
                'performance': {
                    'response_time': '模拟' if not api_configured else '实际API调用',
                    'model_used': result.get('analysis_model', 'unknown'),
                    'elderly_optimized': user_context.get('age', 0) >= 65
                }
            },
            'message': 'DeepSeek情感分析测试完成'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"测试DeepSeek情感分析时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'DeepSeek情感分析测试失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/test/deepseek-elderly', methods=['POST'])
def test_deepseek_elderly_analysis():
    """专门测试DeepSeek针对老人群体的情感分析"""
    try:
        logger.info("开始测试DeepSeek老人情感分析功能")
        
        # 预设的老人测试用例
        elderly_test_cases = [
            {
                "text": "今天孙子来看我了，真的很开心，但是他走了以后又觉得有点孤单",
                "context": {"age": 70, "age_group": "senior", "family_status": "有孙子"},
                "description": "老人家庭情感测试"
            },
            {
                "text": "最近身体不太好，经常失眠，担心会不会有什么大问题",
                "context": {"age": 68, "age_group": "elderly", "health_status": "不佳"},
                "description": "老人健康担忧测试"
            },
            {
                "text": "想起年轻时候和老伴一起的日子，那时候虽然苦但是很快乐",
                "context": {"age": 75, "recent_text": "退休后的生活", "marital_status": "丧偶"},
                "description": "老人怀旧情感测试"
            },
            {
                "text": "邻居家的孩子很吵，但是看到他们活蹦乱跳的样子，也挺羡慕的",
                "context": {"age": 72, "age_group": "senior", "living_situation": "独居"},
                "description": "老人复杂情感测试"
            }
        ]
        
        # 如果请求中包含自定义测试，使用自定义的
        data = request.get_json()
        if data and data.get('text'):
            test_cases = [{
                "text": data['text'],
                "context": data.get('user_context', {"age": 70, "age_group": "senior"}),
                "description": "自定义老人情感测试"
            }]
        else:
            test_cases = elderly_test_cases
        
        results = []
        
        for i, test_case in enumerate(test_cases):
            logger.info(f"执行测试用例 {i+1}: {test_case['description']}")
            
            try:
                # 分析情感
                emotion_result = emotion_analyzer.analyze_text(
                    test_case['text'], 
                    test_case['context']
                )
                
                # 添加测试结果
                test_result = {
                    'test_case': test_case,
                    'emotion_result': emotion_result,
                    'analysis': {
                        'is_elderly_detected': emotion_result.get('elderly_specific') is not None,
                        'has_elderly_suggestions': len(emotion_result.get('ai_suggestions', [])) > 0,
                        'model_used': emotion_result.get('analysis_model', 'unknown'),
                        'confidence_level': 'high' if emotion_result.get('confidence', 0) > 0.8 else 'medium' if emotion_result.get('confidence', 0) > 0.6 else 'low'
                    }
                }
                
                results.append(test_result)
                
            except Exception as e:
                logger.error(f"测试用例 {i+1} 失败: {str(e)}")
                results.append({
                    'test_case': test_case,
                    'error': str(e),
                    'status': 'failed'
                })
        
        # 统计结果
        successful_tests = len([r for r in results if 'error' not in r])
        elderly_optimized_tests = len([r for r in results if r.get('analysis', {}).get('is_elderly_detected', False)])
        
        response_data = {
            'success': True,
            'data': {
                'test_summary': {
                    'total_tests': len(results),
                    'successful_tests': successful_tests,
                    'elderly_optimized_tests': elderly_optimized_tests,
                    'deepseek_configured': bool(config.DEEPSEEK_API_KEY and not config.DEEPSEEK_API_KEY.startswith('your_'))
                },
                'test_results': results,
                'recommendations': [
                    '老人群体情感分析已针对性优化' if elderly_optimized_tests > 0 else '建议配置DeepSeek API以获得更好的老人情感分析效果',
                    '系统能识别家庭、健康、怀旧等老人特有情感主题',
                    '提供针对老人的专业心理建议'
                ]
            },
            'message': f'DeepSeek老人情感分析测试完成，成功率: {successful_tests}/{len(results)}'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"测试DeepSeek老人情感分析时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'DeepSeek老人情感分析测试失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

def init_application():
    """初始化应用"""
    try:
        # 验证配置
        config.validate_config()
        
        # 初始化数据库
        db_manager.init_database()
        
        # 初始化AI服务
        emotion_analyzer.init_models()
        image_generator.init_models()
        speech_service.init_models()
        
        logger.info("✅ PGG情感记忆生成系统启动成功")
        
    except Exception as e:
        logger.error(f"❌ 系统初始化失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.route('/health')
def health():
    """健康检查端点"""
    try:
        # 检查基本功能
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': 'PGG v1.0.0',
            'python_version': platform.python_version(),
            'system': platform.system(),
            'machine': platform.machine(),
            'services': {
                'emotion_analysis': True,
                'image_generation': True,
                'speech_to_text': True,
                'file_storage': True
            }
        }
        
        return jsonify(health_data)
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/config/status')
def config_status():
    """返回系统配置状态信息"""
    try:
        # 获取API配置状态
        api_statuses = {
            'openai': bool(config.OPENAI_API_KEY and not config.OPENAI_API_KEY.startswith('your_')),
            'deepseek': bool(config.DEEPSEEK_API_KEY and not config.DEEPSEEK_API_KEY.startswith('your_')),
            'iflytek_speech': bool(config.IFLYTEK_API_KEY and not config.IFLYTEK_API_KEY.startswith('your_')),
            'iflytek_image': bool(config.IFLYTEK_IMAGE_API_KEY and not config.IFLYTEK_IMAGE_API_KEY.startswith('your_')),
            'iflytek_gender_age': bool(config.IFLYTEK_GENDER_AGE_API_KEY and not config.IFLYTEK_GENDER_AGE_API_KEY.startswith('your_')),
            'midjourney': bool(getattr(config, 'MJ_API_KEY', '') and not getattr(config, 'MJ_API_KEY', '').startswith('your_')),
            'azure_speech': bool(getattr(config, 'AZURE_SPEECH_KEY', '') and not getattr(config, 'AZURE_SPEECH_KEY', '').startswith('your_')),
            'google_speech': bool(getattr(config, 'GOOGLE_SPEECH_KEY', '') and not getattr(config, 'GOOGLE_SPEECH_KEY', '').startswith('your_')),
            'baidu_speech': bool(getattr(config, 'BAIDU_SPEECH_API_KEY', '') and not getattr(config, 'BAIDU_SPEECH_API_KEY', '').startswith('your_')),
            'tencent_speech': bool(getattr(config, 'TENCENT_SPEECH_SECRET_ID', '') and not getattr(config, 'TENCENT_SPEECH_SECRET_ID', '').startswith('your_')),
            'alibaba_speech': bool(getattr(config, 'ALIBABA_SPEECH_ACCESS_KEY', '') and not getattr(config, 'ALIBABA_SPEECH_ACCESS_KEY', '').startswith('your_'))
        }
        
        # 获取模型状态
        model_statuses = {
            'emotion': True,  # 情感分析模型始终可用
            'image': True,    # 图像生成至少有模拟模式
            'speech': True,   # 语音识别至少有模拟模式
            'nlp': True       # 自然语言处理
        }
        
        # 系统配置信息
        system_config = {
            'debug_mode': config.DEBUG,
            'storage_mode': 'Local' if config.USE_LOCAL_STORAGE else 'Database',
            'cpu_mode': config.USE_CPU_ONLY,
            'accuracy_priority': config.PRIORITIZE_ACCURACY,
            'max_memory': config.MAX_MEMORY_USAGE,
            'batch_size': config.BATCH_SIZE,
            'server_port': config.PORT,
            'max_file_size': f"{config.MAX_CONTENT_LENGTH // (1024*1024)}MB",
            'supported_languages': ['zh-CN', 'en-US', 'ja-JP', 'ko-KR']
        }
        
        # 统计信息
        stats = {
            'total_apis': len([k for k, v in api_statuses.items() if v]),
            'total_models': len([k for k, v in model_statuses.items() if v]),
            'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
        }
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'api_statuses': api_statuses,
            'model_statuses': model_statuses,
            'system_config': system_config,
            'stats': stats,
            **system_config  # 将系统配置平铺到根级别，便于前端访问
        })
        
    except Exception as e:
        logger.error(f"获取配置状态失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ==================== 老人数据管理API ====================

@app.route('/elderly/emotions', methods=['GET'])
def get_elderly_emotions():
    """获取老人情感数据"""
    try:
        logger.info("获取老人情感数据请求")
        
        # 获取查询参数
        user_id = request.args.get('user_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        emotion_filter = request.args.get('emotion_filter')
        age_filter = request.args.get('age_filter')
        age_filter = int(age_filter) if age_filter else None
        
        # 获取数据
        result = elderly_data_manager.get_elderly_emotions(
            user_id=user_id,
            page=page,
            per_page=per_page,
            emotion_filter=emotion_filter,
            age_filter=age_filter
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '老人情感数据获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取老人情感数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取老人情感数据失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/elderly/statistics', methods=['GET'])
def get_elderly_statistics():
    """获取老人情感统计数据"""
    try:
        logger.info("获取老人情感统计数据请求")
        
        user_id = request.args.get('user_id')
        
        # 获取统计数据
        stats = elderly_data_manager.get_elderly_statistics(user_id=user_id)
        
        return jsonify({
            'success': True,
            'data': stats,
            'message': '老人情感统计数据获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取老人情感统计数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取老人情感统计数据失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/elderly/export', methods=['POST'])
def export_elderly_data():
    """导出老人情感数据"""
    try:
        logger.info("导出老人情感数据请求")
        
        data = request.get_json()
        format_type = data.get('format', 'csv')
        user_id = data.get('user_id')
        
        # 导出数据
        export_path = elderly_data_manager.export_elderly_data(
            format=format_type,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'export_path': export_path,
                'format': format_type,
                'user_id': user_id
            },
            'message': '老人情感数据导出成功'
        })
        
    except Exception as e:
        logger.error(f"导出老人情感数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '导出老人情感数据失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/elderly/keywords', methods=['GET'])
def get_elderly_keywords():
    """获取老人关键词配置"""
    try:
        logger.info("获取老人关键词配置请求")
        
        return jsonify({
            'success': True,
            'data': {
                'keywords': config.ELDERLY_KEYWORDS,
                'keyword_count': len(config.ELDERLY_KEYWORDS),
                'min_age': config.ELDERLY_MIN_AGE,
                'keyword_threshold': config.ELDERLY_KEYWORD_THRESHOLD,
                'storage_type': config.ELDERLY_DATA_STORAGE_TYPE
            },
            'message': '老人关键词配置获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取老人关键词配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取老人关键词配置失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/elderly/test', methods=['POST'])
def test_elderly_detection():
    """测试老人群体检测"""
    try:
        logger.info("测试老人群体检测请求")
        
        data = request.get_json()
        text = data.get('text', '')
        user_context = data.get('user_context', {})
        
        # 测试检测
        is_elderly = elderly_data_manager.is_elderly_context(user_context, text)
        matched_keywords = elderly_data_manager.get_matched_keywords(text)
        
        return jsonify({
            'success': True,
            'data': {
                'input': {
                    'text': text,
                    'user_context': user_context
                },
                'detection_result': {
                    'is_elderly': is_elderly,
                    'matched_keywords': matched_keywords,
                    'keyword_count': len(matched_keywords),
                    'age_based': user_context.get('age', 0) >= config.ELDERLY_MIN_AGE,
                    'keyword_based': len(matched_keywords) >= config.ELDERLY_KEYWORD_THRESHOLD
                },
                'configuration': {
                    'min_age': config.ELDERLY_MIN_AGE,
                    'keyword_threshold': config.ELDERLY_KEYWORD_THRESHOLD,
                    'total_keywords': len(config.ELDERLY_KEYWORDS)
                }
            },
            'message': '老人群体检测测试完成'
        })
        
    except Exception as e:
        logger.error(f"测试老人群体检测失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '测试老人群体检测失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# ==================== 系统监控API ====================

# ==================== 传感器硬件接口 ====================

@app.route('/sensors/data', methods=['POST'])
def receive_sensor_data():
    """接收传感器数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供有效的传感器数据'
            }), 400
        
        # 解析传感器数据
        sensor_data = SensorData(
            sensor_id=data.get('sensor_id'),
            sensor_type=data.get('sensor_type'),
            device_id=data.get('device_id'),
            user_id=data.get('user_id'),
            value=data.get('data', {}).get('value'),
            unit=data.get('data', {}).get('unit'),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()).replace('Z', '+00:00'))
        )
        
        # 设置可选字段
        sensor_data.quality = data.get('data', {}).get('quality', 'good')
        sensor_data.raw_data = data.get('data', {}).get('raw_data', [])
        sensor_data.metadata = data.get('metadata', {})
        
        # 保存传感器数据
        success = sensor_manager.save_sensor_data(sensor_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': '传感器数据接收成功',
                'data': {
                    'sensor_id': sensor_data.sensor_id,
                    'timestamp': sensor_data.timestamp.isoformat(),
                    'stored': True
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据存储失败',
                'message': '传感器数据保存失败'
            }), 500
            
    except Exception as e:
        logger.error(f"接收传感器数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '数据处理失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/sensors/data/batch', methods=['POST'])
def receive_sensor_data_batch():
    """批量接收传感器数据"""
    try:
        data = request.get_json()
        if not data or 'data_points' not in data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供有效的批量传感器数据'
            }), 400
        
        data_points = data['data_points']
        device_id = data.get('device_id')
        user_id = data.get('user_id')
        
        results = []
        success_count = 0
        
        for point in data_points:
            try:
                sensor_data = SensorData(
                    sensor_id=point.get('sensor_id'),
                    sensor_type=point.get('sensor_type'),
                    device_id=device_id or point.get('device_id'),
                    user_id=user_id or point.get('user_id'),
                    value=point.get('data', {}).get('value'),
                    unit=point.get('data', {}).get('unit'),
                    timestamp=datetime.fromisoformat(point.get('timestamp', datetime.now().isoformat()).replace('Z', '+00:00'))
                )
                
                success = sensor_manager.save_sensor_data(sensor_data)
                results.append({
                    'sensor_id': sensor_data.sensor_id,
                    'success': success,
                    'timestamp': sensor_data.timestamp.isoformat()
                })
                
                if success:
                    success_count += 1
                    
            except Exception as e:
                results.append({
                    'sensor_id': point.get('sensor_id', 'unknown'),
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'message': f'批量处理完成，成功: {success_count}/{len(data_points)}',
            'data': {
                'total_processed': len(data_points),
                'successful': success_count,
                'failed': len(data_points) - success_count,
                'results': results
            }
        })
        
    except Exception as e:
        logger.error(f"批量接收传感器数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '批量处理失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/sensors/status', methods=['GET'])
def get_sensor_status():
    """获取传感器状态"""
    try:
        device_id = request.args.get('device_id')
        sensor_type = request.args.get('sensor_type')
        
        device_status = sensor_manager.get_device_status(device_id)
        
        return jsonify({
            'success': True,
            'data': device_status,
            'message': '成功获取传感器状态'
        })
        
    except Exception as e:
        logger.error(f"获取传感器状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取状态失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/sensors/health', methods=['GET'])
def get_sensor_health():
    """获取传感器系统健康状态"""
    try:
        health_status = sensor_manager.get_health_check()
        
        return jsonify({
            'success': True,
            'data': health_status,
            'message': '成功获取传感器系统健康状态'
        })
        
    except Exception as e:
        logger.error(f"获取传感器健康状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取健康状态失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/sensors/history', methods=['GET'])
def get_sensor_history():
    """获取传感器历史数据"""
    try:
        user_id = request.args.get('user_id')
        sensor_type = request.args.get('sensor_type')
        device_id = request.args.get('device_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = int(request.args.get('limit', 100))
        
        # 解析时间参数
        start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00')) if start_time else None
        end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00')) if end_time else None
        
        # 获取历史数据
        sensor_data_list = sensor_manager.get_sensor_data(
            user_id=user_id,
            sensor_type=sensor_type,
            device_id=device_id,
            start_time=start_datetime,
            end_time=end_datetime,
            limit=limit
        )
        
        # 转换为字典格式
        data_dicts = [data.to_dict() for data in sensor_data_list]
        
        return jsonify({
            'success': True,
            'data': {
                'sensor_data': data_dicts,
                'total_records': len(data_dicts),
                'query_params': {
                    'user_id': user_id,
                    'sensor_type': sensor_type,
                    'device_id': device_id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'limit': limit
                }
            },
            'message': f'成功获取{len(data_dicts)}条传感器历史数据'
        })
        
    except Exception as e:
        logger.error(f"获取传感器历史数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取历史数据失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/sensors/devices/register', methods=['POST'])
def register_sensor_device():
    """注册传感器设备"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供有效的设备信息'
            }), 400
        
        # 创建设备对象
        device = SensorDevice(
            device_id=data.get('device_id'),
            device_type=data.get('device_type'),
            manufacturer=data.get('manufacturer', ''),
            model=data.get('model', ''),
            firmware_version=data.get('firmware_version', ''),
            supported_sensors=data.get('supported_sensors', [])
        )
        
        # 注册设备
        success = sensor_manager.register_device(device)
        
        if success:
            return jsonify({
                'success': True,
                'message': '设备注册成功',
                'data': {
                    'device_id': device.device_id,
                    'device_type': device.device_type,
                    'registered_at': device.last_seen.isoformat(),
                    'supported_sensors': device.supported_sensors
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '设备注册失败',
                'message': '设备信息保存失败'
            }), 500
            
    except Exception as e:
        logger.error(f"注册传感器设备失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '设备注册失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/sensors/analyze/emotion', methods=['POST'])
def analyze_sensor_emotion():
    """基于传感器数据分析情感"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供有效的传感器数据'
            }), 400
        
        user_id = data.get('user_id')
        sensor_data = data.get('sensor_data', {})
        context = data.get('context', {})
        
        if not sensor_data:
            return jsonify({
                'success': False,
                'error': '传感器数据为空',
                'message': '请提供要分析的传感器数据'
            }), 400
        
        # 进行情感分析
        emotion_result = sensor_manager.analyze_sensor_emotion(user_id, sensor_data, context)
        
        return jsonify({
            'success': True,
            'data': {
                'emotion_analysis': emotion_result,
                'user_id': user_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'input_data': {
                    'sensor_data': sensor_data,
                    'context': context
                }
            },
            'message': '传感器情感分析完成'
        })
        
    except Exception as e:
        logger.error(f"传感器情感分析失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '情感分析失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/sensors/analyze/anomaly', methods=['POST'])
def analyze_sensor_anomaly():
    """传感器数据异常检测"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供有效的传感器数据'
            }), 400
        
        sensor_data = data.get('sensor_data', {})
        detection_config = data.get('detection_config', {})
        
        if not sensor_data:
            return jsonify({
                'success': False,
                'error': '传感器数据为空',
                'message': '请提供要检测的传感器数据'
            }), 400
        
        # 进行异常检测
        anomaly_result = sensor_manager.detect_anomalies(sensor_data, detection_config)
        
        return jsonify({
            'success': True,
            'data': {
                'anomaly_detection': anomaly_result,
                'detection_config': detection_config,
                'analysis_timestamp': datetime.now().isoformat()
            },
            'message': '传感器异常检测完成'
        })
        
    except Exception as e:
        logger.error(f"传感器异常检测失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '异常检测失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/sensors/config', methods=['GET'])
def get_sensor_config():
    """获取传感器配置"""
    try:
        sensor_id = request.args.get('sensor_id')
        
        # 返回传感器配置信息
        config_data = {
            'supported_sensor_types': sensor_manager.supported_sensor_types,
            'sensor_value_ranges': sensor_manager.sensor_value_ranges,
            'system_config': {
                'storage_type': 'local' if sensor_manager.use_local_storage else 'database',
                'data_retention_days': getattr(config, 'SENSOR_DATA_RETENTION_DAYS', 30),
                'batch_size': getattr(config, 'SENSOR_BATCH_SIZE', 100),
                'sampling_rate': getattr(config, 'SENSOR_SAMPLING_RATE', 10)
            }
        }
        
        if sensor_id:
            config_data['sensor_id'] = sensor_id
            # TODO: 获取特定传感器的配置
        
        return jsonify({
            'success': True,
            'data': config_data,
            'message': '成功获取传感器配置'
        })
        
    except Exception as e:
        logger.error(f"获取传感器配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取配置失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/sensors/stream', methods=['GET'])
def get_sensor_stream():
    """获取传感器数据流信息"""
    try:
        sensor_id = request.args.get('sensor_id')
        sensor_type = request.args.get('sensor_type')
        data_format = request.args.get('format', 'json')
        
        # 返回流式数据配置信息
        stream_info = {
            'stream_available': True,
            'supported_formats': ['json', 'csv', 'binary'],
            'current_format': data_format,
            'websocket_url': f"ws://{request.host}/sensors/ws",
            'query_params': {
                'sensor_id': sensor_id,
                'sensor_type': sensor_type,
                'format': data_format
            },
            'stream_config': {
                'max_connections': 100,
                'heartbeat_interval': 30,
                'buffer_size': 1000
            }
        }
        
        return jsonify({
            'success': True,
            'data': stream_info,
            'message': '成功获取传感器数据流信息'
        })
        
    except Exception as e:
        logger.error(f"获取传感器数据流失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取数据流失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

# ==================== CSV文档处理接口 ====================

@app.route('/csv/export', methods=['POST'])
def csv_export():
    """CSV数据导出"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供要导出的数据'
            }), 400
        
        export_data = data.get('data', [])
        export_type = data.get('type', 'general')
        filename = data.get('filename')
        options = data.get('options', {})
        
        # 导出选项
        include_headers = options.get('include_headers', True)
        encoding = options.get('encoding', 'utf-8')
        delimiter = options.get('delimiter', ',')
        custom_fields = options.get('custom_fields')
        
        if not export_data:
            return jsonify({
                'success': False,
                'error': '导出数据为空',
                'message': '请提供要导出的数据'
            }), 400
        
        # 执行导出
        export_result = csv_manager.export_to_csv(
            data=export_data,
            export_type=export_type,
            filename=filename,
            include_headers=include_headers,
            encoding=encoding,
            delimiter=delimiter,
            custom_fields=custom_fields
        )
        
        if export_result['success']:
            return jsonify({
                'success': True,
                'message': 'CSV导出成功',
                'data': export_result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'CSV导出失败',
                'message': export_result.get('error', '导出过程中发生错误')
            }), 500
            
    except Exception as e:
        logger.error(f"CSV导出失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'CSV导出失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/import', methods=['POST'])
def csv_import():
    """CSV数据导入"""
    try:
        # 检查上传的文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到上传文件',
                'message': '请选择要导入的CSV文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空',
                'message': '请选择有效的CSV文件'
            }), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                'success': False,
                'error': '文件格式不正确',
                'message': '只支持CSV格式文件'
            }), 400
        
        # 获取导入选项
        import_type = request.form.get('type', 'general')
        encoding = request.form.get('encoding', 'utf-8')
        delimiter = request.form.get('delimiter', ',')
        skip_header = request.form.get('skip_header', 'true').lower() == 'true'
        validate_data = request.form.get('validate_data', 'true').lower() == 'true'
        
        # 保存临时文件
        temp_path = os.path.join(csv_manager.csv_import_path, file.filename)
        file.save(temp_path)
        
        try:
            # 导入数据
            import_result = csv_manager.import_from_csv(
                file_path=temp_path,
                import_type=import_type,
                encoding=encoding,
                delimiter=delimiter,
                skip_header=skip_header,
                validate_data=validate_data
            )
            
            if import_result['success']:
                return jsonify({
                    'success': True,
                    'message': 'CSV导入成功',
                    'data': import_result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'CSV导入失败',
                    'message': import_result.get('error', '导入过程中发生错误')
                }), 500
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
    except Exception as e:
        logger.error(f"CSV导入失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'CSV导入失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/analyze', methods=['POST'])
def csv_analyze():
    """CSV文件结构分析"""
    try:
        # 检查上传的文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到上传文件',
                'message': '请选择要分析的CSV文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename.lower().endswith('.csv'):
            return jsonify({
                'success': False,
                'error': '文件格式不正确',
                'message': '只支持CSV格式文件'
            }), 400
        
        # 获取分析选项
        encoding = request.form.get('encoding', 'utf-8')
        delimiter = request.form.get('delimiter', ',')
        sample_size = int(request.form.get('sample_size', 100))
        
        # 保存临时文件
        temp_path = os.path.join(csv_manager.csv_import_path, file.filename)
        file.save(temp_path)
        
        try:
            # 分析文件结构
            analysis_result = csv_manager.analyze_csv_structure(
                file_path=temp_path,
                encoding=encoding,
                delimiter=delimiter,
                sample_size=sample_size
            )
            
            if analysis_result['success']:
                return jsonify({
                    'success': True,
                    'message': 'CSV文件分析成功',
                    'data': analysis_result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'CSV文件分析失败',
                    'message': analysis_result.get('error', '分析过程中发生错误')
                }), 500
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
    except Exception as e:
        logger.error(f"CSV文件分析失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'CSV文件分析失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/template', methods=['POST'])
def csv_template():
    """创建CSV模板"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'message': '请提供模板配置参数'
            }), 400
        
        template_type = data.get('type', 'general')
        include_examples = data.get('include_examples', True)
        custom_fields = data.get('custom_fields')
        
        # 创建模板
        template_result = csv_manager.create_csv_template(
            template_type=template_type,
            include_examples=include_examples,
            custom_fields=custom_fields
        )
        
        if template_result['success']:
            return jsonify({
                'success': True,
                'message': 'CSV模板创建成功',
                'data': template_result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'CSV模板创建失败',
                'message': template_result.get('error', '创建过程中发生错误')
            }), 500
            
    except Exception as e:
        logger.error(f"CSV模板创建失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'CSV模板创建失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/convert', methods=['POST'])
def csv_convert():
    """CSV格式转换"""
    try:
        # 检查上传的文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到上传文件',
                'message': '请选择要转换的CSV文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename.lower().endswith('.csv'):
            return jsonify({
                'success': False,
                'error': '文件格式不正确',
                'message': '只支持CSV格式文件'
            }), 400
        
        # 获取转换参数
        from_type = request.form.get('from_type', 'general')
        to_type = request.form.get('to_type', 'general')
        mapping_rules = request.form.get('mapping_rules')
        
        if mapping_rules:
            try:
                mapping_rules = json.loads(mapping_rules)
            except:
                mapping_rules = None
        
        # 保存临时文件
        temp_input = os.path.join(csv_manager.csv_import_path, file.filename)
        file.save(temp_input)
        
        # 生成输出文件路径
        output_filename = f"converted_{file.filename}"
        temp_output = os.path.join(csv_manager.csv_export_path, output_filename)
        
        try:
            # 执行转换
            convert_result = csv_manager.convert_csv_format(
                input_file=temp_input,
                output_file=temp_output,
                from_type=from_type,
                to_type=to_type,
                mapping_rules=mapping_rules
            )
            
            if convert_result['success']:
                return jsonify({
                    'success': True,
                    'message': 'CSV格式转换成功',
                    'data': convert_result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'CSV格式转换失败',
                    'message': convert_result.get('error', '转换过程中发生错误')
                }), 500
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_input):
                os.remove(temp_input)
            
    except Exception as e:
        logger.error(f"CSV格式转换失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'CSV格式转换失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/merge', methods=['POST'])
def csv_merge():
    """CSV文件合并"""
    try:
        # 检查上传的文件
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到上传文件',
                'message': '请选择要合并的CSV文件'
            }), 400
        
        files = request.files.getlist('files')
        if not files or len(files) < 2:
            return jsonify({
                'success': False,
                'error': '文件数量不足',
                'message': '至少需要2个CSV文件进行合并'
            }), 400
        
        # 获取合并参数
        merge_type = request.form.get('merge_type', 'union')
        remove_duplicates = request.form.get('remove_duplicates', 'true').lower() == 'true'
        key_fields = request.form.get('key_fields')
        
        if key_fields:
            try:
                key_fields = json.loads(key_fields)
            except:
                key_fields = None
        
        # 保存临时文件
        temp_files = []
        for file in files:
            if file.filename.lower().endswith('.csv'):
                temp_path = os.path.join(csv_manager.csv_import_path, file.filename)
                file.save(temp_path)
                temp_files.append(temp_path)
        
        if not temp_files:
            return jsonify({
                'success': False,
                'error': '没有有效的CSV文件',
                'message': '请确保上传的文件都是CSV格式'
            }), 400
        
        # 生成输出文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"merged_{timestamp}.csv"
        output_path = os.path.join(csv_manager.csv_export_path, output_filename)
        
        try:
            # 执行合并
            merge_result = csv_manager.merge_csv_files(
                input_files=temp_files,
                output_file=output_path,
                merge_type=merge_type,
                remove_duplicates=remove_duplicates,
                key_fields=key_fields
            )
            
            if merge_result['success']:
                return jsonify({
                    'success': True,
                    'message': 'CSV文件合并成功',
                    'data': merge_result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'CSV文件合并失败',
                    'message': merge_result.get('error', '合并过程中发生错误')
                }), 500
                
        finally:
            # 清理临时文件
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
    except Exception as e:
        logger.error(f"CSV文件合并失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'CSV文件合并失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/split', methods=['POST'])
def csv_split():
    """CSV文件拆分"""
    try:
        # 检查上传的文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到上传文件',
                'message': '请选择要拆分的CSV文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename.lower().endswith('.csv'):
            return jsonify({
                'success': False,
                'error': '文件格式不正确',
                'message': '只支持CSV格式文件'
            }), 400
        
        # 获取拆分参数
        split_by = request.form.get('split_by', 'rows')
        split_size = int(request.form.get('split_size', 1000))
        split_field = request.form.get('split_field')
        
        # 保存临时文件
        temp_input = os.path.join(csv_manager.csv_import_path, file.filename)
        file.save(temp_input)
        
        # 创建输出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(csv_manager.csv_export_path, f"split_{timestamp}")
        
        try:
            # 执行拆分
            split_result = csv_manager.split_csv_file(
                input_file=temp_input,
                output_dir=output_dir,
                split_by=split_by,
                split_size=split_size,
                split_field=split_field
            )
            
            if split_result['success']:
                return jsonify({
                    'success': True,
                    'message': 'CSV文件拆分成功',
                    'data': split_result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'CSV文件拆分失败',
                    'message': split_result.get('error', '拆分过程中发生错误')
                }), 500
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_input):
                os.remove(temp_input)
            
    except Exception as e:
        logger.error(f"CSV文件拆分失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'CSV文件拆分失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/validate', methods=['POST'])
def csv_validate():
    """CSV文件验证"""
    try:
        # 检查上传的文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到上传文件',
                'message': '请选择要验证的CSV文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename.lower().endswith('.csv'):
            return jsonify({
                'success': False,
                'error': '文件格式不正确',
                'message': '只支持CSV格式文件'
            }), 400
        
        # 获取验证参数
        validation_type = request.form.get('validation_type', 'general')
        custom_rules = request.form.get('custom_rules')
        
        if custom_rules:
            try:
                custom_rules = json.loads(custom_rules)
            except:
                custom_rules = None
        
        # 保存临时文件
        temp_path = os.path.join(csv_manager.csv_import_path, file.filename)
        file.save(temp_path)
        
        try:
            # 执行验证
            validation_result = csv_manager.validate_csv_file(
                file_path=temp_path,
                validation_type=validation_type,
                custom_rules=custom_rules
            )
            
            if validation_result['success']:
                return jsonify({
                    'success': True,
                    'message': 'CSV文件验证完成',
                    'data': validation_result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'CSV文件验证失败',
                    'message': validation_result.get('error', '验证过程中发生错误')
                }), 500
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
    except Exception as e:
        logger.error(f"CSV文件验证失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'CSV文件验证失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/statistics', methods=['POST'])
def csv_statistics():
    """CSV文件统计分析"""
    try:
        # 检查上传的文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到上传文件',
                'message': '请选择要分析的CSV文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename.lower().endswith('.csv'):
            return jsonify({
                'success': False,
                'error': '文件格式不正确',
                'message': '只支持CSV格式文件'
            }), 400
        
        # 保存临时文件
        temp_path = os.path.join(csv_manager.csv_import_path, file.filename)
        file.save(temp_path)
        
        try:
            # 执行统计分析
            statistics_result = csv_manager.get_csv_statistics(temp_path)
            
            if statistics_result['success']:
                return jsonify({
                    'success': True,
                    'message': 'CSV文件统计分析完成',
                    'data': statistics_result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'CSV文件统计分析失败',
                    'message': statistics_result.get('error', '分析过程中发生错误')
                }), 500
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
    except Exception as e:
        logger.error(f"CSV文件统计分析失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'CSV文件统计分析失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/formats', methods=['GET'])
def csv_formats():
    """获取支持的CSV格式"""
    try:
        formats = csv_manager.supported_formats
        
        return jsonify({
            'success': True,
            'data': {
                'supported_formats': list(formats.keys()),
                'format_details': formats
            },
            'message': '成功获取支持的CSV格式'
        })
        
    except Exception as e:
        logger.error(f"获取CSV格式失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取CSV格式失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/download/<filename>', methods=['GET'])
def csv_download(filename):
    """下载CSV文件"""
    try:
        # 检查文件路径
        file_path = None
        
        # 在导出目录中查找
        export_path = os.path.join(csv_manager.csv_export_path, filename)
        if os.path.exists(export_path):
            file_path = export_path
        
        # 在模板目录中查找
        if not file_path:
            template_path = os.path.join(csv_manager.csv_templates_path, filename)
            if os.path.exists(template_path):
                file_path = template_path
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': '文件不存在',
                'message': f'未找到文件: {filename}'
            }), 404
        
        # 返回文件
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        logger.error(f"CSV文件下载失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'CSV文件下载失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/keywords/analyze', methods=['POST'])
def analyze_csv_keywords():
    """分析CSV数据中的关键词"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
            
        # 获取参数
        csv_data = data.get('data', [])
        format_type = data.get('format', 'general')
        
        if not csv_data:
            return jsonify({
                'success': False,
                'error': '数据为空'
            }), 400
            
        # 执行关键词分析
        result = csv_manager.analyze_keywords(csv_data, format_type)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"CSV关键词分析失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'CSV关键词分析失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/keywords/export', methods=['POST'])
def export_keywords_csv():
    """导出关键词分析结果为CSV"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
            
        # 获取参数
        csv_data = data.get('data', [])
        format_type = data.get('format', 'general')
        filename = data.get('filename', f'keywords_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        if not csv_data:
            return jsonify({
                'success': False,
                'error': '数据为空'
            }), 400
            
        # 执行关键词分析
        analysis_result = csv_manager.analyze_keywords(csv_data, format_type)
        
        if not analysis_result['success']:
            return jsonify(analysis_result), 400
            
        # 准备导出的关键词数据
        keyword_data = []
        keyword_analysis = analysis_result['data']['keyword_analysis']
        
        # 关键词频率数据
        for keyword, count in keyword_analysis['keyword_frequency'].items():
            keyword_data.append({
                'keyword': keyword,
                'frequency': count,
                'category': '未分类'  # 可以根据需要添加分类逻辑
            })
            
        # 导出为CSV
        export_result = csv_manager.export_csv(keyword_data, filename, 'keywords')
        
        return jsonify(export_result)
        
    except Exception as e:
        logger.error(f"关键词CSV导出失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '关键词CSV导出失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

@app.route('/csv/keywords/config', methods=['GET'])
def get_keywords_config():
    """获取关键词配置"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'keywords': config.ELDERLY_KEYWORDS,
                'total_keywords': len(config.ELDERLY_KEYWORDS),
                'keyword_threshold': config.ELDERLY_KEYWORD_THRESHOLD,
                'min_age': config.ELDERLY_MIN_AGE,
                'categories': {
                    '基础关键词': config.ELDERLY_KEYWORDS[0:9],
                    '家庭关系': config.ELDERLY_KEYWORDS[9:25],
                    '生活相关': config.ELDERLY_KEYWORDS[25:42],
                    '社交与活动': config.ELDERLY_KEYWORDS[42:59],
                    '情感状态': config.ELDERLY_KEYWORDS[59:78],
                    '生活状态': config.ELDERLY_KEYWORDS[78:94],
                    '补充关键词': config.ELDERLY_KEYWORDS[94:]
                }
            },
            'message': f'关键词配置获取成功，共{len(config.ELDERLY_KEYWORDS)}个关键词'
        })
        
    except Exception as e:
        logger.error(f"获取关键词配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取关键词配置失败',
            'message': str(e) if config.DEBUG else '请稍后重试'
        }), 500

if __name__ == '__main__':
    try:
        # 初始化应用
        init_application()
        
        # 启动Flask应用
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭系统...")
    except Exception as e:
        logger.error(f"启动失败: {str(e)}")
        logger.error(traceback.format_exc()) 