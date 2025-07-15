# -*- coding: utf-8 -*-
"""
PGG情感记忆生成系统 - 服务器启动脚本
快速启动Flask服务器
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """检查依赖包"""
    logger = logging.getLogger(__name__)
    
    try:
        import flask
        import pymongo
        import requests
        import numpy
        import PIL
        logger.info("✅ 核心依赖包检查通过")
        return True
    except ImportError as e:
        logger.error(f"❌ 缺少依赖包: {e}")
        logger.error("请运行: pip install -r requirements.txt")
        return False

def create_directories():
    """创建必要的目录"""
    logger = logging.getLogger(__name__)
    
    directories = [
        'storage',
        'storage/images',
        'logs',
        'models',
        'models/whisper',
        'models/wav2vec2',
        'models/ecapa',
        'models/stable_diffusion'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"创建目录: {directory}")
    
    logger.info("✅ 目录结构检查完成")

def check_config():
    """检查配置文件"""
    logger = logging.getLogger(__name__)
    
    # 检查.env文件
    env_file = '.env'
    template_file = 'environment_config.template'
    
    if not os.path.exists(env_file):
        if os.path.exists(template_file):
            logger.warning(f"❌ 未找到{env_file}文件")
            logger.info(f"请复制{template_file}为{env_file}并配置相应的参数")
            return False
        else:
            logger.warning("配置文件不存在，将使用默认配置")
            return True
    
    logger.info("✅ 配置文件检查通过")
    return True

def show_system_info():
    """显示系统信息"""
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("🎨 PGG情感记忆生成系统")
    logger.info("=" * 60)
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Python版本: {sys.version.split()[0]}")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info("=" * 60)

def show_usage_instructions():
    """显示使用说明"""
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 服务器启动成功!")
    logger.info("")
    logger.info("📋 API接口说明:")
    logger.info("  - 健康检查: GET  http://localhost:5000/health")
    logger.info("  - 生成回忆: POST http://localhost:5000/generate")
    logger.info("  - 历史记录: GET  http://localhost:5000/history")
    logger.info("  - 回忆详情: GET  http://localhost:5000/memory/<id>")
    logger.info("  - 用户统计: GET  http://localhost:5000/stats")
    logger.info("  - 语音转文本: POST http://localhost:5000/speech-to-text")
    logger.info("  - 语音服务状态: GET http://localhost:5000/speech-to-text/status")
    logger.info("")
    logger.info("📖 使用示例:")
    logger.info("  curl -X POST http://localhost:5000/generate \\")
    logger.info("       -H 'Content-Type: application/json' \\")
    logger.info("       -d '{\"text\":\"今天是美好的一天\", \"user_id\":\"user123\"}'")
    logger.info("")
    logger.info("💡 提示:")
    logger.info("  - 首次运行使用本地存储模式")
    logger.info("  - 配置API密钥以使用第三方服务")
    logger.info("  - 按 Ctrl+C 停止服务器")
    logger.info("")

def main():
    """主函数"""
    logger = setup_logging()
    
    show_system_info()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 创建目录
    create_directories()
    
    # 检查配置
    if not check_config():
        logger.error("配置检查失败，请检查配置文件")
        sys.exit(1)
    
    # 显示使用说明
    show_usage_instructions()
    
    try:
        # 启动Flask应用
        logger.info("正在启动Flask服务器...")
        
        # 导入并运行app
        from app import app, init_application
        
        # 初始化应用
        init_application()
        
        # 启动服务器
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭服务器...")
        logger.info("👋 感谢使用PGG情感记忆生成系统!")
        
    except Exception as e:
        logger.error(f"启动失败: {str(e)}")
        logger.error("请检查错误信息并重试")
        sys.exit(1)

if __name__ == '__main__':
    main() 