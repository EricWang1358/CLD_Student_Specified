import os
from dotenv import load_dotenv
import requests
import logging

# 加载.env文件中的环境变量
# 主要用于加载API密钥等敏感信息
load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    """
    应用配置类
    用途：集中管理应用的所有配置项
    在 app/__init__.py 中被用于初始化Flask应用
    """
    # PDF文件上传目录
    UPLOAD_FOLDER = 'uploads'
    # 处理结果输出目录
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', os.path.join(os.getcwd(), 'output'))
    # 限制上传文件大小为16MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # 从环境变量获取API密钥
    API_KEY = os.getenv('API_KEY', '').strip()
    if not API_KEY:
        raise ValueError("API_KEY must be set in .env file")
    
    # 添加 Flask session 密钥
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    
    @classmethod
    def init_app(cls, app):
        """初始化应用配置"""
        # 确保必要的目录存在
        os.makedirs(cls.OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        
        # 设置 Flask secret key
        app.config['SECRET_KEY'] = cls.SECRET_KEY
        
        # 验证API密钥格式
        if not cls.API_KEY.startswith('sk-'):
            raise ValueError("API_KEY must start with 'sk-'")
        
        logger.info("Application initialized with API key format verified")

    @classmethod
    def validate_api_key(cls):
        """验证API密钥格式"""
        if not cls.API_KEY:
            raise ValueError("API_KEY must be set in .env file")

    PDF_UPLOAD_FOLDER = os.getenv('PDF_UPLOAD_FOLDER', os.path.join(os.getcwd(), 'uploads')) 