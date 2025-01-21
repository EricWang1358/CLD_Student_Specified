import os
from datetime import datetime

def get_output_filename(original_filename, is_chat=False):
    """
    生成输出文件名
    
    Args:
        original_filename: 原始文件名（PDF处理时使用）
        is_chat: 是否为聊天记录文件
    
    Returns:
        str: 格式化的输出文件名（包含日期）
    
    用途：
    - 在PDF处理时生成输出文件名（app/routes/pdf.py）
    - 在保存聊天记录时生成文件名（app/routes/chat.py）
    """
    today = datetime.now().strftime('%Y%m%d')
    if is_chat:
        return f"{today}_chat.md"
    else:
        base_name = original_filename.rsplit('.', 1)[0]
        return f"{today}_{base_name}.md"

def append_to_markdown(content, filepath, is_new_section=False):
    """
    追加内容到markdown文件
    
    Args:
        content: 要写入的内容
        filepath: 目标文件路径
        is_new_section: 是否添加分隔符和时间戳
    
    Returns:
        str: 写入内容的文件路径
    
    用途：
    - 保存PDF处理结果（app/routes/pdf.py）
    - 保存聊天记录（app/routes/chat.py）
    """
    # 确保目标目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # 如果是新章节，添加分隔符和时间戳
    if is_new_section:
        content = f"\n\n---\n### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{content}"
    
    # 追加内容到文件
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)
    
    return filepath 