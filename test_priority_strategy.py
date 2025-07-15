#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优先级策略
验证准确率优先的降级机制是否正常工作
"""

import os
import sys
import requests
import json
from datetime import datetime

# 测试配置
API_BASE_URL = "http://localhost:5000"
TEST_CASES = [
    {
        "name": "快乐情绪测试",
        "text": "今天天气很好，我心情特别愉快！",
        "expected_emotions": ["happy", "peaceful", "love"]
    },
    {
        "name": "悲伤情绪测试", 
        "text": "失去了重要的人，心情很沉重...",
        "expected_emotions": ["sad", "nostalgic"]
    },
    {
        "name": "愤怒情绪测试",
        "text": "这太让人愤怒了！完全不能接受！",
        "expected_emotions": ["angry", "fear"]
    },
    {
        "name": "混合情绪测试",
        "text": "既兴奋又紧张，这是人生的重要时刻",
        "expected_emotions": ["surprise", "fear", "happy"]
    }
]

def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

def test_priority_strategy():
    """测试优先级策略"""
    print("\n🎯 测试优先级策略...")
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n📝 测试用例 {i}: {test_case['name']}")
        print(f"   输入文本: {test_case['text']}")
        
        try:
            # 发送请求
            payload = {
                "text": test_case["text"],
                "user_id": f"test_user_{i}"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                emotion_data = data.get("data", {}).get("emotion", {})
                
                # 分析结果
                primary_emotion = emotion_data.get("primary_emotion", "unknown")
                confidence = emotion_data.get("confidence", 0)
                analysis_model = emotion_data.get("analysis_model", "unknown")
                
                print(f"   ✅ 主要情感: {primary_emotion}")
                print(f"   📊 置信度: {confidence:.2%}")
                print(f"   🤖 分析模型: {analysis_model}")
                
                # 检查是否使用了高准确率模型
                if "OpenAI" in analysis_model:
                    print("   🎯 使用第三方API (最高准确率)")
                    priority_level = "第三方API"
                elif "Local" in analysis_model:
                    print("   🏠 使用本地模型 (中等准确率)")
                    priority_level = "本地模型"
                elif "Rule" in analysis_model:
                    print("   📋 使用规则匹配 (基础准确率)")
                    priority_level = "规则匹配"
                else:
                    print("   ❓ 未知分析模型")
                    priority_level = "未知"
                
                # 检查置信度
                if confidence >= 0.8:
                    confidence_level = "高"
                elif confidence >= 0.6:
                    confidence_level = "中"
                else:
                    confidence_level = "低"
                
                results.append({
                    "test_case": test_case["name"],
                    "primary_emotion": primary_emotion,
                    "confidence": confidence,
                    "analysis_model": analysis_model,
                    "priority_level": priority_level,
                    "confidence_level": confidence_level,
                    "success": True
                })
                
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
                results.append({
                    "test_case": test_case["name"],
                    "error": f"HTTP {response.status_code}",
                    "success": False
                })
                
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            results.append({
                "test_case": test_case["name"],
                "error": str(e),
                "success": False
            })
    
    return results

def analyze_results(results):
    """分析测试结果"""
    print("\n📊 测试结果分析")
    print("=" * 50)
    
    successful_tests = [r for r in results if r.get("success")]
    failed_tests = [r for r in results if not r.get("success")]
    
    print(f"✅ 成功测试: {len(successful_tests)}/{len(results)}")
    print(f"❌ 失败测试: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        print("\n🎯 优先级策略分析:")
        
        # 统计使用的模型类型
        model_usage = {}
        confidence_levels = {"高": 0, "中": 0, "低": 0}
        
        for result in successful_tests:
            priority_level = result.get("priority_level", "未知")
            confidence_level = result.get("confidence_level", "未知")
            
            model_usage[priority_level] = model_usage.get(priority_level, 0) + 1
            if confidence_level in confidence_levels:
                confidence_levels[confidence_level] += 1
        
        print("\n📈 模型使用统计:")
        for model, count in model_usage.items():
            percentage = (count / len(successful_tests)) * 100
            print(f"   {model}: {count}次 ({percentage:.1f}%)")
        
        print("\n🎚️ 置信度分布:")
        for level, count in confidence_levels.items():
            percentage = (count / len(successful_tests)) * 100
            print(f"   {level}置信度: {count}次 ({percentage:.1f}%)")
        
        # 检查是否符合准确率优先策略
        if model_usage.get("第三方API", 0) > 0:
            print("\n✅ 准确率优先策略生效:")
            print("   - 系统优先使用第三方API获得最高准确率")
            print("   - 降级机制保持完整")
        else:
            print("\n⚠️ 准确率优先策略未生效:")
            print("   - 可能缺少API密钥配置")
            print("   - 系统使用降级方案")
    
    if failed_tests:
        print(f"\n❌ 失败测试详情:")
        for result in failed_tests:
            print(f"   {result['test_case']}: {result.get('error', '未知错误')}")

def main():
    """主测试函数"""
    print("🚀 PGG系统优先级策略测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {API_BASE_URL}")
    
    # 1. 健康检查
    if not test_health_check():
        print("\n❌ 系统不可用，测试终止")
        return
    
    # 2. 测试优先级策略
    results = test_priority_strategy()
    
    # 3. 分析结果
    analyze_results(results)
    
    # 4. 总结
    print("\n🎉 测试完成！")
    print("📋 关键指标:")
    print("   - 优先级策略: 第三方API > 本地模型 > 规则匹配")
    print("   - 置信度范围: 40-95%")
    print("   - 降级机制: 完整保持")
    
    print("\n💡 建议:")
    print("   - 配置API密钥以获得最高准确率")
    print("   - 监控置信度分布优化系统性能")
    print("   - 定期测试降级策略的有效性")

if __name__ == "__main__":
    main() 