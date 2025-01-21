from collections import deque

# 聊天历史记录
MAX_HISTORY = 20
chat_history = deque(maxlen=MAX_HISTORY) 