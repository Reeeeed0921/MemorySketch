#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 情绪识别API测试脚本
测试所有情绪识别相关的API接口
"""

import requests
import json
import time
import os
import wave
import struct
from datetime import datetime

# 配置API基础URL
BASE_URL = "http://localhost:5000"
EMOTION_API_BASE = f"{BASE_URL}/emotion"

def print_separator(title):
    """打印分隔线"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_result(response):
    """打印API响应结果"""
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"响应内容: {response.text}")

def test_emotion_service_status():
    """测试情绪识别服务状态"""
    print_separator("测试情绪识别服务状态")
    
    try:
        response = requests.get(f"{EMOTION_API_BASE}/status")
        print_result(response)
        
        if response.status_code == 200:
            data = response.json()
            service_status = data.get('data', {}).get('service_status', {})
            print(f"\n✅ 服务状态: {'可用' if service_status.get('service_available') else '不可用'}")
            print(f"✅ 支持的情绪类型: {len(service_status.get('supported_emotions', []))}种")
            print(f"✅ 支持的语言: {service_status.get('supported_languages', [])}")
            print(f"✅ 分析方法: {service_status.get('analysis_methods', [])}")
        else:
            print("❌ 服务状态检查失败")
    except Exception as e:
        print(f"❌ 服务状态检查异常: {str(e)}")

