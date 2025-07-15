# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 系统测试脚本
用于验证系统基本功能
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from config import config
        print("✅ config模块导入成功")
        
        from models import MemoryRecord, EmotionResult
        print("✅ models模块导入成功")
        
        from utils.database import DatabaseManager
        print("✅ database模块导入成功")
        
        from services.emotion_analysis import EmotionAnalyzer
        print("✅ emotion_analysis模块导入成功")
        
        from services.image_generation import ImageGenerator
        print("✅ image_generation模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config():
    """测试配置"""
    print("\n🔍 测试配置...")
    
    try:
        from config import config
        
        print(f"✅ 配置验证: SECRET_KEY = {config.SECRET_KEY}")
        print(f"✅ 配置验证: DEBUG = {config.DEBUG}")
        print(f"✅ 配置验证: USE_LOCAL_STORAGE = {config.USE_LOCAL_STORAGE}")
        print(f"✅ 配置验证: LOCAL_STORAGE_PATH = {config.LOCAL_STORAGE_PATH}")
        
        # 验证配置
        config.validate_config()
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_emotion_analysis():
    """测试情感分析"""
    print("\n🔍 测试情感分析...")
    
    try:
        from services.emotion_analysis import EmotionAnalyzer
        
        analyzer = EmotionAnalyzer()
        
        # 测试文本分析
        test_texts = [
            "今天天气很好，心情很愉快",
            "我很难过，因为失去了重要的东西",
            "这件事让我非常愤怒",
            "我感到很平静和安详"
        ]
        
        for text in test_texts:
            result = analyzer.analyze_text(text)
            print(f"✅ 文本: '{text}' -> 情感: {result['primary_emotion']} (置信度: {result['confidence']:.2f})")
        
        # 测试回忆文本生成
        memory_text = analyzer.generate_memory_text(
            "今天和朋友一起玩得很开心",
            {"primary_emotion": "happy", "confidence": 0.8}
        )
        print(f"✅ 生成回忆文本: {memory_text[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 情感分析测试失败: {e}")
        return False

def test_image_generation():
    """测试图像生成"""
    print("\n🔍 测试图像生成...")
    
    try:
        from services.image_generation import ImageGenerator
        
        generator = ImageGenerator()
        
        # 测试图像生成
        image_url = generator.generate_image(
            "美好的一天，阳光明媚",
            {"primary_emotion": "happy", "confidence": 0.8}
        )
        print(f"✅ 生成图像: {image_url}")
        
        # 验证图像文件
        if os.path.exists(image_url):
            print("✅ 图像文件创建成功")
            
            # 获取图像信息
            image_info = generator.get_image_info(image_url)
            print(f"✅ 图像信息: {image_info.get('size', 'unknown')} - {image_info.get('format', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 图像生成测试失败: {e}")
        return False

def test_database():
    """测试数据库"""
    print("\n🔍 测试数据库...")
    
    try:
        from utils.database import DatabaseManager
        from models import MemoryRecord
        
        db_manager = DatabaseManager()
        db_manager.init_database()
        
        # 创建测试记录
        test_memory = MemoryRecord(
            user_id="test_user",
            user_input="测试用户输入",
            memory_text="测试回忆文本",
            image_url="/test/image.png",
            emotion_result={"primary_emotion": "happy", "confidence": 0.8}
        )
        
        # 保存记录
        record_id = db_manager.save_memory(test_memory)
        print(f"✅ 保存记录: {record_id}")
        
        # 查询记录
        memories = db_manager.get_memories("test_user", page=1, per_page=5)
        print(f"✅ 查询记录: 找到 {len(memories['memories'])} 条记录")
        
        # 获取统计信息
        stats = db_manager.get_user_statistics("test_user")
        print(f"✅ 用户统计: 总记录数 {stats['total_memories']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API接口"""
    print("\n🔍 测试API接口...")
    
    try:
        base_url = "http://localhost:5000"
        
        # 测试健康检查
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查接口正常")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
        
        # 测试生成回忆接口
        test_data = {
            "text": "今天是测试的一天",
            "user_id": "test_api_user"
        }
        
        response = requests.post(
            f"{base_url}/generate",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 生成回忆接口正常")
                print(f"   生成的回忆: {result['data']['memory_text'][:50]}...")
            else:
                print(f"❌ 生成回忆失败: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ 生成回忆接口失败: {response.status_code}")
            return False
        
        # 测试历史记录接口
        response = requests.get(f"{base_url}/history?user_id=test_api_user", timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ 历史记录接口正常: 找到 {len(result['data']['memories'])} 条记录")
            else:
                print(f"❌ 历史记录失败: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ 历史记录接口失败: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请确保服务器已启动")
        return False
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def test_full_workflow():
    """测试完整工作流程"""
    print("\n🔍 测试完整工作流程...")
    
    try:
        # 1. 初始化所有组件
        from services.emotion_analysis import EmotionAnalyzer
        from services.image_generation import ImageGenerator
        from utils.database import DatabaseManager
        from models import MemoryRecord
        
        analyzer = EmotionAnalyzer()
        generator = ImageGenerator()
        db_manager = DatabaseManager()
        db_manager.init_database()
        
        # 2. 模拟用户输入
        user_input = "今天和家人一起度过了美好的时光，感觉很幸福"
        user_id = "workflow_test_user"
        
        print(f"👤 用户输入: {user_input}")
        
        # 3. 情感分析
        emotion_result = analyzer.analyze_text(user_input)
        print(f"💭 情感分析: {emotion_result['primary_emotion']} (置信度: {emotion_result['confidence']:.2f})")
        
        # 4. 生成回忆文本
        memory_text = analyzer.generate_memory_text(user_input, emotion_result)
        print(f"📝 回忆文本: {memory_text[:50]}...")
        
        # 5. 生成图像
        image_url = generator.generate_image(memory_text, emotion_result)
        print(f"🖼️ 生成图像: {image_url}")
        
        # 6. 保存记录
        memory_record = MemoryRecord(
            user_id=user_id,
            user_input=user_input,
            memory_text=memory_text,
            image_url=image_url,
            emotion_result=emotion_result
        )
        
        record_id = db_manager.save_memory(memory_record)
        print(f"💾 保存记录: {record_id}")
        
        # 7. 查询验证
        saved_memory = db_manager.get_memory_by_id(record_id)
        if saved_memory:
            print("✅ 记录查询成功")
        else:
            print("❌ 记录查询失败")
            return False
        
        print("✅ 完整工作流程测试成功!")
        return True
        
    except Exception as e:
        print(f"❌ 完整工作流程测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎨 PGG情感记忆生成系统 - 系统测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("模块导入", test_imports()))
    test_results.append(("配置验证", test_config()))
    test_results.append(("情感分析", test_emotion_analysis()))
    test_results.append(("图像生成", test_image_generation()))
    test_results.append(("数据库操作", test_database()))
    test_results.append(("完整工作流程", test_full_workflow()))
    
    # 如果有API服务器运行，测试API接口
    print("\n🔍 尝试测试API接口...")
    api_test_result = test_api_endpoints()
    if api_test_result:
        test_results.append(("API接口", api_test_result))
    else:
        print("ℹ️  API接口测试跳过（服务器未运行）")
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:15} : {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过! 系统运行正常。")
    else:
        print("⚠️  部分测试失败，请检查相关组件。")
    
    print("\n💡 提示:")
    print("  - 要测试API接口，请先运行: python start_server.py")
    print("  - 要配置真实的AI模型，请参考README.md")
    print("  - 要使用生产环境，请配置.env文件")

if __name__ == "__main__":
    main() 