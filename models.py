# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 数据模型
定义系统中使用的数据结构
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

class MemoryRecord:
    """回忆记录数据模型"""
    
    def __init__(self, 
                 user_id: str,
                 user_input: str,
                 memory_text: str,
                 image_url: str,
                 emotion_result: Dict[str, Any],
                 created_at: datetime = None,
                 memory_id: str = None):
        """
        初始化回忆记录
        
        Args:
            user_id: 用户ID
            user_input: 用户输入的原始文本
            memory_text: 生成的回忆文本
            image_url: 生成的图像URL
            emotion_result: 情感分析结果
            created_at: 创建时间
            memory_id: 记录ID（可选，用于从数据库加载）
        """
        self.id = memory_id or str(uuid.uuid4())
        self.user_id = user_id
        self.user_input = user_input
        self.memory_text = memory_text
        self.image_url = image_url
        self.emotion_result = emotion_result
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_input': self.user_input,
            'memory_text': self.memory_text,
            'image_url': self.image_url,
            'emotion_result': self.emotion_result,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryRecord':
        """从字典创建回忆记录实例"""
        return cls(
            memory_id=data.get('id'),
            user_id=data.get('user_id'),
            user_input=data.get('user_input'),
            memory_text=data.get('memory_text'),
            image_url=data.get('image_url'),
            emotion_result=data.get('emotion_result', {}),
            created_at=data.get('created_at')
        )
    
    def __str__(self) -> str:
        return f"MemoryRecord(id={self.id}, user_id={self.user_id}, emotion={self.emotion_result.get('primary_emotion', 'unknown')})"
    
    def __repr__(self) -> str:
        return self.__str__()

class EmotionResult:
    """情感分析结果数据模型"""
    
    def __init__(self, 
                 primary_emotion: str,
                 confidence: float,
                 emotion_scores: Dict[str, float],
                 valence: float = 0.0,
                 arousal: float = 0.0,
                 dominance: float = 0.0,
                 analysis_model: str = ""):
        """
        初始化情感分析结果
        
        Args:
            primary_emotion: 主要情感（如happy, sad, angry等）
            confidence: 情感识别的置信度
            emotion_scores: 各种情感的得分
            valence: 效价（正面-负面）
            arousal: 唤醒度（高-低）
            dominance: 支配度（强-弱）
            analysis_model: 使用的分析模型
        """
        self.primary_emotion = primary_emotion
        self.confidence = confidence
        self.emotion_scores = emotion_scores
        self.valence = valence
        self.arousal = arousal
        self.dominance = dominance
        self.analysis_model = analysis_model
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'primary_emotion': self.primary_emotion,
            'confidence': self.confidence,
            'emotion_scores': self.emotion_scores,
            'valence': self.valence,
            'arousal': self.arousal,
            'dominance': self.dominance,
            'analysis_model': self.analysis_model,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionResult':
        """从字典创建情感结果实例"""
        result = cls(
            primary_emotion=data.get('primary_emotion', ''),
            confidence=data.get('confidence', 0.0),
            emotion_scores=data.get('emotion_scores', {}),
            valence=data.get('valence', 0.0),
            arousal=data.get('arousal', 0.0),
            dominance=data.get('dominance', 0.0),
            analysis_model=data.get('analysis_model', '')
        )
        result.timestamp = data.get('timestamp', datetime.now())
        return result
    
    def get_emotion_intensity(self) -> str:
        """获取情感强度描述"""
        if self.confidence >= 0.8:
            return "强烈"
        elif self.confidence >= 0.6:
            return "中等"
        elif self.confidence >= 0.4:
            return "轻微"
        else:
            return "微弱"
    
    def is_positive(self) -> bool:
        """判断情感是否为正面"""
        positive_emotions = ['happy', 'joy', 'love', 'excited', 'peaceful', 'grateful']
        return self.primary_emotion in positive_emotions or self.valence > 0.5
    
    def __str__(self) -> str:
        return f"EmotionResult(emotion={self.primary_emotion}, confidence={self.confidence:.2f})"

class ImageGenerationConfig:
    """图像生成配置模型"""
    
    def __init__(self, 
                 prompt: str,
                 style: str = "realistic",
                 size: str = "512x512",
                 quality: str = "standard",
                 model: str = "stable-diffusion",
                 emotion_influence: float = 0.5):
        """
        初始化图像生成配置
        
        Args:
            prompt: 生成提示词
            style: 图像风格
            size: 图像尺寸
            quality: 图像质量
            model: 使用的模型
            emotion_influence: 情感影响权重
        """
        self.prompt = prompt
        self.style = style
        self.size = size
        self.quality = quality
        self.model = model
        self.emotion_influence = emotion_influence
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'prompt': self.prompt,
            'style': self.style,
            'size': self.size,
            'quality': self.quality,
            'model': self.model,
            'emotion_influence': self.emotion_influence,
            'timestamp': self.timestamp
        }

