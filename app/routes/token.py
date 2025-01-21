from flask import Blueprint, jsonify, current_app
from datetime import datetime
from app.models.session import chat_history

token_bp = Blueprint('token', __name__)

last_token_update = datetime.now()
remaining_tokens = 1000000

@token_bp.route('/token-status', methods=['GET'])
def get_token_status():
    try:
        global last_token_update
        current_time = datetime.now()
        
        should_log = (current_time - last_token_update).total_seconds() > 30
        
        if should_log:
            last_token_update = current_time
        
        max_tokens = 1000000
        usage_percentage = round((max_tokens - remaining_tokens) / max_tokens * 100, 1)
        
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
    try:
        global remaining_tokens
        remaining_tokens = 1000000
        return jsonify({
            'success': True,
            'remaining_tokens': remaining_tokens
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 