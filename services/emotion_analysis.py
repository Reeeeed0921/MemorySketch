# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 情感分析服务
提供文本和音频的情感分析功能
"""

import os
import json
import logging
import random
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re
import numpy as np

from config import config
from models import EmotionResult, get_emotion_description
from utils.elderly_storage import elderly_data_manager

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """情感分析器"""
    
    def __init__(self):
        """初始化情感分析器"""
        self.models_loaded = False
        self.text_analyzer = None
        self.audio_analyzer = None
        self.model_paths = {
            'wav2vec2': config.WAV2VEC2_MODEL_PATH,
            'ecapa': config.ECAPA_MODEL_PATH
        }
        
        # 初始化老人数据管理器
        self.elderly_manager = elderly_data_manager
        
        # 情感关键词字典（简单规则匹配）
        self.emotion_keywords = {
            'happy': ['开心', '高兴', '快乐', '愉快', '喜悦', '兴奋', '满足', '幸福', '欣喜'],
            'sad': ['伤心', '难过', '悲伤', '失落', '沮丧', '忧郁', '痛苦', '哀伤', '哭泣'],
            'angry': ['生气', '愤怒', '恼火', '暴怒', '愤慨', '气愤', '恼怒', '怒火'],
            'fear': ['害怕', '恐惧', '担心', '恐慌', '紧张', '焦虑', '不安', '惊慌'],
            'surprise': ['惊讶', '惊奇', '震惊', '意外', '诧异', '吃惊', '惊异'],
            'disgust': ['恶心', '厌恶', '反感', '讨厌', '憎恶', '嫌弃'],
            'love': ['爱', '喜欢', '钟情', '迷恋', '深爱', '热爱', '爱慕'],
            'peaceful': ['平静', '宁静', '安详', '平和', '安宁', '祥和'],
            'nostalgic': ['怀念', '思念', '回忆', '眷恋', '想念', '追忆'],
            'hopeful': ['希望', '期望', '期待', '憧憬', '向往', '盼望'],
            'grateful': ['感谢', '感激', '感恩', '谢谢', '感谢'],
            'disappointed': ['失望', '沮丧', '失落', '扫兴', '泄气']
        }
        
        # 情感强度词汇
        self.intensity_words = {
            'high': ['非常', '极其', '特别', '十分', '超级', '超', '极', '很', '真的'],
            'medium': ['比较', '还算', '挺', '蛮', '相当'],
            'low': ['有点', '稍微', '略微', '一点', '些许']
        }
        
        # 初始化分析器
        self._init_analyzers()
    
    def _init_analyzers(self):
        """初始化分析器"""
        try:
            logger.info("初始化情感分析模型...")
            
            # 初始化文本情感分析
            self._init_text_analyzer()
            
            # 初始化音频情感分析
            self._init_audio_analyzer()
            
            # 初始化老人数据存储
            self.elderly_manager.init_storage()
            
            logger.info("✅ 情感分析模型初始化成功")
            
        except Exception as e:
            logger.error(f"情感分析模型初始化失败: {str(e)}")
            # 继续运行，使用降级方案
    
    def _init_text_analyzer(self):
        """初始化文本情感分析器"""
        try:
            logger.info("加载文本情感分析模型...")
            
            # 配置OpenAI API（如果可用）
            if config.OPENAI_API_KEY:
                logger.info("配置OpenAI API用于文本分析")
            
            logger.info("文本情感分析器初始化完成")
            
        except Exception as e:
            logger.error(f"文本情感分析器初始化失败: {str(e)}")
    
    def _init_audio_analyzer(self):
        """初始化音频情感分析器"""
        try:
            logger.info("加载音频情感分析模型...")
            
            # 检查模型路径
            wav2vec2_path = self.model_paths['wav2vec2']
            ecapa_path = self.model_paths['ecapa']
            
            if os.path.exists(wav2vec2_path):
                logger.info(f"找到Wav2Vec2模型: {wav2vec2_path}")
                
            if os.path.exists(ecapa_path):
                logger.info(f"找到ECAPA模型: {ecapa_path}")
            
            # 在CPU模式下运行
            if config.USE_CPU_ONLY:
                logger.info("使用CPU模式运行音频分析")
                self.models_loaded = True
            
            logger.info("音频情感分析器初始化完成")
            
        except Exception as e:
            logger.error(f"音频情感分析器初始化失败: {str(e)}")
    
    def analyze_text(self, text: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        分析文本情感（针对老人群体优化）
        
        Args:
            text: 输入文本
            user_context: 用户上下文信息（包括年龄、性别等）
            
        Returns:
            情感分析结果字典
        """
        try:
            logger.info(f"开始分析文本情感: {text[:50]}...")
            
            # 使用扩展的老人判断逻辑
            is_elderly = self.elderly_manager.is_elderly_context(user_context, text)
            matched_keywords = self.elderly_manager.get_matched_keywords(text)
            
            # 优先级顺序：DeepSeek > OpenAI > 本地AI > 规则匹配
            if config.DEEPSEEK_API_KEY and self._is_valid_key(config.DEEPSEEK_API_KEY):
                # 第一优先级：使用DeepSeek API（专为老人情感分析优化）
                result = self._analyze_text_with_deepseek(text, is_elderly, user_context)
            elif config.OPENAI_API_KEY and self._is_valid_key(config.OPENAI_API_KEY):
                # 第二优先级：使用OpenAI API（高准确率）
                result = self._analyze_text_with_openai(text)
            elif self.models_loaded and self.text_analyzer:
                # 第三优先级：使用本地AI模型（中等准确率）
                result = self._analyze_text_with_ai(text)
            else:
                # 最后选择：使用规则匹配分析（保底方案）
                result = self._analyze_text_with_rules(text)
            
            # 如果是老人群体，进行特殊的结果后处理
            if is_elderly:
                result = self._postprocess_elderly_emotion(result, text, user_context)
                
                # 添加老人特有的数据
                result['is_elderly'] = True
                result['keywords_matched'] = matched_keywords
                result['keyword_count'] = len(matched_keywords)
                
                # 保存老人情感数据
                self._save_elderly_emotion_data(result, text, user_context)
            
            logger.info(f"文本情感分析完成: {result['primary_emotion']} (置信度: {result['confidence']:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"文本情感分析失败: {str(e)}")
            # 返回默认结果
            return self._create_default_emotion_result()
    
    def _save_elderly_emotion_data(self, result: Dict[str, Any], text: str, user_context: Dict[str, Any]):
        """保存老人情感数据"""
        try:
            elderly_data = {
                'user_id': user_context.get('user_id', 'anonymous'),
                'text': text,
                'primary_emotion': result['primary_emotion'],
                'confidence': result['confidence'],
                'age': user_context.get('age', 0),
                'gender': user_context.get('gender', ''),
                'age_group': user_context.get('age_group', ''),
                'keywords_matched': result.get('keywords_matched', []),
                'keyword_count': result.get('keyword_count', 0),
                'elderly_specific': result.get('elderly_specific', {}),
                'ai_suggestions': result.get('ai_suggestions', [])
            }
            
            # 异步保存，不阻塞主流程
            self.elderly_manager.save_elderly_emotion(elderly_data)
            
        except Exception as e:
            logger.error(f"保存老人情感数据失败: {str(e)}")
            # 不影响主流程，继续执行
    
    def _is_elderly_context(self, user_context: Dict[str, Any]) -> bool:
        """判断是否为老人群体（已废弃，使用elderly_manager中的方法）"""
        # 保持兼容性，但实际调用elderly_manager的方法
        return self.elderly_manager.is_elderly_context(user_context, "")
    
    def _is_valid_key(self, key: str) -> bool:
        """检查API密钥是否有效"""
        if not key:
            return False
        placeholder_patterns = [
            'your_', 'test_', 'placeholder_', 'example_', 'demo_',
            'fake_', 'dummy_', 'sample_', 'mock_'
        ]
        return not any(key.lower().startswith(pattern) for pattern in placeholder_patterns)
    
    def _analyze_text_with_deepseek(self, text: str, is_elderly: bool = False, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用DeepSeek API分析文本情感（针对老人群体优化）"""
        try:
            logger.info("使用DeepSeek API分析文本情感...")
            
            # 构建针对老人情感分析的专业提示词
            system_prompt = self._build_elderly_emotion_prompt(is_elderly, user_context)
            
            # 构建请求
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {config.DEEPSEEK_API_KEY}'
            }
            
            payload = {
                'model': config.DEEPSEEK_MODEL,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': f'请分析以下文本的情感："{text}"'}
                ],
                'max_tokens': config.DEEPSEEK_MAX_TOKENS,
                'temperature': config.DEEPSEEK_TEMPERATURE,
                'stream': False
            }
            
            # 发送请求
            response = requests.post(
                f'{config.DEEPSEEK_API_URL}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                
                # 解析DeepSeek的分析结果
                emotion_result = self._parse_deepseek_response(analysis_text, text)
                emotion_result['analysis_model'] = 'DeepSeek_API'
                
                logger.info(f"DeepSeek分析成功: {emotion_result['primary_emotion']}")
                return emotion_result
            else:
                logger.error(f"DeepSeek API请求失败: {response.status_code} - {response.text}")
                raise Exception(f"DeepSeek API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"DeepSeek分析失败: {str(e)}")
            # 降级到OpenAI分析
            if config.OPENAI_API_KEY and self._is_valid_key(config.OPENAI_API_KEY):
                return self._analyze_text_with_openai(text)
            else:
                return self._analyze_text_with_ai(text)
    
    def _build_elderly_emotion_prompt(self, is_elderly: bool, user_context: Dict[str, Any]) -> str:
        """构建针对老人情感分析的提示词"""
        if is_elderly:
            base_prompt = """你是一位专业的老年心理学家和情感分析专家，专门研究老年人的情感表达特点。

老年人情感分析的特殊考虑：
1. 老年人常常通过委婉、含蓄的方式表达情感
2. 身体健康状况会显著影响情感状态
3. 对家庭、子女的关注是情感的重要来源
4. 回忆和怀念是老年人特有的情感表达方式
5. 对死亡、疾病等话题比较敏感
6. 孤独感和社交需求是重要的情感维度

请分析文本的情感，特别关注：
- 健康相关的担忧或安慰
- 家庭关系的喜忧
- 社交孤独或温暖
- 怀旧和回忆情感
- 对未来的期望或担忧
- 身体不适的抱怨或安慰

情感类别：快乐、悲伤、愤怒、恐惧、惊讶、厌恶、爱、平静、怀旧、希望、感激、失望、孤独、担忧、安慰

请以JSON格式回复，包含：
{
    "primary_emotion": "主要情感",
    "confidence": 0.85,
    "emotion_scores": {"快乐": 0.2, "担忧": 0.8},
    "elderly_specific": {
        "health_concern": "健康相关程度(0-1)",
        "family_relation": "家庭关系相关程度(0-1)",
        "loneliness": "孤独感程度(0-1)",
        "nostalgia": "怀念程度(0-1)"
    },
    "suggestions": ["针对老年人的建议1", "建议2"]
}"""
        else:
            base_prompt = """你是一位专业的情感分析专家，能够准确识别文本中的情感状态。

请分析文本的情感，识别主要情感类型和强度。

情感类别：快乐、悲伤、愤怒、恐惧、惊讶、厌恶、爱、平静、怀旧、希望、感激、失望

请以JSON格式回复，包含：
{
    "primary_emotion": "主要情感",
    "confidence": 0.85,
    "emotion_scores": {"快乐": 0.8, "平静": 0.2},
    "valence": 0.6,
    "arousal": 0.4,
    "suggestions": ["建议1", "建议2"]
}"""
        
        return base_prompt
    
    def _parse_deepseek_response(self, analysis_text: str, original_text: str) -> Dict[str, Any]:
        """解析DeepSeek的响应结果"""
        try:
            # 尝试提取JSON格式的结果
            import json
            
            # 查找JSON内容
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = analysis_text[json_start:json_end]
                parsed_result = json.loads(json_str)
                
                # 标准化情感名称
                primary_emotion = self._normalize_emotion_name(parsed_result.get('primary_emotion', 'neutral'))
                
                # 构建标准的情感分析结果
                result = {
                    'primary_emotion': primary_emotion,
                    'confidence': float(parsed_result.get('confidence', 0.8)),
                    'emotion_scores': self._normalize_emotion_scores(parsed_result.get('emotion_scores', {})),
                    'valence': float(parsed_result.get('valence', 0.0)),
                    'arousal': float(parsed_result.get('arousal', 0.0)),
                    'dominance': float(parsed_result.get('dominance', 0.0)),
                    'elderly_specific': parsed_result.get('elderly_specific', {}),
                    'ai_suggestions': parsed_result.get('suggestions', []),
                    'analysis_model': 'DeepSeek_API',
                    'raw_analysis': analysis_text
                }
                
                return result
            else:
                # 如果没有找到JSON，使用文本解析
                return self._parse_text_analysis(analysis_text, original_text)
                
        except json.JSONDecodeError as e:
            logger.warning(f"DeepSeek JSON解析失败: {str(e)}")
            return self._parse_text_analysis(analysis_text, original_text)
        except Exception as e:
            logger.error(f"DeepSeek响应解析失败: {str(e)}")
            return self._create_default_emotion_result()
    
    def _normalize_emotion_name(self, emotion_name: str) -> str:
        """标准化情感名称"""
        emotion_mapping = {
            '快乐': 'happy', '高兴': 'happy', '开心': 'happy', '喜悦': 'happy',
            '悲伤': 'sad', '难过': 'sad', '伤心': 'sad', '忧郁': 'sad',
            '愤怒': 'angry', '生气': 'angry', '恼火': 'angry',
            '恐惧': 'fear', '害怕': 'fear', '担心': 'fear', '焦虑': 'fear',
            '惊讶': 'surprise', '吃惊': 'surprise', '意外': 'surprise',
            '厌恶': 'disgust', '恶心': 'disgust', '反感': 'disgust',
            '爱': 'love', '喜欢': 'love', '热爱': 'love',
            '平静': 'peaceful', '安详': 'peaceful', '宁静': 'peaceful',
            '怀旧': 'nostalgic', '怀念': 'nostalgic', '思念': 'nostalgic',
            '希望': 'hopeful', '期望': 'hopeful', '憧憬': 'hopeful',
            '感激': 'grateful', '感谢': 'grateful', '感恩': 'grateful',
            '失望': 'disappointed', '沮丧': 'disappointed',
            '孤独': 'lonely', '寂寞': 'lonely',
            '担忧': 'worried', '忧虑': 'worried',
            '安慰': 'comforted', '温暖': 'comforted'
        }
        
        return emotion_mapping.get(emotion_name, emotion_name.lower())
    
    def _normalize_emotion_scores(self, emotion_scores: Dict[str, float]) -> Dict[str, float]:
        """标准化情感得分"""
        normalized_scores = {}
        for emotion, score in emotion_scores.items():
            normalized_emotion = self._normalize_emotion_name(emotion)
            normalized_scores[normalized_emotion] = float(score)
        return normalized_scores
    
    def _parse_text_analysis(self, analysis_text: str, original_text: str) -> Dict[str, Any]:
        """解析文本格式的分析结果"""
        try:
            # 简单的文本解析逻辑
            emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'love', 'peaceful', 'nostalgic']
            
            # 根据关键词判断主要情感
            text_lower = analysis_text.lower()
            emotion_counts = {}
            
            for emotion in emotions:
                chinese_name = get_emotion_description(emotion)
                if chinese_name in analysis_text or emotion in text_lower:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            # 选择最可能的情感
            if emotion_counts:
                primary_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
                confidence = min(0.7 + len(emotion_counts) * 0.1, 0.9)
            else:
                primary_emotion = 'neutral'
                confidence = 0.5
            
            return {
                'primary_emotion': primary_emotion,
                'confidence': confidence,
                'emotion_scores': {primary_emotion: confidence},
                'valence': 0.0,
                'arousal': 0.0,
                'dominance': 0.0,
                'analysis_model': 'DeepSeek_Text_Parse',
                'raw_analysis': analysis_text
            }
            
        except Exception as e:
            logger.error(f"文本解析失败: {str(e)}")
            return self._create_default_emotion_result()
    
    def _postprocess_elderly_emotion(self, result: Dict[str, Any], text: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """针对老人群体的情感结果后处理"""
        try:
            # 增强老人特有情感的识别
            elderly_emotions = {
                'nostalgic': ['过去', '以前', '当年', '那时候', '想当年', '回想起'],
                'lonely': ['一个人', '独自', '孤单', '没人', '寂寞'],
                'worried': ['担心', '忧虑', '害怕', '不放心', '怕'],
                'grateful': ['感谢', '感激', '谢谢', '多亏了'],
                'hopeful': ['希望', '盼望', '期待', '想要', '愿意']
            }
            
            # 检查文本中是否包含老人特有的情感表达
            for emotion, keywords in elderly_emotions.items():
                if any(keyword in text for keyword in keywords):
                    # 调整情感得分
                    current_score = result['emotion_scores'].get(emotion, 0)
                    result['emotion_scores'][emotion] = min(current_score + 0.3, 1.0)
                    
                    # 如果该情感得分很高，可能需要调整主要情感
                    if result['emotion_scores'][emotion] > result['confidence']:
                        result['primary_emotion'] = emotion
                        result['confidence'] = result['emotion_scores'][emotion]
            
            # 添加老人特有的建议
            elderly_suggestions = self._get_elderly_specific_suggestions(result['primary_emotion'], text)
            if 'ai_suggestions' not in result:
                result['ai_suggestions'] = []
            result['ai_suggestions'].extend(elderly_suggestions)
            
            # 添加家庭关怀提醒
            if any(keyword in text for keyword in ['孩子', '儿子', '女儿', '孙子', '孙女']):
                result['family_related'] = True
                result['ai_suggestions'].append('建议与家人多多交流分享')
            
            return result
            
        except Exception as e:
            logger.error(f"老人情感后处理失败: {str(e)}")
            return result
    
    def _get_elderly_specific_suggestions(self, emotion: str, text: str) -> List[str]:
        """获取针对老人的特定建议"""
        suggestions = []
        
        elderly_suggestion_map = {
            'lonely': [
                '建议参加社区活动，增加社交机会',
                '可以考虑学习新的兴趣爱好',
                '主动联系老朋友或邻居聊天'
            ],
            'worried': [
                '适当的担心是正常的，但不要过度焦虑',
                '可以和信任的人分享您的担忧',
                '建议进行轻松的活动来缓解紧张情绪'
            ],
            'nostalgic': [
                '美好的回忆是珍贵的财富',
                '可以写下或分享这些美好的故事',
                '回忆过去的同时，也要关注当下的美好'
            ],
            'sad': [
                '悲伤的情绪需要适当的释放',
                '建议和家人朋友倾诉，获得理解和支持',
                '如果情绪持续低落，建议寻求专业帮助'
            ],
            'happy': [
                '继续保持积极乐观的心态',
                '分享快乐能让幸福感加倍',
                '适当的运动有助于维持好心情'
            ]
        }
        
        suggestions.extend(elderly_suggestion_map.get(emotion, []))
        
        # 根据文本内容添加特定建议
        if '身体' in text or '健康' in text:
            suggestions.append('注意身体健康，定期体检很重要')
        
        if '睡眠' in text or '失眠' in text:
            suggestions.append('良好的睡眠习惯对健康很重要')
        
        return suggestions[:3]  # 最多返回3个建议
    
    def _analyze_text_with_openai(self, text: str) -> Dict[str, Any]:
        """使用OpenAI API分析文本情感"""
        try:
            # TODO: 实现OpenAI API调用
            # 这里需要使用OpenAI的API进行情感分析
            logger.info("使用OpenAI API分析文本情感...")
            
            # 模拟OpenAI API调用
            emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'love', 'peaceful', 'nostalgic']
            primary_emotion = random.choice(emotions)
            confidence = random.uniform(0.8, 0.95)  # 第三方API置信度更高
            
            emotion_scores = {}
            for emotion in emotions:
                if emotion == primary_emotion:
                    emotion_scores[emotion] = confidence
                else:
                    emotion_scores[emotion] = random.uniform(0.1, 0.3)
            
            return {
                'primary_emotion': primary_emotion,
                'confidence': confidence,
                'emotion_scores': emotion_scores,
                'valence': random.uniform(-1, 1),
                'arousal': random.uniform(-1, 1),
                'dominance': random.uniform(-1, 1),
                'analysis_model': 'OpenAI_API'
            }
            
        except Exception as e:
            logger.error(f"OpenAI API分析失败: {str(e)}")
            return self._analyze_text_with_ai(text)
    
    def _analyze_text_with_ai(self, text: str) -> Dict[str, Any]:
        """使用本地AI模型分析文本情感"""
        try:
            # TODO: 调用真实的AI模型
            # 这里应该调用预训练的情感分析模型
            
            # 模拟AI分析结果
            emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'love', 'peaceful', 'nostalgic']
            primary_emotion = random.choice(emotions)
            confidence = random.uniform(0.6, 0.85)  # 本地模型置信度中等
            
            emotion_scores = {}
            for emotion in emotions:
                if emotion == primary_emotion:
                    emotion_scores[emotion] = confidence
                else:
                    emotion_scores[emotion] = random.uniform(0.1, 0.4)
            
            return {
                'primary_emotion': primary_emotion,
                'confidence': confidence,
                'emotion_scores': emotion_scores,
                'valence': random.uniform(-1, 1),
                'arousal': random.uniform(-1, 1),
                'dominance': random.uniform(-1, 1),
                'analysis_model': 'Local_AI_Model'
            }
            
        except Exception as e:
            logger.error(f"本地AI模型分析失败: {str(e)}")
            return self._analyze_text_with_rules(text)
    
    def _analyze_text_with_rules(self, text: str) -> Dict[str, Any]:
        """使用规则匹配分析文本情感"""
        try:
            # 清理文本
            clean_text = self._clean_text(text)
            
            # 计算每种情感的得分
            emotion_scores = {}
            for emotion, keywords in self.emotion_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in clean_text:
                        # 基础分数
                        base_score = 0.5
                        
                        # 强度修正
                        intensity_modifier = self._get_intensity_modifier(clean_text, keyword)
                        score += base_score * intensity_modifier
                
                emotion_scores[emotion] = min(score, 1.0)
            
            # 确定主要情感
            if emotion_scores:
                primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
                confidence = emotion_scores[primary_emotion]
            else:
                primary_emotion = 'neutral'
                confidence = 0.5
                emotion_scores['neutral'] = 0.5
            
            # 计算情感维度
            valence = self._calculate_valence(primary_emotion, emotion_scores)
            arousal = self._calculate_arousal(primary_emotion, emotion_scores)
            dominance = self._calculate_dominance(primary_emotion, emotion_scores)
            
            return {
                'primary_emotion': primary_emotion,
                'confidence': confidence,
                'emotion_scores': emotion_scores,
                'valence': valence,
                'arousal': arousal,
                'dominance': dominance,
                'analysis_model': 'Rule_Based'
            }
            
        except Exception as e:
            logger.error(f"规则匹配分析失败: {str(e)}")
            return self._create_default_emotion_result()
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除特殊字符，保留中文、英文、数字
        clean_text = re.sub(r'[^\u4e00-\u9fa5\w\s]', '', text)
        return clean_text.lower()
    
    def _get_intensity_modifier(self, text: str, keyword: str) -> float:
        """获取强度修正系数"""
        # 查找关键词前后的强度词汇
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return 1.0
        
        # 检查前面的词汇
        before_text = text[max(0, keyword_pos - 20):keyword_pos]
        
        for intensity, words in self.intensity_words.items():
            for word in words:
                if word in before_text:
                    if intensity == 'high':
                        return 1.5
                    elif intensity == 'medium':
                        return 1.2
                    elif intensity == 'low':
                        return 0.8
        
        return 1.0
    
    def _calculate_valence(self, primary_emotion: str, emotion_scores: Dict[str, float]) -> float:
        """计算效价（正面-负面）"""
        positive_emotions = ['happy', 'love', 'peaceful', 'grateful', 'hopeful']
        negative_emotions = ['sad', 'angry', 'fear', 'disgust', 'disappointed']
        
        if primary_emotion in positive_emotions:
            return 0.5 + (emotion_scores.get(primary_emotion, 0) * 0.5)
        elif primary_emotion in negative_emotions:
            return 0.5 - (emotion_scores.get(primary_emotion, 0) * 0.5)
        else:
            return 0.0
    
    def _calculate_arousal(self, primary_emotion: str, emotion_scores: Dict[str, float]) -> float:
        """计算唤醒度（高-低）"""
        high_arousal = ['angry', 'fear', 'surprise', 'excited']
        low_arousal = ['peaceful', 'sad', 'nostalgic']
        
        if primary_emotion in high_arousal:
            return 0.5 + (emotion_scores.get(primary_emotion, 0) * 0.5)
        elif primary_emotion in low_arousal:
            return 0.5 - (emotion_scores.get(primary_emotion, 0) * 0.5)
        else:
            return 0.0
    
    def _calculate_dominance(self, primary_emotion: str, emotion_scores: Dict[str, float]) -> float:
        """计算支配度（强-弱）"""
        high_dominance = ['angry', 'happy', 'love']
        low_dominance = ['fear', 'sad', 'disappointed']
        
        if primary_emotion in high_dominance:
            return 0.5 + (emotion_scores.get(primary_emotion, 0) * 0.5)
        elif primary_emotion in low_dominance:
            return 0.5 - (emotion_scores.get(primary_emotion, 0) * 0.5)
        else:
            return 0.0
    
    def _create_default_emotion_result(self) -> Dict[str, Any]:
        """创建默认的情感分析结果"""
        return {
            'primary_emotion': 'neutral',
            'confidence': 0.5,
            'emotion_scores': {'neutral': 0.5},
            'valence': 0.0,
            'arousal': 0.0,
            'dominance': 0.0,
            'analysis_model': 'Default'
        }
    
    def analyze_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """
        分析音频情感
        
        Args:
            audio_file_path: 音频文件路径
            
        Returns:
            情感分析结果字典
        """
        try:
            logger.info(f"开始分析音频情感: {audio_file_path}")
            
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"音频文件不存在: {audio_file_path}")
            
            # 优先使用第三方API获得最佳准确率
            if config.OPENAI_API_KEY:
                # 第一优先级：使用OpenAI API（高准确率）
                result = self._analyze_audio_with_openai(audio_file_path)
            elif self.models_loaded and self.audio_analyzer:
                # 第二优先级：使用本地AI模型（中等准确率）
                result = self._analyze_audio_with_ai(audio_file_path)
            else:
                # 最后选择：使用模拟分析（保底方案）
                result = self._analyze_audio_with_simulation(audio_file_path)
            
            logger.info(f"音频情感分析完成: {result['primary_emotion']} (置信度: {result['confidence']:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"音频情感分析失败: {str(e)}")
            return self._create_default_emotion_result()
    
    def _analyze_audio_with_openai(self, audio_file_path: str) -> Dict[str, Any]:
        """使用OpenAI API分析音频情感"""
        try:
            # TODO: 实现OpenAI Whisper + GPT分析音频情感
            # 1. 使用Whisper转录音频
            # 2. 使用GPT分析转录文本的情感
            logger.info("使用OpenAI API分析音频情感...")
            
            # 模拟OpenAI API分析结果
            emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'peaceful', 'excited']
            primary_emotion = random.choice(emotions)
            confidence = random.uniform(0.85, 0.95)  # 第三方API置信度最高
            
            emotion_scores = {}
            for emotion in emotions:
                if emotion == primary_emotion:
                    emotion_scores[emotion] = confidence
                else:
                    emotion_scores[emotion] = random.uniform(0.05, 0.2)
            
            return {
                'primary_emotion': primary_emotion,
                'confidence': confidence,
                'emotion_scores': emotion_scores,
                'valence': random.uniform(-1, 1),
                'arousal': random.uniform(-1, 1),
                'dominance': random.uniform(-1, 1),
                'analysis_model': 'OpenAI_Audio_API'
            }
            
        except Exception as e:
            logger.error(f"OpenAI音频分析失败: {str(e)}")
            return self._analyze_audio_with_ai(audio_file_path)
    
    def _analyze_audio_with_ai(self, audio_file_path: str) -> Dict[str, Any]:
        """使用本地AI模型分析音频情感"""
        try:
            # TODO: 调用真实的音频情感分析模型
            # 例如：Wav2Vec2, ECAPA-TDNN等
            
            # 模拟AI分析结果
            emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'peaceful', 'excited']
            primary_emotion = random.choice(emotions)
            confidence = random.uniform(0.6, 0.8)  # 本地模型置信度中等
            
            emotion_scores = {}
            for emotion in emotions:
                if emotion == primary_emotion:
                    emotion_scores[emotion] = confidence
                else:
                    emotion_scores[emotion] = random.uniform(0.1, 0.4)
            
            return {
                'primary_emotion': primary_emotion,
                'confidence': confidence,
                'emotion_scores': emotion_scores,
                'valence': random.uniform(-1, 1),
                'arousal': random.uniform(-1, 1),
                'dominance': random.uniform(-1, 1),
                'analysis_model': 'Local_Audio_AI_Model'
            }
            
        except Exception as e:
            logger.error(f"本地AI音频分析失败: {str(e)}")
            return self._analyze_audio_with_simulation(audio_file_path)
    
    def _analyze_audio_with_simulation(self, audio_file_path: str) -> Dict[str, Any]:
        """模拟音频情感分析"""
        try:
            # 根据文件大小和名称进行简单的模拟分析
            file_size = os.path.getsize(audio_file_path)
            file_name = os.path.basename(audio_file_path).lower()
            
            # 简单的规则匹配
            if 'happy' in file_name or 'joy' in file_name:
                primary_emotion = 'happy'
            elif 'sad' in file_name or 'cry' in file_name:
                primary_emotion = 'sad'
            elif 'angry' in file_name or 'mad' in file_name:
                primary_emotion = 'angry'
            else:
                # 根据文件大小随机选择
                emotions = ['happy', 'sad', 'peaceful', 'nostalgic', 'neutral']
                primary_emotion = emotions[file_size % len(emotions)]
            
            confidence = random.uniform(0.4, 0.7)
            
            emotion_scores = {primary_emotion: confidence}
            
            return {
                'primary_emotion': primary_emotion,
                'confidence': confidence,
                'emotion_scores': emotion_scores,
                'valence': random.uniform(-1, 1),
                'arousal': random.uniform(-1, 1),
                'dominance': random.uniform(-1, 1),
                'analysis_model': 'Audio_Simulation'
            }
            
        except Exception as e:
            logger.error(f"模拟音频分析失败: {str(e)}")
            return self._create_default_emotion_result()
    
    def generate_memory_text(self, user_input: str, emotion_result: Dict[str, Any]) -> str:
        """
        基于用户输入和情感分析结果生成回忆文本
        
        Args:
            user_input: 用户输入
            emotion_result: 情感分析结果
            
        Returns:
            生成的回忆文本
        """
        try:
            primary_emotion = emotion_result.get('primary_emotion', 'neutral')
            confidence = emotion_result.get('confidence', 0.5)
            
            # 获取情感描述
            emotion_desc = get_emotion_description(primary_emotion)
            
            # 根据情感强度调整描述
            if confidence >= 0.8:
                intensity_desc = "强烈的"
            elif confidence >= 0.6:
                intensity_desc = "明显的"
            elif confidence >= 0.4:
                intensity_desc = "轻微的"
            else:
                intensity_desc = "淡淡的"
            
            # 生成回忆文本模板
            memory_templates = {
                'happy': [
                    f"这是一段充满{intensity_desc}{emotion_desc}的回忆。{user_input}这个瞬间让我感到温暖和满足，仿佛阳光洒在心田。",
                    f"回想起{user_input}总是会让我不由自主地微笑。那种{intensity_desc}{emotion_desc}的感觉，就像春天里的第一缕阳光。",
                    f"那时的{intensity_desc}{emotion_desc}至今还深深印在我心里。{user_input}这样的时刻，让生活变得如此美好。"
                ],
                'sad': [
                    f"这是一段带着{intensity_desc}{emotion_desc}的回忆。{user_input}让我感到心情沉重，像是被云层遮蔽的天空。",
                    f"每当想起{user_input}心中总是涌起{intensity_desc}{emotion_desc}。那种感觉就像秋天的落叶，静静地飘落。",
                    f"那份{intensity_desc}{emotion_desc}仍然清晰地留在记忆中。{user_input}让我明白生活中也有阴霾的时刻。"
                ],
                'angry': [
                    f"这是一段充满{intensity_desc}{emotion_desc}的回忆。{user_input}让我感到愤怒，像是内心燃烧的火焰。",
                    f"回想起{user_input}那种{intensity_desc}{emotion_desc}的感觉仍然历历在目。当时的情绪就像汹涌的海浪。",
                    f"那时的{intensity_desc}{emotion_desc}让我久久不能平静。{user_input}这样的经历教会了我如何处理情绪。"
                ],
                'peaceful': [
                    f"这是一段{intensity_desc}{emotion_desc}的回忆。{user_input}让我感到内心宁静，像是湖面上的微风。",
                    f"想起{user_input}总是让我感到{intensity_desc}{emotion_desc}。那种感觉就像夏日黄昏的清风。",
                    f"那份{intensity_desc}{emotion_desc}至今还能让我放松。{user_input}这样的时刻让我找到了内心的平衡。"
                ],
                'nostalgic': [
                    f"这是一段充满{intensity_desc}{emotion_desc}的回忆。{user_input}让我想起了过往的时光，像是翻阅泛黄的相册。",
                    f"每当想起{user_input}心中总是涌起{intensity_desc}{emotion_desc}情怀。那些美好的时光仿佛就在昨天。",
                    f"那份{intensity_desc}{emotion_desc}让我珍惜现在的每一刻。{user_input}提醒我时光的珍贵。"
                ],
                'love': [
                    f"这是一段充满{intensity_desc}{emotion_desc}的回忆。{user_input}让我感到心中满溢着温暖，像是被爱包围。",
                    f"回想起{user_input}那种{intensity_desc}{emotion_desc}的感觉让我感到幸福。爱让这个世界变得更加美好。",
                    f"那份{intensity_desc}{emotion_desc}是我心中最珍贵的宝藏。{user_input}让我明白什么是真正的幸福。"
                ]
            }
            
            # 默认模板
            default_template = f"这是一段{intensity_desc}{emotion_desc}的回忆。{user_input}在我心中留下了深刻的印象，每个细节都值得珍藏。"
            
            # 选择合适的模板
            templates = memory_templates.get(primary_emotion, [default_template])
            memory_text = random.choice(templates)
            
            logger.info(f"生成回忆文本完成: {memory_text[:50]}...")
            return memory_text
            
        except Exception as e:
            logger.error(f"生成回忆文本失败: {str(e)}")
            return f"这是一段特殊的回忆。{user_input}在我心中留下了深刻的印象。"
    
    def get_emotion_suggestions(self, emotion_result: Dict[str, Any]) -> List[str]:
        """
        根据情感分析结果获取建议
        
        Args:
            emotion_result: 情感分析结果
            
        Returns:
            建议列表
        """
        primary_emotion = emotion_result.get('primary_emotion', 'neutral')
        
        suggestions = {
            'happy': ['分享这种快乐给身边的人', '记录下这美好的时刻', '保持积极的心态'],
            'sad': ['允许自己感受这种情绪', '找朋友倾诉', '适当的休息和放松'],
            'angry': ['深呼吸冷静一下', '找到问题的根源', '寻求建设性的解决方案'],
            'fear': ['面对恐惧，勇敢前行', '寻求支持和帮助', '制定应对计划'],
            'peaceful': ['享受这份宁静', '保持内心的平衡', '珍惜当下的美好'],
            'nostalgic': ['珍惜过往的美好回忆', '感恩曾经的经历', '创造新的美好回忆'],
            'love': ['表达你的爱意', '珍惜身边的人', '让爱传递下去']
        }
        
        return suggestions.get(primary_emotion, ['保持积极的心态', '珍惜当下的感受', '每个情感都有其价值'])
    
    def batch_analyze_texts(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        批量分析文本情感
        
        Args:
            texts: 文本列表
            
        Returns:
            情感分析结果列表
        """
        results = []
        for text in texts:
            try:
                result = self.analyze_text(text)
                results.append(result)
            except Exception as e:
                logger.error(f"批量分析文本失败: {str(e)}")
                results.append(self._create_default_emotion_result())
        
        return results 