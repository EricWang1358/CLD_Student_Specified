from collections import deque

# 设置聊天历史记录的最大长度
# 用于限制内存使用和保持对话上下文的相关性
MAX_HISTORY = 20

# 使用双端队列存储聊天历史
# 当历史记录超过MAX_HISTORY时，自动移除最早的消息
# 在 app/routes/chat.py 中被用于存储和管理聊天记录
chat_history = deque(maxlen=MAX_HISTORY) 