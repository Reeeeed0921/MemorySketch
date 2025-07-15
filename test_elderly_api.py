#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 老人数据API测试
测试老人数据管理相关的API接口
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://127.0.0.1:5000"

def print_separator(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_elderly_keywords_api():
    """测试老人关键词配置API"""
    print_separator("老人关键词配置API测试")
    
    try:
        response = requests.get(f"{BASE_URL}/elderly/keywords")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 老人关键词配置获取成功")
            print(f"📊 关键词总数: {data['data']['keyword_count']}")
            print(f"🎯 最小年龄: {data['data']['min_age']}")
            print(f"🔢 关键词阈值: {data['data']['keyword_threshold']}")
            print(f"💾 存储类型: {data['data']['storage_type']}")
            print(f"📝 部分关键词: {data['data']['keywords'][:10]}...")
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_elderly_detection_api():
    """测试老人群体检测API"""
    print_separator("老人群体检测API测试")
    
    test_cases = [
        {
            "text": "今天孙子来看我了，真的很开心",
            "user_context": {"age": 70, "gender": "女", "age_group": "senior"},
            "description": "年龄+关键词双重匹配"
        },
        {
            "text": "昨天去广场舞，遇到了老朋友",
            "user_context": {"age": 45, "gender": "女"},
            "description": "仅关键词匹配"
        },
        {
            "text": "今天天气很好，心情也不错",
            "user_context": {"age": 30, "gender": "男"},
            "description": "无匹配条件"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {test_case['description']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/elderly/test",
                json={
                    "text": test_case["text"],
                    "user_context": test_case["user_context"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data['data']['detection_result']
                config = data['data']['configuration']
                
                print(f"✅ 检测成功:")
                print(f"   - 文本: {test_case['text']}")
                print(f"   - 是否为老人群体: {result['is_elderly']}")
                print(f"   - 匹配关键词: {result['matched_keywords']}")
                print(f"   - 关键词数量: {result['keyword_count']}")
                print(f"   - 年龄判断: {result['age_based']}")
                print(f"   - 关键词判断: {result['keyword_based']}")
                
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到服务器")
            break
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")

def test_elderly_emotions_api():
    """测试老人情感数据查询API"""
    print_separator("老人情感数据查询API测试")
    
    try:
        # 查询所有老人情感数据
        print("📋 查询所有老人情感数据...")
        response = requests.get(f"{BASE_URL}/elderly/emotions")
        
        if response.status_code == 200:
            data = response.json()
            result = data['data']
            
            print(f"✅ 查询成功:")
            print(f"   - 总记录数: {result['total']}")
            print(f"   - 当前页: {result['page']}")
            print(f"   - 每页数量: {result['per_page']}")
            print(f"   - 总页数: {result['pages']}")
            print(f"   - 当前页记录数: {len(result['emotions'])}")
            
            if result['emotions']:
                emotion = result['emotions'][0]
                print(f"\n📝 示例记录:")
                print(f"   - ID: {emotion['id']}")
                print(f"   - 用户ID: {emotion['user_id']}")
                print(f"   - 主要情感: {emotion['primary_emotion']}")
                print(f"   - 置信度: {emotion['confidence']}")
                print(f"   - 年龄: {emotion['age']}")
                print(f"   - 关键词: {emotion['keywords_matched']}")
            
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
        
        # 按情感过滤查询
        print("\n😊 按情感过滤查询...")
        response = requests.get(f"{BASE_URL}/elderly/emotions?emotion_filter=happy")
        
        if response.status_code == 200:
            data = response.json()
            result = data['data']
            print(f"✅ 开心情感记录: {result['total']} 条")
        else:
            print(f"❌ 情感过滤查询失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_elderly_statistics_api():
    """测试老人情感统计API"""
    print_separator("老人情感统计API测试")
    
    try:
        response = requests.get(f"{BASE_URL}/elderly/statistics")
        
        if response.status_code == 200:
            data = response.json()
            stats = data['data']
            
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
            
            print(f"\n🔤 关键词频率 (前5):")
            sorted_keywords = sorted(stats['keyword_frequency'].items(), key=lambda x: x[1], reverse=True)
            for keyword, count in sorted_keywords[:5]:
                print(f"   - {keyword}: {count} 次")
            
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_elderly_export_api():
    """测试老人数据导出API"""
    print_separator("老人数据导出API测试")
    
    try:
        response = requests.post(
            f"{BASE_URL}/elderly/export",
            json={
                "format": "csv",
                "user_id": None  # 导出所有用户数据
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data['data']
            
            print(f"✅ 数据导出成功:")
            print(f"   - 导出路径: {result['export_path']}")
            print(f"   - 导出格式: {result['format']}")
            print(f"   - 用户ID: {result['user_id'] or '全部用户'}")
            
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def main():
    """主函数"""
    print("🚀 PGG老人数据API测试开始")
    print("📝 请确保服务器正在运行 (python app.py)")
    
    # 等待用户确认
    input("\n按回车键开始测试...")
    
    try:
        # 测试各个API接口
        test_elderly_keywords_api()
        test_elderly_detection_api()
        test_elderly_emotions_api()
        test_elderly_statistics_api()
        test_elderly_export_api()
        
        print_separator("测试完成")
        print("✅ 所有API测试完成！")
        print("📊 建议：可以通过浏览器访问 http://127.0.0.1:5000 查看完整的系统界面")
        
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main() 