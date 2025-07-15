#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 老人数据系统测试
测试老人关键词识别、数据存储、查询和统计功能
"""

import sys
import os
import json
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from utils.elderly_storage import elderly_data_manager
# 暂时注释掉emotion_analyzer的导入以避免循环依赖
# from services.emotion_analysis import emotion_analyzer

def print_separator(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_elderly_keywords():
    """测试老人关键词识别"""
    print_separator("老人关键词识别测试")
    
    test_texts = [
        "今天孙子来看我了，真的很开心",
        "最近老伴身体不太好，需要经常看病",
        "退休后的生活很无聊，想念年轻时的日子",
        "昨天去广场舞，遇到了老朋友",
        "血压有点高，医生说要按时吃药",
        "今天天气很好，心情也不错",  # 非老人文本
        "工作很忙，压力很大"  # 非老人文本
    ]
    
    print("🔍 测试关键词匹配功能...")
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 测试文本 {i}: {text}")
        
        # 获取匹配的关键词
        matched_keywords = elderly_data_manager.get_matched_keywords(text)
        
        print(f"✅ 匹配的关键词: {matched_keywords}")
        print(f"📊 关键词数量: {len(matched_keywords)}")
        
        # 判断是否为老人群体（基于关键词）
        is_elderly_by_keywords = len(matched_keywords) >= config.ELDERLY_KEYWORD_THRESHOLD
        print(f"🎯 基于关键词的老人判断: {is_elderly_by_keywords}")
    
    print(f"\n📋 系统配置:")
    print(f"   - 总关键词数: {len(config.ELDERLY_KEYWORDS)}")
    print(f"   - 关键词阈值: {config.ELDERLY_KEYWORD_THRESHOLD}")
    print(f"   - 最小年龄: {config.ELDERLY_MIN_AGE}")

def test_elderly_detection():
    """测试老人群体检测"""
    print_separator("老人群体检测测试")
    
    test_cases = [
        {
            "text": "今天孙子来看我了，真的很开心",
            "context": {"age": 70, "gender": "女", "age_group": "senior"},
            "description": "年龄+关键词双重匹配"
        },
        {
            "text": "最近工作很忙，压力很大",
            "context": {"age": 68, "gender": "男"},
            "description": "仅年龄匹配"
        },
        {
            "text": "昨天去广场舞，遇到了老朋友",
            "context": {"age": 45, "gender": "女"},
            "description": "仅关键词匹配"
        },
        {
            "text": "今天天气很好，心情也不错",
            "context": {"age": 30, "gender": "男"},
            "description": "无匹配条件"
        },
        {
            "text": "退休后经常想念老伴，觉得很孤独",
            "context": {"age_group": "elderly"},
            "description": "年龄组别匹配"
        }
    ]
    
    print("🎯 测试老人群体检测功能...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {test_case['description']}")
        print(f"文本: {test_case['text']}")
        print(f"用户上下文: {test_case['context']}")
        
        # 执行检测
        is_elderly = elderly_data_manager.is_elderly_context(test_case['context'], test_case['text'])
        matched_keywords = elderly_data_manager.get_matched_keywords(test_case['text'])
        
        print(f"✅ 检测结果:")
        print(f"   - 是否为老人群体: {is_elderly}")
        print(f"   - 匹配关键词: {matched_keywords}")
        print(f"   - 关键词数量: {len(matched_keywords)}")
        
        # 详细分析
        age_based = test_case['context'].get('age', 0) >= config.ELDERLY_MIN_AGE
        age_group_based = test_case['context'].get('age_group', '') in ['senior', 'elderly', '老年', '老人']
        keyword_based = len(matched_keywords) >= config.ELDERLY_KEYWORD_THRESHOLD
        
        print(f"   - 年龄判断: {age_based} (年龄: {test_case['context'].get('age', 0)})")
        print(f"   - 年龄组判断: {age_group_based} (组别: {test_case['context'].get('age_group', '')})")
        print(f"   - 关键词判断: {keyword_based} (阈值: {config.ELDERLY_KEYWORD_THRESHOLD})")

def test_elderly_storage():
    """测试老人数据存储"""
    print_separator("老人数据存储测试")
    
    # 初始化存储
    print("🔧 初始化老人数据存储...")
    elderly_data_manager.init_storage()
    
    # 准备测试数据
    test_data = [
        {
            "user_id": "elderly_user_001",
            "text": "今天孙子来看我了，真的很开心，但是他走了以后又觉得有点孤单",
            "primary_emotion": "happy",
            "confidence": 0.85,
            "age": 70,
            "gender": "女",
            "age_group": "senior",
            "keywords_matched": ["孙子", "开心", "孤单"],
            "keyword_count": 3,
            "elderly_specific": {
                "health_concern": 0.1,
                "family_relation": 0.9,
                "loneliness": 0.6,
                "nostalgia": 0.2
            },
            "ai_suggestions": ["建议与家人多多交流分享", "可以考虑参加社区活动"]
        },
        {
            "user_id": "elderly_user_002",
            "text": "最近身体不太好，经常失眠，担心会不会有什么大问题",
            "primary_emotion": "worried",
            "confidence": 0.78,
            "age": 68,
            "gender": "男",
            "age_group": "elderly",
            "keywords_matched": ["身体", "失眠", "担心"],
            "keyword_count": 3,
            "elderly_specific": {
                "health_concern": 0.9,
                "family_relation": 0.2,
                "loneliness": 0.3,
                "nostalgia": 0.1
            },
            "ai_suggestions": ["建议定期体检", "适当的担心是正常的，但不要过度焦虑"]
        }
    ]
    
    print("💾 测试数据保存...")
    saved_ids = []
    
    for i, data in enumerate(test_data, 1):
        print(f"\n📝 保存测试数据 {i}")
        print(f"用户ID: {data['user_id']}")
        print(f"文本: {data['text'][:30]}...")
        
        try:
            saved_id = elderly_data_manager.save_elderly_emotion(data)
            saved_ids.append(saved_id)
            print(f"✅ 保存成功，ID: {saved_id}")
        except Exception as e:
            print(f"❌ 保存失败: {str(e)}")
    
    print(f"\n📋 保存总结:")
    print(f"   - 成功保存: {len(saved_ids)} 条记录")
    print(f"   - 存储类型: {config.ELDERLY_DATA_STORAGE_TYPE}")
    print(f"   - 存储路径: {config.ELDERLY_CSV_PATH}")
    
    return saved_ids

def test_elderly_query():
    """测试老人数据查询"""
    print_separator("老人数据查询测试")
    
    print("🔍 测试数据查询功能...")
    
    # 查询所有数据
    print("\n📋 查询所有老人情感数据:")
    try:
        result = elderly_data_manager.get_elderly_emotions(page=1, per_page=10)
        print(f"✅ 查询成功:")
        print(f"   - 总记录数: {result['total']}")
        print(f"   - 当前页: {result['page']}")
        print(f"   - 每页数量: {result['per_page']}")
        print(f"   - 总页数: {result['pages']}")
        print(f"   - 当前页记录数: {len(result['emotions'])}")
        
        if result['emotions']:
            print(f"\n📝 示例记录:")
            emotion = result['emotions'][0]
            print(f"   - ID: {emotion['id']}")
            print(f"   - 用户ID: {emotion['user_id']}")
            print(f"   - 主要情感: {emotion['primary_emotion']}")
            print(f"   - 置信度: {emotion['confidence']}")
            print(f"   - 年龄: {emotion['age']}")
            print(f"   - 关键词: {emotion['keywords_matched']}")
            
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
    
    # 按用户ID查询
    print("\n👤 按用户ID查询:")
    try:
        result = elderly_data_manager.get_elderly_emotions(user_id="elderly_user_001", page=1, per_page=5)
        print(f"✅ 查询成功，找到 {result['total']} 条记录")
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
    
    # 按情感过滤
    print("\n😊 按情感过滤查询:")
    try:
        result = elderly_data_manager.get_elderly_emotions(emotion_filter="happy", page=1, per_page=5)
        print(f"✅ 查询成功，找到 {result['total']} 条开心情感记录")
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")

def test_elderly_statistics():
    """测试老人数据统计"""
    print_separator("老人数据统计测试")
    
    print("📊 测试统计功能...")
    
    try:
        # 获取总体统计
        stats = elderly_data_manager.get_elderly_statistics()
        
        print(f"✅ 统计数据获取成功:")
        print(f"   - 总记录数: {stats['total_records']}")
        print(f"   - 平均年龄: {stats['average_age']:.1f}岁")
        print(f"   - 最常见情感: {stats['most_common_emotion']}")
        
        print(f"\n📈 情感分布:")
        for emotion, count in stats['emotion_distribution'].items():
            print(f"   - {emotion}: {count} 次")
        
        print(f"\n📊 年龄分布:")
        for age, count in stats['age_distribution'].items():
            print(f"   - {age}岁: {count} 次")
        
        print(f"\n🔤 关键词频率 (前10):")
        sorted_keywords = sorted(stats['keyword_frequency'].items(), key=lambda x: x[1], reverse=True)
        for keyword, count in sorted_keywords[:10]:
            print(f"   - {keyword}: {count} 次")
        
    except Exception as e:
        print(f"❌ 统计功能测试失败: {str(e)}")

def test_elderly_emotion_analysis():
    """测试老人情感分析集成"""
    print_separator("老人情感分析集成测试")
    
    print("🧠 测试老人数据存储管理器的核心功能...")
    print("📝 注意：为避免循环依赖，暂时跳过emotion_analyzer集成测试")
    
    test_cases = [
        {
            "text": "今天孙子来看我了，真的很开心，但是他走了以后又觉得有点孤单",
            "context": {"user_id": "test_elderly_001", "age": 70, "gender": "女", "age_group": "senior"},
            "description": "老人家庭情感"
        },
        {
            "text": "最近身体不太好，经常失眠，担心会不会有什么大问题",
            "context": {"user_id": "test_elderly_002", "age": 68, "gender": "男"},
            "description": "老人健康担忧"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {test_case['description']}")
        print(f"文本: {test_case['text']}")
        print(f"上下文: {test_case['context']}")
        
        try:
            # 测试老人群体检测
            is_elderly = elderly_data_manager.is_elderly_context(test_case['context'], test_case['text'])
            matched_keywords = elderly_data_manager.get_matched_keywords(test_case['text'])
            
            print(f"✅ 老人群体检测结果:")
            print(f"   - 是否为老人群体: {is_elderly}")
            print(f"   - 匹配关键词: {matched_keywords}")
            print(f"   - 关键词数量: {len(matched_keywords)}")
            
            # 模拟保存老人情感数据
            elderly_data = {
                'user_id': test_case['context']['user_id'],
                'text': test_case['text'],
                'primary_emotion': 'happy' if i == 1 else 'worried',
                'confidence': 0.85,
                'age': test_case['context'].get('age', 0),
                'gender': test_case['context'].get('gender', ''),
                'age_group': test_case['context'].get('age_group', ''),
                'keywords_matched': matched_keywords,
                'keyword_count': len(matched_keywords),
                'elderly_specific': {
                    'health_concern': 0.1 if i == 1 else 0.9,
                    'family_relation': 0.9 if i == 1 else 0.2,
                    'loneliness': 0.6 if i == 1 else 0.3,
                    'nostalgia': 0.2 if i == 1 else 0.1
                },
                'ai_suggestions': ['建议与家人多多交流分享'] if i == 1 else ['建议定期体检']
            }
            
            if is_elderly:
                saved_id = elderly_data_manager.save_elderly_emotion(elderly_data)
                print(f"✅ 老人情感数据保存成功，ID: {saved_id}")
            else:
                print("ℹ️  未检测为老人群体，跳过数据保存")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    print("🚀 PGG老人数据系统测试开始")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 测试关键词识别
        test_elderly_keywords()
        
        # 测试老人群体检测
        test_elderly_detection()
        
        # 测试数据存储
        test_elderly_storage()
        
        # 测试数据查询
        test_elderly_query()
        
        # 测试统计功能
        test_elderly_statistics()
        
        # 测试情感分析集成
        test_elderly_emotion_analysis()
        
        print_separator("测试完成")
        print("✅ 所有测试完成！")
        print(f"📊 存储类型: {config.ELDERLY_DATA_STORAGE_TYPE}")
        print(f"📁 存储路径: {config.ELDERLY_CSV_PATH if config.ELDERLY_DATA_STORAGE_TYPE == 'CSV' else 'MongoDB'}")
        
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 