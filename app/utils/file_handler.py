import os
from datetime import datetime

def get_output_filename(original_filename, is_chat=False):
    """生成输出文件名"""
    today = datetime.now().strftime('%Y%m%d')
    if is_chat:
        return f"{today}_chat.md"
    else:
        base_name = original_filename.rsplit('.', 1)[0]
        return f"{today}_{base_name}.md"

def append_to_markdown(content, filepath, is_new_section=False):
    """追加内容到markdown文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    if is_new_section:
        content = f"\n\n---\n### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{content}"
    
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)
    
    return filepath 