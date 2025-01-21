from flask import Blueprint, jsonify, request, Response, current_app, session
from app.services.ai_processor import AIProcessor
from app.utils.file_handler import get_output_filename, append_to_markdown
from app.models.session import chat_history, add_to_history
import os
import json
import logging
from datetime import datetime
from app.utils.prompt_manager import PromptManager
import traceback

# 创建日志记录器
logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

# 创建提示管理器实例
prompt_manager = PromptManager()

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        logger.info("="*50)
        logger.info("新的聊天请求")
        logger.info(f"用户消息: {message}")
        
        current_prompt = session.get('current_prompt', "你是一个友好的AI助手，请用简洁专业的方式回答问题。")
        
        processor = AIProcessor()
        response = processor.process_text(message, current_prompt, is_chat=True)
        
        if 'error' in response:
            logger.error(f"处理消息时出错: {response['error']}")
            return jsonify({'error': response['error']}), 500
            
        content = response['content']  # 不再尝试从 choices 中获取
        logger.info(f"AI回复: {content}")
        
        # 添加消息到聊天历史
        add_to_history('user', message)
        add_to_history('assistant', content)
        
        logger.info("聊天历史已更新")
        logger.info("="*50)
        
        return jsonify({
            'response': content
        })
        
    except Exception as e:
        logger.error("="*50)
        logger.error(f"聊天错误: {str(e)}")
        logger.error(f"错误追踪: {traceback.format_exc()}")
        logger.error("="*50)
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chat-history', methods=['GET'])
def get_chat_history():
    return jsonify(list(chat_history))

@chat_bp.route('/save-chat', methods=['POST'])
def save_chat():
    try:
        # 确保输出目录存在
        output_dir = current_app.config.get('OUTPUT_FOLDER', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = get_output_filename("", is_chat=True)
        output_path = os.path.join(output_dir, output_filename)
        
        chat_content = "# 聊天记录\n\n"
        for msg in chat_history:
            role = "用户" if msg["role"] == "user" else "AI助手"
            chat_content += f"### {role}\n\n{msg['content']}\n\n"
        
        append_to_markdown(chat_content, output_path, True)
        
        return jsonify({
            'success': True,
            'output_file': output_filename,
            'output_path': output_path
        })
    except Exception as e:
        logger.error(f"Failed to save chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/test-api', methods=['GET'])
def test_api():
    """测试API连接"""
    processor = AIProcessor()
    result = processor.test_api()
    return jsonify(result)

@chat_bp.route('/prompts', methods=['GET'])
def get_prompts():
    """获取所有提示模板"""
    try:
        prompts = prompt_manager.get_all_prompts()
        return jsonify(prompts)
    except Exception as e:
        logger.error(f"Failed to get prompts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/update-prompt', methods=['POST'])
def update_prompt():
    """更新当前使用的提示"""
    try:
        data = request.get_json()
        prompt_id = data.get('promptId')
        
        # 获取所有提示
        prompts = prompt_manager.get_all_prompts()
        
        # 查找选中的提示
        selected_prompt = next((p for p in prompts if p['id'] == prompt_id), None)
        if not selected_prompt:
            return jsonify({'error': 'Prompt not found'}), 404
            
        # 存储到会话中
        session['current_prompt'] = selected_prompt['prompt']
        session['current_prompt_id'] = prompt_id
        
        return jsonify({
            'success': True,
            'prompt': selected_prompt['prompt']
        })
        
    except Exception as e:
        logger.error(f"Failed to update prompt: {str(e)}")
        return jsonify({'error': str(e)}), 500 