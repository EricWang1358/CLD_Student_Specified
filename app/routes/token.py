from flask import Blueprint, jsonify, current_app
from datetime import datetime
from app.models.session import chat_history

# 创建token蓝图，用于管理token相关路由
token_bp = Blueprint('token', __name__)

# 记录上次token更新时间，用于控制日志频率
last_token_update = datetime.now()
# 初始token数量
remaining_tokens = 1000000

@token_bp.route('/token-status', methods=['GET'])
def get_token_status():
    """
    获取token使用状态
    用途：返回当前token使用情况，包括剩余数量和使用百分比
    在前端通过定时请求获取最新token状态
    """
    try:
        global last_token_update
        current_time = datetime.now()
        
        # 控制日志记录频率，避免日志文件过大
        should_log = (current_time - last_token_update).total_seconds() > 30
        
        if should_log:
            last_token_update = current_time
        
        # 计算token使用情况
        max_tokens = 1000000
        usage_percentage = round((max_tokens - remaining_tokens) / max_tokens * 100, 1)
        
        # 计算最近10条消息的token使用量
        recent_usage = sum(msg.get('tokens_used', 0) for msg in list(chat_history)[-10:])
        
        return jsonify({
            'remaining_tokens': remaining_tokens,
            'max_tokens': max_tokens,
            'usage_percentage': usage_percentage,
            'recent_usage': recent_usage,
            'last_updated': current_time.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@token_bp.route('/reset-tokens', methods=['POST'])
def reset_tokens():
    """
    重置token计数
    用途：将token计数重置为初始值
    在需要手动重置token计数时通过前端调用
    """
    try:
        global remaining_tokens
        remaining_tokens = 1000000
        return jsonify({
            'success': True,
            'remaining_tokens': remaining_tokens
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 