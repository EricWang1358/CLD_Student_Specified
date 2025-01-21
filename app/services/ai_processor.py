import requests
import json
from flask import current_app
import logging
from app.models.session import chat_history
import time
import traceback

logger = logging.getLogger(__name__)

class AIProcessor:
    """
    AI处理服务类
    用途：处理与Claude API的所有交互
    
    主要功能：
    - 处理聊天消息
    - 处理PDF文本内容
    - 追踪token使用情况
    
    被调用位置：
    - app/routes/chat.py: 处理聊天请求
    - app/routes/pdf.py: 处理PDF文本转换
    """

    def __init__(self):
        """
        初始化AI处理器
        
        设置：
        - API端点
        - 认证信息
        - Token计数器
        """
        # 使用 xiaoai.plus 的 API
        self.url = "https://api.xiaoai.plus/v1/chat/completions"
        self.api_key = current_app.config['API_KEY']
        
        if not self.api_key:
            raise ValueError("API_KEY not found in environment variables")
        
        # 使用正确的请求头格式
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"  # 使用 Bearer token
        }

    def process_text(self, text, instruction, is_chat=False):
        """处理文本请求"""
        try:
            if is_chat:
                logger.info("-"*30 + " API请求开始 " + "-"*30)
                logger.info(f"用户输入: {text[:100]}...")
            else:
                logger.info("-"*30 + " PDF处理开始 " + "-"*30)
                logger.info(f"处理PDF文本 (长度: {len(text)} 字符)")
            
            payload = {
                "model": "claude-3-opus-20240229",
                "messages": [
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            }
            
            logger.debug(f"请求内容: {json.dumps(payload, ensure_ascii=False)}")
            
            max_retries = 5
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    logger.info(f"发送API请求 (第 {retry_count + 1}/{max_retries} 次尝试)")
                    response = requests.post(
                        self.url,
                        headers=self.headers,
                        json=payload,
                        timeout=(30, 120),  # 增加连接超时和读取超时时间
                        verify=True
                    )
                    
                    logger.debug(f"Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                        logger.info(f"AI响应: {content[:100]}...")
                        
                        usage = response_data.get('usage', {})
                        logger.info(f"Token使用情况:")
                        logger.info(f"  - 提示tokens: {usage.get('prompt_tokens', 0)}")
                        logger.info(f"  - 回复tokens: {usage.get('completion_tokens', 0)}")
                        logger.info(f"  - 总计tokens: {usage.get('total_tokens', 0)}")
                        logger.info("-"*30 + " API请求结束 " + "-"*30)
                        
                        return response_data
                        
                    elif response.status_code == 408:
                        logger.warning(f"请求超时 (第 {retry_count + 1}/{max_retries} 次尝试)")
                        retry_count += 1
                        if retry_count == max_retries:
                            raise TimeoutError("API request timed out after multiple retries")
                        time.sleep(2)  # 增加重试等待时间
                    else:
                        error_msg = f"API request failed: {response.text}"
                        logger.error(error_msg)
                        return {"error": error_msg}
                        
                except (requests.Timeout, requests.ConnectionError) as e:
                    logger.warning(f"请求失败 (第 {retry_count + 1}/{max_retries} 次尝试): {str(e)}")
                    retry_count += 1
                    if retry_count == max_retries:
                        error_msg = "API request timed out after multiple retries"
                        logger.error(error_msg)
                        return {"error": error_msg}
                    time.sleep(2)  # 增加重试等待时间
                except requests.RequestException as e:
                    error_msg = f"Request failed: {str(e)}"
                    logger.error(error_msg)
                    return {"error": error_msg}
            
        except Exception as e:
            logger.error("-"*30 + " 错误信息 " + "-"*30)
            logger.error(f"处理请求时出错: {str(e)}")
            logger.error(f"错误追踪: {traceback.format_exc()}")
            logger.error("-"*30 + " 错误结束 " + "-"*30)
            return {"error": str(e)}

    def test_api(self):
        """测试API连接和响应"""
        try:
            test_payload = {
                "model": "claude-3-opus-20240229",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, are you working?"
                    }
                ]
            }
            
            logger.info("Making test API request...")
            response = requests.post(
                self.url,
                headers=self.headers,
                json=test_payload,
                timeout=10
            )
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            logger.info(f"Response body: {response.text}")
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text
            }
            
        except Exception as e:
            logger.error(f"Test API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 