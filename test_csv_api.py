# -*- coding: utf-8 -*-
"""
PGG系统CSV接口测试工具
快速测试CSV文档处理功能
"""

import os
import json
import requests
import time
from datetime import datetime

# 服务器配置
BASE_URL = "http://localhost:5000"
TEST_DATA_DIR = "./test_data"

def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)

def create_test_data():
    """创建测试数据"""
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # 创建测试数据
    test_data = [
        {
            "id": "memory_001",
            "user_id": "user_123",
            "user_input": "今天天气很好",
            "memory_text": "今天天气很好，让我想起了春天的阳光",
            "image_url": "https://example.com/image1.jpg",
            "primary_emotion": "happy",
            "confidence": 0.85,
            "emotion_scores": {"happy": 0.85, "neutral": 0.15},
            "created_at": "2024-01-01T12:00:00"
        },
        {
            "id": "memory_002", 
            "user_id": "user_456",
            "user_input": "昨天下雨了",
            "memory_text": "昨天下雨了，让我感到有些忧郁",
            "image_url": "https://example.com/image2.jpg",
            "primary_emotion": "sad",
            "confidence": 0.78,
            "emotion_scores": {"sad": 0.78, "neutral": 0.22},
            "created_at": "2024-01-02T14:30:00"
        },
        {
            "id": "memory_003",
            "user_id": "user_789",
            "user_input": "看到了美丽的彩虹",
            "memory_text": "看到了美丽的彩虹，心情非常愉快",
            "image_url": "https://example.com/image3.jpg",
            "primary_emotion": "joy",
            "confidence": 0.92,
            "emotion_scores": {"joy": 0.92, "surprise": 0.08},
            "created_at": "2024-01-03T16:45:00"
        }
    ]
    
    return test_data

