import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
# 主要用于加载API密钥等敏感信息
load_dotenv()

class Config:
    """
    应用配置类
    用途：集中管理应用的所有配置项
    在 app/__init__.py 中被用于初始化Flask应用
    """
    # PDF文件上传目录
    UPLOAD_FOLDER = 'uploads'
    # 处理结果输出目录
    OUTPUT_FOLDER = 'outputs'
    # 限制上传文件大小为16MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    # 从环境变量获取API密钥
    API_KEY = os.getenv('API_KEY') 