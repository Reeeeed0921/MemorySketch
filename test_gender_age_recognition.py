#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科大讯飞性别年龄识别功能测试
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from config import config
from services.speech_to_text import speech_service


def test_gender_age_recognition():
    """测试科大讯飞性别年龄识别功能"""
    print("🎤 科大讯飞性别年龄识别功能测试")
    print("=" * 50)
    
    # 验证配置
    print("1. 验证配置...")
    api_info = config.get_api_priority()
    print(f"   - 科大讯飞语音: {'✅' if api_info['has_iflytek_speech_key'] else '❌'}")
    print(f"   - 科大讯飞性别年龄: {'✅' if api_info['has_iflytek_gender_age_key'] else '❌'}")
    print(f"   - API ID: {config.IFLYTEK_GENDER_AGE_API_ID}")
    print(f"   - API URL: {config.IFLYTEK_GENDER_AGE_API_URL}")
    print()
    
    # 初始化服务
    print("2. 初始化语音服务...")
    speech_service.init_models()
    service_status = speech_service.get_service_status()
    print(f"   - API可用状态: {service_status['api_available']}")
    print()
    
    # 创建测试音频文件（模拟）
    print("3. 创建测试音频文件...")
    test_audio_dir = os.path.join(config.LOCAL_STORAGE_PATH, 'test_audio')
    os.makedirs(test_audio_dir, exist_ok=True)
    
    # 创建一个简单的测试音频文件（模拟）
    test_audio_path = os.path.join(test_audio_dir, 'test_voice.wav')
    with open(test_audio_path, 'wb') as f:
        # 写入一些模拟的音频数据（这不是真正的音频格式，仅用于测试）
        f.write(b'RIFF\x00\x00\x00\x00WAVE' + b'\x00' * 100)
    
    print(f"   - 测试音频文件: {test_audio_path}")
    print()
    
    # 测试语音转文字+性别年龄识别
    print("4. 测试语音转文字+性别年龄识别...")
    try:
        result = speech_service.convert_audio_to_text(
            test_audio_path,
            language="zh-CN"
        )
        
        print("   - 语音转文字结果:")
        print(f"     * 文本: {result.get('text', 'N/A')}")
        print(f"     * 置信度: {result.get('confidence', 0):.2f}")
        print(f"     * 服务: {result.get('service', 'N/A')}")
        print()
        
        if 'gender_age' in result:
            gender_age = result['gender_age']
            print("   - 性别年龄识别结果:")
            print(f"     * 性别: {gender_age.get('gender', 'N/A')}")
            print(f"     * 性别置信度: {gender_age.get('gender_confidence', 0):.2f}")
            print(f"     * 年龄: {gender_age.get('age', 'N/A')}")
            print(f"     * 年龄置信度: {gender_age.get('age_confidence', 0):.2f}")
            print(f"     * 服务: {gender_age.get('service', 'N/A')}")
            
            if gender_age.get('note'):
                print(f"     * 注意: {gender_age['note']}")
        else:
            print("   - 未检测到性别年龄信息")
        
        print()
        print("✅ 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    finally:
        # 清理测试文件
        try:
            os.remove(test_audio_path)
            os.rmdir(test_audio_dir)
        except:
            pass


def test_api_configuration():
    """测试API配置"""
    print("\n📊 API配置详情:")
    print("=" * 30)
    
    configs = [
        ("科大讯飞语音API ID", config.IFLYTEK_APP_ID),
        ("科大讯飞语音API Key", config.IFLYTEK_API_KEY[:10] + "..." if config.IFLYTEK_API_KEY else "未配置"),
        ("科大讯飞语音API Secret", config.IFLYTEK_API_SECRET[:10] + "..." if config.IFLYTEK_API_SECRET else "未配置"),
        ("科大讯飞性别年龄API ID", config.IFLYTEK_GENDER_AGE_API_ID),
        ("科大讯飞性别年龄API Key", config.IFLYTEK_GENDER_AGE_API_KEY[:10] + "..." if config.IFLYTEK_GENDER_AGE_API_KEY else "未配置"),
        ("科大讯飞性别年龄API Secret", config.IFLYTEK_GENDER_AGE_API_SECRET[:10] + "..." if config.IFLYTEK_GENDER_AGE_API_SECRET else "未配置"),
        ("科大讯飞性别年龄API URL", config.IFLYTEK_GENDER_AGE_API_URL),
    ]
    
    for name, value in configs:
        print(f"{name}: {value}")


if __name__ == "__main__":
    print("🚀 启动科大讯飞性别年龄识别测试")
    print()
    
    test_api_configuration()
    test_gender_age_recognition()
    
    print()
    print("📝 说明:")
    print("   - 这是一个功能测试，使用模拟数据")
    print("   - 真实的API调用需要有效的音频文件")
    print("   - 性别年龄识别与语音转文字同时进行")
    print("   - 支持的性别: male, female")
    print("   - 支持的年龄段: child, youth, middle_aged, senior") 