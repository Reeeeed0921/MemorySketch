#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - DeepSeek情感分析测试脚本
测试DeepSeek API集成，特别针对老人群体的情感分析
"""

import requests
import json
import os
from datetime import datetime
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.emotion_analysis import EmotionAnalyzer

def print_separator(title):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_deepseek_integration():
    """测试DeepSeek集成"""
    print_separator("DeepSeek情感分析集成测试")
    
    # 创建情感分析器
    analyzer = EmotionAnalyzer()
    
    # 测试文本样本（针对老人群体）
    test_cases = [
        {
            "text": "今天孙子来看我了，真的很开心，但是他走了以后又觉得有点孤单",
            "context": {"age": 70, "age_group": "senior"},
            "description": "老人家庭情感测试"
        },
        {
            "text": "最近身体不太好，经常失眠，担心会不会有什么大问题",
            "context": {"age": 68, "age_group": "elderly"},
            "description": "老人健康担忧测试"
        },
        {
            "text": "想起年轻时候和老伴一起的日子，那时候虽然苦但是很快乐",
            "context": {"age": 75, "recent_text": "退休后的生活"},
            "description": "老人怀旧情感测试"
        },
        {
            "text": "今天天气很好，心情也不错，准备去公园散步",
            "context": {"age": 30},
            "description": "年轻人情感测试（对比）"
        },
        {
            "text": "邻居家的孩子很吵，但是看到他们活蹦乱跳的样子，也挺羡慕的",
            "context": {"age": 72, "age_group": "senior"},
            "description": "老人复杂情感测试"
        }
    ]
    
    print("🧪 开始测试DeepSeek情感分析...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {test_case['description']}")
        print(f"文本: {test_case['text']}")
        print(f"用户上下文: {test_case['context']}")
        
        try:
            # 调用情感分析
            result = analyzer.analyze_text(test_case['text'], test_case['context'])
            
            # 打印结果
            print(f"✅ 分析结果:")
            print(f"   主要情感: {result['primary_emotion']}")
            print(f"   置信度: {result['confidence']:.2f}")
            print(f"   分析模型: {result['analysis_model']}")
            
            # 显示老人特有的分析结果
            if 'elderly_specific' in result:
                print(f"   老人特有指标: {result['elderly_specific']}")
            
            # 显示AI建议
            if 'ai_suggestions' in result and result['ai_suggestions']:
                print(f"   AI建议:")
                for suggestion in result['ai_suggestions']:
                    print(f"     - {suggestion}")
            
            # 显示情感得分
            if 'emotion_scores' in result:
                print(f"   情感得分:")
                for emotion, score in result['emotion_scores'].items():
                    if score > 0.1:  # 只显示显著的情感
                        print(f"     {emotion}: {score:.2f}")
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    return True

def test_deepseek_api_direct():
    """直接测试DeepSeek API"""
    print_separator("直接测试DeepSeek API")
    
    # 从环境变量获取API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key or api_key.startswith('your_'):
        print("❌ DeepSeek API密钥未配置，跳过直接API测试")
        return False
    
    print(f"🔑 使用API密钥: {api_key[:8]}...")
    
    # 测试API连接
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': '你是一位专业的情感分析专家。'},
            {'role': 'user', 'content': '请分析这句话的情感："今天心情很好，但是有点想家。"'}
        ],
        'max_tokens': 500,
        'temperature': 0.7
    }
    
    try:
        response = requests.post(
            'https://api.deepseek.com/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ DeepSeek API连接成功!")
            print(f"响应: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ DeepSeek API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek API连接失败: {str(e)}")
        return False

def test_config_status():
    """测试配置状态"""
    print_separator("配置状态检查")
    
    from config import config
    
    # 检查DeepSeek配置
    deepseek_config = {
        'API_KEY': config.DEEPSEEK_API_KEY,
        'API_URL': config.DEEPSEEK_API_URL,
        'MODEL': config.DEEPSEEK_MODEL,
        'MAX_TOKENS': config.DEEPSEEK_MAX_TOKENS,
        'TEMPERATURE': config.DEEPSEEK_TEMPERATURE
    }
    
    print("🔧 DeepSeek配置:")
    for key, value in deepseek_config.items():
        if 'KEY' in key:
            # 隐藏API密钥
            display_value = f"{value[:8]}..." if value and len(value) > 8 else value
            is_valid = value and not value.startswith('your_')
            status = "✅" if is_valid else "❌"
            print(f"   {key}: {display_value} {status}")
        else:
            print(f"   {key}: {value}")
    
    # 检查其他相关配置
    print("\n🔧 其他API配置:")
    other_apis = {
        'OpenAI': config.OPENAI_API_KEY,
        '科大讯飞语音': config.IFLYTEK_API_KEY,
        '科大讯飞图像': config.IFLYTEK_IMAGE_API_KEY
    }
    
    for name, key in other_apis.items():
        is_valid = key and not key.startswith('your_')
        status = "✅" if is_valid else "❌"
        display_key = f"{key[:8]}..." if key and len(key) > 8 else key
        print(f"   {name}: {display_key} {status}")

def main():
    """主测试函数"""
    print("🚀 启动DeepSeek情感分析测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 配置检查
    test_config_status()
    
    # 2. 直接API测试
    api_available = test_deepseek_api_direct()
    
    # 3. 集成测试
    if api_available:
        test_deepseek_integration()
    else:
        print("\n⚠️  DeepSeek API不可用，将使用降级方案测试")
        test_deepseek_integration()
    
    print_separator("测试完成")
    print("✅ 所有测试已完成！")
    print("\n💡 使用建议:")
    print("1. 如果API不可用，请检查DEEPSEEK_API_KEY环境变量")
    print("2. 确保API密钥有效且有足够的额度")
    print("3. 老人群体的情感分析会有特殊的处理逻辑")
    print("4. 系统会自动降级到其他分析方法")

if __name__ == "__main__":
    main() 