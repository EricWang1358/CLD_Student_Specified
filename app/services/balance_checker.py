import requests
import logging
from flask import current_app
import json
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)

class BalanceChecker:
    """
    API余额查询服务
    用于查询 xiaoai.plus 的 API 余额
    """
    def __init__(self):
        self.base_url = "https://query.xiaoai.plus"
        self.api_key = current_app.config['API_KEY']
        if not self.api_key:
            raise ValueError("API key not found in configuration")
        logger.debug(f"Initialized BalanceChecker with API key: {self.api_key[:8]}...")

    def check_balance(self):
        """查询API余额和使用记录"""
        try:
            if not hasattr(self, 'base_url') or not hasattr(self, 'api_key'):
                raise AttributeError("Required attributes not initialized")
            
            # 直接使用完整的API key
            params = {
                "key": self.api_key
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Referer": "https://query.xiaoai.plus/",
                "Origin": "https://query.xiaoai.plus",
                "Connection": "keep-alive"
            }
            
            # 先尝试获取余额信息
            quota_url = f"{self.base_url}/quota"
            try:
                logger.debug(f"Sending quota request to: {quota_url}")
                logger.debug(f"With params: {params}")
                logger.debug(f"With headers: {headers}")
                
                quota_response = requests.get(
                    quota_url,
                    params=params,
                    headers=headers,
                    timeout=10,
                    verify=True  # 确保 SSL 验证
                )
                
                # 打印完整的请求和响应信息
                logger.debug(f"Full URL called: {quota_response.url}")
                logger.debug(f"Response status: {quota_response.status_code}")
                logger.debug(f"Response headers: {dict(quota_response.headers)}")
                logger.debug(f"Raw response: {quota_response.text}")
                
                if quota_response.status_code == 200:
                    try:
                        quota_data = quota_response.json()
                        # 如果成功获取余额，再获取日志
                        logs_url = f"{self.base_url}/logs"
                        logs_response = requests.get(
                            logs_url,
                            params={**params, "p": 1, "page_size": 10, "type": "all"},
                            headers=headers,
                            timeout=10
                        )
                        
                        logs_data = logs_response.json() if logs_response.status_code == 200 else {"data": []}
                        
                        result = {
                            'success': True,
                            'balance': {
                                'id': quota_data.get('id'),
                                'user_id': quota_data.get('user_id'),
                                'key': quota_data.get('key', '')[:11] + '...',
                                'status': quota_data.get('status'),
                                'name': quota_data.get('name'),
                                'quota': quota_data.get('quota', 0),
                                'used': quota_data.get('used', 0)
                            },
                            'recent_logs': logs_data.get('data', []),
                            'last_updated': datetime.now().isoformat()
                        }
                        
                        return result
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse quota response: {str(e)}")
                        logger.error(f"Response content: {quota_response.text}")
                        return {
                            'success': False,
                            'error': f"Invalid quota response format: {str(e)}"
                        }
                else:
                    error_msg = f"Quota API error {quota_response.status_code}: {quota_response.text}"
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg
                    }
                
            except requests.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
                return {
                    'success': False,
                    'error': f"Request failed: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            } 