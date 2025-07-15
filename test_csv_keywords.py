# -*- coding: utf-8 -*-
"""
PGG系统 - CSV关键词功能测试
测试CSV系统中的关键词分析、导出和配置功能
"""

import requests
import json
from datetime import datetime

# 测试服务器地址
BASE_URL = "http://localhost:5000"

def print_separator(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def test_keywords_config():
    """测试关键词配置获取"""
    print_separator("测试关键词配置获取")
    
    try:
        response = requests.get(f"{BASE_URL}/csv/keywords/config")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 关键词配置获取成功")
            print(f"📊 总关键词数: {data['data']['total_keywords']}")
            print(f"🎯 关键词阈值: {data['data']['keyword_threshold']}")
            print(f"👴 最小年龄: {data['data']['min_age']}")
            print(f"📝 分类数量: {len(data['data']['categories'])}")
            
            # 显示部分关键词
            for category, keywords in data['data']['categories'].items():
                print(f"   {category}: {keywords[:5]}...")
                
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_keywords_analyze():
    """测试关键词分析"""
    print_separator("测试关键词分析")
    
    # 测试数据
    test_data = [
        {
            "text": "今天孙子来看我了，很开心，一起吃饭聊天",
            "user_id": "user_001",
            "primary_emotion": "happy"
        },
        {
            "text": "最近血压有点高，需要按时吃药，去医院复查",
            "user_id": "user_002", 
            "primary_emotion": "worry"
        },
        {
            "text": "一个人在家很孤独，想念老朋友，怀念过去的日子",
            "user_id": "user_003",
            "primary_emotion": "sad"
        },
        {
            "text": "昨天去参加广场舞，遇到了老同事，聊得很开心",
            "user_id": "user_004",
            "primary_emotion": "happy"
        },
        {
            "text": "儿子女儿都在外地工作，很少回家，放心不下",
            "user_id": "user_005",
            "primary_emotion": "worry"
        }
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/csv/keywords/analyze", json={
            "data": test_data,
            "format": "general"
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 关键词分析成功")
            
            # 基本统计
            keyword_analysis = data['data']['keyword_analysis']
            print(f"📊 总关键词数: {keyword_analysis['total_keywords']}")
            print(f"🎯 匹配记录数: {keyword_analysis['matched_records']}")
            print(f"📝 未匹配记录数: {keyword_analysis['unmatched_records']}")
            print(f"📈 平均关键词密度: {keyword_analysis['average_keywords_per_record']:.2f}")
            
            # 最常见关键词
            print("\n🔝 最常见关键词:")
            for keyword, count in list(keyword_analysis['most_common_keywords'].items())[:10]:
                print(f"   - {keyword}: {count}次")
            
            # 老人特定洞察
            elderly_insights = data['data']['elderly_specific_insights']
            print("\n🏥 健康关键词:")
            for keyword, count in elderly_insights['health_keywords'].items():
                print(f"   - {keyword}: {count}次")
                
            print("\n👨‍👩‍👧‍👦 家庭关键词:")
            for keyword, count in elderly_insights['family_keywords'].items():
                print(f"   - {keyword}: {count}次")
                
            print("\n😔 孤独关键词:")
            for keyword, count in elderly_insights['loneliness_keywords'].items():
                print(f"   - {keyword}: {count}次")
                
            print("\n🤝 社交关键词:")
            for keyword, count in elderly_insights['social_keywords'].items():
                print(f"   - {keyword}: {count}次")
                
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_keywords_export():
    """测试关键词导出"""
    print_separator("测试关键词导出")
    
    # 测试数据
    test_data = [
        {
            "text": "今天孙子来看我了，很开心",
            "user_id": "user_001",
            "primary_emotion": "happy"
        },
        {
            "text": "血压有点高，需要按时吃药",
            "user_id": "user_002",
            "primary_emotion": "worry"
        },
        {
            "text": "一个人在家很孤独，想念老朋友",
            "user_id": "user_003",
            "primary_emotion": "sad"
        }
    ]
    
    filename = f"keywords_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        response = requests.post(f"{BASE_URL}/csv/keywords/export", json={
            "data": test_data,
            "format": "general",
            "filename": filename
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 关键词导出成功")
            print(f"📁 文件名: {data['data']['filename']}")
            print(f"📊 处理记录数: {data['data']['processed_records']}")
            print(f"🔑 发现关键词数: {data['data']['keywords_found']}")
            print(f"🔗 下载链接: {data['data']['download_url']}")
            
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_keywords_comprehensive():
    """综合测试关键词功能"""
    print_separator("综合测试关键词功能")
    
    # 模拟老人数据
    elderly_data = [
        {
            "text": "孙子今天来看我了，给我带了保健品，陪我聊天很开心",
            "user_id": "elderly_001",
            "primary_emotion": "happy",
            "age": 75,
            "gender": "女"
        },
        {
            "text": "昨天去医院复查，血压还是有点高，医生说要按时吃降压药",
            "user_id": "elderly_002", 
            "primary_emotion": "worry",
            "age": 68,
            "gender": "男"
        },
        {
            "text": "儿子女儿都在外地工作，很少回家，我一个人独居感觉很孤独",
            "user_id": "elderly_003",
            "primary_emotion": "sad",
            "age": 72,
            "gender": "女"
        },
        {
            "text": "今天去参加广场舞，遇到了老同事，大家一起聊天很热闹",
            "user_id": "elderly_004",
            "primary_emotion": "happy",
            "age": 69,
            "gender": "女"
        },
        {
            "text": "最近记忆力不太好，老是忘事，担心是老年痴呆的征象",
            "user_id": "elderly_005",
            "primary_emotion": "worry",
            "age": 74,
            "gender": "男"
        }
    ]
    
    try:
        # 1. 分析关键词
        print("🔍 正在分析关键词...")
        response = requests.post(f"{BASE_URL}/csv/keywords/analyze", json={
            "data": elderly_data,
            "format": "elderly_data"
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 关键词分析完成")
            
            # 显示分析结果
            keyword_analysis = data['data']['keyword_analysis']
            print(f"📊 匹配记录: {keyword_analysis['matched_records']}/{len(elderly_data)}")
            print(f"📈 关键词密度: {keyword_analysis['average_keywords_per_record']:.2f}")
            
            # 显示按类别分组的关键词
            elderly_insights = data['data']['elderly_specific_insights']
            categories = [
                ('健康关键词', elderly_insights['health_keywords']),
                ('家庭关键词', elderly_insights['family_keywords']),
                ('孤独关键词', elderly_insights['loneliness_keywords']),
                ('社交关键词', elderly_insights['social_keywords'])
            ]
            
            for category_name, keywords in categories:
                if keywords:
                    print(f"\n{category_name}:")
                    for keyword, count in keywords.items():
                        print(f"   - {keyword}: {count}次")
            
            # 2. 导出关键词分析结果
            print("\n📤 正在导出关键词分析结果...")
            filename = f"elderly_keywords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            export_response = requests.post(f"{BASE_URL}/csv/keywords/export", json={
                "data": elderly_data,
                "format": "elderly_data",
                "filename": filename
            })
            
            if export_response.status_code == 200:
                export_data = export_response.json()
                print("✅ 关键词导出成功")
                print(f"📁 文件: {export_data['data']['filename']}")
                print(f"🔗 下载: {export_data['data']['download_url']}")
            else:
                print(f"❌ 导出失败: {export_response.status_code}")
                
        else:
            print(f"❌ 分析失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def main():
    """主函数"""
    print("🎉 PGG系统 - CSV关键词功能测试")
    print("=" * 60)
    
    # 执行所有测试
    test_keywords_config()
    test_keywords_analyze()
    test_keywords_export()
    test_keywords_comprehensive()
    
    print("\n" + "="*60)
    print("✅ 所有测试已完成！")
    print("="*60)

if __name__ == "__main__":
    main() 