from collections import deque
from datetime import datetime

# 使用deque限制历史记录数量
chat_history = deque(maxlen=100)

def add_to_history(role, content, tokens_used=0):
    """添加消息到聊天历史"""
    chat_history.append({
        'role': role,
        'content': content,
        'tokens_used': tokens_used,
        'timestamp': datetime.now().isoformat()
    }) 