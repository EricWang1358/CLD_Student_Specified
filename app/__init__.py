from flask import Flask, render_template
from config import Config
import logging
import os

def create_app(config_class=Config):
    """
    Flask应用工厂函数
    用途：创建和配置Flask应用实例
    
    Args:
        config_class: 配置类，默认使用Config类
    
    Returns:
        配置完成的Flask应用实例
    """
    # 获取当前文件的绝对路径，用于确定模板目录位置
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 指定模板目录为 app/templates
    template_dir = os.path.join(current_dir, 'templates')
    
    # 创建 Flask 应用实例
    app = Flask(__name__)
    
    # 确保模板目录存在，如果不存在则创建
    # 用于存放前端HTML模板文件
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
        print(f"Created template directory at: {template_dir}")
    else:
        print(f"Template directory exists at: {template_dir}")
    
    # 检查index.html模板文件是否存在
    # 这是应用的主页面模板
    template_file = os.path.join(template_dir, 'index.html')
    if os.path.exists(template_file):
        print(f"Template file exists at: {template_file}")
    else:
        print(f"Template file not found at: {template_file}")
    
    # 从配置类加载配置
    app.config.from_object(config_class)

    # 确保上传和输出目录存在
    # uploads/: 存储上传的PDF文件
    # outputs/: 存储处理结果和导出的文件
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    # 配置日志系统
    # 设置日志级别为INFO，记录到pdf_processing.log文件
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    file_handler = logging.FileHandler('pdf_processing.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 注册蓝图，将不同功能模块的路由注册到应用
    # chat_bp: 处理聊天相关的路由
    # pdf_bp: 处理PDF文件相关的路由
    # token_bp: 处理token计数相关的路由
    from app.routes import chat_bp, pdf_bp, token_bp
    app.register_blueprint(chat_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(token_bp)

    # 添加根路由，处理主页访问
    # 在前端请求 '/' 时调用
    @app.route('/')
    def index():
        try:
            return render_template('index.html')
        except Exception as e:
            # 如果模板渲染失败，打印详细错误信息
            print(f"Error rendering template: {str(e)}")
            print(f"Template folders: {app.jinja_loader.searchpath}")
            raise

    return app 