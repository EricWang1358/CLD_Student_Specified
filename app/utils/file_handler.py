import os
from datetime import datetime

def get_output_filename(prefix="", is_chat=False):
    """
    生成输出文件名
    
    Args:
        prefix: 前缀（PDF处理时使用）
        is_chat: 是否为聊天记录文件
    
    Returns:
        str: 格式化的输出文件名（包含日期和时间）
    
    用途：
    - 在PDF处理时生成输出文件名（app/routes/pdf.py）
    - 在保存聊天记录时生成文件名（app/routes/chat.py）
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if is_chat:
        return f"chat_{timestamp}.md"
    return f"{prefix}_{timestamp}.md" if prefix else f"output_{timestamp}.md"

def append_to_markdown(content, filepath, create_new=False):
    """
    写入或追加内容到Markdown文件
    
    Args:
        content: 要写入的内容
        filepath: 目标文件路径
        create_new: 是否创建新文件
    
    Returns:
        str: 写入内容的文件路径
    
    用途：
    - 保存PDF处理结果（app/routes/pdf.py）
    - 保存聊天记录（app/routes/chat.py）
    """
    mode = 'w' if create_new else 'a'
    with open(filepath, mode, encoding='utf-8') as f:
        f.write(content)
    
    return filepath 