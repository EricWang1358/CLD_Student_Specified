from flask import Blueprint, jsonify, request
from app.services.ai_processor import AIProcessor
from app.utils.file_handler import get_output_filename, append_to_markdown
from app.models.session import chat_history
import os

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    ai_processor = AIProcessor()
    response = ai_processor.process_text(
        message,
        "You are a friendly AI assistant. Please respond concisely and professionally.",
        is_chat=True
    )
    
    return jsonify({
        'response': response.get('choices', [{}])[0].get('message', {}).get('content', ''),
        'remaining_tokens': ai_processor.remaining_tokens
    })

@chat_bp.route('/chat-history', methods=['GET'])
def get_chat_history():
    return jsonify(list(chat_history))

@chat_bp.route('/save-chat', methods=['POST'])
def save_chat():
    try:
        output_filename = get_output_filename("", is_chat=True)
        output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)
        
        chat_content = "# 聊天记录\n\n"
        for msg in chat_history:
            role = "用户" if msg["role"] == "user" else "AI助手"
            chat_content += f"### {role} ({datetime.now().strftime('%H:%M:%S')})\n\n{msg['content']}\n\n"
        
        append_to_markdown(chat_content, output_path, True)
        
        return jsonify({
            'success': True,
            'output_file': output_filename,
            'output_path': output_path
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 