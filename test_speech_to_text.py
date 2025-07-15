#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音转文本功能测试脚本
测试优先级策略和各种API接口
"""

import os
import sys
import requests
import json
from datetime import datetime
import time
import random

# 测试配置
API_BASE_URL = "http://localhost:5000"

def test_speech_service_status():
    """测试语音服务状态接口"""
    print("🔍 测试语音服务状态...")
    try:
        response = requests.get(f"{API_BASE_URL}/speech-to-text/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ 语音服务状态检查通过")
            
            status = data.get('data', {})
            print(f"   API可用状态: {status.get('api_available', {})}")
            print(f"   模型加载状态: {status.get('models_loaded', False)}")
            print(f"   支持语言: {status.get('supported_languages', [])}")
            print(f"   支持格式: {status.get('supported_formats', [])}")
            print(f"   优先级顺序: {status.get('priority_order', [])}")
            
            return True
        else:
            print(f"❌ 语音服务状态检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 语音服务状态检查异常: {str(e)}")
        return False

def create_test_audio_file(filename="test_audio.wav"):
    """创建测试音频文件（模拟）"""
    try:
        # 创建一个简单的音频文件模拟
        test_audio_path = os.path.join("./temp", filename)
        os.makedirs("./temp", exist_ok=True)
        
        # 写入一些模拟的音频数据（实际上是文本文件）
        with open(test_audio_path, 'w', encoding='utf-8') as f:
            f.write("这是一个模拟的音频文件，用于测试语音转文本功能。")
        
        return test_audio_path
    except Exception as e:
        print(f"❌ 创建测试音频文件失败: {str(e)}")
        return None

def test_speech_to_text():
    """测试语音转文本接口"""
    print("\n🎯 测试语音转文本功能...")
    
    # 测试用例
    test_cases = [
        {
            "name": "中文语音测试",
            "filename": "chinese_test.wav",
            "language": "zh-CN"
        },
        {
            "name": "英文语音测试", 
            "filename": "english_test.wav",
            "language": "en-US"
        },
        {
            "name": "默认语言测试",
            "filename": "default_test.wav",
            "language": None  # 使用默认语言
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {test_case['name']}")
        
        try:
            # 创建测试音频文件
            audio_path = create_test_audio_file(test_case['filename'])
            if not audio_path:
                print("   ❌ 无法创建测试音频文件")
                continue
            
            # 准备请求数据
            files = {
                'audio': open(audio_path, 'rb')
            }
            
            data = {}
            if test_case['language']:
                data['language'] = test_case['language']
            
            print(f"   语言设置: {test_case.get('language', '默认(zh-CN)')}")
            
            # 发送请求
            response = requests.post(
                f"{API_BASE_URL}/speech-to-text",
                files=files,
                data=data
            )
            
            # 关闭文件
            files['audio'].close()
            
            # 清理测试文件
            try:
                os.remove(audio_path)
            except:
                pass
            
            if response.status_code == 200:
                result_data = response.json()
                
                if result_data.get('success'):
                    speech_data = result_data.get('data', {})
                    
                    print(f"   ✅ 转换成功")
                    print(f"   📝 转换文本: {speech_data.get('text', '')}")
                    print(f"   📊 置信度: {speech_data.get('confidence', 0):.2%}")
                    print(f"   🌐 语言: {speech_data.get('language', 'unknown')}")
                    print(f"   🤖 服务: {speech_data.get('service', 'unknown')}")
                    print(f"   ⏱️ 时长: {speech_data.get('duration', 0):.2f}秒")
                    
                    # 检查优先级策略
                    service = speech_data.get('service', '')
                    if 'OpenAI' in service:
                        print("   🎯 使用第三方API (最高准确率)")
                        priority_level = "第三方API"
                    elif 'iFlytek' in service:
                        print("   🏢 使用科大讯飞API (高准确率)")
                        priority_level = "第三方API"
                    elif 'Local' in service:
                        print("   🏠 使用本地模型 (中等准确率)")
                        priority_level = "本地模型"
                    elif 'Simulation' in service:
                        print("   🎭 使用模拟模式 (保底方案)")
                        priority_level = "模拟模式"
                    else:
                        print("   ❓ 未知服务类型")
                        priority_level = "未知"
                    
                    results.append({
                        'test_case': test_case['name'],
                        'text': speech_data.get('text', ''),
                        'confidence': speech_data.get('confidence', 0),
                        'language': speech_data.get('language', ''),
                        'service': speech_data.get('service', ''),
                        'priority_level': priority_level,
                        'success': True
                    })
                else:
                    print(f"   ❌ 转换失败: {result_data.get('message', '未知错误')}")
                    results.append({
                        'test_case': test_case['name'],
                        'error': result_data.get('message', '未知错误'),
                        'success': False
                    })
            else:
                print(f"   ❌ 请求失败: HTTP {response.status_code}")
                results.append({
                    'test_case': test_case['name'],
                    'error': f"HTTP {response.status_code}",
                    'success': False
                })
                
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            results.append({
                'test_case': test_case['name'],
                'error': str(e),
                'success': False
            })
    
    return results

def analyze_speech_results(results):
    """分析语音转文本测试结果"""
    print("\n📊 语音转文本测试结果分析")
    print("=" * 50)
    
    successful_tests = [r for r in results if r.get('success')]
    failed_tests = [r for r in results if not r.get('success')]
    
    print(f"✅ 成功测试: {len(successful_tests)}/{len(results)}")
    print(f"❌ 失败测试: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        print("\n🎯 优先级策略分析:")
        
        # 统计使用的服务类型
        service_usage = {}
        confidence_sum = 0
        
        for result in successful_tests:
            priority_level = result.get('priority_level', '未知')
            confidence = result.get('confidence', 0)
            
            service_usage[priority_level] = service_usage.get(priority_level, 0) + 1
            confidence_sum += confidence
        
        print("\n📈 服务使用统计:")
        for service, count in service_usage.items():
            percentage = (count / len(successful_tests)) * 100
            print(f"   {service}: {count}次 ({percentage:.1f}%)")
        
        # 平均置信度
        avg_confidence = confidence_sum / len(successful_tests)
        print(f"\n📊 平均置信度: {avg_confidence:.2%}")
        
        # 检查优先级策略
        if service_usage.get("第三方API", 0) > 0:
            print("\n✅ 准确率优先策略生效:")
            print("   - 系统优先使用第三方API获得最高准确率")
            print("   - 语音转文本功能正常工作")
        else:
            print("\n⚠️ 准确率优先策略未完全生效:")
            print("   - 可能缺少API密钥配置")
            print("   - 系统使用降级方案")
    
    if failed_tests:
        print(f"\n❌ 失败测试详情:")
        for result in failed_tests:
            print(f"   {result['test_case']}: {result.get('error', '未知错误')}")

def test_health_check():
    """测试健康检查"""
    print("🔍 测试系统健康状态...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 系统健康检查通过")
            return True
        else:
            print(f"❌ 系统健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 系统健康检查异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 PGG系统语音转文本功能测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {API_BASE_URL}")
    
    # 1. 健康检查
    if not test_health_check():
        print("\n❌ 系统不可用，测试终止")
        return
    
    # 2. 语音服务状态检查
    if not test_speech_service_status():
        print("\n❌ 语音服务不可用，测试终止")
        return
    
    # 3. 语音转文本功能测试
    results = test_speech_to_text()
    
    # 4. 分析结果
    analyze_speech_results(results)
    
    # 5. 清理临时文件
    try:
        import shutil
        if os.path.exists("./temp"):
            shutil.rmtree("./temp")
    except:
        pass
    
    # 6. 总结
    print("\n🎉 语音转文本功能测试完成！")
    print("📋 功能特点:")
    print("   - 优先级策略: OpenAI API > 科大讯飞API > 本地模型 > 模拟模式")
    print("   - 支持多种语言: 中文、英文、日文、韩文")
    print("   - 支持多种格式: WAV、MP3、FLAC、M4A等")
    print("   - 智能降级: 确保服务可用性")
    
    print("\n💡 使用建议:")
    print("   - 配置OpenAI API密钥以获得最佳效果")
    print("   - 配置科大讯飞API密钥作为备选方案")
    print("   - 音频文件大小限制25MB")
    print("   - 支持实时语音转文本和批量处理")

if __name__ == "__main__":
    main() 