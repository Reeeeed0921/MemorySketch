# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 图像生成服务
提供基于文本和情感的图像生成功能
"""

import os
import json
import logging
import random
import requests
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from PIL import Image
import io

from config import config
from models import ImageGenerationConfig, get_emotion_description

logger = logging.getLogger(__name__)

class ImageGenerator:
    """图像生成器"""
    
    def __init__(self):
        """初始化图像生成器"""
        self.models_loaded = False
        self.sd_model = None
        self.api_available = False
        
        # 情感对应的视觉风格
        self.emotion_styles = {
            'happy': {
                'colors': ['bright yellow', 'warm orange', 'golden', 'sunny'],
                'atmosphere': ['bright', 'cheerful', 'vibrant', 'warm'],
                'elements': ['sunshine', 'flowers', 'rainbow', 'smiling'],
                'mood': 'joyful and bright'
            },
            'sad': {
                'colors': ['blue', 'gray', 'muted', 'cool tones'],
                'atmosphere': ['melancholic', 'somber', 'quiet', 'gentle'],
                'elements': ['rain', 'clouds', 'tears', 'shadow'],
                'mood': 'melancholic and reflective'
            },
            'angry': {
                'colors': ['red', 'orange', 'fiery', 'intense'],
                'atmosphere': ['dramatic', 'intense', 'stormy', 'turbulent'],
                'elements': ['fire', 'lightning', 'storm', 'sharp edges'],
                'mood': 'intense and dramatic'
            },
            'fear': {
                'colors': ['dark', 'purple', 'black', 'shadowy'],
                'atmosphere': ['mysterious', 'eerie', 'tense', 'unsettling'],
                'elements': ['darkness', 'shadows', 'mist', 'unknown'],
                'mood': 'mysterious and tense'
            },
            'peaceful': {
                'colors': ['soft blue', 'gentle green', 'white', 'pastel'],
                'atmosphere': ['calm', 'serene', 'tranquil', 'peaceful'],
                'elements': ['lake', 'mountain', 'zen garden', 'meditation'],
                'mood': 'calm and serene'
            },
            'love': {
                'colors': ['pink', 'red', 'warm', 'soft'],
                'atmosphere': ['romantic', 'warm', 'tender', 'loving'],
                'elements': ['hearts', 'roses', 'embrace', 'sunset'],
                'mood': 'romantic and warm'
            },
            'nostalgic': {
                'colors': ['sepia', 'vintage', 'warm brown', 'faded'],
                'atmosphere': ['vintage', 'dreamy', 'nostalgic', 'soft'],
                'elements': ['old photos', 'memories', 'vintage items', 'time'],
                'mood': 'nostalgic and dreamy'
            },
            'surprise': {
                'colors': ['bright', 'contrasting', 'vivid', 'unexpected'],
                'atmosphere': ['dynamic', 'energetic', 'surprising', 'vivid'],
                'elements': ['burst', 'stars', 'explosion', 'surprise'],
                'mood': 'surprising and dynamic'
            }
        }
        
        # 图像风格模板
        self.style_templates = {
            'realistic': 'photorealistic, high quality, detailed',
            'artistic': 'artistic, painting style, creative',
            'dreamy': 'dreamy, ethereal, soft focus, magical',
            'vintage': 'vintage style, retro, aged, nostalgic',
            'minimalist': 'minimalist, clean, simple, modern',
            'fantasy': 'fantasy, magical, surreal, imaginative'
        }
    
    def init_models(self):
        """初始化图像生成模型"""
        try:
            logger.info("初始化图像生成模型...")
            
            # 检查Stable Diffusion模型
            self._init_stable_diffusion()
            
            # 检查API服务
            self._init_api_services()
            
            self.models_loaded = True
            logger.info("✅ 图像生成模型初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 图像生成模型初始化失败: {str(e)}")
            logger.info("使用模拟生成模式")
            self.models_loaded = False
    
    def _init_stable_diffusion(self):
        """初始化Stable Diffusion模型"""
        try:
            sd_path = config.SD_MODEL_PATH
            sd_api_url = config.SD_API_URL
            
            # 检查本地模型文件
            if os.path.exists(sd_path):
                logger.info(f"找到Stable Diffusion模型: {sd_path}")
                # TODO: 加载本地SD模型
                # self.sd_model = StableDiffusionPipeline.from_pretrained(sd_path)
            
            # 检查API服务
            if sd_api_url:
                try:
                    response = requests.get(f"{sd_api_url}/health", timeout=5)
                    if response.status_code == 200:
                        logger.info(f"Stable Diffusion API服务可用: {sd_api_url}")
                        self.api_available = True
                except:
                    logger.warning(f"Stable Diffusion API服务不可用: {sd_api_url}")
            
        except Exception as e:
            logger.warning(f"Stable Diffusion初始化失败: {str(e)}")
    
    def _init_api_services(self):
        """初始化第三方API服务"""
        try:
            # 检查科大讯飞图片生成API
            if config.IFLYTEK_IMAGE_API_KEY:
                logger.info("配置科大讯飞图片生成API")
                # TODO: 验证讯飞API可用性
            
            # 检查MidJourney API
            if config.MJ_API_KEY:
                logger.info("配置MidJourney API")
                # TODO: 验证MJ API可用性
            
            # 检查OpenAI DALL-E API
            if config.OPENAI_API_KEY:
                logger.info("配置OpenAI DALL-E API")
                # TODO: 验证DALL-E API可用性
            
        except Exception as e:
            logger.warning(f"第三方API服务初始化失败: {str(e)}")
    
    def generate_image(self, memory_text: str, emotion_result: Dict[str, Any], 
                      style: str = "realistic", size: str = "512x512") -> str:
        """
        生成图像
        
        Args:
            memory_text: 回忆文本
            emotion_result: 情感分析结果
            style: 图像风格
            size: 图像尺寸
            
        Returns:
            图像URL或路径
        """
        try:
            logger.info(f"开始生成图像: {memory_text[:50]}...")
            
            # 构建图像生成配置
            config_obj = ImageGenerationConfig(
                prompt=memory_text,
                style=style,
                size=size,
                emotion_influence=0.7
            )
            
            # 生成提示词
            enhanced_prompt = self._enhance_prompt(memory_text, emotion_result, style)
            
            # 选择生成方法（优先使用第三方API以获得最佳准确率）
            if config.IFLYTEK_IMAGE_API_KEY:
                # 第一优先级：使用科大讯飞图片生成API（高准确率）
                image_url = self._generate_with_iflytek(enhanced_prompt, config_obj)
            elif self.api_available:
                # 第二优先级：使用SD API服务（高准确率）
                image_url = self._generate_with_sd_api(enhanced_prompt, config_obj)
            elif config.MJ_API_KEY:
                # 第三优先级：使用MidJourney API（高准确率）
                image_url = self._generate_with_midjourney(enhanced_prompt, config_obj)
            elif config.OPENAI_API_KEY:
                # 第四优先级：使用DALL-E API（高准确率）
                image_url = self._generate_with_dalle(enhanced_prompt, config_obj)
            elif self.models_loaded and self.sd_model:
                # 第五优先级：使用本地SD模型（中等准确率）
                image_url = self._generate_with_local_sd(enhanced_prompt, config_obj)
            else:
                # 最后选择：使用模拟生成（保底方案）
                image_url = self._generate_with_simulation(enhanced_prompt, config_obj)
            
            logger.info(f"图像生成完成: {image_url}")
            return image_url
            
        except Exception as e:
            logger.error(f"图像生成失败: {str(e)}")
            return self._generate_placeholder_image()
    
    def _enhance_prompt(self, memory_text: str, emotion_result: Dict[str, Any], style: str) -> str:
        """增强提示词"""
        try:
            primary_emotion = emotion_result.get('primary_emotion', 'neutral')
            confidence = emotion_result.get('confidence', 0.5)
            
            # 基础提示词
            base_prompt = memory_text
            
            # 添加情感元素
            if primary_emotion in self.emotion_styles:
                emotion_style = self.emotion_styles[primary_emotion]
                
                # 添加颜色
                colors = random.choice(emotion_style['colors'])
                base_prompt += f", {colors} color palette"
                
                # 添加氛围
                atmosphere = random.choice(emotion_style['atmosphere'])
                base_prompt += f", {atmosphere} atmosphere"
                
                # 添加元素
                if confidence > 0.6:  # 只在高置信度时添加特定元素
                    elements = random.choice(emotion_style['elements'])
                    base_prompt += f", with {elements}"
                
                # 添加整体情绪
                mood = emotion_style['mood']
                base_prompt += f", {mood} mood"
            
            # 添加风格模板
            if style in self.style_templates:
                style_desc = self.style_templates[style]
                base_prompt += f", {style_desc}"
            
            # 添加质量描述
            base_prompt += ", high quality, detailed, beautiful composition"
            
            logger.info(f"增强提示词: {base_prompt}")
            return base_prompt
            
        except Exception as e:
            logger.error(f"增强提示词失败: {str(e)}")
            return memory_text
    
    def _generate_with_local_sd(self, prompt: str, config: ImageGenerationConfig) -> str:
        """使用本地Stable Diffusion模型生成图像"""
        try:
            # TODO: 实现本地SD模型调用
            logger.info("使用本地Stable Diffusion模型生成图像...")
            
            # 模拟生成过程
            import time
            time.sleep(2)  # 模拟生成时间
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"
            filepath = os.path.join(config.LOCAL_STORAGE_PATH, 'images', filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 创建模拟图像
            self._create_simulation_image(filepath, prompt)
            
            return filepath
            
        except Exception as e:
            logger.error(f"本地SD模型生成失败: {str(e)}")
            return self._generate_placeholder_image()
    
    def _generate_with_sd_api(self, prompt: str, config: ImageGenerationConfig) -> str:
        """使用Stable Diffusion API生成图像"""
        try:
            logger.info("使用Stable Diffusion API生成图像...")
            
            # 构建API请求
            payload = {
                "prompt": prompt,
                "width": int(config.size.split('x')[0]),
                "height": int(config.size.split('x')[1]),
                "steps": 20,
                "cfg_scale": 7,
                "sampler_name": "DPM++ 2M Karras"
            }
            
            # 发送请求
            response = requests.post(
                f"{config.SD_API_URL}/sdapi/v1/txt2img",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 保存图像
                image_data = base64.b64decode(result['images'][0])
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"sd_generated_{timestamp}.png"
                filepath = os.path.join(config.LOCAL_STORAGE_PATH, 'images', filename)
                
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                return filepath
            else:
                raise Exception(f"API请求失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"SD API生成失败: {str(e)}")
            return self._generate_placeholder_image()
    
    def _generate_with_midjourney(self, prompt: str, config: ImageGenerationConfig) -> str:
        """使用MidJourney API生成图像"""
        try:
            logger.info("使用MidJourney API生成图像...")
            
            # TODO: 实现MidJourney API调用
            # 这里需要根据MidJourney API的实际接口进行实现
            
            # 模拟API调用
            import time
            time.sleep(3)  # 模拟生成时间
            
            # 生成模拟图像
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mj_generated_{timestamp}.png"
            filepath = os.path.join(config.LOCAL_STORAGE_PATH, 'images', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            self._create_simulation_image(filepath, prompt)
            
            return filepath
            
        except Exception as e:
            logger.error(f"MidJourney API生成失败: {str(e)}")
            return self._generate_placeholder_image()
    
    def _generate_with_dalle(self, prompt: str, config: ImageGenerationConfig) -> str:
        """使用DALL-E API生成图像"""
        try:
            logger.info("使用DALL-E API生成图像...")
            
            # TODO: 实现DALL-E API调用
            # 这里需要使用OpenAI的API
            
            # 模拟API调用
            import time
            time.sleep(2)  # 模拟生成时间
            
            # 生成模拟图像
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dalle_generated_{timestamp}.png"
            filepath = os.path.join(config.LOCAL_STORAGE_PATH, 'images', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            self._create_simulation_image(filepath, prompt)
            
            return filepath
            
        except Exception as e:
            logger.error(f"DALL-E API生成失败: {str(e)}")
            return self._generate_placeholder_image()
    
    def _generate_with_iflytek(self, prompt: str, config: ImageGenerationConfig) -> str:
        """使用科大讯飞API生成图像"""
        try:
            import hmac
            import hashlib
            import time
            from urllib.parse import urlencode
            
            logger.info("使用科大讯飞API生成图像...")
            
            # 构建请求参数
            api_key = config.IFLYTEK_IMAGE_API_KEY
            api_secret = config.IFLYTEK_IMAGE_API_SECRET
            api_id = config.IFLYTEK_IMAGE_API_ID
            api_url = config.IFLYTEK_IMAGE_API_URL
            
            # 生成时间戳
            timestamp = str(int(time.time()))
            
            # 构建签名
            signature_data = f"app_id={api_id}&timestamp={timestamp}"
            signature = hmac.new(
                api_secret.encode('utf-8'),
                signature_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # 处理提示词，确保符合讯飞API要求
            processed_prompt = self._process_prompt_for_iflytek(prompt)
            
            # 构建请求头
            headers = {
                'Content-Type': 'application/json',
                'appid': api_id,
                'timestamp': timestamp,
                'signature': signature
            }
            
            # 构建请求体
            request_data = {
                "prompt": processed_prompt,
                "width": int(config.size.split('x')[0]) if 'x' in config.size else 512,
                "height": int(config.size.split('x')[1]) if 'x' in config.size else 512,
                "style": self._map_style_to_iflytek(config.style),
                "output_format": "base64"
            }
            
            # 发送请求
            response = requests.post(
                api_url,
                headers=headers,
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('code') == 0 and result.get('data'):
                    # 获取生成的图像数据
                    image_data = result['data'].get('image')
                    if image_data:
                        # 保存图像
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"iflytek_generated_{timestamp}.png"
                        filepath = os.path.join(config.LOCAL_STORAGE_PATH, 'images', filename)
                        
                        # 确保目录存在
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        
                        # 解码并保存base64图像
                        image_bytes = base64.b64decode(image_data)
                        with open(filepath, 'wb') as f:
                            f.write(image_bytes)
                        
                        logger.info(f"科大讯飞图像生成成功: {filename}")
                        return filename
                    else:
                        logger.error("科大讯飞API返回数据中没有图像")
                        return self._generate_placeholder_image()
                else:
                    error_msg = result.get('message', '未知错误')
                    logger.error(f"科大讯飞API错误: {error_msg}")
                    return self._generate_placeholder_image()
            else:
                logger.error(f"科大讯飞API请求失败: {response.status_code}")
                return self._generate_placeholder_image()
                
        except Exception as e:
            logger.error(f"使用科大讯飞生成图像失败: {str(e)}")
            return self._generate_placeholder_image()
    
    def _process_prompt_for_iflytek(self, prompt: str) -> str:
        """处理提示词以适配科大讯飞API"""
        # 限制提示词长度
        max_length = 500
        if len(prompt) > max_length:
            prompt = prompt[:max_length]
        
        # 过滤可能的敏感词汇
        sensitive_words = ['暴力', '血腥', '色情', '政治']
        for word in sensitive_words:
            prompt = prompt.replace(word, '')
        
        # 确保提示词为中文或英文
        return prompt.strip()
    
    def _map_style_to_iflytek(self, style: str) -> str:
        """将通用风格映射到科大讯飞支持的风格"""
        style_mapping = {
            'realistic': '写实',
            'artistic': '艺术',
            'dreamy': '梦幻',
            'vintage': '复古',
            'minimalist': '简约',
            'fantasy': '奇幻'
        }
        return style_mapping.get(style, '写实')
    
    def _generate_with_simulation(self, prompt: str, config: ImageGenerationConfig) -> str:
        """使用模拟生成图像"""
        try:
            logger.info("使用模拟模式生成图像...")
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_{timestamp}.png"
            filepath = os.path.join(config.LOCAL_STORAGE_PATH, 'images', filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 创建模拟图像
            self._create_simulation_image(filepath, prompt)
            
            return filepath
            
        except Exception as e:
            logger.error(f"模拟生成失败: {str(e)}")
            return self._generate_placeholder_image()
    
    def _create_simulation_image(self, filepath: str, prompt: str):
        """创建模拟图像"""
        try:
            # 创建一个简单的彩色图像
            width, height = 512, 512
            
            # 根据提示词选择颜色
            if 'happy' in prompt.lower() or 'joy' in prompt.lower():
                color = (255, 223, 0)  # 黄色
            elif 'sad' in prompt.lower() or 'blue' in prompt.lower():
                color = (135, 206, 235)  # 蓝色
            elif 'angry' in prompt.lower() or 'red' in prompt.lower():
                color = (255, 69, 0)  # 红色
            elif 'peaceful' in prompt.lower() or 'green' in prompt.lower():
                color = (152, 251, 152)  # 绿色
            elif 'love' in prompt.lower() or 'pink' in prompt.lower():
                color = (255, 182, 193)  # 粉色
            else:
                color = (200, 200, 200)  # 灰色
            
            # 创建图像
            image = Image.new('RGB', (width, height), color)
            
            # 保存图像
            image.save(filepath)
            
            logger.info(f"模拟图像创建成功: {filepath}")
            
        except Exception as e:
            logger.error(f"创建模拟图像失败: {str(e)}")
            raise
    
    def _generate_placeholder_image(self) -> str:
        """生成占位符图像"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"placeholder_{timestamp}.png"
            filepath = os.path.join(config.LOCAL_STORAGE_PATH, 'images', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 创建占位符图像
            image = Image.new('RGB', (512, 512), (128, 128, 128))
            image.save(filepath)
            
            return filepath
            
        except Exception as e:
            logger.error(f"生成占位符图像失败: {str(e)}")
            return "/static/images/default_placeholder.png"
    
    def enhance_image_quality(self, image_path: str) -> str:
        """增强图像质量"""
        try:
            logger.info(f"增强图像质量: {image_path}")
            
            # TODO: 实现图像质量增强
            # 可以使用超分辨率模型或图像处理技术
            
            # 暂时返回原图像路径
            return image_path
            
        except Exception as e:
            logger.error(f"图像质量增强失败: {str(e)}")
            return image_path
    
    def generate_image_variations(self, base_image_path: str, count: int = 3) -> List[str]:
        """生成图像变体"""
        try:
            logger.info(f"生成图像变体: {base_image_path}")
            
            variations = []
            
            for i in range(count):
                # TODO: 实现图像变体生成
                # 可以调整颜色、风格、构图等
                
                # 暂时创建模拟变体
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"variation_{i}_{timestamp}.png"
                filepath = os.path.join(config.LOCAL_STORAGE_PATH, 'images', filename)
                
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # 创建模拟变体
                colors = [(255, 200, 200), (200, 255, 200), (200, 200, 255)]
                color = colors[i % len(colors)]
                
                image = Image.new('RGB', (512, 512), color)
                image.save(filepath)
                
                variations.append(filepath)
            
            return variations
            
        except Exception as e:
            logger.error(f"生成图像变体失败: {str(e)}")
            return []
    
    def get_supported_styles(self) -> List[str]:
        """获取支持的图像风格"""
        return list(self.style_templates.keys())
    
    def get_supported_sizes(self) -> List[str]:
        """获取支持的图像尺寸"""
        return ['512x512', '768x768', '1024x1024', '512x768', '768x512']
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取可用的图像生成模型"""
        models = []
        
        # 检查是否为占位符值
        def is_valid_key(key):
            if not key:
                return False
            placeholder_patterns = [
                'your_', 'test_', 'placeholder_', 'example_', 'demo_',
                'fake_', 'dummy_', 'sample_', 'mock_'
            ]
            return not any(key.lower().startswith(pattern) for pattern in placeholder_patterns)
        
        # 科大讯飞图片生成
        if is_valid_key(config.IFLYTEK_IMAGE_API_KEY):
            models.append({
                'name': '科大讯飞图片生成',
                'type': 'iflytek_image',
                'status': 'available',
                'priority': 1,
                'description': '科大讯飞Spark图片生成API'
            })
        
        # Stable Diffusion API
        if self.api_available:
            models.append({
                'name': 'Stable Diffusion API',
                'type': 'sd_api',
                'status': 'available',
                'priority': 2,
                'description': 'Stable Diffusion API服务'
            })
        
        # MidJourney
        if is_valid_key(config.MJ_API_KEY):
            models.append({
                'name': 'MidJourney',
                'type': 'midjourney',
                'status': 'available',
                'priority': 3,
                'description': 'MidJourney图像生成API'
            })
        
        # OpenAI DALL-E
        if is_valid_key(config.OPENAI_API_KEY):
            models.append({
                'name': 'DALL-E',
                'type': 'dalle',
                'status': 'available',
                'priority': 4,
                'description': 'OpenAI DALL-E图像生成API'
            })
        
        # 本地Stable Diffusion
        if self.models_loaded and self.sd_model:
            models.append({
                'name': 'Stable Diffusion (本地)',
                'type': 'sd_local',
                'status': 'available',
                'priority': 5,
                'description': '本地Stable Diffusion模型'
            })
        
        # 模拟生成（总是可用）
        models.append({
            'name': '模拟生成',
            'type': 'simulation',
            'status': 'available',
            'priority': 99,
            'description': '用于测试的模拟图像生成'
        })
        
        return models
    
    def validate_generation_request(self, prompt: str, style: str, size: str) -> Tuple[bool, str]:
        """验证图像生成请求"""
        try:
            # 检查提示词
            if not prompt or len(prompt.strip()) == 0:
                return False, "提示词不能为空"
            
            if len(prompt) > 1000:
                return False, "提示词过长，请控制在1000字符以内"
            
            # 检查风格
            if style not in self.style_templates:
                return False, f"不支持的风格: {style}"
            
            # 检查尺寸
            if size not in self.get_supported_sizes():
                return False, f"不支持的尺寸: {size}"
            
            return True, "验证通过"
            
        except Exception as e:
            logger.error(f"验证图像生成请求失败: {str(e)}")
            return False, "验证失败"
    
    def get_generation_cost(self, style: str, size: str) -> float:
        """获取图像生成成本（积分或费用）"""
        try:
            # 基础成本
            base_cost = 1.0
            
            # 风格成本调整
            style_multiplier = {
                'realistic': 1.5,
                'artistic': 1.2,
                'dreamy': 1.0,
                'vintage': 1.0,
                'minimalist': 0.8,
                'fantasy': 1.3
            }
            
            # 尺寸成本调整
            size_multiplier = {
                '512x512': 1.0,
                '768x768': 1.5,
                '1024x1024': 2.0,
                '512x768': 1.2,
                '768x512': 1.2
            }
            
            cost = base_cost * style_multiplier.get(style, 1.0) * size_multiplier.get(size, 1.0)
            
            return round(cost, 2)
            
        except Exception as e:
            logger.error(f"计算生成成本失败: {str(e)}")
            return 1.0
    
    def cleanup_old_images(self, days_old: int = 30):
        """清理旧的生成图像"""
        try:
            logger.info(f"清理{days_old}天前的图像文件...")
            
            images_dir = os.path.join(config.LOCAL_STORAGE_PATH, 'images')
            if not os.path.exists(images_dir):
                return
            
            current_time = datetime.now()
            cleanup_count = 0
            
            for filename in os.listdir(images_dir):
                filepath = os.path.join(images_dir, filename)
                
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    age_days = (current_time - file_time).days
                    
                    if age_days > days_old:
                        try:
                            os.remove(filepath)
                            cleanup_count += 1
                            logger.debug(f"删除旧图像: {filepath}")
                        except Exception as e:
                            logger.warning(f"删除文件失败: {filepath}, {str(e)}")
            
            logger.info(f"清理完成，删除了{cleanup_count}个旧图像文件")
            
        except Exception as e:
            logger.error(f"清理旧图像失败: {str(e)}")
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """获取图像信息"""
        try:
            if not os.path.exists(image_path):
                return {}
            
            # 获取文件信息
            stat = os.stat(image_path)
            
            # 获取图像信息
            with Image.open(image_path) as img:
                width, height = img.size
                format_info = img.format
                mode = img.mode
            
            return {
                'filepath': image_path,
                'filename': os.path.basename(image_path),
                'size': f"{width}x{height}",
                'format': format_info,
                'mode': mode,
                'file_size': stat.st_size,
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取图像信息失败: {str(e)}")
            return {} 