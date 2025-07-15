# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 老人数据存储管理器
专门处理老人相关数据的存储和管理，支持CSV和MongoDB两种存储方式
"""

import os
import csv
import json
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database
import math

from config import config

logger = logging.getLogger(__name__)

class ElderlyDataManager:
    """老人数据存储管理器"""
    
    def __init__(self):
        """初始化老人数据管理器"""
        self.storage_type = config.ELDERLY_DATA_STORAGE_TYPE
        self.csv_path = config.ELDERLY_CSV_PATH
        self.mongodb_collection = config.ELDERLY_MONGODB_COLLECTION
        
        # MongoDB相关
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None
        
        # 确保存储目录存在
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
        # 老人关键词列表
        self.elderly_keywords = config.ELDERLY_KEYWORDS
        self.keyword_threshold = config.ELDERLY_KEYWORD_THRESHOLD
        self.min_age = config.ELDERLY_MIN_AGE
        
        logger.info(f"老人数据管理器初始化：存储类型={self.storage_type}")
    
    def init_storage(self):
        """初始化存储"""
        try:
            if self.storage_type.upper() == 'CSV':
                self._init_csv_storage()
            elif self.storage_type.upper() == 'MONGODB':
                self._init_mongodb_storage()
            else:
                raise ValueError(f"不支持的存储类型: {self.storage_type}")
                
            logger.info("✅ 老人数据存储初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 老人数据存储初始化失败: {str(e)}")
            # 降级到CSV存储
            if self.storage_type.upper() != 'CSV':
                logger.info("降级到CSV存储")
                self.storage_type = 'CSV'
                self._init_csv_storage()
    
    def _init_csv_storage(self):
        """初始化CSV存储"""
        try:
            # 创建CSV文件（如果不存在）
            if not os.path.exists(self.csv_path):
                with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # 写入表头
                    headers = [
                        'id', 'user_id', 'text', 'primary_emotion', 'confidence',
                        'age', 'gender', 'age_group', 'keywords_matched',
                        'keyword_count', 'elderly_specific_health', 'elderly_specific_family',
                        'elderly_specific_loneliness', 'elderly_specific_nostalgia',
                        'ai_suggestions', 'created_at', 'updated_at'
                    ]
                    writer.writerow(headers)
            
            logger.info(f"CSV存储初始化成功: {self.csv_path}")
            
        except Exception as e:
            logger.error(f"CSV存储初始化失败: {str(e)}")
            raise
    
    def _init_mongodb_storage(self):
        """初始化MongoDB存储"""
        try:
            # 连接MongoDB
            self.client = MongoClient(
                config.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            
            # 测试连接
            self.client.admin.command('ping')
            
            # 获取数据库和集合
            self.db = self.client[config.DATABASE_NAME]
            self.collection = self.db[self.mongodb_collection]
            
            # 创建索引
            self._create_elderly_indexes()
            
            logger.info(f"MongoDB存储初始化成功: {config.MONGODB_URI}/{config.DATABASE_NAME}/{self.mongodb_collection}")
            
        except Exception as e:
            logger.error(f"MongoDB存储初始化失败: {str(e)}")
            raise
    
    def _create_elderly_indexes(self):
        """创建老人数据专用索引"""
        try:
            # 用户ID索引
            self.collection.create_index("user_id")
            # 年龄索引
            self.collection.create_index("age")
            # 情感索引
            self.collection.create_index("primary_emotion")
            # 时间索引
            self.collection.create_index("created_at")
            # 复合索引
            self.collection.create_index([("user_id", ASCENDING), ("age", ASCENDING)])
            self.collection.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
            
            logger.info("老人数据MongoDB索引创建成功")
            
        except Exception as e:
            logger.warning(f"创建老人数据索引时发生警告: {str(e)}")
    
    def is_elderly_context(self, user_context: Dict[str, Any], text: str = "") -> bool:
        """判断是否为老人群体（扩展版）"""
        if not user_context:
            return False
        
        # 1. 根据年龄判断
        age = user_context.get('age', 0)
        if age >= self.min_age:
            return True
        
        # 2. 根据年龄段判断
        age_group = user_context.get('age_group', '')
        if age_group in ['senior', 'elderly', '老年', '老人']:
            return True
        
        # 3. 根据关键词判断（扩展版）
        combined_text = f"{text} {user_context.get('recent_text', '')} {user_context.get('description', '')}"
        
        matched_keywords = []
        for keyword in self.elderly_keywords:
            if keyword in combined_text:
                matched_keywords.append(keyword)
        
        # 如果匹配到足够多的关键词，则认为是老人群体
        if len(matched_keywords) >= self.keyword_threshold:
            return True
        
        return False
    
    def get_matched_keywords(self, text: str) -> List[str]:
        """获取文本中匹配的老人关键词"""
        matched_keywords = []
        for keyword in self.elderly_keywords:
            if keyword in text:
                matched_keywords.append(keyword)
        return matched_keywords
    
    def save_elderly_emotion(self, data: Dict[str, Any]) -> str:
        """保存老人情感数据"""
        try:
            # 添加时间戳
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()
            
            # 生成ID
            if 'id' not in data:
                data['id'] = f"elderly_{int(datetime.now().timestamp() * 1000)}"
            
            if self.storage_type.upper() == 'CSV':
                return self._save_to_csv(data)
            elif self.storage_type.upper() == 'MONGODB':
                return self._save_to_mongodb(data)
            else:
                raise ValueError(f"不支持的存储类型: {self.storage_type}")
                
        except Exception as e:
            logger.error(f"保存老人情感数据失败: {str(e)}")
            raise
    
    def _save_to_csv(self, data: Dict[str, Any]) -> str:
        """保存到CSV文件"""
        try:
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 构建行数据
                row = [
                    data.get('id', ''),
                    data.get('user_id', ''),
                    data.get('text', ''),
                    data.get('primary_emotion', ''),
                    data.get('confidence', 0),
                    data.get('age', 0),
                    data.get('gender', ''),
                    data.get('age_group', ''),
                    ','.join(data.get('keywords_matched', [])),
                    data.get('keyword_count', 0),
                    data.get('elderly_specific', {}).get('health_concern', 0),
                    data.get('elderly_specific', {}).get('family_relation', 0),
                    data.get('elderly_specific', {}).get('loneliness', 0),
                    data.get('elderly_specific', {}).get('nostalgia', 0),
                    ','.join(data.get('ai_suggestions', [])),
                    data.get('created_at', '').isoformat() if data.get('created_at') else '',
                    data.get('updated_at', '').isoformat() if data.get('updated_at') else ''
                ]
                
                writer.writerow(row)
            
            logger.info(f"老人情感数据保存到CSV成功: {data['id']}")
            return data['id']
            
        except Exception as e:
            logger.error(f"保存到CSV失败: {str(e)}")
            raise
    
    def _save_to_mongodb(self, data: Dict[str, Any]) -> str:
        """保存到MongoDB"""
        try:
            # 插入数据
            result = self.collection.insert_one(data)
            
            logger.info(f"老人情感数据保存到MongoDB成功: {data['id']}")
            return data['id']
            
        except Exception as e:
            logger.error(f"保存到MongoDB失败: {str(e)}")
            raise
    
    def get_elderly_emotions(self, user_id: str = None, page: int = 1, per_page: int = 20, 
                            emotion_filter: str = None, age_filter: int = None) -> Dict[str, Any]:
        """获取老人情感数据"""
        try:
            if self.storage_type.upper() == 'CSV':
                return self._get_from_csv(user_id, page, per_page, emotion_filter, age_filter)
            elif self.storage_type.upper() == 'MONGODB':
                return self._get_from_mongodb(user_id, page, per_page, emotion_filter, age_filter)
            else:
                raise ValueError(f"不支持的存储类型: {self.storage_type}")
                
        except Exception as e:
            logger.error(f"获取老人情感数据失败: {str(e)}")
            raise
    
    def _get_from_csv(self, user_id: str, page: int, per_page: int, 
                     emotion_filter: str, age_filter: int) -> Dict[str, Any]:
        """从CSV获取数据"""
        try:
            # 读取CSV文件
            df = pd.read_csv(self.csv_path)
            
            # 过滤数据
            if user_id:
                df = df[df['user_id'] == user_id]
            
            if emotion_filter:
                df = df[df['primary_emotion'] == emotion_filter]
            
            if age_filter:
                df = df[df['age'] >= age_filter]
            
            # 按时间排序
            df = df.sort_values('created_at', ascending=False)
            
            # 分页
            total = len(df)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_df = df.iloc[start_idx:end_idx]
            
            # 转换为字典列表
            emotions = []
            for _, row in page_df.iterrows():
                emotion_data = {
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'text': row['text'],
                    'primary_emotion': row['primary_emotion'],
                    'confidence': row['confidence'],
                    'age': row['age'],
                    'gender': row['gender'],
                    'age_group': row['age_group'],
                    'keywords_matched': row['keywords_matched'].split(',') if row['keywords_matched'] else [],
                    'keyword_count': row['keyword_count'],
                    'elderly_specific': {
                        'health_concern': row['elderly_specific_health'],
                        'family_relation': row['elderly_specific_family'],
                        'loneliness': row['elderly_specific_loneliness'],
                        'nostalgia': row['elderly_specific_nostalgia']
                    },
                    'ai_suggestions': row['ai_suggestions'].split(',') if row['ai_suggestions'] else [],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                emotions.append(emotion_data)
            
            return {
                'emotions': emotions,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': math.ceil(total / per_page)
            }
            
        except Exception as e:
            logger.error(f"从CSV获取数据失败: {str(e)}")
            raise
    
    def _get_from_mongodb(self, user_id: str, page: int, per_page: int, 
                         emotion_filter: str, age_filter: int) -> Dict[str, Any]:
        """从MongoDB获取数据"""
        try:
            # 构建查询条件
            query = {}
            if user_id:
                query['user_id'] = user_id
            if emotion_filter:
                query['primary_emotion'] = emotion_filter
            if age_filter:
                query['age'] = {'$gte': age_filter}
            
            # 获取总数
            total = self.collection.count_documents(query)
            
            # 分页查询
            skip = (page - 1) * per_page
            cursor = self.collection.find(query).sort('created_at', DESCENDING).skip(skip).limit(per_page)
            
            # 转换为列表
            emotions = []
            for doc in cursor:
                # 移除MongoDB的_id字段
                if '_id' in doc:
                    del doc['_id']
                emotions.append(doc)
            
            return {
                'emotions': emotions,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': math.ceil(total / per_page)
            }
            
        except Exception as e:
            logger.error(f"从MongoDB获取数据失败: {str(e)}")
            raise
    
    def get_elderly_statistics(self, user_id: str = None) -> Dict[str, Any]:
        """获取老人情感统计数据"""
        try:
            if self.storage_type.upper() == 'CSV':
                return self._get_statistics_from_csv(user_id)
            elif self.storage_type.upper() == 'MONGODB':
                return self._get_statistics_from_mongodb(user_id)
            else:
                raise ValueError(f"不支持的存储类型: {self.storage_type}")
                
        except Exception as e:
            logger.error(f"获取老人情感统计数据失败: {str(e)}")
            raise
    
    def _get_statistics_from_csv(self, user_id: str) -> Dict[str, Any]:
        """从CSV获取统计数据"""
        try:
            # 读取CSV文件
            df = pd.read_csv(self.csv_path)
            
            # 过滤用户数据
            if user_id:
                df = df[df['user_id'] == user_id]
            
            # 计算统计数据
            total_records = len(df)
            
            # 情感分布
            emotion_distribution = df['primary_emotion'].value_counts().to_dict()
            
            # 年龄分布
            age_distribution = df['age'].value_counts().to_dict()
            
            # 最常见情感
            most_common_emotion = df['primary_emotion'].mode().iloc[0] if not df.empty else ''
            
            # 平均年龄
            avg_age = df['age'].mean() if not df.empty else 0
            
            # 关键词统计
            all_keywords = []
            for keywords_str in df['keywords_matched'].dropna():
                if keywords_str:
                    all_keywords.extend(keywords_str.split(','))
            
            keyword_frequency = pd.Series(all_keywords).value_counts().to_dict()
            
            return {
                'total_records': total_records,
                'emotion_distribution': emotion_distribution,
                'age_distribution': age_distribution,
                'most_common_emotion': most_common_emotion,
                'average_age': avg_age,
                'keyword_frequency': keyword_frequency,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"从CSV获取统计数据失败: {str(e)}")
            raise
    
    def _get_statistics_from_mongodb(self, user_id: str) -> Dict[str, Any]:
        """从MongoDB获取统计数据"""
        try:
            # 构建匹配条件
            match_condition = {}
            if user_id:
                match_condition['user_id'] = user_id
            
            # 聚合查询
            pipeline = [
                {'$match': match_condition},
                {
                    '$group': {
                        '_id': None,
                        'total_records': {'$sum': 1},
                        'emotion_distribution': {
                            '$push': '$primary_emotion'
                        },
                        'age_distribution': {
                            '$push': '$age'
                        },
                        'average_age': {'$avg': '$age'},
                        'keywords': {
                            '$push': '$keywords_matched'
                        }
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result:
                stats = result[0]
                
                # 计算情感分布
                emotion_dist = {}
                for emotion in stats['emotion_distribution']:
                    emotion_dist[emotion] = emotion_dist.get(emotion, 0) + 1
                
                # 计算年龄分布
                age_dist = {}
                for age in stats['age_distribution']:
                    age_dist[age] = age_dist.get(age, 0) + 1
                
                # 计算关键词频率
                keyword_freq = {}
                for keywords_list in stats['keywords']:
                    if keywords_list:
                        for keyword in keywords_list:
                            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
                
                # 最常见情感
                most_common_emotion = max(emotion_dist.items(), key=lambda x: x[1])[0] if emotion_dist else ''
                
                return {
                    'total_records': stats['total_records'],
                    'emotion_distribution': emotion_dist,
                    'age_distribution': age_dist,
                    'most_common_emotion': most_common_emotion,
                    'average_age': stats['average_age'],
                    'keyword_frequency': keyword_freq,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'total_records': 0,
                    'emotion_distribution': {},
                    'age_distribution': {},
                    'most_common_emotion': '',
                    'average_age': 0,
                    'keyword_frequency': {},
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"从MongoDB获取统计数据失败: {str(e)}")
            raise
    
    def export_elderly_data(self, format: str = 'csv', user_id: str = None) -> str:
        """导出老人数据"""
        if not config.ELDERLY_EXPORT_ENABLED:
            raise ValueError("老人数据导出功能已禁用")
        
        try:
            data = self.get_elderly_emotions(user_id=user_id, per_page=10000)
            
            if format.lower() == 'csv':
                return self._export_to_csv(data['emotions'])
            elif format.lower() == 'json':
                return self._export_to_json(data['emotions'])
            else:
                raise ValueError(f"不支持的导出格式: {format}")
                
        except Exception as e:
            logger.error(f"导出老人数据失败: {str(e)}")
            raise
    
    def _export_to_csv(self, emotions: List[Dict[str, Any]]) -> str:
        """导出为CSV格式"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = f"./storage/elderly_export_{timestamp}.csv"
        
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            if emotions:
                writer = csv.DictWriter(f, fieldnames=emotions[0].keys())
                writer.writeheader()
                writer.writerows(emotions)
        
        return export_path
    
    def _export_to_json(self, emotions: List[Dict[str, Any]]) -> str:
        """导出为JSON格式"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = f"./storage/elderly_export_{timestamp}.json"
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(emotions, f, ensure_ascii=False, indent=2, default=str)
        
        return export_path
    
    def close(self):
        """关闭连接"""
        try:
            if self.client:
                self.client.close()
                logger.info("老人数据MongoDB连接已关闭")
        except Exception as e:
            logger.error(f"关闭老人数据连接时发生错误: {str(e)}")
    
    def __del__(self):
        """析构函数"""
        self.close()

# 创建全局实例
elderly_data_manager = ElderlyDataManager() 