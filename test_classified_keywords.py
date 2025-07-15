# -*- coding: utf-8 -*-
"""
分类关键词CSV文件测试
测试归类后的关键词数据并生成分析报告
"""

import pandas as pd
import json
import requests
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_classified_keywords():
    """加载分类后的关键词CSV文件"""
    try:
        df = pd.read_csv('keywords_classified.csv')
        print(f"✅ 成功加载 {len(df)} 条关键词数据")
        return df
    except FileNotFoundError:
        print("❌ 未找到 keywords_classified.csv 文件")
        return None
    except Exception as e:
        print(f"❌ 加载文件失败: {str(e)}")
        return None

def analyze_classification_distribution(df):
    """分析分类分布"""
    print("\n📊 分类分布分析:")
    print("=" * 50)
    
    # 按分类统计
    category_counts = df['分类'].value_counts()
    print("🏷️  按分类统计:")
    for category, count in category_counts.items():
        print(f"   {category}: {count} 条")
    
    # 按情感倾向统计
    emotion_counts = df['情感倾向'].value_counts()
    print("\n💭 按情感倾向统计:")
    for emotion, count in emotion_counts.items():
        print(f"   {emotion}: {count} 条")
    
    # 按严重程度统计
    severity_counts = df['严重程度'].value_counts()
    print("\n⚠️  按严重程度统计:")
    for severity, count in severity_counts.items():
        print(f"   {severity}: {count} 条")
    
    # 按使用场景统计
    scene_counts = df['使用场景'].value_counts()
    print("\n🎬 按使用场景统计:")
    for scene, count in scene_counts.head(10).items():
        print(f"   {scene}: {count} 条")
    
    return {
        'category_counts': category_counts,
        'emotion_counts': emotion_counts,
        'severity_counts': severity_counts,
        'scene_counts': scene_counts
    }

def generate_keyword_analysis_report(df):
    """生成关键词分析报告"""
    print("\n📋 关键词分析报告:")
    print("=" * 50)
    
    # 高优先级关键词（严重程度为"高"）
    high_priority = df[df['严重程度'] == '高']
    print(f"🚨 高优先级关键词 ({len(high_priority)} 条):")
    for idx, row in high_priority.iterrows():
        print(f"   • {row['关键词']} ({row['分类']}) - {row['建议处理方式']}")
    
    # 医疗相关关键词
    medical_keywords = df[df['使用场景'] == '医疗场景']
    print(f"\n🏥 医疗相关关键词 ({len(medical_keywords)} 条):")
    for idx, row in medical_keywords.iterrows():
        print(f"   • {row['关键词']} - {row['建议处理方式']}")
    
    # 正面情感关键词
    positive_keywords = df[df['情感倾向'] == '正面']
    print(f"\n😊 正面情感关键词 ({len(positive_keywords)} 条):")
    for idx, row in positive_keywords.head(10).iterrows():
        print(f"   • {row['关键词']} ({row['分类']})")
    
    # 投诉相关关键词
    complaint_keywords = df[df['分类'].str.contains('投诉|抱怨', na=False)]
    print(f"\n📞 投诉相关关键词 ({len(complaint_keywords)} 条):")
    for idx, row in complaint_keywords.head(10).iterrows():
        print(f"   • {row['关键词']} - {row['建议处理方式']}")