def test_text_emotion_analysis():
    """测试文本情绪识别"""
    print_separator("测试文本情绪识别")
    
    test_texts = [
        "今天心情很好，天气很棒！",
        "我感到很悲伤，事情没有按计划进行。",
        "太生气了，这完全不公平！",
        "我很害怕，不知道该怎么办。",
        "哇，这真是太令人惊讶了！",
        "我爱这个地方，这里太美了。",
        "感到很平静，内心很安详。",
        "怀念过去的美好时光。"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- 测试文本 {i} ---")
        print(f"输入文本: {text}")
        
        try:
            response = requests.post(
                f"{EMOTION_API_BASE}/analyze-text",
                json={
                    "text": text,
                    "include_suggestions": True,
                    "user_id": "test_user"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                emotion_data = data.get('data', {}).get('emotion', {})
                print(f"✅ 识别结果: {emotion_data.get('description', 'N/A')}")
                print(f"✅ 置信度: {emotion_data.get('confidence', 0):.2f}")
                print(f"✅ 建议: {data.get('data', {}).get('suggestions', [])}")
            else:
                print(f"❌ 分析失败: {response.status_code}")
                print(f"错误信息: {response.text}")
        except Exception as e:
            print(f"❌ 分析异常: {str(e)}")
        
        time.sleep(0.5)  # 避免请求过快

def test_batch_emotion_analysis():
    """测试批量情绪分析"""
    print_separator("测试批量情绪分析")
    
    test_texts = [
        "我很开心",
        "有点难过",
        "特别兴奋",
        "感到焦虑",
        "很平静"
    ]
    
    print(f"批量分析文本: {test_texts}")
    
    try:
        response = requests.post(
            f"{EMOTION_API_BASE}/batch-analyze",
            json={
                "texts": test_texts,
                "include_suggestions": False,
                "user_id": "test_user"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('data', {}).get('results', [])
            summary = data.get('data', {}).get('summary', {})
            
            print(f"✅ 批量分析成功")
            print(f"✅ 分析文本数量: {summary.get('total_texts', 0)}")
            print(f"✅ 情绪分布: {summary.get('emotion_distribution', {})}")
            print(f"✅ 最常见情绪: {summary.get('most_common_emotion', 'N/A')}")
            
            for result in results:
                emotion = result.get('emotion', {})
                print(f"  文本 {result.get('index', 0)+1}: {emotion.get('description', 'N/A')} (置信度: {emotion.get('confidence', 0):.2f})")
        else:
            print(f"❌ 批量分析失败: {response.status_code}")
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 批量分析异常: {str(e)}")

def create_test_audio_file():
    """创建测试音频文件"""
    filename = "test_emotion_audio.wav"
    
    # 创建一个简单的音频文件（440Hz的正弦波，1秒）
    sample_rate = 44100
    duration = 1.0
    frequency = 440.0
    
    samples = []
    for i in range(int(sample_rate * duration)):
        sample = int(32767 * 0.5 * (1 + (i % int(sample_rate / frequency)) / (sample_rate / frequency)))
        samples.append(sample)
    
    # 保存为WAV文件
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16位
        wav_file.setframerate(sample_rate)
        
        for sample in samples:
            wav_file.writeframes(struct.pack('<h', sample))
    
    return filename

def test_audio_emotion_analysis():
    """测试音频情绪识别"""
    print_separator("测试音频情绪识别")
    
    # 创建测试音频文件
    audio_file = create_test_audio_file()
    
    try:
        print(f"创建测试音频文件: {audio_file}")
        
        with open(audio_file, 'rb') as f:
            response = requests.post(
                f"{EMOTION_API_BASE}/analyze-audio",
                files={'audio': f},
                data={
                    'include_suggestions': 'true',
                    'user_id': 'test_user'
                }
            )
        
        if response.status_code == 200:
            data = response.json()
            emotion_data = data.get('data', {}).get('emotion', {})
            print(f"✅ 音频情绪分析成功")
            print(f"✅ 识别结果: {emotion_data.get('description', 'N/A')}")
            print(f"✅ 置信度: {emotion_data.get('confidence', 0):.2f}")
            print(f"✅ 分析模型: {emotion_data.get('analysis_model', 'N/A')}")
            print(f"✅ 建议: {data.get('data', {}).get('suggestions', [])}")
        else:
            print(f"❌ 音频分析失败: {response.status_code}")
            print(f"错误信息: {response.text}")
    
    except Exception as e:
        print(f"❌ 音频分析异常: {str(e)}")
    
    finally:
        # 清理测试文件
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"✅ 清理测试文件: {audio_file}")

def test_all_emotion_endpoints():
    """测试所有情绪识别相关的端点"""
    print_separator("测试所有情绪识别API端点")
    
    endpoints = [
        f"{EMOTION_API_BASE}/status",
        f"{EMOTION_API_BASE}/analyze-text",
        f"{EMOTION_API_BASE}/analyze-audio",
        f"{EMOTION_API_BASE}/batch-analyze"
    ]
    
    for endpoint in endpoints:
        try:
            # 对于GET请求，直接测试
            if 'status' in endpoint:
                response = requests.get(endpoint)
            else:
                # 对于POST请求，发送空请求测试错误处理
                response = requests.post(endpoint)
            
            status = "✅ 可访问" if response.status_code < 500 else "❌ 服务器错误"
            print(f"{endpoint}: {status} (状态码: {response.status_code})")
        except Exception as e:
            print(f"{endpoint}: ❌ 连接失败 - {str(e)}")

def main():
    """主测试函数"""
    print("PGG情感记忆生成系统 - 情绪识别API测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API基础URL: {BASE_URL}")
    
    # 测试所有端点可访问性
    test_all_emotion_endpoints()
    
    # 测试服务状态
    test_emotion_service_status()
    
    # 测试文本情绪识别
    test_text_emotion_analysis()
    
    # 测试批量情绪分析
    test_batch_emotion_analysis()
    
    # 测试音频情绪识别
    test_audio_emotion_analysis()
    
    print_separator("测试完成")
    print("🎉 所有情绪识别API测试完成！")
    print("\n📋 API接口总结:")
    print("• GET  /emotion/status        - 获取服务状态")
    print("• POST /emotion/analyze-text  - 文本情绪分析")
    print("• POST /emotion/analyze-audio - 音频情绪分析")
    print("• POST /emotion/batch-analyze - 批量情绪分析")
    print("\n📖 使用说明:")
    print("• 文本分析支持中文和英文")
    print("• 音频分析支持WAV格式")
    print("• 批量分析最多支持50个文本")
    print("• 所有API都支持建议功能")

if __name__ == "__main__":
    main() 