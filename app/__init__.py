from flask import Flask, render_template
from config import Config
import logging
import os

def create_app(config_class=Config):
    # 获取当前文件的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 指定模板目录为 app/templates
    template_dir = os.path.join(current_dir, 'templates')
    
    # 创建 Flask 应用
    app = Flask(__name__)
    
    # 确保模板目录存在
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
        print(f"Created template directory at: {template_dir}")
    else:
        print(f"Template directory exists at: {template_dir}")
    
    # 检查模板文件是否存在
    template_file = os.path.join(template_dir, 'index.html')
    if os.path.exists(template_file):
        print(f"Template file exists at: {template_file}")
    else:
        print(f"Template file not found at: {template_file}")
    
    app.config.from_object(config_class)

    # 确保上传和输出目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    file_handler = logging.FileHandler('pdf_processing.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 注册蓝图
    from app.routes import chat_bp, pdf_bp, token_bp
    app.register_blueprint(chat_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(token_bp)

    # 添加根路由
    @app.route('/')
    def index():
        try:
            return render_template('index.html')
        except Exception as e:
            print(f"Error rendering template: {str(e)}")
            print(f"Template folders: {app.jinja_loader.searchpath}")
            raise

    return app 