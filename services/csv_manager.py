# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - CSV文档管理器
专门处理CSV文档的导入、导出、解析和格式化功能
"""

import os
import csv
import json
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from io import StringIO, BytesIO
import zipfile
import tempfile
from pathlib import Path

from config import config

logger = logging.getLogger(__name__)

class CSVManager:
    """CSV文档管理器"""
    
    def __init__(self):
        """初始化CSV管理器"""
        self.storage_path = config.LOCAL_STORAGE_PATH
        self.csv_export_path = os.path.join(self.storage_path, 'csv_exports')
        self.csv_import_path = os.path.join(self.storage_path, 'csv_imports')
        self.csv_templates_path = os.path.join(self.storage_path, 'csv_templates')
        
        # 创建必要的目录
        for path in [self.csv_export_path, self.csv_import_path, self.csv_templates_path]:
            os.makedirs(path, exist_ok=True)
        
        # 支持的CSV格式
        self.supported_formats = {
            'memories': {
                'fields': ['id', 'user_id', 'user_input', 'memory_text', 'image_url', 
                          'primary_emotion', 'confidence', 'emotion_scores', 'created_at'],
                'required': ['user_id', 'user_input', 'memory_text'],
                'types': {
                    'confidence': float,
                    'created_at': datetime,
                    'emotion_scores': dict
                }
            },
            'emotions': {
                'fields': ['id', 'user_id', 'text', 'primary_emotion', 'confidence', 
                          'emotion_scores', 'valence', 'arousal', 'dominance', 'created_at'],
                'required': ['user_id', 'text', 'primary_emotion'],
                'types': {
                    'confidence': float,
                    'valence': float,
                    'arousal': float,
                    'dominance': float,
                    'created_at': datetime,
                    'emotion_scores': dict
                }
            },
            'elderly_data': {
                'fields': ['id', 'user_id', 'text', 'primary_emotion', 'confidence', 
                          'age', 'gender', 'age_group', 'keywords_matched', 'keyword_count',
                          'elderly_specific_health', 'elderly_specific_family', 
                          'elderly_specific_loneliness', 'elderly_specific_nostalgia',
                          'ai_suggestions', 'created_at', 'updated_at'],
                'required': ['user_id', 'text', 'primary_emotion'],
                'types': {
                    'confidence': float,
                    'age': int,
                    'keyword_count': int,
                    'elderly_specific_health': int,
                    'elderly_specific_family': int,
                    'elderly_specific_loneliness': int,
                    'elderly_specific_nostalgia': int,
                    'created_at': datetime,
                    'updated_at': datetime
                }
            },
            'sensor_data': {
                'fields': ['sensor_id', 'sensor_type', 'device_id', 'user_id', 
                          'value', 'unit', 'timestamp', 'quality', 'metadata'],
                'required': ['sensor_id', 'sensor_type', 'device_id', 'user_id', 'value'],
                'types': {
                    'value': float,
                    'timestamp': datetime,
                    'metadata': dict
                }
            },
            'user_statistics': {
                'fields': ['user_id', 'total_memories', 'emotion_distribution', 
                          'most_common_emotion', 'first_memory_date', 'last_memory_date',
                          'emotional_trend', 'updated_at'],
                'required': ['user_id'],
                'types': {
                    'total_memories': int,
                    'emotion_distribution': dict,
                    'first_memory_date': datetime,
                    'last_memory_date': datetime,
                    'emotional_trend': dict,
                    'updated_at': datetime
                }
            },
            'keywords': {
                'fields': ['keyword', 'frequency', 'category', 'emotional_correlation',
                          'usage_context', 'first_appearance', 'last_appearance', 'trend'],
                'required': ['keyword', 'frequency'],
                'types': {
                    'frequency': int,
                    'emotional_correlation': dict,
                    'first_appearance': datetime,
                    'last_appearance': datetime,
                    'trend': float
                }
            }
        }
    
    def export_to_csv(self, data: Union[List[Dict], Dict], 
                     export_type: str = 'general',
                     filename: str = None,
                     include_headers: bool = True,
                     encoding: str = 'utf-8',
                     delimiter: str = ',',
                     custom_fields: List[str] = None) -> Dict[str, Any]:
        """
        导出数据到CSV文件
        
        Args:
            data: 要导出的数据
            export_type: 导出类型 (memories, emotions, elderly_data, sensor_data, user_statistics, general)
            filename: 自定义文件名
            include_headers: 是否包含表头
            encoding: 文件编码
            delimiter: 字段分隔符
            custom_fields: 自定义字段列表
            
        Returns:
            Dict: 导出结果信息
        """
        try:
            # 准备数据
            if isinstance(data, dict):
                data = [data]
            
            if not data:
                raise ValueError("没有数据可导出")
            
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{export_type}_export_{timestamp}.csv"
            
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            file_path = os.path.join(self.csv_export_path, filename)
            
            # 确定字段列表
            if custom_fields:
                fields = custom_fields
            elif export_type in self.supported_formats:
                fields = self.supported_formats[export_type]['fields']
            else:
                # 自动检测字段
                fields = list(data[0].keys()) if data else []
            
            # 写入CSV文件
            with open(file_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fields, delimiter=delimiter)
                
                if include_headers:
                    writer.writeheader()
                
                # 处理数据类型转换
                processed_data = []
                for row in data:
                    processed_row = self._process_row_for_export(row, export_type, fields)
                    processed_data.append(processed_row)
                
                writer.writerows(processed_data)
            
            # 获取文件信息
            file_size = os.path.getsize(file_path)
            
            logger.info(f"CSV导出成功: {filename}, 记录数: {len(data)}, 大小: {file_size} bytes")
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': filename,
                'file_size': file_size,
                'record_count': len(data),
                'fields': fields,
                'export_type': export_type,
                'encoding': encoding,
                'delimiter': delimiter,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CSV导出失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_path': None
            }
    
    def import_from_csv(self, file_path: str,
                       import_type: str = 'general',
                       encoding: str = 'utf-8',
                       delimiter: str = ',',
                       skip_header: bool = True,
                       validate_data: bool = True,
                       custom_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """
        从CSV文件导入数据
        
        Args:
            file_path: CSV文件路径
            import_type: 导入类型
            encoding: 文件编码
            delimiter: 字段分隔符
            skip_header: 是否跳过表头
            validate_data: 是否验证数据
            custom_mapping: 自定义字段映射
            
        Returns:
            Dict: 导入结果信息
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 读取CSV文件
            data = []
            errors = []
            
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                
                if skip_header:
                    next(reader, None)
                
                for row_num, row in enumerate(reader, start=1):
                    try:
                        # 应用自定义映射
                        if custom_mapping:
                            row = self._apply_field_mapping(row, custom_mapping)
                        
                        # 处理数据类型转换
                        processed_row = self._process_row_for_import(row, import_type)
                        
                        # 验证数据
                        if validate_data:
                            validation_result = self._validate_row(processed_row, import_type)
                            if not validation_result['valid']:
                                errors.append({
                                    'row': row_num,
                                    'error': validation_result['error'],
                                    'data': row
                                })
                                continue
                        
                        data.append(processed_row)
                        
                    except Exception as e:
                        errors.append({
                            'row': row_num,
                            'error': str(e),
                            'data': row
                        })
            
            # 获取文件信息
            file_size = os.path.getsize(file_path)
            
            logger.info(f"CSV导入完成: {file_path}, 成功: {len(data)}, 错误: {len(errors)}")
            
            return {
                'success': True,
                'data': data,
                'total_rows': len(data) + len(errors),
                'success_count': len(data),
                'error_count': len(errors),
                'errors': errors,
                'file_path': file_path,
                'file_size': file_size,
                'import_type': import_type,
                'encoding': encoding,
                'delimiter': delimiter,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CSV导入失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': [],
                'total_rows': 0,
                'success_count': 0,
                'error_count': 0
            }
    
    def convert_csv_format(self, input_file: str, output_file: str,
                          from_type: str, to_type: str,
                          mapping_rules: Dict[str, str] = None) -> Dict[str, Any]:
        """
        转换CSV格式
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            from_type: 源数据类型
            to_type: 目标数据类型
            mapping_rules: 字段映射规则
            
        Returns:
            Dict: 转换结果信息
        """
        try:
            # 导入源数据
            import_result = self.import_from_csv(input_file, from_type, validate_data=False)
            
            if not import_result['success']:
                return {
                    'success': False,
                    'error': f"导入失败: {import_result['error']}"
                }
            
            data = import_result['data']
            
            # 应用字段映射
            if mapping_rules:
                converted_data = []
                for row in data:
                    converted_row = {}
                    for target_field, source_field in mapping_rules.items():
                        if source_field in row:
                            converted_row[target_field] = row[source_field]
                    converted_data.append(converted_row)
                data = converted_data
            
            # 导出到目标格式
            export_result = self.export_to_csv(
                data, 
                export_type=to_type,
                filename=os.path.basename(output_file)
            )
            
            if export_result['success']:
                # 移动文件到指定位置
                if output_file != export_result['file_path']:
                    os.rename(export_result['file_path'], output_file)
                    export_result['file_path'] = output_file
                
                return {
                    'success': True,
                    'input_file': input_file,
                    'output_file': output_file,
                    'from_type': from_type,
                    'to_type': to_type,
                    'converted_records': len(data),
                    'export_info': export_result
                }
            else:
                return {
                    'success': False,
                    'error': f"导出失败: {export_result['error']}"
                }
                
        except Exception as e:
            logger.error(f"CSV格式转换失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_csv_structure(self, file_path: str,
                             encoding: str = 'utf-8',
                             delimiter: str = ',',
                             sample_size: int = 100) -> Dict[str, Any]:
        """
        分析CSV文件结构
        
        Args:
            file_path: CSV文件路径
            encoding: 文件编码
            delimiter: 字段分隔符
            sample_size: 样本大小
            
        Returns:
            Dict: 分析结果
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 读取样本数据
            sample_data = []
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                headers = reader.fieldnames
                
                for i, row in enumerate(reader):
                    if i >= sample_size:
                        break
                    sample_data.append(row)
            
            # 分析字段类型
            field_analysis = {}
            for field in headers:
                field_analysis[field] = self._analyze_field_type(sample_data, field)
            
            # 统计信息
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'r', encoding=encoding) as f:
                total_rows = sum(1 for _ in f) - 1  # 减去表头
            
            return {
                'success': True,
                'file_path': file_path,
                'file_size': file_size,
                'total_rows': total_rows,
                'headers': headers,
                'field_count': len(headers),
                'field_analysis': field_analysis,
                'sample_data': sample_data[:10],  # 返回前10条样本
                'encoding': encoding,
                'delimiter': delimiter,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CSV结构分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_csv_template(self, template_type: str,
                           include_examples: bool = True,
                           custom_fields: List[str] = None) -> Dict[str, Any]:
        """
        创建CSV模板文件
        
        Args:
            template_type: 模板类型
            include_examples: 是否包含示例数据
            custom_fields: 自定义字段列表
            
        Returns:
            Dict: 模板创建结果
        """
        try:
            # 确定字段列表
            if custom_fields:
                fields = custom_fields
            elif template_type in self.supported_formats:
                fields = self.supported_formats[template_type]['fields']
            else:
                raise ValueError(f"不支持的模板类型: {template_type}")
            
            # 生成模板文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{template_type}_template_{timestamp}.csv"
            file_path = os.path.join(self.csv_templates_path, filename)
            
            # 创建模板数据
            template_data = []
            
            if include_examples:
                # 添加示例数据
                if template_type == 'memories':
                    template_data.append({
                        'id': 'memory_001',
                        'user_id': 'user_123',
                        'user_input': '今天天气很好',
                        'memory_text': '今天天气很好，让我想起了小时候的春天',
                        'image_url': 'https://example.com/image1.jpg',
                        'primary_emotion': 'happy',
                        'confidence': '0.85',
                        'emotion_scores': '{"happy": 0.85, "neutral": 0.15}',
                        'created_at': '2024-01-01T12:00:00'
                    })
                elif template_type == 'emotions':
                    template_data.append({
                        'id': 'emotion_001',
                        'user_id': 'user_123',
                        'text': '今天心情很好',
                        'primary_emotion': 'happy',
                        'confidence': '0.90',
                        'emotion_scores': '{"happy": 0.90, "neutral": 0.10}',
                        'valence': '0.8',
                        'arousal': '0.6',
                        'dominance': '0.7',
                        'created_at': '2024-01-01T12:00:00'
                    })
                elif template_type == 'sensor_data':
                    template_data.append({
                        'sensor_id': 'sensor_001',
                        'sensor_type': 'heart_rate',
                        'device_id': 'device_123',
                        'user_id': 'user_456',
                        'value': '72',
                        'unit': 'bpm',
                        'timestamp': '2024-01-01T12:00:00',
                        'quality': 'good',
                        'metadata': '{"battery_level": 85, "signal_strength": 90}'
                    })
            
            # 写入模板文件
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                
                if template_data:
                    writer.writerows(template_data)
            
            # 获取文件信息
            file_size = os.path.getsize(file_path)
            
            logger.info(f"CSV模板创建成功: {filename}")
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': filename,
                'file_size': file_size,
                'template_type': template_type,
                'fields': fields,
                'field_count': len(fields),
                'include_examples': include_examples,
                'example_count': len(template_data),
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CSV模板创建失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def merge_csv_files(self, input_files: List[str],
                       output_file: str,
                       merge_type: str = 'union',
                       remove_duplicates: bool = True,
                       key_fields: List[str] = None) -> Dict[str, Any]:
        """
        合并CSV文件
        
        Args:
            input_files: 输入文件列表
            output_file: 输出文件路径
            merge_type: 合并类型 (union, intersection, left_join, inner_join)
            remove_duplicates: 是否移除重复行
            key_fields: 合并关键字段
            
        Returns:
            Dict: 合并结果
        """
        try:
            if not input_files:
                raise ValueError("没有输入文件")
            
            # 读取所有文件
            all_data = []
            file_info = []
            
            for file_path in input_files:
                import_result = self.import_from_csv(file_path, validate_data=False)
                if import_result['success']:
                    all_data.extend(import_result['data'])
                    file_info.append({
                        'file_path': file_path,
                        'record_count': import_result['success_count'],
                        'errors': import_result['error_count']
                    })
                else:
                    logger.warning(f"跳过无效文件: {file_path}")
            
            # 合并数据
            if merge_type == 'union':
                merged_data = all_data
            elif merge_type == 'intersection':
                # 实现数据交集逻辑
                merged_data = self._merge_intersection(all_data, key_fields)
            else:
                # 默认使用union
                merged_data = all_data
            
            # 移除重复行
            if remove_duplicates and key_fields:
                merged_data = self._remove_duplicates(merged_data, key_fields)
            
            # 导出合并结果
            export_result = self.export_to_csv(
                merged_data,
                export_type='general',
                filename=os.path.basename(output_file)
            )
            
            if export_result['success']:
                # 移动文件到指定位置
                if output_file != export_result['file_path']:
                    os.rename(export_result['file_path'], output_file)
                    export_result['file_path'] = output_file
                
                return {
                    'success': True,
                    'input_files': input_files,
                    'output_file': output_file,
                    'merge_type': merge_type,
                    'total_input_records': len(all_data),
                    'merged_records': len(merged_data),
                    'file_info': file_info,
                    'export_info': export_result
                }
            else:
                return {
                    'success': False,
                    'error': f"导出失败: {export_result['error']}"
                }
                
        except Exception as e:
            logger.error(f"CSV文件合并失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def split_csv_file(self, input_file: str,
                      output_dir: str,
                      split_by: str = 'rows',
                      split_size: int = 1000,
                      split_field: str = None) -> Dict[str, Any]:
        """
        拆分CSV文件
        
        Args:
            input_file: 输入文件路径
            output_dir: 输出目录
            split_by: 拆分方式 (rows, field, size)
            split_size: 拆分大小
            split_field: 拆分字段
            
        Returns:
            Dict: 拆分结果
        """
        try:
            # 导入数据
            import_result = self.import_from_csv(input_file, validate_data=False)
            if not import_result['success']:
                return {
                    'success': False,
                    'error': f"导入失败: {import_result['error']}"
                }
            
            data = import_result['data']
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 拆分数据
            split_files = []
            
            if split_by == 'rows':
                # 按行数拆分
                for i in range(0, len(data), split_size):
                    chunk = data[i:i + split_size]
                    chunk_filename = f"chunk_{i//split_size + 1}.csv"
                    chunk_path = os.path.join(output_dir, chunk_filename)
                    
                    export_result = self.export_to_csv(
                        chunk,
                        export_type='general',
                        filename=chunk_filename
                    )
                    
                    if export_result['success']:
                        os.rename(export_result['file_path'], chunk_path)
                        split_files.append({
                            'file_path': chunk_path,
                            'filename': chunk_filename,
                            'record_count': len(chunk)
                        })
            
            elif split_by == 'field' and split_field:
                # 按字段值拆分
                field_groups = {}
                for row in data:
                    field_value = row.get(split_field, 'unknown')
                    if field_value not in field_groups:
                        field_groups[field_value] = []
                    field_groups[field_value].append(row)
                
                for field_value, group_data in field_groups.items():
                    chunk_filename = f"{split_field}_{field_value}.csv"
                    chunk_path = os.path.join(output_dir, chunk_filename)
                    
                    export_result = self.export_to_csv(
                        group_data,
                        export_type='general',
                        filename=chunk_filename
                    )
                    
                    if export_result['success']:
                        os.rename(export_result['file_path'], chunk_path)
                        split_files.append({
                            'file_path': chunk_path,
                            'filename': chunk_filename,
                            'record_count': len(group_data),
                            'field_value': field_value
                        })
            
            return {
                'success': True,
                'input_file': input_file,
                'output_dir': output_dir,
                'split_by': split_by,
                'split_size': split_size,
                'split_field': split_field,
                'total_records': len(data),
                'split_files': split_files,
                'file_count': len(split_files)
            }
            
        except Exception as e:
            logger.error(f"CSV文件拆分失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_csv_file(self, file_path: str,
                         validation_type: str = 'general',
                         custom_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        验证CSV文件
        
        Args:
            file_path: 文件路径
            validation_type: 验证类型
            custom_rules: 自定义验证规则
            
        Returns:
            Dict: 验证结果
        """
        try:
            # 导入数据
            import_result = self.import_from_csv(file_path, validate_data=True, import_type=validation_type)
            
            validation_result = {
                'success': True,
                'file_path': file_path,
                'validation_type': validation_type,
                'total_rows': import_result['total_rows'],
                'valid_rows': import_result['success_count'],
                'invalid_rows': import_result['error_count'],
                'errors': import_result['errors'],
                'validation_rate': import_result['success_count'] / import_result['total_rows'] if import_result['total_rows'] > 0 else 0,
                'validated_at': datetime.now().isoformat()
            }
            
            # 应用自定义验证规则
            if custom_rules:
                custom_validation = self._apply_custom_validation(import_result['data'], custom_rules)
                validation_result['custom_validation'] = custom_validation
            
            return validation_result
            
        except Exception as e:
            logger.error(f"CSV文件验证失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_csv_statistics(self, file_path: str) -> Dict[str, Any]:
        """
        获取CSV文件统计信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 统计信息
        """
        try:
            # 使用pandas进行统计分析
            df = pd.read_csv(file_path)
            
            statistics = {
                'success': True,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': df.columns.tolist(),
                'data_types': df.dtypes.to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'null_counts': df.isnull().sum().to_dict(),
                'describe': df.describe().to_dict(),
                'analyzed_at': datetime.now().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"CSV统计分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_keywords(self, data: List[Dict[str, Any]], format_type: str = 'general') -> Dict[str, Any]:
        """
        分析关键词数据
        
        Args:
            data: 要分析的数据
            format_type: 数据格式类型
            
        Returns:
            关键词分析结果
        """
        try:
            if not data:
                return {'success': False, 'error': '数据为空'}
            
            # 从config导入关键词列表
            from config import config
            elderly_keywords = config.ELDERLY_KEYWORDS
            
            # 关键词分析结果
            result = {
                'keyword_analysis': {
                    'total_keywords': len(elderly_keywords),
                    'keyword_categories': {
                        '基础关键词': 9,
                        '家庭关系': 16,
                        '生活相关': 17,
                        '社交与活动': 17,
                        '情感状态': 19,
                        '生活状态': 16,
                        '补充关键词': 4
                    },
                    'most_common_keywords': {},
                    'keyword_frequency': {},
                    'keyword_distribution': {},
                    'matched_records': 0,
                    'unmatched_records': 0,
                    'average_keywords_per_record': 0
                },
                'text_analysis': {
                    'total_records': len(data),
                    'records_with_keywords': 0,
                    'records_without_keywords': 0,
                    'keyword_density': 0,
                    'common_patterns': []
                },
                'emotional_keyword_correlation': {},
                'elderly_specific_insights': {}
            }
            
            # 分析每条记录
            keyword_counts = {}
            text_fields = ['text', 'user_input', 'memory_text']
            records_with_keywords = 0
            total_keyword_matches = 0
            
            for record in data:
                # 获取文本内容
                text_content = ""
                for field in text_fields:
                    if field in record and record[field]:
                        text_content += str(record[field]) + " "
                
                # 检查关键词匹配
                matched_keywords = []
                for keyword in elderly_keywords:
                    if keyword in text_content:
                        matched_keywords.append(keyword)
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
                
                if matched_keywords:
                    records_with_keywords += 1
                    total_keyword_matches += len(matched_keywords)
                
                # 分析情感与关键词的关联
                if 'primary_emotion' in record and matched_keywords:
                    emotion = record['primary_emotion']
                    if emotion not in result['emotional_keyword_correlation']:
                        result['emotional_keyword_correlation'][emotion] = {}
                    
                    for keyword in matched_keywords:
                        if keyword not in result['emotional_keyword_correlation'][emotion]:
                            result['emotional_keyword_correlation'][emotion][keyword] = 0
                        result['emotional_keyword_correlation'][emotion][keyword] += 1
            
            # 填充分析结果
            result['keyword_analysis']['keyword_frequency'] = keyword_counts
            result['keyword_analysis']['most_common_keywords'] = dict(
                sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            )
            result['keyword_analysis']['matched_records'] = records_with_keywords
            result['keyword_analysis']['unmatched_records'] = len(data) - records_with_keywords
            result['keyword_analysis']['average_keywords_per_record'] = (
                total_keyword_matches / len(data) if data else 0
            )
            
            # 文本分析
            result['text_analysis']['records_with_keywords'] = records_with_keywords
            result['text_analysis']['records_without_keywords'] = len(data) - records_with_keywords
            result['text_analysis']['keyword_density'] = (
                records_with_keywords / len(data) * 100 if data else 0
            )
            
            # 老人特定洞察
            result['elderly_specific_insights'] = {
                'health_keywords': {k: v for k, v in keyword_counts.items() 
                                  if k in ['血压', '血糖', '心脏', '头晕', '失眠', '关节', '骨头', '药物', '医生', '医院', '体检', '身体', '健康', '疼痛', '不舒服', '生病', '复查', '治疗', '康复', '手术', '住院']},
                'family_keywords': {k: v for k, v in keyword_counts.items() 
                                  if k in ['孙子', '孙女', '重孙', '重孙女', '外孙', '外孙女', '曾孙', '曾孙女', '孙媳妇', '孙女婿', '大儿子', '小儿子', '大女儿', '小女儿', '长子', '次子', '长女', '次女', '孩子', '子女', '儿子', '女儿', '老公', '老婆', '家人', '家里', '团聚', '思念', '亲人', '孙辈', '晚辈', '后代', '家族']},
                'loneliness_keywords': {k: v for k, v in keyword_counts.items() 
                                      if k in ['孤独', '寂寞', '想念', '怀念', '操心', '担心', '放心不下', '牵挂', '惦记', '想家', '想儿子', '想女儿', '无聊', '空虚', '冷清', '一个人', '没人', '独自']},
                'social_keywords': {k: v for k, v in keyword_counts.items() 
                                  if k in ['广场舞', '太极', '晨练', '散步', '下棋', '打牌', '唱戏', '看戏', '听戏', '老年大学', '老年活动', '社区活动', '邻居', '老朋友', '老同事', '老战友', '朋友', '同伴', '聊天', '说话', '交流', '沟通', '相伴', '聚会', '聚餐', '热闹']}
            }
            
            return {
                'success': True,
                'data': result,
                'message': f'关键词分析完成，共分析{len(data)}条记录，发现{len(keyword_counts)}个不同关键词'
            }
            
        except Exception as e:
            logger.error(f"关键词分析失败: {str(e)}")
            return {
                'success': False,
                'error': '关键词分析失败',
                'message': str(e)
            }
    
    def _process_row_for_export(self, row: Dict[str, Any], 
                               export_type: str, 
                               fields: List[str]) -> Dict[str, Any]:
        """处理导出行数据"""
        processed_row = {}
        
        for field in fields:
            value = row.get(field, '')
            
            # 处理特殊数据类型
            if isinstance(value, dict):
                processed_row[field] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, list):
                processed_row[field] = ','.join(str(v) for v in value)
            elif isinstance(value, datetime):
                processed_row[field] = value.isoformat()
            else:
                processed_row[field] = str(value) if value is not None else ''
        
        return processed_row
    
    def _process_row_for_import(self, row: Dict[str, Any], 
                               import_type: str) -> Dict[str, Any]:
        """处理导入行数据"""
        processed_row = {}
        
        if import_type in self.supported_formats:
            field_types = self.supported_formats[import_type]['types']
            
            for field, value in row.items():
                if field in field_types:
                    field_type = field_types[field]
                    
                    try:
                        if field_type == datetime:
                            processed_row[field] = pd.to_datetime(value) if value else None
                        elif field_type == dict:
                            processed_row[field] = json.loads(value) if value else {}
                        elif field_type == float:
                            processed_row[field] = float(value) if value else 0.0
                        elif field_type == int:
                            processed_row[field] = int(value) if value else 0
                        else:
                            processed_row[field] = value
                    except (ValueError, TypeError):
                        processed_row[field] = value
                else:
                    processed_row[field] = value
        else:
            processed_row = row
        
        return processed_row
    
    def _validate_row(self, row: Dict[str, Any], 
                     validation_type: str) -> Dict[str, Any]:
        """验证行数据"""
        if validation_type not in self.supported_formats:
            return {'valid': True, 'error': None}
        
        format_config = self.supported_formats[validation_type]
        required_fields = format_config['required']
        
        # 检查必填字段
        for field in required_fields:
            if field not in row or not row[field]:
                return {
                    'valid': False,
                    'error': f"缺少必填字段: {field}"
                }
        
        return {'valid': True, 'error': None}
    
    def _apply_field_mapping(self, row: Dict[str, Any], 
                           mapping: Dict[str, str]) -> Dict[str, Any]:
        """应用字段映射"""
        mapped_row = {}
        for target_field, source_field in mapping.items():
            if source_field in row:
                mapped_row[target_field] = row[source_field]
        return mapped_row
    
    def _analyze_field_type(self, sample_data: List[Dict], 
                           field_name: str) -> Dict[str, Any]:
        """分析字段类型"""
        values = [row.get(field_name, '') for row in sample_data if row.get(field_name)]
        
        if not values:
            return {'type': 'unknown', 'null_count': len(sample_data)}
        
        # 类型检测
        type_counts = {
            'string': 0,
            'integer': 0,
            'float': 0,
            'boolean': 0,
            'datetime': 0,
            'json': 0
        }
        
        for value in values:
            str_value = str(value).strip()
            
            if self._is_integer(str_value):
                type_counts['integer'] += 1
            elif self._is_float(str_value):
                type_counts['float'] += 1
            elif self._is_boolean(str_value):
                type_counts['boolean'] += 1
            elif self._is_datetime(str_value):
                type_counts['datetime'] += 1
            elif self._is_json(str_value):
                type_counts['json'] += 1
            else:
                type_counts['string'] += 1
        
        # 确定主要类型
        main_type = max(type_counts, key=type_counts.get)
        
        return {
            'type': main_type,
            'type_counts': type_counts,
            'null_count': len(sample_data) - len(values),
            'unique_values': len(set(values)),
            'sample_values': list(set(values))[:5]
        }
    
    def _is_integer(self, value: str) -> bool:
        """检查是否为整数"""
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def _is_float(self, value: str) -> bool:
        """检查是否为浮点数"""
        try:
            float(value)
            return '.' in value
        except ValueError:
            return False
    
    def _is_boolean(self, value: str) -> bool:
        """检查是否为布尔值"""
        return value.lower() in ['true', 'false', '1', '0', 'yes', 'no']
    
    def _is_datetime(self, value: str) -> bool:
        """检查是否为日期时间"""
        try:
            pd.to_datetime(value)
            return True
        except:
            return False
    
    def _is_json(self, value: str) -> bool:
        """检查是否为JSON"""
        try:
            json.loads(value)
            return True
        except:
            return False
    
    def _merge_intersection(self, data: List[Dict], 
                           key_fields: List[str]) -> List[Dict]:
        """计算数据交集"""
        if not key_fields:
            return data
        
        # 简化实现，返回原数据
        return data
    
    def _remove_duplicates(self, data: List[Dict], 
                          key_fields: List[str]) -> List[Dict]:
        """移除重复数据"""
        seen = set()
        unique_data = []
        
        for row in data:
            key = tuple(row.get(field, '') for field in key_fields)
            if key not in seen:
                seen.add(key)
                unique_data.append(row)
        
        return unique_data
    
    def _apply_custom_validation(self, data: List[Dict], 
                                rules: Dict[str, Any]) -> Dict[str, Any]:
        """应用自定义验证规则"""
        validation_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
        for i, row in enumerate(data):
            try:
                # 实现自定义验证逻辑
                # 这里可以根据具体需求扩展
                validation_results['passed'] += 1
            except Exception as e:
                validation_results['failed'] += 1
                validation_results['errors'].append({
                    'row': i + 1,
                    'error': str(e)
                })
        
        return validation_results 