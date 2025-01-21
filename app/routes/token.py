from flask import Blueprint, jsonify, current_app
from datetime import datetime
from app.models.session import chat_history
from app.services.ai_processor import AIProcessor
from app.services.balance_checker import BalanceChecker
import logging
import json
import traceback

# 创建token蓝图，用于管理token相关路由
token_bp = Blueprint('token', __name__)

# 记录上次token更新时间，用于控制日志频率
last_token_update = datetime.now()
# 初始token数量
remaining_tokens = 1000000

logger = logging.getLogger(__name__)

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
        max_tokens = 100000
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

@token_bp.route('/verify-api-key', methods=['GET'])
def verify_api_key():
    """验证API密钥是否有效"""
    try:
        ai_processor = AIProcessor()
        response = ai_processor.process_text(
            "test",
            "This is a test message",
            is_chat=True
        )
        
        if 'error' in response:
            return jsonify({
                'valid': False,
                'error': response['error']
            })
            
        return jsonify({
            'valid': True,
            'message': 'API key is valid'
        })
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 500

@token_bp.route('/test-api', methods=['GET'])
def test_api():
    """测试API连接"""
    try:
        ai_processor = AIProcessor()
        test_response = ai_processor.process_text(
            "Hello",
            "Please respond with 'API test successful' if you receive this message.",
            is_chat=True
        )
        
        if 'error' in test_response:
            logger.error(f"API test failed: {test_response['error']}")
            return jsonify({
                'success': False,
                'error': test_response['error']
            }), 500
            
        return jsonify({
            'success': True,
            'response': test_response
        })
        
    except Exception as e:
        logger.error(f"API test error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@token_bp.route('/check-balance', methods=['GET'])
def check_balance():
    """查询API余额"""
    try:
        checker = BalanceChecker()
        result = checker.check_balance()
        
        if result['success']:
            return jsonify({
                'success': True,
                'balance': result['balance'],
                'total_used': result['total_used'],
                'last_updated': result['last_updated']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Balance check error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@token_bp.route('/test-balance', methods=['GET'])
def test_balance():
    """测试余额查询功能"""
    try:
        checker = BalanceChecker()
        result = checker.check_balance()
        
        # 打印详细信息到日志
        logger.info(f"Balance check test result: {json.dumps(result, indent=2)}")
        
        return jsonify({
            'success': True,
            'test_result': result,
            'api_key_used': checker.api_key[:8] + '...'  # 只显示前8位
        })
    except Exception as e:
        logger.error(f"Balance check test error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@token_bp.route('/test-balance-detailed', methods=['GET'])
def test_balance_detailed():
    """详细测试余额查询功能"""
    try:
        # 创建测试实例
        checker = BalanceChecker()
        
        # 记录测试信息
        logger.info(f"Testing balance check with API key: {checker.api_key[:8]}...")
        logger.info(f"Using base URL: {checker.base_url}")  # 使用 base_url 而不是 query_url
        
        # 发送请求并获取结果
        result = checker.check_balance()
        
        # 返回详细信息
        return jsonify({
            'success': True,
            'test_info': {
                'api_key_prefix': checker.api_key[:8],
                'base_url': checker.base_url  # 使用 base_url
            },
            'test_result': result
        })
        
    except Exception as e:
        logger.error(f"Detailed balance test error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@token_bp.route('/test-selenium', methods=['GET'])
def test_selenium():
    """使用Selenium测试余额查询"""
    try:
        checker = BalanceChecker()
        result = checker.check_balance()
        
        return jsonify({
            'success': True,
            'message': 'Selenium test completed',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Selenium test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 