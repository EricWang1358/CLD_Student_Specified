import os

def check_project_structure():
    """
    检查项目文件结构完整性
    
    用途：
    - 验证所有必需的目录和文件是否存在
    - 帮助诊断项目设置问题
    - 在部署前进行完整性检查
    
    检查项目：
    - 模板文件 (app/templates/index.html)
    - 初始化文件 (app/__init__.py)
    - 路由文件 (app/routes/__init__.py)
    - 配置文件 (config.py)
    - 启动文件 (run.py)
    """
    # 获取项目根目录的绝对路径
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义需要检查的关键文件和描述
    checks = [
        ('app/templates/index.html', 'Template file'),
        ('app/__init__.py', 'Init file'),
        ('app/routes/__init__.py', 'Routes init'),
        ('config.py', 'Config file'),
        ('run.py', 'Run file')
    ]
    
    print("Checking project structure...")
    print(f"Project root: {root_dir}")
    
    # 检查每个文件是否存在
    all_good = True
    for path, desc in checks:
        full_path = os.path.join(root_dir, path)
        exists = os.path.exists(full_path)
        print(f"{desc}: {'✓' if exists else '✗'} ({path})")
        if not exists:
            all_good = False
    
    # 输出检查结果
    if all_good:
        print("\nAll files are in place!")
    else:
        print("\nSome files are missing!")

if __name__ == "__main__":
    """
    脚本入口点
    
    使用方法：
    python check_structure.py
    
    用途：
    - 在项目设置后验证结构
    - 在遇到导入或路径问题时进行诊断
    - 在部署前进行检查
    """
    check_project_structure() 