import os

def check_project_structure():
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查关键目录和文件
    checks = [
        ('app/templates/index.html', 'Template file'),
        ('app/__init__.py', 'Init file'),
        ('app/routes/__init__.py', 'Routes init'),
        ('config.py', 'Config file'),
        ('run.py', 'Run file')
    ]
    
    print("Checking project structure...")
    print(f"Project root: {root_dir}")
    
    all_good = True
    for path, desc in checks:
        full_path = os.path.join(root_dir, path)
        exists = os.path.exists(full_path)
        print(f"{desc}: {'✓' if exists else '✗'} ({path})")
        if not exists:
            all_good = False
    
    if all_good:
        print("\nAll files are in place!")
    else:
        print("\nSome files are missing!")

if __name__ == "__main__":
    check_project_structure() 