def create_visualization(stats):
    """创建可视化图表"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 分类分布饼图
    axes[0, 0].pie(stats['category_counts'].values, labels=stats['category_counts'].index, 
                   autopct='%1.1f%%', startangle=90)
    axes[0, 0].set_title('关键词分类分布')
    
    # 情感倾向柱状图
    axes[0, 1].bar(stats['emotion_counts'].index, stats['emotion_counts'].values)
    axes[0, 1].set_title('情感倾向分布')
    axes[0, 1].set_xlabel('情感倾向')
    axes[0, 1].set_ylabel('数量')
    
    # 严重程度分布
    axes[1, 0].bar(stats['severity_counts'].index, stats['severity_counts'].values)
    axes[1, 0].set_title('严重程度分布')
    axes[1, 0].set_xlabel('严重程度')
    axes[1, 0].set_ylabel('数量')
    
    # 使用场景分布（前10）
    top_scenes = stats['scene_counts'].head(10)
    axes[1, 1].barh(range(len(top_scenes)), top_scenes.values)
    axes[1, 1].set_yticks(range(len(top_scenes)))
    axes[1, 1].set_yticklabels(top_scenes.index)
    axes[1, 1].set_title('使用场景分布（前10）')
    axes[1, 1].set_xlabel('数量')
    
    plt.tight_layout()
    plt.savefig('keywords_analysis_report.png', dpi=300, bbox_inches='tight')
    print("✅ 可视化图表已保存为 keywords_analysis_report.png")

def test_with_csv_api(df):
    """使用CSV关键词分析API测试"""
    print("\n🔍 使用CSV关键词分析API测试:")
    print("=" * 50)
    
    # 准备测试数据
    sample_data = []
    for idx, row in df.head(20).iterrows():
        sample_data.append({
            'text': row['关键词'],
            'user_id': f'user_{idx}',
            'primary_emotion': row['情感倾向'],
            'category': row['分类'],
            'severity': row['严重程度']
        })
    
    try:
        # 调用关键词分析API
        BASE_URL = "http://localhost:5000"
        response = requests.post(f"{BASE_URL}/csv/keywords/analyze", json={
            "data": sample_data,
            "format": "general"
        })
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功")
            
            # 显示分析结果
            keyword_analysis = result['data']['keyword_analysis']
            print(f"📊 匹配关键词: {keyword_analysis['matched_records']} / {len(sample_data)}")
            print(f"📈 平均关键词密度: {keyword_analysis['average_keywords_per_record']:.2f}")
            
            # 显示最常见关键词
            print("\n🔝 最常见关键词:")
            for keyword, count in list(keyword_analysis['most_common_keywords'].items())[:10]:
                print(f"   • {keyword}: {count} 次")
                
        else:
            print(f"❌ API调用失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保PGG服务器正在运行")
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")

def export_analysis_results(df, stats):
    """导出分析结果"""
    print("\n📤 导出分析结果:")
    print("=" * 50)
    
    # 创建分析报告
    analysis_report = {
        'total_keywords': len(df),
        'categories': stats['category_counts'].to_dict(),
        'emotions': stats['emotion_counts'].to_dict(),
        'severities': stats['severity_counts'].to_dict(),
        'scenes': stats['scene_counts'].to_dict(),
        'high_priority_keywords': df[df['严重程度'] == '高']['关键词'].tolist(),
        'medical_keywords': df[df['使用场景'] == '医疗场景']['关键词'].tolist(),
        'positive_keywords': df[df['情感倾向'] == '正面']['关键词'].tolist(),
        'generated_at': datetime.now().isoformat()
    }
    
    # 保存为JSON
    with open('keywords_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, ensure_ascii=False, indent=2)
    
    print("✅ 分析报告已保存为 keywords_analysis_report.json")
    
    # 导出高优先级关键词CSV
    high_priority_df = df[df['严重程度'] == '高']
    high_priority_df.to_csv('high_priority_keywords.csv', index=False, encoding='utf-8')
    print("✅ 高优先级关键词已导出为 high_priority_keywords.csv")
    
    # 导出按分类分组的CSV
    for category in df['分类'].unique():
        category_df = df[df['分类'] == category]
        filename = f'keywords_{category}.csv'
        category_df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ {category} 关键词已导出为 {filename}")

def create_processing_guidelines(df):
    """创建处理指导方针"""
    print("\n📋 处理指导方针:")
    print("=" * 50)
    
    # 按严重程度分组处理建议
    severity_guidelines = {
        '高': '🚨 立即响应（5分钟内）',
        '中等': '⚠️ 优先处理（30分钟内）',
        '低': '📝 正常处理（2小时内）'
    }
    
    for severity, guideline in severity_guidelines.items():
        count = len(df[df['严重程度'] == severity])
        print(f"{guideline} - {count} 条关键词")
    
    # 按场景分组处理建议
    scene_guidelines = {
        '医疗场景': '🏥 立即联系医护人员',
        '客户服务': '📞 转接客服主管',
        '冲突场景': '🚨 紧急处理，安抚情绪',
        '法律场景': '⚖️ 联系法务部门',
        '情绪场景': '💭 心理疏导，情感支持'
    }
    
    print("\n🎬 场景处理指导:")
    for scene, guideline in scene_guidelines.items():
        count = len(df[df['使用场景'] == scene])
        if count > 0:
            print(f"{guideline} - {count} 条关键词")

def main():
    """主函数"""
    print("🎉 分类关键词CSV文件分析")
    print("=" * 60)
    
    # 加载数据
    df = load_classified_keywords()
    if df is None:
        return
    
    # 分析分类分布
    stats = analyze_classification_distribution(df)
    
    # 生成分析报告
    generate_keyword_analysis_report(df)
    
    # 创建可视化图表
    try:
        create_visualization(stats)
    except Exception as e:
        print(f"⚠️ 图表生成失败: {str(e)}")
    
    # 测试CSV API
    test_with_csv_api(df)
    
    # 导出分析结果
    export_analysis_results(df, stats)
    
    # 创建处理指导方针
    create_processing_guidelines(df)
    
    print("\n" + "=" * 60)
    print("✅ 分类关键词分析完成！")
    print("📁 生成的文件:")
    print("   • keywords_analysis_report.json - 分析报告")
    print("   • keywords_analysis_report.png - 可视化图表")
    print("   • high_priority_keywords.csv - 高优先级关键词")
    print("   • keywords_*.csv - 按分类分组的关键词文件")
    print("=" * 60)

if __name__ == "__main__":
    main() 