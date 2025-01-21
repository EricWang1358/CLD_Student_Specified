import requests
import json
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import fitz  # type: ignore # PyMuPDF库用于处理PDF
from datetime import datetime
from collections import deque
import logging
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.config['MAX_HISTORY'] = 20  # 保存最近20条消息
chat_history = deque(maxlen=app.config['MAX_HISTORY'])
remaining_tokens = 1000000  # 初始token数，实际应该从API获取

# 确保上传和输出目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建文件处理器
file_handler = logging.FileHandler('pdf_processing.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 添加一个变量来追踪上次token更新时间
last_token_update = datetime.now()

class AIProcessor:
    def __init__(self, api_key):
        self.url = "https://xiaoai.plus/v1/chat/completions"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def process_text(self, text, instruction, is_chat=False):
        try:
            global remaining_tokens  # 在函数开始就声明global
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
                remaining_tokens -= total_tokens
                logger.info(f"Updated remaining tokens: {remaining_tokens}")
            else:
                estimated_tokens = len(text) // 4
                remaining_tokens -= estimated_tokens
                logger.warning(f"No token info from API, estimated usage: {estimated_tokens} tokens")
            
            if is_chat:
                chat_content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                if not chat_content:  # 检查回复内容是否为空
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

def process_pdf(file_path):
    """Process PDF file and extract text"""
    logger.info(f"Starting PDF processing: {file_path}")
    doc = fitz.open(file_path)
    text_content = []
    
    try:
        total_pages = len(doc)
        logger.info(f"Total PDF pages: {total_pages}")
        
        for page_num, page in enumerate(doc, 1):
            logger.debug(f"Processing page {page_num}/{total_pages}")
            text = page.get_text()
            text_content.append(text)
            logger.debug(f"Page {page_num} extracted {len(text)} characters")
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise
    finally:
        doc.close()
        logger.info("PDF processing completed")
    
    return text_content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logger.warning("No file uploaded")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.warning("No file selected")
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            logger.info(f"File saved: {file_path}")
            
            text_content = process_pdf(file_path)
            total_pages = len(text_content)
            
            ai_processor = AIProcessor("sk-LtHl3eFXpPn1HwbZ0LNVyRUJ0WlbaKvyl5gMsb6FODhBEw0X")
            processed_content = []
            
            for index, page_text in enumerate(text_content, 1):
                logger.info(f"AI processing page {index}/{total_pages}")
                try:
                    result = ai_processor.process_text(
                        page_text,
                        "Please convert this text into detailed markdown notes with headings, key points, and additional notes."
                    )
                    processed_content.append(result)
                    logger.debug(f"Page {index} AI processing completed")
                except Exception as e:
                    logger.error(f"Error processing page {index} with AI: {str(e)}")
                    raise
            
            output_filename = f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for content in processed_content:
                    f.write(content + '\n\n')
            logger.info(f"Results saved to: {output_path}")
            
            return jsonify({
                'success': True,
                'message': 'File processed successfully',
                'output_file': output_filename,
                'total_pages': total_pages
            })
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    logger.warning(f"Unsupported file type: {file.filename}")
    return jsonify({'error': 'Invalid file type'}), 400

# 添加进度查询端点
@app.route('/progress', methods=['GET'])
def get_progress():
    # 这里可以实现进度存储和查询逻辑
    return jsonify({
        'current_page': current_page,
        'total_pages': total_pages,
        'percentage': percentage
    })

# 添加新的路由处理聊天功能
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    if not message:
        logger.warning("Empty message received")
        return jsonify({'error': 'No message provided'}), 400
    
    logger.info("New chat request received")
    logger.debug(f"Message length: {len(message)} characters")
    
    try:
        ai_processor = AIProcessor("sk-LtHl3eFXpPn1HwbZ0LNVyRUJ0WlbaKvyl5gMsb6FODhBEw0X")
        response = ai_processor.process_text(
            message,
            "You are a friendly AI assistant. Please respond concisely and professionally.",
            is_chat=True
        )
        
        if 'error' in response:
            logger.error(f"Error processing chat message: {response['error']}")
            return jsonify({'error': response['error']}), 500
        
        response_content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        if not response_content:
            logger.warning("Empty response from API")
            return jsonify({'error': 'No response from AI'}), 500
            
        logger.info("Chat response generated")
        logger.debug(f"Response length: {len(response_content)} characters")
        
        return jsonify({
            'response': response_content,
            'remaining_tokens': remaining_tokens
        })
    except Exception as e:
        logger.error(f"Exception in chat request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat-history', methods=['GET'])
def get_chat_history():
    return jsonify(list(chat_history))

# 添加新的路由用于获取token状态
@app.route('/token-status', methods=['GET'])
def get_token_status():
    try:
        global last_token_update
        current_time = datetime.now()
        
        # 只有在以下情况下才记录日志：
        # 1. 距离上次更新超过30秒
        # 2. token数量发生变化
        # 3. 出现错误
        should_log = (current_time - last_token_update).total_seconds() > 30
        
        if should_log:
            logger.info("Checking token status")  # 改为INFO级别
            last_token_update = current_time
        
        max_tokens = 1000000
        usage_percentage = round((max_tokens - remaining_tokens) / max_tokens * 100, 1)
        
        recent_usage = sum(msg.get('tokens_used', 0) for msg in list(chat_history)[-10:])
        
        if remaining_tokens < 100000:
            logger.warning(f"Low token balance: {remaining_tokens}")
        
        return jsonify({
            'remaining_tokens': remaining_tokens,
            'max_tokens': max_tokens,
            'usage_percentage': usage_percentage,
            'recent_usage': recent_usage,
            'last_updated': current_time.isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting token status: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 添加新的路由用于获取处理日志
@app.route('/processing-logs', methods=['GET'])
def get_processing_logs():
    try:
        with open('pdf_processing.log', 'r', encoding='utf-8') as f:
            logs = f.readlines()
        return jsonify({
            'logs': logs[-50:]  # 返回最后50行日志
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加新的路由用于重置token计数
@app.route('/reset-tokens', methods=['POST'])
def reset_tokens():
    try:
        global remaining_tokens
        remaining_tokens = 1000000
        logger.info(f"Token count reset to: {remaining_tokens}")
        return jsonify({
            'success': True,
            'remaining_tokens': remaining_tokens
        })
    except Exception as e:
        logger.error(f"Error resetting tokens: {str(e)}")
        return jsonify({'error': str(e)}), 500

class PDFProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = fitz.open(file_path)
        self.total_pages = len(self.doc)
        self.current_page = 0
        self.extracted_text = ""
        self.is_paused = False
        logger.info(f"Initialized PDF processor for {file_path} with {self.total_pages} pages")

    def get_next_page(self):
        """获取下一页的文本内容"""
        if self.current_page < self.total_pages:
            page = self.doc[self.current_page]
            self.extracted_text = page.get_text()
            page_info = {
                'page_number': self.current_page + 1,
                'total_pages': self.total_pages,
                'text': self.extracted_text
            }
            logger.info(f"Extracted text from page {self.current_page + 1}")
            return page_info
        return None

    def close(self):
        self.doc.close()
        logger.info("PDF document closed")

# 存储当前处理的PDF会话
pdf_sessions = {}

@app.route('/start-pdf-processing', methods=['POST'])
def start_pdf_processing():
    if 'file' not in request.files:
        logger.warning("No file uploaded")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.warning("No file selected")
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            logger.info(f"File saved: {file_path}")
            
            # 创建新的PDF处理会话
            session_id = str(uuid.uuid4())
            pdf_sessions[session_id] = {
                'processor': PDFProcessor(file_path),
                'output_content': [],
                'current_prompt': "Please convert this text into detailed markdown notes with headings, key points, and additional notes."
            }
            
            # 获取第一页内容
            first_page = pdf_sessions[session_id]['processor'].get_next_page()
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'page_info': first_page
            })
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    logger.warning(f"Unsupported file type: {file.filename}")
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/process-page', methods=['POST'])
def process_page():
    data = request.json
    session_id = data.get('session_id')
    custom_prompt = data.get('prompt')
    auto_continue = data.get('auto_continue', False)
    
    if not session_id or session_id not in pdf_sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = pdf_sessions[session_id]
    processor = session['processor']
    
    try:
        current_prompt = custom_prompt or session['current_prompt']
        ai_processor = AIProcessor("sk-LtHl3eFXpPn1HwbZ0LNVyRUJ0WlbaKvyl5gMsb6FODhBEw0X")
        
        response = ai_processor.process_text(
            processor.extracted_text,
            current_prompt
        )
        
        processed_content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # 获取输出文件路径
        output_filename = get_output_filename(os.path.basename(processor.file_path))
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # 添加页码信息并保存处理结果
        page_content = f"\n## 第 {processor.current_page + 1} 页\n\n{processed_content}\n"
        append_to_markdown(page_content, output_path, processor.current_page == 0)
        
        session['output_content'].append(processed_content)
        processor.current_page += 1
        next_page = processor.get_next_page()
        
        if not next_page or not auto_continue:
            if not next_page:
                logger.info(f"PDF processing completed, saved to: {output_path}")
                processor.close()
                del pdf_sessions[session_id]
                
                return jsonify({
                    'success': True,
                    'is_complete': True,
                    'output_file': output_filename,
                    'output_path': output_path
                })
        
        return jsonify({
            'success': True,
            'is_complete': False,
            'page_info': next_page,
            'last_processed': processed_content,
            'current_output_file': output_filename,
            'output_path': output_path
        })
        
    except Exception as e:
        logger.error(f"Error processing page: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/update-prompt', methods=['POST'])
def update_prompt():
    data = request.json
    session_id = data.get('session_id')
    new_prompt = data.get('prompt')
    
    if not session_id or session_id not in pdf_sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    pdf_sessions[session_id]['current_prompt'] = new_prompt
    return jsonify({'success': True})

# 添加新的辅助函数
def get_output_filename(original_filename, is_chat=False):
    """生成输出文件名"""
    today = datetime.now().strftime('%Y%m%d')
    if is_chat:
        return f"{today}_chat.md"
    else:
        # 移除.pdf后缀并添加日期
        base_name = original_filename.rsplit('.', 1)[0]
        return f"{today}_{base_name}.md"

def append_to_markdown(content, filepath, is_new_section=False):
    """追加内容到markdown文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # 如果是新章节，添加分隔符和时间戳
    if is_new_section:
        content = f"\n\n---\n### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{content}"
    
    # 追加内容到文件
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

# 添加保存聊天记录的路由
@app.route('/save-chat', methods=['POST'])
def save_chat():
    try:
        output_filename = get_output_filename("", is_chat=True)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # 格式化聊天记录
        chat_content = "# 聊天记录\n\n"
        for msg in chat_history:
            role = "用户" if msg["role"] == "user" else "AI助手"
            chat_content += f"### {role} ({datetime.now().strftime('%H:%M:%S')})\n\n{msg['content']}\n\n"
        
        # 保存聊天记录
        append_to_markdown(chat_content, output_path, True)
        
        return jsonify({
            'success': True,
            'output_file': output_filename,
            'output_path': output_path
        })
    except Exception as e:
        logger.error(f"Error saving chat history: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
