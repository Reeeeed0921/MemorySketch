# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 数据库管理
提供MongoDB数据库连接和数据操作功能
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database
import math

from config import config
from models import MemoryRecord, UserStatistics, EmotionResult

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        """初始化数据库管理器"""
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.memories_collection: Optional[Collection] = None
        self.stats_collection: Optional[Collection] = None
        self.use_local_storage = config.USE_LOCAL_STORAGE
        self.local_storage_path = config.LOCAL_STORAGE_PATH
        
        # 如果使用本地存储，创建存储目录
        if self.use_local_storage:
            os.makedirs(self.local_storage_path, exist_ok=True)
            self.memories_file = os.path.join(self.local_storage_path, 'memories.json')
            self.stats_file = os.path.join(self.local_storage_path, 'user_stats.json')
    
    def init_database(self):
        """初始化数据库连接"""
        try:
            if self.use_local_storage:
                logger.info("使用本地存储模式")
                self._init_local_storage()
            else:
                logger.info("使用MongoDB数据库")
                self._init_mongodb()
            
            logger.info("✅ 数据库初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {str(e)}")
            raise
    
    def _init_mongodb(self):
        """初始化MongoDB连接"""
        try:
            # 连接MongoDB
            self.client = MongoClient(
                config.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            
            # 测试连接
            self.client.admin.command('ping')
            
            # 获取数据库
            self.db = self.client[config.DATABASE_NAME]
            
            # 获取集合
            self.memories_collection = self.db.memories
            self.stats_collection = self.db.user_statistics
            
            # 创建索引
            self._create_indexes()
            
            logger.info(f"MongoDB连接成功: {config.MONGODB_URI}")
            
        except Exception as e:
            logger.error(f"MongoDB连接失败: {str(e)}")
            logger.info("切换到本地存储模式")
            self.use_local_storage = True
            self._init_local_storage()
    
    def _init_local_storage(self):
        """初始化本地存储"""
        try:
            # 创建存储文件（如果不存在）
            if not os.path.exists(self.memories_file):
                with open(self.memories_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            
            if not os.path.exists(self.stats_file):
                with open(self.stats_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
            
            logger.info(f"本地存储初始化成功: {self.local_storage_path}")
            
        except Exception as e:
            logger.error(f"本地存储初始化失败: {str(e)}")
            raise
    
    def _create_indexes(self):
        """创建MongoDB索引"""
        try:
            # 回忆记录索引
            self.memories_collection.create_index("user_id")
            self.memories_collection.create_index("created_at")
            self.memories_collection.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
            self.memories_collection.create_index("emotion_result.primary_emotion")
            
            # 用户统计索引
            self.stats_collection.create_index("user_id", unique=True)
            
            logger.info("MongoDB索引创建成功")
            
        except Exception as e:
            logger.warning(f"创建索引时发生警告: {str(e)}")
    
    def save_memory(self, memory: MemoryRecord) -> str:
        """保存回忆记录"""
        try:
            if self.use_local_storage:
                return self._save_memory_local(memory)
            else:
                return self._save_memory_mongodb(memory)
        except Exception as e:
            logger.error(f"保存回忆记录失败: {str(e)}")
            raise
    
    def _save_memory_local(self, memory: MemoryRecord) -> str:
        """本地存储保存回忆记录"""
        try:
            # 读取现有数据
            with open(self.memories_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            # 添加新记录
            memory_data = memory.to_dict()
            memory_data['created_at'] = memory_data['created_at'].isoformat()
            memories.append(memory_data)
            
            # 保存到文件
            with open(self.memories_file, 'w', encoding='utf-8') as f:
                json.dump(memories, f, ensure_ascii=False, indent=2)
            
            # 更新用户统计
            self._update_user_stats_local(memory.user_id, memory.emotion_result.get('primary_emotion', ''), memory.created_at)
            
            logger.info(f"本地保存回忆记录成功: {memory.id}")
            return memory.id
            
        except Exception as e:
            logger.error(f"本地保存回忆记录失败: {str(e)}")
            raise
    
    def _save_memory_mongodb(self, memory: MemoryRecord) -> str:
        """MongoDB保存回忆记录"""
        try:
            # 插入记录
            result = self.memories_collection.insert_one(memory.to_dict())
            
            # 更新用户统计
            self._update_user_stats_mongodb(memory.user_id, memory.emotion_result.get('primary_emotion', ''), memory.created_at)
            
            logger.info(f"MongoDB保存回忆记录成功: {memory.id}")
            return memory.id
            
        except Exception as e:
            logger.error(f"MongoDB保存回忆记录失败: {str(e)}")
            raise
    
    def get_memories(self, user_id: str, page: int = 1, per_page: int = 20, emotion_filter: str = None) -> Dict[str, Any]:
        """获取用户回忆记录"""
        try:
            if self.use_local_storage:
                return self._get_memories_local(user_id, page, per_page, emotion_filter)
            else:
                return self._get_memories_mongodb(user_id, page, per_page, emotion_filter)
        except Exception as e:
            logger.error(f"获取回忆记录失败: {str(e)}")
            raise
    
    def _get_memories_local(self, user_id: str, page: int, per_page: int, emotion_filter: str) -> Dict[str, Any]:
        """本地存储获取回忆记录"""
        try:
            # 读取所有记录
            with open(self.memories_file, 'r', encoding='utf-8') as f:
                all_memories = json.load(f)
            
            # 过滤用户记录
            user_memories = [m for m in all_memories if m.get('user_id') == user_id]
            
            # 情感过滤
            if emotion_filter:
                user_memories = [m for m in user_memories if m.get('emotion_result', {}).get('primary_emotion') == emotion_filter]
            
            # 按时间排序（最新的在前）
            user_memories.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # 分页
            total = len(user_memories)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_memories = user_memories[start_idx:end_idx]
            
            # 转换为MemoryRecord对象
            memories = []
            for mem_data in page_memories:
                mem_data['created_at'] = datetime.fromisoformat(mem_data['created_at'])
                memories.append(MemoryRecord.from_dict(mem_data))
            
            return {
                'memories': memories,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': math.ceil(total / per_page)
            }
            
        except Exception as e:
            logger.error(f"本地获取回忆记录失败: {str(e)}")
            raise
    
    def _get_memories_mongodb(self, user_id: str, page: int, per_page: int, emotion_filter: str) -> Dict[str, Any]:
        """MongoDB获取回忆记录"""
        try:
            # 构建查询条件
            query = {'user_id': user_id}
            if emotion_filter:
                query['emotion_result.primary_emotion'] = emotion_filter
            
            # 获取总数
            total = self.memories_collection.count_documents(query)
            
            # 分页查询
            skip = (page - 1) * per_page
            cursor = self.memories_collection.find(query).sort('created_at', DESCENDING).skip(skip).limit(per_page)
            
            # 转换为MemoryRecord对象
            memories = []
            for doc in cursor:
                memories.append(MemoryRecord.from_dict(doc))
            
            return {
                'memories': memories,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': math.ceil(total / per_page)
            }
            
        except Exception as e:
            logger.error(f"MongoDB获取回忆记录失败: {str(e)}")
            raise
    
    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryRecord]:
        """根据ID获取回忆记录"""
        try:
            if self.use_local_storage:
                return self._get_memory_by_id_local(memory_id)
            else:
                return self._get_memory_by_id_mongodb(memory_id)
        except Exception as e:
            logger.error(f"根据ID获取回忆记录失败: {str(e)}")
            raise
    
    def _get_memory_by_id_local(self, memory_id: str) -> Optional[MemoryRecord]:
        """本地存储根据ID获取回忆记录"""
        try:
            with open(self.memories_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            for mem_data in memories:
                if mem_data.get('id') == memory_id:
                    mem_data['created_at'] = datetime.fromisoformat(mem_data['created_at'])
                    return MemoryRecord.from_dict(mem_data)
            
            return None
            
        except Exception as e:
            logger.error(f"本地根据ID获取回忆记录失败: {str(e)}")
            raise
    
    def _get_memory_by_id_mongodb(self, memory_id: str) -> Optional[MemoryRecord]:
        """MongoDB根据ID获取回忆记录"""
        try:
            doc = self.memories_collection.find_one({'id': memory_id})
            if doc:
                return MemoryRecord.from_dict(doc)
            return None
            
        except Exception as e:
            logger.error(f"MongoDB根据ID获取回忆记录失败: {str(e)}")
            raise
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            if self.use_local_storage:
                return self._get_user_statistics_local(user_id)
            else:
                return self._get_user_statistics_mongodb(user_id)
        except Exception as e:
            logger.error(f"获取用户统计信息失败: {str(e)}")
            raise
    
    def _get_user_statistics_local(self, user_id: str) -> Dict[str, Any]:
        """本地存储获取用户统计信息"""
        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                all_stats = json.load(f)
            
            user_stats = all_stats.get(user_id, {})
            if not user_stats:
                return self._create_empty_stats(user_id)
            
            # 转换日期格式
            if 'first_memory_date' in user_stats and user_stats['first_memory_date']:
                user_stats['first_memory_date'] = datetime.fromisoformat(user_stats['first_memory_date']).isoformat()
            if 'last_memory_date' in user_stats and user_stats['last_memory_date']:
                user_stats['last_memory_date'] = datetime.fromisoformat(user_stats['last_memory_date']).isoformat()
            
            return user_stats
            
        except Exception as e:
            logger.error(f"本地获取用户统计信息失败: {str(e)}")
            return self._create_empty_stats(user_id)
    
    def _get_user_statistics_mongodb(self, user_id: str) -> Dict[str, Any]:
        """MongoDB获取用户统计信息"""
        try:
            doc = self.stats_collection.find_one({'user_id': user_id})
            if doc:
                stats = UserStatistics.from_dict(doc)
                result = stats.to_dict()
                # 格式化日期
                if result['first_memory_date']:
                    result['first_memory_date'] = result['first_memory_date'].isoformat()
                if result['last_memory_date']:
                    result['last_memory_date'] = result['last_memory_date'].isoformat()
                return result
            else:
                return self._create_empty_stats(user_id)
                
        except Exception as e:
            logger.error(f"MongoDB获取用户统计信息失败: {str(e)}")
            return self._create_empty_stats(user_id)
    
    def _create_empty_stats(self, user_id: str) -> Dict[str, Any]:
        """创建空的统计信息"""
        return {
            'user_id': user_id,
            'total_memories': 0,
            'emotion_distribution': {},
            'most_common_emotion': '',
            'first_memory_date': None,
            'last_memory_date': None,
            'emotional_trend': {},
            'updated_at': datetime.now().isoformat()
        }
    
    def _update_user_stats_local(self, user_id: str, emotion: str, memory_date: datetime):
        """本地存储更新用户统计信息"""
        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                all_stats = json.load(f)
            
            if user_id not in all_stats:
                all_stats[user_id] = UserStatistics(user_id).to_dict()
            
            # 更新统计信息
            stats = UserStatistics.from_dict(all_stats[user_id])
            stats.add_memory(emotion, memory_date)
            all_stats[user_id] = stats.to_dict()
            
            # 格式化日期
            if all_stats[user_id]['first_memory_date']:
                all_stats[user_id]['first_memory_date'] = all_stats[user_id]['first_memory_date'].isoformat()
            if all_stats[user_id]['last_memory_date']:
                all_stats[user_id]['last_memory_date'] = all_stats[user_id]['last_memory_date'].isoformat()
            if all_stats[user_id]['updated_at']:
                all_stats[user_id]['updated_at'] = all_stats[user_id]['updated_at'].isoformat()
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(all_stats, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"本地更新用户统计信息失败: {str(e)}")
    
    def _update_user_stats_mongodb(self, user_id: str, emotion: str, memory_date: datetime):
        """MongoDB更新用户统计信息"""
        try:
            # 获取现有统计信息
            doc = self.stats_collection.find_one({'user_id': user_id})
            if doc:
                stats = UserStatistics.from_dict(doc)
            else:
                stats = UserStatistics(user_id)
            
            # 更新统计信息
            stats.add_memory(emotion, memory_date)
            
            # 保存到数据库
            self.stats_collection.replace_one(
                {'user_id': user_id},
                stats.to_dict(),
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"MongoDB更新用户统计信息失败: {str(e)}")
    
    def close(self):
        """关闭数据库连接"""
        try:
            if self.client:
                self.client.close()
                logger.info("MongoDB连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接时发生错误: {str(e)}")
    
    def __del__(self):
        """析构函数"""
        self.close() 