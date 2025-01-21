from app import create_app

# 创建Flask应用实例
# create_app函数在app/__init__.py中定义
app = create_app()

if __name__ == '__main__':
    """
    应用入口点
    用途：启动Flask开发服务器
    
    启动方式：
    1. 直接运行: python run.py
    2. Flask命令: flask run (需要设置FLASK_APP环境变量)
    
    开发模式下：
    - 启用调试模式
    - 代码修改后自动重载
    - 详细的错误页面
    """
    app.run(debug=True) 