def test_csv_export():
    """测试CSV导出功能"""
    print_separator("CSV导出功能测试")
    
    try:
        test_data = create_test_data()
        
        # 测试数据导出
        export_payload = {
            "data": test_data,
            "type": "memories",
            "filename": "test_export.csv",
            "options": {
                "include_headers": True,
                "encoding": "utf-8",
                "delimiter": ",",
                "custom_fields": ["id", "user_id", "user_input", "primary_emotion", "confidence"]
            }
        }
        
        response = requests.post(f"{BASE_URL}/csv/export", json=export_payload)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ CSV导出成功:")
                print(f"   - 文件名: {result['data']['filename']}")
                print(f"   - 记录数: {result['data']['record_count']}")
                print(f"   - 文件大小: {result['data']['file_size']} bytes")
                print(f"   - 字段数: {len(result['data']['fields'])}")
                return result['data']['filename']
            else:
                print(f"❌ CSV导出失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    return None

def test_csv_template():
    """测试CSV模板创建"""
    print_separator("CSV模板创建测试")
    
    try:
        # 测试不同类型的模板
        template_types = ["memories", "emotions", "elderly_data", "sensor_data"]
        
        for template_type in template_types:
            template_payload = {
                "type": template_type,
                "include_examples": True
            }
            
            response = requests.post(f"{BASE_URL}/csv/template", json=template_payload)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"✅ {template_type} 模板创建成功:")
                    print(f"   - 文件名: {result['data']['filename']}")
                    print(f"   - 字段数: {result['data']['field_count']}")
                    print(f"   - 示例数: {result['data']['example_count']}")
                else:
                    print(f"❌ {template_type} 模板创建失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_csv_formats():
    """测试获取支持的CSV格式"""
    print_separator("CSV格式查询测试")
    
    try:
        response = requests.get(f"{BASE_URL}/csv/formats")
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 支持的CSV格式:")
                formats = result['data']['supported_formats']
                for fmt in formats:
                    print(f"   - {fmt}")
                
                print(f"\n✅ 格式详情示例 (memories):")
                memories_format = result['data']['format_details']['memories']
                print(f"   - 字段数: {len(memories_format['fields'])}")
                print(f"   - 必填字段: {memories_format['required']}")
                print(f"   - 特殊类型: {list(memories_format['types'].keys())}")
            else:
                print(f"❌ 获取格式失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ API请求失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_csv_import():
    """测试CSV导入功能"""
    print_separator("CSV导入功能测试")
    
    try:
        # 首先创建一个测试文件
        test_csv_content = """id,user_id,user_input,primary_emotion,confidence
memory_001,user_123,今天天气很好,happy,0.85
memory_002,user_456,昨天下雨了,sad,0.78
memory_003,user_789,看到了美丽的彩虹,joy,0.92"""
        
        test_file_path = os.path.join(TEST_DATA_DIR, "test_import.csv")
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_csv_content)
        
        # 测试导入
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'type': 'memories',
                'encoding': 'utf-8',
                'delimiter': ',',
                'skip_header': 'true',
                'validate_data': 'true'
            }
            
            response = requests.post(f"{BASE_URL}/csv/import", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print("✅ CSV导入成功:")
                    print(f"   - 总行数: {result['data']['total_rows']}")
                    print(f"   - 成功导入: {result['data']['success_count']}")
                    print(f"   - 失败数量: {result['data']['error_count']}")
                    print(f"   - 文件大小: {result['data']['file_size']} bytes")
                    
                    if result['data']['data']:
                        print(f"   - 导入的数据样本:")
                        for i, record in enumerate(result['data']['data'][:2]):
                            print(f"     {i+1}. {record['id']}: {record['user_input']} ({record['primary_emotion']})")
                else:
                    print(f"❌ CSV导入失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_csv_analyze():
    """测试CSV文件分析功能"""
    print_separator("CSV文件分析测试")
    
    try:
        # 创建测试文件
        test_csv_content = """id,user_id,user_input,primary_emotion,confidence,age,gender
memory_001,user_123,今天天气很好,happy,0.85,25,男
memory_002,user_456,昨天下雨了,sad,0.78,30,女
memory_003,user_789,看到了美丽的彩虹,joy,0.92,35,男
memory_004,user_101,感觉很累,tired,0.70,28,女"""
        
        test_file_path = os.path.join(TEST_DATA_DIR, "test_analyze.csv")
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_csv_content)
        
        # 分析文件
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'encoding': 'utf-8',
                'delimiter': ',',
                'sample_size': '10'
            }
            
            response = requests.post(f"{BASE_URL}/csv/analyze", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print("✅ CSV文件分析成功:")
                    data = result['data']
                    print(f"   - 总行数: {data['total_rows']}")
                    print(f"   - 字段数: {data['field_count']}")
                    print(f"   - 文件大小: {data['file_size']} bytes")
                    print(f"   - 字段列表: {', '.join(data['headers'])}")
                    
                    print(f"\n   - 字段类型分析:")
                    for field, analysis in data['field_analysis'].items():
                        print(f"     {field}: {analysis['type']} (空值: {analysis['null_count']})")
                        
                    print(f"\n   - 数据样本:")
                    for i, sample in enumerate(data['sample_data'][:2]):
                        print(f"     {i+1}. {sample}")
                else:
                    print(f"❌ CSV文件分析失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_csv_validate():
    """测试CSV文件验证功能"""
    print_separator("CSV文件验证测试")
    
    try:
        # 创建包含错误的测试文件
        test_csv_content = """id,user_id,user_input,primary_emotion,confidence
memory_001,user_123,今天天气很好,happy,0.85
memory_002,,昨天下雨了,sad,0.78
memory_003,user_789,,joy,0.92
memory_004,user_101,感觉很累,tired,invalid_confidence"""
        
        test_file_path = os.path.join(TEST_DATA_DIR, "test_validate.csv")
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_csv_content)
        
        # 验证文件
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'validation_type': 'memories'
            }
            
            response = requests.post(f"{BASE_URL}/csv/validate", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print("✅ CSV文件验证完成:")
                    data = result['data']
                    print(f"   - 总行数: {data['total_rows']}")
                    print(f"   - 有效行数: {data['valid_rows']}")
                    print(f"   - 无效行数: {data['invalid_rows']}")
                    print(f"   - 验证通过率: {data['validation_rate']:.2%}")
                    
                    if data['errors']:
                        print(f"\n   - 验证错误:")
                        for error in data['errors'][:3]:  # 显示前3个错误
                            print(f"     第{error['row']}行: {error['error']}")
                else:
                    print(f"❌ CSV文件验证失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_csv_statistics():
    """测试CSV文件统计功能"""
    print_separator("CSV文件统计测试")
    
    try:
        # 创建包含数字数据的测试文件
        test_csv_content = """id,user_id,confidence,age,score
memory_001,user_123,0.85,25,8.5
memory_002,user_456,0.78,30,7.8
memory_003,user_789,0.92,35,9.2
memory_004,user_101,0.70,28,7.0
memory_005,user_202,0.88,32,8.8"""
        
        test_file_path = os.path.join(TEST_DATA_DIR, "test_statistics.csv")
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_csv_content)
        
        # 统计分析
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            
            response = requests.post(f"{BASE_URL}/csv/statistics", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print("✅ CSV文件统计分析完成:")
                    data = result['data']
                    print(f"   - 行数: {data['row_count']}")
                    print(f"   - 列数: {data['column_count']}")
                    print(f"   - 内存使用: {data['memory_usage']} bytes")
                    
                    print(f"\n   - 列名和类型:")
                    for col, dtype in data['data_types'].items():
                        print(f"     {col}: {dtype}")
                    
                    print(f"\n   - 空值统计:")
                    for col, null_count in data['null_counts'].items():
                        print(f"     {col}: {null_count}")
                        
                    if 'describe' in data and data['describe']:
                        print(f"\n   - 数值统计:")
                        for col, stats in data['describe'].items():
                            if isinstance(stats, dict) and 'mean' in stats:
                                print(f"     {col}: 平均值={stats['mean']:.2f}, 标准差={stats['std']:.2f}")
                else:
                    print(f"❌ CSV文件统计失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_csv_merge():
    """测试CSV文件合并功能"""
    print_separator("CSV文件合并测试")
    
    try:
        # 创建两个测试文件
        file1_content = """id,user_id,text,emotion
1,user_123,开心的一天,happy
2,user_456,阴雨天气,sad"""
        
        file2_content = """id,user_id,text,emotion
3,user_789,美好的回忆,joy
4,user_101,感觉累了,tired"""
        
        file1_path = os.path.join(TEST_DATA_DIR, "merge_test1.csv")
        file2_path = os.path.join(TEST_DATA_DIR, "merge_test2.csv")
        
        with open(file1_path, 'w', encoding='utf-8') as f:
            f.write(file1_content)
        with open(file2_path, 'w', encoding='utf-8') as f:
            f.write(file2_content)
        
        # 合并文件
        with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
            files = {'files': [f1, f2]}
            data = {
                'merge_type': 'union',
                'remove_duplicates': 'true'
            }
            
            response = requests.post(f"{BASE_URL}/csv/merge", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print("✅ CSV文件合并成功:")
                    data = result['data']
                    print(f"   - 输入文件数: {len(data['input_files'])}")
                    print(f"   - 总输入记录: {data['total_input_records']}")
                    print(f"   - 合并后记录: {data['merged_records']}")
                    print(f"   - 合并类型: {data['merge_type']}")
                    
                    print(f"\n   - 文件信息:")
                    for file_info in data['file_info']:
                        print(f"     {os.path.basename(file_info['file_path'])}: {file_info['record_count']} 条记录")
                else:
                    print(f"❌ CSV文件合并失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_csv_split():
    """测试CSV文件拆分功能"""
    print_separator("CSV文件拆分测试")
    
    try:
        # 创建包含多条记录的测试文件
        test_csv_content = """id,user_id,text,emotion
1,user_123,开心的一天,happy
2,user_456,阴雨天气,sad
3,user_789,美好的回忆,joy
4,user_101,感觉累了,tired
5,user_202,阳光明媚,joy
6,user_303,心情低落,sad"""
        
        test_file_path = os.path.join(TEST_DATA_DIR, "test_split.csv")
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_csv_content)
        
        # 拆分文件
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'split_by': 'rows',
                'split_size': '2'
            }
            
            response = requests.post(f"{BASE_URL}/csv/split", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print("✅ CSV文件拆分成功:")
                    data = result['data']
                    print(f"   - 总记录数: {data['total_records']}")
                    print(f"   - 拆分方式: {data['split_by']}")
                    print(f"   - 拆分大小: {data['split_size']}")
                    print(f"   - 生成文件数: {data['file_count']}")
                    
                    print(f"\n   - 拆分文件:")
                    for file_info in data['split_files']:
                        print(f"     {file_info['filename']}: {file_info['record_count']} 条记录")
                else:
                    print(f"❌ CSV文件拆分失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def run_all_tests():
    """运行所有测试"""
    print_separator("PGG系统CSV接口全功能测试")
    
    print(f"🚀 开始测试 CSV 接口功能...")
    print(f"📡 服务器地址: {BASE_URL}")
    print(f"📁 测试数据目录: {TEST_DATA_DIR}")
    
    # 按顺序运行测试
    tests = [
        ("支持格式查询", test_csv_formats),
        ("CSV导出功能", test_csv_export),
        ("CSV模板创建", test_csv_template),
        ("CSV导入功能", test_csv_import),
        ("CSV文件分析", test_csv_analyze),
        ("CSV文件验证", test_csv_validate),
        ("CSV文件统计", test_csv_statistics),
        ("CSV文件合并", test_csv_merge),
        ("CSV文件拆分", test_csv_split)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 正在测试: {test_name}")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {test_name} - {str(e)}")
            failed += 1
        
        time.sleep(0.5)  # 短暂延迟
    
    # 总结
    print_separator("测试结果总结")
    print(f"✅ 通过: {passed} 个测试")
    print(f"❌ 失败: {failed} 个测试")
    print(f"📊 成功率: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有CSV接口功能测试通过！")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查服务器状态")

if __name__ == "__main__":
    run_all_tests() 