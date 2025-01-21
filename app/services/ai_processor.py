import requests
import json
from flask import current_app
import logging
from app.models.session import chat_history

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        self.url = "https://xiaoai.plus/v1/chat/completions"
        self.api_key = current_app.config['API_KEY']
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.remaining_tokens = 1000000

    def process_text(self, text, instruction, is_chat=False):
        try:
            logger.info(f"Starting {'chat' if is_chat else 'PDF'} request processing")
            logger.debug(f"Input text length: {len(text)} characters")
            
            payload = json.dumps({
                "messages": [
                    {
                        "role": "system",
                        "content": instruction
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.7,
                "presence_penalty": 0,
                "frequency_penalty": 0,
                "top_p": 1
            })
            
            logger.debug("Sending API request")
            response = requests.post(self.url, headers=self.headers, data=payload)
            response_data = response.json()
            
            if 'error' in response_data:
                logger.error(f"API returned error: {response_data['error']}")
                return response_data
            
            usage = response_data.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            logger.info(f"Token usage - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")
            
            if total_tokens > 0:
                self.remaining_tokens -= total_tokens
                logger.info(f"Updated remaining tokens: {self.remaining_tokens}")
            else:
                estimated_tokens = len(text) // 4
                self.remaining_tokens -= estimated_tokens
                logger.warning(f"No token info from API, estimated usage: {estimated_tokens} tokens")
            
            if is_chat:
                chat_content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                if not chat_content:
                    logger.warning("Empty response content from API")
                    chat_content = "Sorry, I couldn't generate a response. Please try again."
                
                chat_history.append({
                    "role": "user",
                    "content": text,
                    "tokens_used": prompt_tokens
                })
                chat_history.append({
                    "role": "assistant",
                    "content": chat_content,
                    "tokens_used": completion_tokens
                })
                logger.info("Chat history updated")
            
            return response_data
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {"error": str(e)} 