class UserStatistics:
    """用户统计信息模型"""
    
    def __init__(self, 
                 user_id: str,
                 total_memories: int = 0,
                 emotion_distribution: Dict[str, int] = None,
                 most_common_emotion: str = "",
                 first_memory_date: datetime = None,
                 last_memory_date: datetime = None):
        """
        初始化用户统计信息
        
        Args:
            user_id: 用户ID
            total_memories: 总回忆数量
            emotion_distribution: 情感分布
            most_common_emotion: 最常见的情感
            first_memory_date: 首次回忆时间
            last_memory_date: 最后一次回忆时间
        """
        self.user_id = user_id
        self.total_memories = total_memories
        self.emotion_distribution = emotion_distribution or {}
        self.most_common_emotion = most_common_emotion
        self.first_memory_date = first_memory_date
        self.last_memory_date = last_memory_date
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'user_id': self.user_id,
            'total_memories': self.total_memories,
            'emotion_distribution': self.emotion_distribution,
            'most_common_emotion': self.most_common_emotion,
            'first_memory_date': self.first_memory_date,
            'last_memory_date': self.last_memory_date,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserStatistics':
        """从字典创建用户统计实例"""
        stats = cls(
            user_id=data.get('user_id'),
            total_memories=data.get('total_memories', 0),
            emotion_distribution=data.get('emotion_distribution', {}),
            most_common_emotion=data.get('most_common_emotion', ''),
            first_memory_date=data.get('first_memory_date'),
            last_memory_date=data.get('last_memory_date')
        )
        stats.updated_at = data.get('updated_at', datetime.now())
        return stats
    
    def add_memory(self, emotion: str, memory_date: datetime):
        """添加新回忆时更新统计信息"""
        self.total_memories += 1
        
        # 更新情感分布
        if emotion in self.emotion_distribution:
            self.emotion_distribution[emotion] += 1
        else:
            self.emotion_distribution[emotion] = 1
        
        # 更新最常见情感
        max_count = max(self.emotion_distribution.values())
        for emotion_key, count in self.emotion_distribution.items():
            if count == max_count:
                self.most_common_emotion = emotion_key
                break
        
        # 更新时间记录
        if not self.first_memory_date or memory_date < self.first_memory_date:
            self.first_memory_date = memory_date
        
        if not self.last_memory_date or memory_date > self.last_memory_date:
            self.last_memory_date = memory_date
        
        self.updated_at = datetime.now()
    
    def get_emotional_trend(self) -> Dict[str, float]:
        """获取情感趋势（百分比）"""
        if self.total_memories == 0:
            return {}
        
        return {
            emotion: (count / self.total_memories) * 100
            for emotion, count in self.emotion_distribution.items()
        }
    
    def __str__(self) -> str:
        return f"UserStatistics(user_id={self.user_id}, total_memories={self.total_memories})"

# 情感标签映射
EMOTION_LABELS = {
    'happy': '快乐',
    'sad': '悲伤',
    'angry': '愤怒',
    'fear': '恐惧',
    'surprise': '惊讶',
    'disgust': '厌恶',
    'neutral': '中性',
    'love': '爱',
    'joy': '喜悦',
    'peaceful': '平静',
    'excited': '兴奋',
    'grateful': '感激',
    'anxious': '焦虑',
    'disappointed': '失望',
    'nostalgic': '怀旧',
    'hopeful': '充满希望'
}

# 情感颜色映射（用于前端展示）
EMOTION_COLORS = {
    'happy': '#FFD700',
    'sad': '#87CEEB',
    'angry': '#FF6B6B',
    'fear': '#DDA0DD',
    'surprise': '#FFA500',
    'disgust': '#8FBC8F',
    'neutral': '#D3D3D3',
    'love': '#FF69B4',
    'joy': '#FFE4B5',
    'peaceful': '#98FB98',
    'excited': '#FF4500',
    'grateful': '#DEB887',
    'anxious': '#F0E68C',
    'disappointed': '#CD853F',
    'nostalgic': '#DDA0DD',
    'hopeful': '#90EE90'
}

def get_emotion_description(emotion: str) -> str:
    """获取情感的中文描述"""
    return EMOTION_LABELS.get(emotion, emotion)

def get_emotion_color(emotion: str) -> str:
    """获取情感对应的颜色"""
    return EMOTION_COLORS.get(emotion, '#D3D3D3') 